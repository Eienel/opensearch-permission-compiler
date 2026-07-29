from __future__ import annotations

import pytest

from permission_compiler.core import (
    Evidence,
    WorkflowError,
    compile_role,
    parse_evidence_document,
    parse_missing_privileges,
    validate_workflow,
    verify_workflow,
)


def workflow():
    return {
        "name": "reader",
        "role_name": "reader-observed",
        "steps": [
            {
                "id": "search",
                "method": "POST",
                "path": "/logs-*/_search",
                "index_patterns": ["logs-*"],
                "expect": "allow",
            },
            {
                "id": "health",
                "method": "GET",
                "path": "/_cluster/health",
                "index_patterns": [],
                "expect": "allow",
            },
            {
                "id": "delete",
                "method": "DELETE",
                "path": "/logs-2026",
                "index_patterns": ["logs-*"],
                "expect": "deny",
            },
        ],
    }


def test_parse_direct_missing_privileges():
    response = {
        "accessAllowed": False,
        "missingPrivileges": ["indices:data/read/search", "cluster:monitor/health"],
    }
    assert parse_missing_privileges(response) == (
        "cluster:monitor/health",
        "indices:data/read/search",
    )


def test_parse_nested_security_exception_with_bracketed_action():
    response = {
        "error": {
            "root_cause": [
                {
                    "reason": (
                        "no permissions for [indices:data/write/bulk[s]] and User "
                        "[name=a, backend_roles=[], requestedTenant=null]"
                    )
                }
            ]
        }
    }
    assert parse_missing_privileges(response) == ("indices:data/write/bulk[s]",)


def test_parse_audit_record():
    response = {
        "audit_category": "MISSING_PRIVILEGES",
        "audit_request_privilege": "indices:admin/get",
    }
    assert parse_missing_privileges(response) == ("indices:admin/get",)


def test_empty_permission_is_not_invented():
    response = {
        "error": {
            "reason": (
                "no permissions for [] and User "
                "[name=admin, backend_roles=[admin], requestedTenant=null]"
            )
        }
    }
    assert parse_missing_privileges(response) == ()


def test_workflow_rejects_duplicate_ids():
    document = workflow()
    document["steps"].append(document["steps"][0])
    with pytest.raises(WorkflowError, match="duplicate"):
        validate_workflow(document)


def test_compile_partitions_cluster_and_index_actions():
    evidence = [
        Evidence(
            "search", False, ("indices:data/read/search",), "test"
        ),
        Evidence(
            "health", False, ("cluster:monitor/health",), "test"
        ),
    ]
    candidate, report = compile_role(workflow(), evidence)
    role = candidate["reader-observed"]
    assert role["cluster_permissions"] == ["cluster:monitor/health"]
    assert role["index_permissions"][0]["index_patterns"] == ["logs-*"]
    assert role["index_permissions"][0]["allowed_actions"] == [
        "indices:data/read/search"
    ]
    assert report["unobserved_steps"] == ["delete"]
    assert report["permission_evidence"]["indices:data/read/search"] == {
        "steps": ["search"],
        "sources": ["test"],
        "index_patterns": ["logs-*"],
    }


def test_negative_evidence_never_creates_grant():
    evidence = [
        Evidence("delete", False, ("indices:admin/delete",), "test")
    ]
    candidate, _ = compile_role(workflow(), evidence)
    assert candidate["reader-observed"]["index_permissions"] == []


def test_allowed_negative_probe_is_violation():
    evidence = [Evidence("delete", True, (), "test")]
    _, report = compile_role(workflow(), evidence)
    assert report["negative_probe_violations"] == ["delete"]
    assert report["safe_to_review"] is False


def test_unscoped_index_permission_stops_review():
    document = workflow()
    document["steps"][0]["index_patterns"] = []
    evidence = [
        Evidence("search", False, ("indices:data/read/search",), "test")
    ]
    candidate, report = compile_role(document, evidence)
    assert candidate["reader-observed"]["index_permissions"] == []
    assert report["unscoped_index_actions"]
    assert report["safe_to_review"] is False


def test_unknown_evidence_step_stops_review():
    evidence = [Evidence("not-in-workflow", False, ("cluster:monitor/state",), "test")]
    _, report = compile_role(workflow(), evidence)
    assert report["unknown_evidence_steps"] == ["not-in-workflow"]
    assert report["safe_to_review"] is False


def test_parse_evidence_document_requires_step_id():
    with pytest.raises(WorkflowError, match="step_id"):
        parse_evidence_document({"response": {"accessAllowed": True}})


def test_verify_workflow_passes_positive_and_negative_contract():
    evidence = [
        Evidence("search", True, (), "after"),
        Evidence("health", True, (), "after"),
        Evidence("delete", False, ("indices:admin/delete",), "after"),
    ]
    report = verify_workflow(workflow(), evidence)
    assert report["passed"] is True
    assert {item["outcome"] for item in report["results"]} == {"passed"}


def test_verify_workflow_rejects_allowed_negative_probe():
    evidence = [
        Evidence("search", True, (), "after"),
        Evidence("health", True, (), "after"),
        Evidence("delete", True, (), "after"),
    ]
    report = verify_workflow(workflow(), evidence)
    assert report["passed"] is False
    assert report["negative_probe_violations"] == [{"step_id": "delete"}]


def test_verify_workflow_rejects_conflicting_observations():
    evidence = [
        Evidence("search", True, (), "run-1"),
        Evidence("search", False, ("indices:data/read/search",), "run-2"),
        Evidence("health", True, (), "after"),
        Evidence("delete", False, ("indices:admin/delete",), "after"),
    ]
    report = verify_workflow(workflow(), evidence)
    assert report["passed"] is False
    assert report["conflicting_steps"] == ["search"]
