from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

from permission_compiler.cli import (
    _permission_check_path,
    _ssl_context,
    main,
)
from permission_compiler.core import WorkflowError


def test_permission_check_path_preserves_existing_query():
    path = _permission_check_path("/logs/_search?preference=local")
    query = parse_qs(urlsplit(path).query)
    assert query == {
        "perform_permission_check": ["true"],
        "preference": ["local"],
    }


def test_skip_hostname_verification_requires_ca():
    with pytest.raises(WorkflowError, match="requires --ca-cert"):
        _ssl_context(None, skip_hostname_verification=True)


def test_probe_is_permission_check_and_does_not_persist_credentials(
    tmp_path, monkeypatch
):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            requests.append(
                {
                    "path": self.path,
                    "authorization": self.headers.get("Authorization"),
                    "body": self.rfile.read(length).decode("utf-8"),
                }
            )
            payload = json.dumps(
                {
                    "accessAllowed": False,
                    "missingPrivileges": ["indices:data/read/search"],
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        workflow_path = tmp_path / "workflow.json"
        evidence_path = tmp_path / "evidence.json"
        workflow_path.write_text(
            json.dumps(
                {
                    "name": "query",
                    "steps": [
                        {
                            "id": "search",
                            "method": "POST",
                            "path": "/logs/_search",
                            "body": {"query": {"match_all": {}}},
                            "index_patterns": ["logs"],
                            "expect": "allow",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("OPENSEARCH_USERNAME", "test-user")
        monkeypatch.setenv("OPENSEARCH_PASSWORD", "correct-horse")
        exit_code = main(
            [
                "probe",
                "--workflow",
                str(workflow_path),
                "--output",
                str(evidence_path),
                "--url",
                f"http://127.0.0.1:{server.server_port}",
            ]
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert exit_code == 0
    assert len(requests) == 1
    query = parse_qs(urlsplit(requests[0]["path"]).query)
    assert query["perform_permission_check"] == ["true"]
    assert requests[0]["authorization"].startswith("Basic ")
    persisted = evidence_path.read_text(encoding="utf-8")
    assert "correct-horse" not in persisted
    assert "test-user" not in persisted
    assert "Authorization" not in persisted
