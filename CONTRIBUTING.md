# Contributing

Thank you for improving OpenSearch Permission Compiler.

## Development

Use Python 3.11 or newer:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest
```

On macOS or Linux, use `.venv/bin/python`.

## Pull requests

- Preserve every safety invariant in `AGENTS.md`.
- Add or update tests for behavior changes.
- Keep runtime dependencies vendor-neutral and minimal.
- Do not include credentials, authorization headers, production data, or
  private audit records.
- Run the full test suite before opening a pull request.
- Sign commits with the Developer Certificate of Origin:

```bash
git commit -s -m "Describe the change"
```

DCO signoff is required if the change is later contributed to the OpenSearch
Project.

## Proposed upstream layout

An OpenSearch contribution will likely place the leaf skill under:

```text
skills/opensearch-skills/security/permission-compiler/
```

That upstream change should also add a security category router, update the
top-level router and README, add tests, and update the upstream changelog.
Maintainer guidance takes precedence.
