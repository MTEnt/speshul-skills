#!/usr/bin/env python3
"""Bounded, provider-neutral JSON HTTP client for verified marketing APIs."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


READ_METHODS = {"GET", "HEAD", "OPTIONS"}
SECRET_PARTS = ("authorization", "api-key", "apikey", "secret", "token", "password")
DEFAULT_LIMIT = 5 * 1024 * 1024


class InputError(ValueError):
    pass


def json_object(raw: str | None, label: str) -> dict[str, Any]:
    if raw is None:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"{label} must be valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{label} must decode to an object")
    return value


def key_value(items: list[str], label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise InputError(f"{label} entry must use NAME=VALUE")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise InputError(f"{label} name cannot be empty")
        result[key] = value
    return result


def required_env(name: str | None) -> str:
    if not name:
        raise InputError("the selected authentication mode requires --credential-env")
    value = os.environ.get(name)
    if not value:
        raise InputError(f"required credential environment variable is missing: {name}")
    return value


def is_secret_name(name: str) -> bool:
    normalized = name.lower().replace("_", "-")
    return any(part in normalized for part in SECRET_PARTS)


def redact_mapping(values: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in values.items():
        if is_secret_name(str(key)):
            redacted[key] = "***"
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        elif isinstance(value, list):
            redacted[key] = [redact_mapping(v) if isinstance(v, dict) else v for v in value]
        else:
            redacted[key] = value
    return redacted


def validate_base_url(raw: str, allow_http_localhost: bool) -> str:
    parsed = urllib.parse.urlsplit(raw)
    if not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise InputError("--base-url must contain only scheme, host, optional port, and base path")
    host = (parsed.hostname or "").lower()
    local = host in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (allow_http_localhost and parsed.scheme == "http" and local):
        raise InputError("--base-url must use HTTPS; HTTP is allowed only for localhost testing")
    return raw if raw.endswith("/") else raw + "/"


def build_request(args: argparse.Namespace, include_credentials: bool) -> tuple[str, dict[str, str], bytes | None, dict[str, Any]]:
    base = validate_base_url(args.base_url, args.allow_http_localhost)
    if urllib.parse.urlsplit(args.path).scheme or args.path.startswith("//"):
        raise InputError("--path must be relative to --base-url")

    query = json_object(args.query_json, "--query-json")
    body = json_object(args.body_json, "--body-json") if args.body_json is not None else None
    headers = key_value(args.header, "--header")
    env_headers = key_value(args.env_header, "--env-header")
    for header, env_name in env_headers.items():
        headers[header] = required_env(env_name) if include_credentials else f"${{{env_name}}}"

    credential = required_env(args.credential_env) if include_credentials and args.auth != "none" else None
    if args.auth == "bearer":
        headers["Authorization"] = f"Bearer {credential}" if include_credentials else f"Bearer ${{{args.credential_env}}}"
    elif args.auth == "header":
        if not args.auth_header:
            raise InputError("header authentication requires --auth-header")
        headers[args.auth_header] = credential if include_credentials else f"${{{args.credential_env}}}"
    elif args.auth == "basic":
        username = credential or ""
        password = required_env(args.secret_env) if include_credentials else f"${{{args.secret_env}}}"
        if not args.secret_env:
            raise InputError("basic authentication requires --secret-env")
        if include_credentials:
            token = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        else:
            headers["Authorization"] = f"Basic ${{{args.credential_env}}}:${{{args.secret_env}}}"
    elif args.auth == "query":
        if not args.auth_query:
            raise InputError("query authentication requires --auth-query")
        query[args.auth_query] = credential if include_credentials else f"${{{args.credential_env}}}"

    url = urllib.parse.urljoin(base, args.path.lstrip("/"))
    if query:
        encoded = urllib.parse.urlencode(query, doseq=True)
        url += ("&" if "?" in url else "?") + encoded

    payload: bytes | None = None
    if body is not None:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    headers.setdefault("Accept", "application/json")
    headers.setdefault("User-Agent", "speshul-marketing-api/1.0")

    preview = {
        "method": args.method,
        "url": redact_url(url),
        "headers": redact_mapping(headers),
        "body": redact_mapping(body) if body is not None else None,
    }
    return url, headers, payload, preview


def redact_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    safe = [(key, "***" if is_secret_name(key) else value) for key, value in pairs]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(safe), ""))


def decode_body(data: bytes, content_type: str) -> tuple[str, Any]:
    if not data:
        return "empty", None
    charset = "utf-8"
    for part in content_type.split(";")[1:]:
        if part.strip().lower().startswith("charset="):
            charset = part.split("=", 1)[1].strip()
    try:
        text = data.decode(charset, errors="strict")
    except (LookupError, UnicodeDecodeError):
        return "base64", base64.b64encode(data).decode("ascii")
    if "json" in content_type.lower() or text.lstrip().startswith(("{", "[")):
        try:
            return "json", json.loads(text)
        except json.JSONDecodeError:
            pass
    return "text", text


def selected_headers(headers: Any) -> dict[str, str]:
    keep = {"content-type", "date", "etag", "last-modified", "location", "request-id", "retry-after", "x-request-id", "x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset"}
    return {key: value for key, value in headers.items() if key.lower() in keep}


def emit(value: dict[str, Any], stream: Any = sys.stdout) -> None:
    print(json.dumps(value, indent=2, sort_keys=True), file=stream)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--base-url", required=True)
    result.add_argument("--path", required=True)
    result.add_argument("--method", default="GET", type=str.upper)
    result.add_argument("--query-json")
    result.add_argument("--body-json")
    result.add_argument("--header", action="append", default=[], metavar="NAME=VALUE")
    result.add_argument("--env-header", action="append", default=[], metavar="NAME=ENV_VAR")
    result.add_argument("--auth", choices=("none", "bearer", "header", "basic", "query"), default="none")
    result.add_argument("--credential-env")
    result.add_argument("--secret-env")
    result.add_argument("--auth-header", default="X-API-Key")
    result.add_argument("--auth-query", default="api_key")
    result.add_argument("--timeout", type=float, default=30.0)
    result.add_argument("--max-response-bytes", type=int, default=DEFAULT_LIMIT)
    result.add_argument("--dry-run", action="store_true")
    result.add_argument("--execute-write", action="store_true")
    result.add_argument("--approval")
    result.add_argument("--allow-http-localhost", action="store_true", help=argparse.SUPPRESS)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.timeout <= 0 or args.timeout > 300:
            raise InputError("--timeout must be greater than 0 and no more than 300 seconds")
        if args.max_response_bytes <= 0 or args.max_response_bytes > 50 * 1024 * 1024:
            raise InputError("--max-response-bytes must be between 1 and 52428800")
        write = args.method not in READ_METHODS
        if write and not args.dry_run and (not args.execute_write or not args.approval):
            raise InputError("write methods require --execute-write and a non-empty --approval label")

        url, headers, payload, preview = build_request(args, include_credentials=not args.dry_run)
        if args.dry_run:
            emit({"dry_run": True, "write": write, "request": preview})
            return 0

        request = urllib.request.Request(url, data=payload, headers=headers, method=args.method)
        try:
            response = urllib.request.urlopen(request, timeout=args.timeout)
            status = response.status
            response_headers = response.headers
            data = response.read(args.max_response_bytes + 1)
        except urllib.error.HTTPError as exc:
            status = exc.code
            response_headers = exc.headers
            data = exc.read(args.max_response_bytes + 1)

        truncated = len(data) > args.max_response_bytes
        data = data[: args.max_response_bytes]
        body_kind, body = decode_body(data, response_headers.get("Content-Type", ""))
        result = {
            "ok": 200 <= status < 300,
            "method": args.method,
            "url": redact_url(url),
            "status": status,
            "headers": selected_headers(response_headers),
            "body_kind": body_kind,
            "body": body,
            "truncated": truncated,
            "approval": args.approval if write else None,
        }
        emit(result)
        return 0 if result["ok"] else 3
    except InputError as exc:
        emit({"error": str(exc), "kind": "input"}, sys.stderr)
        return 2
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        emit({"error": str(exc), "kind": "network"}, sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
