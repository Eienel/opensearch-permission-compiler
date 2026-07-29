# Disposable live integration

This fixture proves the compiler against OpenSearch 3.7.0 with the Security
plugin enabled. It is intentionally limited to a disposable, single-node
container.

## Prerequisites

- Docker Desktop with at least 4 GB available
- Python 3.11 or newer
- PowerShell 7 or Windows PowerShell 5.1
- FFmpeg and Pillow only when rendering the optional video

Run:

```powershell
.\scripts\demo.ps1
```

The harness generates fresh administrator and test-user passwords in memory,
starts a localhost-only cluster, copies its demo CA, and seeds one synthetic
log document. It first maps the test user to an empty role, gathers
`perform_permission_check=true` evidence, compiles a candidate, and then
explicitly applies that candidate. A second probe must allow both required
operations and deny both forbidden operations.

The live contract uses the standard Search API. In OpenSearch 3.7.0, the PPL
endpoint returns an `Unexpected exception cluster:admin/opensearch/ppl` error
under `perform_permission_check=true` instead of a reliable
`missingPrivileges` list. The compiler deliberately treats that response as
unresolved evidence and does not guess a PPL grant.

Generated evidence is written to `integration/build/`. Credentials are not
written there. Unless `-KeepCluster` is specified, the container and its named
volume are removed in a `finally` block.

## Safety boundaries

- Never point `setup_cluster.py` at a shared or production cluster.
- The compiler still never applies roles; application lives only in this
  explicit demo harness.
- The bundled demo node certificate does not name `localhost`. The harness
  verifies its copied CA chain but disables hostname matching. This is a
  disposable-demo exception, not production guidance.
- Permission discovery is non-mutating. Mutating workflow methods are sent
  only with `perform_permission_check=true`.
- Negative probes are assertions and never contribute grants.

## Optional recording

```powershell
.\scripts\record_demo.ps1
```

This writes a sanitized transcript and an MP4 to `demo/`. It renders only
purpose-built slides from the transcript and JSON artifacts; it does not
capture the screen.
