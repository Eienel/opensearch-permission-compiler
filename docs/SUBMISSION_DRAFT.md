# Draft hackathon submission

## Submission name

OpenSearch Permission Compiler

## Team

`@your-github-username`

Replace this placeholder before registration.

## What are you building?

OpenSearch Permission Compiler is an agent skill that turns a representative
user or service workflow into an evidence-backed, observed-minimum OpenSearch
Security role.

OpenSearch authorizes underlying transport actions rather than REST routes, so
one user-visible operation can require several non-obvious permissions. Today,
administrators discover those permissions by creating a test user, executing
requests, reading 403 or `MISSING_PRIVILEGES` output, adding a permission, and
repeating. Teams often fall back to broad roles when this loop becomes slow or
uncertain.

The skill asks the user to define a capability contract: operations that must
succeed, operations that must remain denied, and explicit index boundaries. It
then runs non-mutating `perform_permission_check=true` probes, normalizes
OpenSearch permission and audit evidence, compiles exact observed actions into
a candidate role, and produces a coverage and blast-radius report. It refuses
to infer missing index scopes, flags wildcards, never treats denied negative
tests as grant evidence, and never applies a role without human review.

The result is a repeatable workflow primitive for PPL, Dashboards, search,
ingest, snapshots, monitoring, and future OpenSearch plugins - without a
proprietary dependency.

## Additional information

- Python 3.11+ with no runtime dependencies.
- Apache 2.0.
- TLS verification and secret-safe defaults.
- Works from OpenSearch-native permission checks and Security audit records.
- Unit tests require no cluster; end-to-end Docker validation is planned.
- Output is explicitly "observed minimum," preventing false claims of
  mathematical least privilege.

## Five-minute demo spine

1. Show PPL autocomplete failing with a hidden
   `indices:monitor/settings/get` permission.
2. Show the capability contract with allowed query/autocomplete steps and
   denied delete/security-index steps.
3. Run safe probes and compile the candidate.
4. Open the evidence report: exact action provenance, no inferred scope, and
   wildcard warnings.
5. Apply the role to a disposable test user.
6. Re-run: PPL works; index deletion and security-index access remain denied.
7. Close with measurable impact: minutes to a reviewable role, zero mutating
   discovery requests, and machine-verifiable negative boundaries.
