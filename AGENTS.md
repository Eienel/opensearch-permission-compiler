# Project guidance

## Purpose

Build an Apache-2.0 OpenSearch Agent Skill that compiles representative
workflows into evidence-backed, observed-minimum Security role candidates.

## Non-negotiable safety invariants

- Do not claim mathematical least privilege.
- Do not infer index patterns.
- Do not derive grants from negative probes.
- Do not execute mutating discovery requests.
- Do not apply generated roles automatically.
- Do not persist credentials or authorization headers.
- Verify TLS by default.
- Do not invent a permission when OpenSearch reports
  `no permissions for []`.

## Commands

```bash
python -m pytest
python skills/permission-compiler/scripts/permission_compiler.py --help
python skills/permission-compiler/scripts/permission_compiler.py compile \
  --workflow skills/permission-compiler/assets/ppl-readonly-workflow.json \
  --evidence examples/ppl-evidence.json \
  --output build/candidate-role.json \
  --report build/evidence-report.json
python skills/permission-compiler/scripts/permission_compiler.py verify \
  --workflow skills/permission-compiler/assets/ppl-readonly-workflow.json \
  --evidence examples/ppl-verification-evidence.json \
  --report build/verification-report.json
```

## Conventions

- Python 3.11+ and standard-library runtime dependencies.
- Tests must not require a live cluster; end-to-end tests use disposable
  containers and must be separately marked.
- Keep `SKILL.md` under 500 lines and move detail to focused references.
- Every emitted permission must retain step and evidence provenance.
- A change to compiler behavior requires a unit test.
