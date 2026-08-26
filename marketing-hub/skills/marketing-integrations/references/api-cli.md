# Provider-neutral API CLI

`scripts/api_request.py` is a standard-library HTTP adapter for marketing systems that expose a REST API. It replaces frozen vendor aliases with an explicit request assembled from current official documentation.

Use an existing authorized MCP, official CLI, or SDK when it already provides the operation safely. Use this adapter when the API contract is simple, the exact endpoint has been verified, and installing another dependency adds no value.

## Contract

- credentials come from named environment variables, never command values;
- the base URL must use HTTPS unless a localhost-only testing flag is supplied;
- the path must be relative to the base URL;
- GET, HEAD, and OPTIONS are treated as reads;
- every other method requires both `--execute-write` and a non-empty `--approval` value;
- `--dry-run` emits a redacted request and makes no network call;
- response bodies are bounded and returned as JSON, text, or base64;
- HTTP failures remain machine-readable and produce a nonzero exit code.

The approval string is an audit label, not proof of human consent. The operating agent must still obtain task-specific authorization before supplying it.

## Examples

Dry-run a bearer-authenticated read:

```text
python -B scripts/api_request.py \
  --base-url https://api.vendor.example/v1/ \
  --path reports \
  --auth bearer \
  --credential-env VENDOR_ACCESS_TOKEN \
  --query-json '{"start":"2026-08-01","end":"2026-08-26"}' \
  --dry-run
```

Execute an authorized JSON mutation:

```text
python -B scripts/api_request.py \
  --base-url https://api.vendor.example/v1/ \
  --path drafts \
  --method POST \
  --auth header \
  --auth-header X-API-Key \
  --credential-env VENDOR_API_KEY \
  --body-json '{"name":"Reviewed draft"}' \
  --execute-write \
  --approval approved-draft-creation
```

Other supported authentication shapes are Basic auth, a credential in a named query parameter, no authentication, and additional headers populated from environment variables.

## Request preparation

Before using the CLI, record the official documentation URL and checked date, API version, account and environment, scopes, method and endpoint, query and body schema, pagination, rate behavior, idempotency, expected response, sensitive fields, and verification read.

Do not use a generic request adapter to bypass a vendor's required signing flow, OAuth exchange, SDK-only safety checks, or upload protocol. Build a narrow adapter or use the official client when those mechanics are part of the contract.

## Exit behavior

- `0`: dry run or successful 2xx response;
- `2`: invalid input, missing credential, unsafe URL, or missing write gate;
- `3`: HTTP response outside 2xx;
- `4`: network, timeout, or response-processing failure.

The result includes method, redacted URL, status, selected response headers, decoded body, truncation state, and the approval label for an executed mutation. Secret-looking header and query fields are redacted.
