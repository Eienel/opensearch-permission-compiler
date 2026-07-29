#!/usr/bin/env python3
"""Set up and explicitly apply roles in the disposable integration cluster."""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEMO_INDEX = "permission-demo-logs-2026.07.29"
EMPTY_ROLE = "permission-compiler-empty"
DEMO_USER = "permission-compiler-user"


def request_json(
    base_url: str,
    method: str,
    path: str,
    username: str,
    password: str,
    body=None,
    ca_cert: str | None = None,
):
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, data=data, method=method)
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    request.add_header("Authorization", f"Basic {token}")
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    context = ssl.create_default_context(cafile=ca_cert)
    if ca_cert:
        # OpenSearch's bundled demo node certificate is issued by the copied
        # CA but names the container node rather than localhost.
        context.check_hostname = False
    try:
        with urlopen(request, context=context, timeout=15) as response:
            payload = response.read().decode("utf-8")
            return response.status, json.loads(payload) if payload else {}
    except HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = {"raw": payload}
        return exc.code, parsed


def require_success(status: int, payload, operation: str):
    if not 200 <= status < 300:
        raise RuntimeError(
            f"{operation} failed with HTTP {status}: "
            f"{json.dumps(payload, sort_keys=True)}"
        )


def wait_for_cluster(args):
    deadline = time.monotonic() + args.wait_seconds
    last_error = "cluster not contacted"
    while time.monotonic() < deadline:
        try:
            status, payload = request_json(
                args.url,
                "GET",
                "/_cluster/health",
                args.admin_user,
                args.admin_password,
                ca_cert=args.ca_cert,
            )
            if 200 <= status < 300:
                print(f"OpenSearch ready: {payload.get('status', 'unknown')}")
                return
            last_error = f"HTTP {status}"
        except (URLError, TimeoutError, ssl.SSLError) as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"OpenSearch did not become ready: {last_error}")


def setup(args):
    wait_for_cluster(args)
    operations = [
        (
            "create empty role",
            "PUT",
            f"/_plugins/_security/api/roles/{EMPTY_ROLE}",
            {
                "cluster_permissions": [],
                "index_permissions": [],
                "tenant_permissions": [],
            },
        ),
        (
            "create demo user",
            "PUT",
            f"/_plugins/_security/api/internalusers/{DEMO_USER}",
            {
                "password": args.test_password,
                "backend_roles": [],
                "attributes": {},
            },
        ),
        (
            "map empty role",
            "PUT",
            f"/_plugins/_security/api/rolesmapping/{EMPTY_ROLE}",
            {"backend_roles": [], "hosts": [], "users": [DEMO_USER]},
        ),
        (
            "seed demo document",
            "PUT",
            f"/{DEMO_INDEX}/_doc/1?refresh=true",
            {
                "@timestamp": "2026-07-29T09:00:00Z",
                "service": "checkout",
                "message": "permission compiler live demo",
            },
        ),
    ]
    for label, method, path, body in operations:
        status, payload = request_json(
            args.url,
            method,
            path,
            args.admin_user,
            args.admin_password,
            body,
            args.ca_cert,
        )
        require_success(status, payload, label)
        print(f"Configured: {label}")


def apply_role(args):
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    if len(candidate) != 1:
        raise RuntimeError("candidate role file must contain exactly one role")
    role_name, role_body = next(iter(candidate.items()))
    status, payload = request_json(
        args.url,
        "PUT",
        f"/_plugins/_security/api/roles/{role_name}",
        args.admin_user,
        args.admin_password,
        role_body,
        args.ca_cert,
    )
    require_success(status, payload, "apply candidate role")
    status, payload = request_json(
        args.url,
        "PUT",
        f"/_plugins/_security/api/rolesmapping/{role_name}",
        args.admin_user,
        args.admin_password,
        {"backend_roles": [], "hosts": [], "users": [DEMO_USER]},
        args.ca_cert,
    )
    require_success(status, payload, "map candidate role")
    status, payload = request_json(
        args.url,
        "PUT",
        f"/_plugins/_security/api/rolesmapping/{EMPTY_ROLE}",
        args.admin_user,
        args.admin_password,
        {"backend_roles": [], "hosts": [], "users": []},
        args.ca_cert,
    )
    require_success(status, payload, "remove empty role mapping")
    print(f"Explicitly applied and mapped candidate role: {role_name}")


def parser():
    result = argparse.ArgumentParser()
    result.add_argument("command", choices=["setup", "apply-role"])
    result.add_argument("--url", default="https://localhost:9200")
    result.add_argument("--admin-user", default="admin")
    result.add_argument(
        "--admin-password",
        default=os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"),
    )
    result.add_argument("--test-password", default=os.getenv("DEMO_TEST_PASSWORD"))
    result.add_argument("--ca-cert")
    result.add_argument("--candidate")
    result.add_argument("--wait-seconds", type=int, default=180)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if not args.admin_password:
        print("error: administrator password is required", file=sys.stderr)
        return 2
    if args.command == "setup":
        if not args.test_password:
            print("error: test password is required", file=sys.stderr)
            return 2
        setup(args)
    else:
        if not args.candidate:
            print("error: --candidate is required", file=sys.stderr)
            return 2
        apply_role(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
