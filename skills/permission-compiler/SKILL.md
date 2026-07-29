---
name: permission-compiler
description: >
  Compile a representative OpenSearch workflow into an evidence-backed,
  observed-minimum Security role. Use when a user is debugging 403 or
  MISSING_PRIVILEGES errors, designing least-privilege roles, validating
  permissions for PPL, Dashboards, snapshots, ingest, search, or automation,
  or replacing broad all_access and security_rest_api_access grants.
metadata:
  version: "0.1.0"
---

# OpenSearch Permission Compiler

Turn what a service must do into a narrow, reviewable role candidate backed by
OpenSearch's own permission decisions.

## Key rules

1. Never claim mathematical least privilege. The output is the minimum observed
   for the representative workflow and evidence supplied.
2. Never infer an index pattern. Require the user or workflow manifest to name
   the intended index boundary.
3. Never execute a mutating probe. Add `perform_permission_check=true` to every
   representative request.
4. Never apply a generated role automatically. Emit a candidate, evidence
   coverage, wildcards, and negative-test results for human review.
5. Never derive grants from a negative probe. A denied operation is an
   invariant that must remain denied.
6. Prefer exact actions observed from OpenSearch. Do not replace them with a
   broader action group merely for convenience.
7. Credentials must come from environment variables or the user's secret
   manager. Do not write credentials into workflow or evidence files.
8. Verify TLS by default. Require a CA certificate for private certificate
   authorities; do not silently disable verification.

## Workflow

### 1. Define the capability contract

Create a JSON workflow with:

- a stable workflow name and candidate role name;
- one representative request per required operation;
- explicit `index_patterns` for index-scoped operations;
- `expect: "allow"` for required operations;
- `expect: "deny"` for destructive or out-of-scope operations.

Start from [workflow-schema.md](workflow-schema.md) and the bundled
[example workflow](assets/ppl-readonly-workflow.json).

### 2. Run safe probes

Use test-user credentials, never the administrator identity:
Run commands from this skill's directory so all bundled paths resolve.

```bash
export OPENSEARCH_URL="https://localhost:9200"
export OPENSEARCH_USERNAME="workflow-test-user"
export OPENSEARCH_PASSWORD="..."

python scripts/permission_compiler.py probe \
  --workflow assets/ppl-readonly-workflow.json \
  --ca-cert /path/to/root-ca.pem \
  --output build/evidence.json
```

The probe adds `perform_permission_check=true`; write-like requests are
authorized but not executed.

### 3. Compile exact observed actions

```bash
python scripts/permission_compiler.py compile \
  --workflow assets/ppl-readonly-workflow.json \
  --evidence build/evidence.json \
  --output build/candidate-role.json \
  --report build/evidence-report.json
```

Stop if the report contains:

- unknown evidence steps;
- index actions with no declared index scope;
- a negative probe that was allowed.

Treat wildcards as a mandatory review item.

### 4. Review blast radius

For each permission, show:

- which workflow step produced it;
- whether it is cluster- or index-scoped;
- the declared index boundary;
- whether it contains a wildcard;
- which negative probes protect the boundary.

Do not hide raw OpenSearch action names behind a narrative summary.

### 5. Validate after a human applies the candidate

Re-run every positive and negative probe using the test identity.

```bash
python scripts/permission_compiler.py verify \
  --workflow assets/ppl-readonly-workflow.json \
  --evidence build/post-apply-evidence.json \
  --report build/verification-report.json
```

Success requires:

- every positive probe is allowed;
- every negative probe is denied;
- no unobserved required step remains;
- no permission was added without evidence or an explicit reviewed exception.

### 6. Produce the handoff

Return:

1. candidate role JSON;
2. evidence and coverage report;
3. unresolved gaps;
4. exact commands for a human administrator to review and apply;
5. rollback instructions;
6. an explicit statement that production traffic may exercise capabilities
   absent from the representative workflow.

## Interpreting common evidence

- `missingPrivileges`: use the exact returned actions.
- `security_exception` with `no permissions for [...]`: extract the action list.
- audit category `MISSING_PRIVILEGES`: use `audit_request_privilege`.
- `no permissions for []`: do not invent an action. Flag it for manual
  investigation, because system-index or administrator-certificate rules may
  be involved.

## Completion condition

The task is complete only when the candidate is evidence-backed, positive
probes pass, negative probes remain denied, and the remaining uncertainty is
stated plainly.
