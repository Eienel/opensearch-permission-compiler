# Workflow schema

The compiler accepts a JSON object:

```json
{
  "name": "ppl-readonly",
  "role_name": "ppl-readonly-observed",
  "steps": [
    {
      "id": "query-logs",
      "method": "POST",
      "path": "/_plugins/_ppl",
      "body": {"query": "source=logs-* | head 10"},
      "index_patterns": ["logs-*"],
      "expect": "allow"
    },
    {
      "id": "must-not-delete",
      "method": "DELETE",
      "path": "/logs-2026.07.29",
      "index_patterns": ["logs-*"],
      "expect": "deny"
    }
  ]
}
```

## Fields

- `name`: stable capability-contract name.
- `role_name`: OpenSearch role name to emit.
- `steps[].id`: stable evidence join key.
- `steps[].method`: HTTP method.
- `steps[].path`: path beginning with `/`.
- `steps[].body`: optional JSON request body.
- `steps[].index_patterns`: the intended data boundary. Required whenever
  evidence yields an `indices:*` action.
- `steps[].expect`: `allow` or `deny`.
- `tenant_permissions`: optional, explicitly reviewed tenant grants. Tenant
  permissions are not inferred from transport-action errors.

The current format is intentionally small. It captures the security contract,
not a general API test suite.
