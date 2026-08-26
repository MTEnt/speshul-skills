from __future__ import annotations

import contextlib
import http.server
import json
import os
import pathlib
import subprocess
import sys
import threading
import unittest


SCRIPT = pathlib.Path(__file__).with_name("api_request.py")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps({"path": self.path, "authorization": self.headers.get("Authorization")}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: object) -> None:
        return


class ApiRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-B", str(SCRIPT), "--base-url", self.base, "--allow-http-localhost", *args]
        return subprocess.run(command, text=True, capture_output=True, env=env, check=False)

    def test_dry_run_masks_credential_without_requiring_environment(self) -> None:
        result = self.run_cli("--path", "reports", "--auth", "bearer", "--credential-env", "MISSING_TOKEN", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["request"]["headers"]["Authorization"], "***")

    def test_read_uses_environment_credential(self) -> None:
        env = os.environ.copy()
        env["TEST_TOKEN"] = "secret-value"
        result = self.run_cli("--path", "items", "--auth", "bearer", "--credential-env", "TEST_TOKEN", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["body"]["authorization"], "Bearer secret-value")
        self.assertNotIn("secret-value", payload["url"])

    def test_write_requires_both_gates(self) -> None:
        result = self.run_cli("--path", "drafts", "--method", "POST", "--body-json", "{}")
        self.assertEqual(result.returncode, 2)
        self.assertIn("execute-write", result.stderr)

    def test_authorized_write_returns_json(self) -> None:
        result = self.run_cli(
            "--path", "drafts",
            "--method", "POST",
            "--body-json", '{"name":"draft"}',
            "--execute-write",
            "--approval", "test-only",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], 201)
        self.assertEqual(payload["body"], {"name": "draft"})
        self.assertEqual(payload["approval"], "test-only")

    def test_rejects_non_https_remote_url(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--base-url", "http://example.test/", "--path", "x", "--dry-run"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("HTTPS", result.stderr)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        unittest.main()
