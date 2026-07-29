# Architecture

```text
Capability contract
  positive requests + negative requests + explicit index boundaries
            |
            v
Safe probe runner
  TLS verified + test identity + perform_permission_check=true
            |
            v
Evidence normalizer
  missingPrivileges | security_exception | audit MISSING_PRIVILEGES
            |
            v
Deterministic compiler
  exact cluster actions + exact index actions grouped by declared patterns
            |
            +--------------------+
            |                    |
            v                    v
Candidate role JSON       Evidence report
                          coverage, wildcards,
                          unscoped grants,
                          negative violations
            |                    |
            +---------+----------+
                      v
              Human review/apply
                      |
                      v
              Positive + negative
                validation rerun
```

## Boundary decisions

- The agent chooses representative workflows with the user; code decides how
  evidence becomes a role.
- The compiler emits exact observed action names instead of broad action
  groups.
- Index scope is declared, never inferred from an error string.
- Negative tests are first-class contract assertions.
- Applying a role is outside the automated boundary in v0.1.
- The executable and its Python package live inside the skill folder so a
  standalone Agent Skill installation remains functional.

## Threat model

| Threat | Control |
|---|---|
| A probe mutates production | Always add `perform_permission_check=true`; use a test identity. |
| Credential leakage | Environment variables only; never include authorization headers in evidence. |
| Man-in-the-middle | TLS verification by default; explicit CA support. |
| Hallucinated permission | Deterministic extraction only; empty permission errors stay unresolved. |
| Over-broad index access | Require declared patterns; flag wildcards. |
| "Least privilege" overclaim | Call output observed-minimum and report coverage gaps. |
| Unsafe generated role applied blindly | Never apply automatically; require human review. |
| Happy-path-only validation | Required negative probes must remain denied. |

## Next build milestones

1. Preserve step-to-permission provenance in the emitted report.
2. Add a Docker test cluster and disposable test-user convergence harness.
3. Add role-diff and rollback generation.
4. Add cross-version fixtures for OpenSearch 2.x and 3.x.
5. Add optional ingestion of Security audit index records.
6. Add deterministic recommendations for narrower built-in action groups only
   when equivalence can be proven.
