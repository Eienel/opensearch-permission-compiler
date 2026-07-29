# Pain-point research

## Finding

The strongest mechanism is not "security is hard." It is this:

> OpenSearch authorizes underlying actions rather than REST endpoints; one
> representative operation can require multiple hidden actions, and the user
> must discover them through permission checks or failures.

That makes a user's workflow the missing input to role design. Static role
templates cannot know the workflow, and broad action groups erase the boundary
the security administrator is trying to preserve.

## Witnessed pain

1. The official documentation says permissions do not directly map to REST
   operations, even simple requests can perform several actions, and the
   current least-privilege procedure is to repeatedly send representative
   requests and add missing permissions. It also provides the
   `perform_permission_check=true` primitive needed for safe probing.
   [Security permissions documentation](https://docs.opensearch.org/latest/security/access-control/permissions/)

2. A PPL user receives a 403 for a hidden
   `indices:monitor/settings/get` action while trying to use autocomplete.
   This is a clean example of a user-visible workflow depending on a
   non-obvious transport permission.
   [PPL security exception](https://forum.opensearch.org/t/security-exception-in-ppl/23961)

3. A user seeking least privilege for user creation reports that a suggested
   action group does not work, while `security_rest_api_access` works but
   grants too much.
   [Least-privilege role discussion](https://forum.opensearch.org/t/role-permission-for-creating-users-with-read-all-reports-privilege/23795)

4. A contributor reports losing several hours because valid-looking backend
   role configuration did not grant the expected underlying permissions.
   [Security issue #1766](https://github.com/opensearch-project/security/issues/1766)

5. The security project's tenant RFC describes significant administrator
   back-and-forth when users cannot tell which permissions are missing and
   calls out confusing, fragmented permission workflows.
   [Security RFC #1869](https://github.com/opensearch-project/security/issues/1869)

6. OpenSearch audit logs already expose `MISSING_PRIVILEGES` and
   `audit_request_privilege`, providing a vendor-native evidence channel.
   [Audit log documentation](https://docs.opensearch.org/latest/security/audit-logs/index/)

## Adjacent pain clusters used for idea generation

- Migration mapping conflicts, flattened nested fields, and unclear
  compatibility:
  [mapping mismatch report](https://forum.opensearch.org/t/data-type-mismatch-during-migration-from-elasticsearch-to-opensearch/24740),
  [two-phase migration report](https://forum.opensearch.org/t/two-phase-migration-from-elasticsearch/27642).
- Red clusters and shard allocation errors whose true causes span disk,
  allocation rules, system indices, and storage behavior:
  [red system-index report](https://forum.opensearch.org/t/problem-with-the-opendistro-anomaly-checkpoints-index/22025),
  [allocation failure report](https://forum.opensearch.org/t/shard-allocation-failure-due-to-negative-free-space/21793).
- Snapshot restores fail due to security-index rules or cross-version metadata:
  [snapshot permission thread](https://forum.opensearch.org/t/no-permissions-for-snapshot/14772),
  [writer_uuid restore thread](https://forum.opensearch.org/t/writer-uuid-issue-on-restore-from-elasticsearch-snapshot-to-opensearch/27934).
- Hybrid relevance lacks easy profiling/explanation across score-normalization
  stages:
  [hybrid explainability RFC](https://github.com/opensearch-project/neural-search/issues/905),
  [hybrid profiling report](https://forum.opensearch.org/t/profile-true-does-not-work-with-hybrid-query/26720).
- Ingest users ask how to tell whether pipelines are succeeding or failing:
  [ingest status discussion](https://forum.opensearch.org/t/checking-status-of-ingest-pipelines/13844).

## Why Permission Compiler wins the research round

- Named sufferers exist: OpenSearch security administrators, SREs, and plugin
  users configuring PPL, Dashboards, snapshots, and automation identities.
- The complaint is repeated across official docs, forums, and GitHub.
- The gap is mechanistic: workflow-to-transport-action discovery.
- OpenSearch already supplies the hard primitive: permission checks and audit
  evidence.
- The solution can be small, deterministic, safe, portable, and demoable.
- The primitive widens beyond one feature: any OpenSearch workflow can be
  compiled, including future plugins.
