# OpenSearch Permission Compiler

Compile a representative OpenSearch workflow into an evidence-backed,
observed-minimum Security role - then prove that out-of-scope actions remain
denied.

## Why this exists

OpenSearch permissions govern underlying transport actions, not HTTP routes.
One API request can require several actions, and permission failures may reveal
them incrementally. The documented manual workflow is to create a test user,
run representative requests, add missing permissions, and repeat.

Permission Compiler turns that trial-and-error loop into a capability contract:

1. describe required and forbidden requests;
2. probe them with OpenSearch's non-mutating
   `perform_permission_check=true`;
3. compile exact observed actions into a candidate role;
4. reject unscoped index grants and allowed negative probes;
5. return evidence coverage and wildcard warnings for human review.

It does not claim a mathematically minimal role. It produces the minimum
observed by the supplied workflow.

## Status

This is the first production-oriented foundation:

- deterministic response and audit-record parsing;
- exact cluster/index permission partitioning;
- negative probes that never become grants;
- safe, TLS-verified permission-check runner;
- evidence coverage, wildcard, and scope reporting;
- post-application verification of required and forbidden operations;
- Agent Skills specification-compatible `SKILL.md`;
- unit tests with no running cluster required.

The repository also includes a Docker-backed end-to-end fixture that applies a
reviewed candidate to a disposable test user and proves required operations are
allowed while forbidden operations stay denied.

## Quick start

Python 3.11+ is required. The compiler has no runtime dependencies.

```bash
python skills/permission-compiler/scripts/permission_compiler.py compile \
  --workflow skills/permission-compiler/assets/ppl-readonly-workflow.json \
  --evidence examples/ppl-evidence.json \
  --output build/candidate-role.json \
  --report build/evidence-report.json
```

Verify a post-application evidence run:

```bash
python skills/permission-compiler/scripts/permission_compiler.py verify \
  --workflow skills/permission-compiler/assets/ppl-readonly-workflow.json \
  --evidence examples/ppl-verification-evidence.json \
  --report build/verification-report.json
```

Probe a real test identity:

```bash
export OPENSEARCH_URL="https://localhost:9200"
export OPENSEARCH_USERNAME="workflow-test-user"
export OPENSEARCH_PASSWORD="..."

python skills/permission-compiler/scripts/permission_compiler.py probe \
  --workflow skills/permission-compiler/assets/ppl-readonly-workflow.json \
  --ca-cert /path/to/root-ca.pem \
  --output build/evidence.json
```

Credentials are read from environment variables and are never persisted.

## Safety model

- Mutating probes always include `perform_permission_check=true`.
- TLS verification is on by default; there is no silent insecure mode.
- Index-scoped actions without an explicit index pattern block review.
- Negative probes are assertions and cannot create grants.
- Generated roles are never applied automatically.
- Wildcards are reported as mandatory review items.
- Raw `no permissions for []` errors are not guessed.

See [the skill](skills/permission-compiler/SKILL.md) for the complete agent
workflow and [the schema](skills/permission-compiler/workflow-schema.md) for the
capability-contract format.

## Research and selection trail

- [Rules checklist](docs/RULES_CHECKLIST.md)
- [Pain-point research](docs/RESEARCH.md)
- [Idea Interrogator results](docs/IDEA_INTERROGATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Draft hackathon submission](docs/SUBMISSION_DRAFT.md)

## Test

```bash
python -m pytest
```

## Live OpenSearch demo

The disposable integration pins OpenSearch 3.7.0, enables the Security plugin,
binds port 9200 to localhost only, and deletes its Docker volume afterward:

```powershell
.\scripts\demo.ps1
```

The demo uses OpenSearch's bundled development certificates. It verifies the
copied CA chain while explicitly skipping hostname matching because the demo
node certificate names the container rather than `localhost`. Do not use that
option for production clusters.

To run the same demo, retain a sanitized transcript, and render a short MP4:

```powershell
.\scripts\record_demo.ps1
```

Recording requires FFmpeg and Pillow. The video is generated only from the
dedicated demo transcript and verification artifacts; it never captures the
desktop or credential environment.

[Watch the verified live-demo recording](demo/permission-compiler-live-demo.mp4).

See [the integration guide](integration/README.md) for prerequisites, safety
boundaries, artifact locations, and cleanup behavior.

## License

Apache License 2.0.
