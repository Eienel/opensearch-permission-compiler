# Idea Interrogator results

This document applies the supplied **Idea Interrogator** in its stated order:
mode first, then precise statement/secret word, three kill questions,
feasibility only after survival, cheap probes, and survival conditions.

The goal was not to maximize the number of plausible ideas. It was to generate
widely, kill pattern-completions quickly, and spend detail only on ideas that
thickened.

## Round 1 - 30 ideas through the kill filter

Legend:

- **PC**: pattern-completion.
- **MD**: mechanism-driven.
- **Layer**: tied to one current feature.
- **Primitive**: reusable mechanism.
- **Kill**: thinned under questioning.
- **Semifinal**: survived and receives full probes below.

| # | Raw idea | Mode and secret word | Named pain / gap under gap | Altitude | Verdict |
|---:|---|---|---|---|---|
| 1 | Generic cluster doctor | PC; "doctor" secretly means trusted diagnosis | SRE with a red cluster, but generic diagnosis is already the obvious agent demo; missing evidence ordering is the real gap | Layer | Kill |
| 2 | Chat with OpenSearch docs | PC; "chat" does all the work | Cannot name pain beyond finding docs; retrieval is the feature, not a missing mechanism | Layer | Kill |
| 3 | Log-triage agent | PC; "triage" is vague | SREs have log pain, but the official repo already has log analytics and duplication is disallowed | Layer | Kill |
| 4 | Trace root-cause agent | PC; "root cause" overclaims causality | Tracing pain is real, but an official trace-analytics skill already exists | Layer | Kill |
| 5 | Agent marketplace for OpenSearch | PC; "marketplace" is category completion | No named sufferer; distribution is not the customer mechanism | Layer | Kill |
| 6 | Natural-language query builder | PC; "natural" hides correctness | Search users can already use LLM query generation; correctness/provenance is unsolved but this version does not own it | Layer | Kill |
| 7 | Dashboard generator | PC; "automatic" hides data semantics | Analyst setup is slow, but generating charts does not solve missing field meaning | Layer | Kill |
| 8 | Alert summarizer | PC; "summary" is not remediation | On-call engineers face noise, but summary alone does not change the alert mechanism | Layer | Kill |
| 9 | Migration chatbot | PC; "migration" hides data-dependent compatibility | Migrators have witnessed pain, but a chatbot is just a layer over docs | Layer | Kill |
| 10 | Mapping contract compiler | MD; "contract" means executable source/target invariants | ES-to-OpenSearch migrator with type drift; gap is that compatibility is data-dependent, not a version-table lookup | Primitive | Semifinal |
| 11 | Zero-downtime client bridge planner | MD; "zero" must mean bounded compatibility window, not no risk | Teams cannot upgrade server and clients independently; gap is protocol/version sequencing | Layer | Kill: proxy solutions exist and portability is weak |
| 12 | Upgrade invariant runner | MD; "safe" means explicit pre/post invariants | SRE upgrading clusters; gap is no executable proof that security, ingestion, queries, and saved objects still work | Primitive | Semifinal |
| 13 | Snapshot compatibility linter | MD; "compatible" means metadata and restore preconditions | DR owner hits security-index or cross-version restore failures; gap is snapshots are tested too late | Primitive | Semifinal |
| 14 | Disaster-recovery rehearsal agent | MD; "rehearsal" means disposable restore plus invariant checks | DR owner cannot trust an untested backup; gap is backup success is not recoverability | Primitive | Semifinal |
| 15 | Shard allocation explainer | Mixed; "explain" means ranked evidence, not paraphrase | SRE with unassigned shards; gap is competing deciders and unsafe remediation ordering | Layer | Kill: useful but too close to generic cluster doctor |
| 16 | System-index recovery guide | MD; "system" identifies special safety rules | SRE fears making red hidden indices worse; gap is ownership/recreation semantics | Layer | Kill: narrow and version-sensitive |
| 17 | Ingest failure flight recorder | MD; "flight recorder" means per-document processor lineage | Pipeline owner cannot see pass/fail and data loss; gap is failure provenance across processors | Primitive | Semifinal |
| 18 | Schema-drift guard | MD; "drift" means observed contract delta | Data engineer suffers mapping conflicts; gap is unannounced producer changes | Primitive | Kill: overlaps mapping compiler but with weaker hackathon story |
| 19 | Field-explosion budgeter | MD; "budget" means bounded cardinality and memory cost | Cluster owner faces dynamic-field growth; gap is schema admission control | Primitive | Kill: strong but narrower utility |
| 20 | ISM safety simulator | MD; "simulate" means time/data transition model | SRE sees delayed deletion and disk-watermark failures; gap is coupled timing/capacity | Layer | Kill: reliable simulation is too large for the build window |
| 21 | Hybrid score attribution lab | MD; "why" means per-channel score transformation | Search engineer cannot profile/explain hybrid results; gap is coordinator-stage normalization | Primitive | Semifinal |
| 22 | Relevance regression bisector | MD; "regression" means a measurable query-set delta | Search engineer loses conversions/productivity after tuning; gap is attributing quality change to one configuration delta | Primitive | Semifinal |
| 23 | Embedding drift sentry | Mixed; "drift" needs ground truth | Semantic search owner experiences silent relevance decay; gap is no labels, not no monitor | Layer | Kill |
| 24 | RAG provenance auditor | PC-to-MD attempt; "grounded" remains underspecified | RAG owner needs source coverage, but this is a crowded agent pattern and not OpenSearch-specific enough | Layer | Kill |
| 25 | Capacity and retention forecaster | MD; "forecast" means uncertainty-bounded disk/shard trajectory | SRE hits watermarks before ISM catches up; gap is coupled ingest/retention/recovery load | Primitive | Kill: good product, weak agent-skill differentiation |
| 26 | Cross-cluster replication lag diagnostician | Mixed; "lag" hides network/source/sink causes | Replication operator has pain, but the idea does not widen beyond CCR | Layer | Kill |
| 27 | Permission compiler | MD; "compile" means workflow -> observed actions -> role + negative proof | Security admin repeatedly adds hidden permissions or grants broad roles; gap is missing workflow-to-action discovery | Primitive | Semifinal |
| 28 | Tenant access visualizer | MD; "access" means effective user/object/data reachability | Dashboard admin faces many-to-many mappings; gap is effective-permission composition | Layer | Kill: valuable but UI-heavy and tenant-model-specific |
| 29 | PII exposure auditor | Mixed; "PII" requires domain classification | InfoSec needs field/DLS/FLS checks, but classification accuracy becomes the unsolved hard thing | Layer | Kill |
| 30 | Incident evidence timeline | Mixed; "causal" would overclaim | Incident commander needs logs, traces, audit, and changes aligned; gap is clock/entity normalization | Primitive | Kill: broad observability competition and large scope |

## Round 2 - full interrogation of survivors

### A. Mapping Contract Compiler

**0. Mode:** Mechanism-driven. Source mappings, templates, dynamic mapping,
sample documents, and target behavior can disagree.

**1. Plain statement:** Given source and target cluster metadata plus sampled
documents, generate an executable migration contract and canary reindex plan.
The secret word is **compatible**: it must mean preserving named query, sort,
aggregation, and field-type invariants - not merely accepting documents.

**2. Kill questions**

- **Who hurts?** Elasticsearch 7.x migrators reporting changed keyword,
  integer, nested, and array behavior.
- **Gap under gap:** A version matrix cannot express data-dependent mapping and
  application-query compatibility.
- **Layer or primitive?** Primitive: executable schema/query invariants can
  guard migrations, upgrades, and producer changes.

**3. Feasible version:** Stand on mapping APIs, index templates, `_field_caps`,
sampled documents, and canary indices. Do not build a general type theorem
prover.

**4. Cheap probes**

1. Reproduce one public mapping mismatch with a 100-document fixture.
2. Compare a static mapping diff against an observed query/aggregation test;
   kill if static diff adds no useful signal.
3. Generate a canary target mapping and prove a nested/keyword regression is
   caught before bulk migration.

**5. Survival conditions:** Must detect failures that Migration Assistant does
not already surface, work without proprietary infrastructure, and finish a
useful preflight in minutes. Otherwise: beautiful idea, wrong time, file it.

**Result:** Thickens, but broad fixture construction raises delivery risk.

### B. Upgrade Invariant Runner

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Capture user-selected behavioral invariants before an
upgrade and replay them against a canary target. "Safe" means those invariants
pass, not that the upgrade has no risk.

**2. Kill questions**

- **Who hurts?** Operators discovering saved-object, security, snapshot, or
  client breakage only after an upgrade.
- **Gap under gap:** Release-note compatibility is not the same as application
  behavior.
- **Layer or primitive?** Primitive: executable before/after invariants apply
  to upgrades and configuration changes.

**3. Feasible version:** JSON request/response assertions, redaction, and
version-aware normalization.

**4. Cheap probes**

1. Capture and replay ten read-only API invariants across two Docker versions.
2. Inject one expected response-shape change and test whether normalization
   distinguishes harmless from breaking.
3. Add a forbidden-operation invariant; kill if the harness only proves happy
   paths.

**5. Survival conditions:** Must handle nondeterministic fields, secrets, and
destructive endpoints safely. Otherwise file it.

**Result:** Thickens; strong primitive, but cross-version demo setup is costly.

### C. Snapshot Compatibility Linter

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Inspect repository metadata, source/target versions,
security-index inclusion, and restore request shape before a restore.
"Compatible" means OpenSearch can enumerate and restore the selected indices
under the target's rules.

**2. Kill questions**

- **Who hurts?** Operators encountering `writer_uuid`, unknown metadata,
  missing-snapshot, or security-index permission failures.
- **Gap under gap:** Snapshot completion proves storage, not target
  recoverability.
- **Layer or primitive?** Primitive if expressed as restore preconditions;
  layer if hard-coded to one metadata version.

**3. Feasible version:** Read repository registration and snapshot metadata;
never mutate repository files.

**4. Cheap probes**

1. Collect three public failing metadata shapes and make an offline linter.
2. Detect security-index/global-state risk from a restore manifest.
3. Test whether official restore APIs expose enough metadata; kill if raw
   repository parsing is required.

**5. Survival conditions:** Read-only inspection must catch common failures
without depending on S3/GCS internals.

**Result:** Thickens, but may become a version-specific layer.

### D. Disaster-Recovery Rehearsal Agent

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Restore a snapshot into a disposable target and verify
data, aliases, templates, security boundaries, and critical queries.
"Rehearsal" means measured recovery evidence, not a restore command.

**2. Kill questions**

- **Who hurts?** The owner accountable for RPO/RTO with backups never restored.
- **Gap under gap:** Backup existence is not recoverability.
- **Layer or primitive?** Primitive: recovery contracts apply across
  distributions and storage backends.

**3. Feasible version:** Docker target, explicit sample/critical-query
invariants, teardown plan.

**4. Cheap probes**

1. Restore a small fixture and compare document counts plus sampled hashes.
2. Break one alias and prove the rehearsal fails.
3. Measure whether setup fits inside a five-minute demo.

**5. Survival conditions:** Must avoid production mutation, keep credentials
safe, and yield evidence more useful than `_snapshot/_status`.

**Result:** Thickens; excellent operational value, heavier demo.

### E. Ingest Failure Flight Recorder

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Attach a trace identifier and processor-level outcome
to sampled documents so an operator can locate where and why ingest changed or
dropped data. "Flight recorder" means bounded sampled lineage, not logging
everything.

**2. Kill questions**

- **Who hurts?** Pipeline owners asking whether documents hit, passed, or
  failed processors.
- **Gap under gap:** Final-index inspection loses the transformation path.
- **Layer or primitive?** Primitive: lineage applies across ingest pipelines.

**3. Feasible version:** Use `on_failure`, pipeline simulation, sampled shadow
documents, and correlation IDs.

**4. Cheap probes**

1. Build a three-processor pipeline with one silent transformation bug.
2. Compare pipeline `_simulate` with flight-recorder evidence.
3. Measure storage overhead at 0.1%, 1%, and 10% sampling.

**5. Survival conditions:** Must add bounded overhead and expose information
not already available from simulation.

**Result:** Thickens, but requires careful production-overhead proof.

### F. Hybrid Score Attribution Lab

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Explain how lexical and neural candidates become final
hybrid rankings, including normalization and combination. "Explain" means
stage-specific numbers, not prose.

**2. Kill questions**

- **Who hurts?** Search engineers unable to profile hybrid queries or understand
which channel moved a result.
- **Gap under gap:** Scores exist at different execution stages and are not
jointly visible.
- **Layer or primitive?** Primitive if it accepts arbitrary score channels;
layer if tied to one processor response.

**3. Feasible version:** Stand on hybrid explain output where available and
build counterfactual weight replay from captured scores.

**4. Cheap probes**

1. Capture raw and normalized scores for a small labeled corpus.
2. Recompute rankings for alternate weights without rerunning retrieval.
3. Kill if current OpenSearch explain output already provides the same usable
   workflow end to end.

**5. Survival conditions:** Numerical replay must match OpenSearch and work
across supported normalization techniques.

**Result:** Thickens; high innovation, but existing RFC/implementation creates
duplication risk.

### G. Relevance Regression Bisector

**0. Mode:** Mechanism-driven.

**1. Plain statement:** Given two search configurations and a labeled query
set, find the smallest configuration delta explaining a relevance regression.
"Explaining" means a reproducible metric/candidate change, not an LLM story.

**2. Kill questions**

- **Who hurts?** Search engineers whose tuning changes reduce NDCG, conversion,
  or zero-result performance.
- **Gap under gap:** Aggregate metrics show that quality changed, not which
  retrieval/ranking mechanism caused it.
- **Layer or primitive?** Primitive: delta minimization applies to BM25,
  semantic, hybrid, analyzers, weights, and rerankers.

**3. Feasible version:** Stand on existing evaluation metrics and perform
bounded configuration delta-debugging.

**4. Cheap probes**

1. Inject one bad synonym and see whether bisection isolates it.
2. Inject interacting weight/analyzer changes and observe combinatorial cost.
3. Compare insight against the repository's existing evaluation tooling.

**5. Survival conditions:** Must add causal localization beyond existing
side-by-side evaluation within a short runtime.

**Result:** Thickens; promising, but overlaps the repository's search-quality
foundation.

### H. Permission Compiler

**0. Mode:** Mechanism-driven. The official authorization model creates the
mechanism: workflows invoke hidden transport actions, not one-to-one REST
permissions.

**1. Plain statement:** Given representative allowed and forbidden requests,
use OpenSearch's own permission decisions to emit a narrow role candidate and
evidence that the security boundary still holds.

The secret word is **minimum**. It means **observed minimum for this declared
workflow**, not mathematical least privilege and not proof about unobserved
production traffic.

**2. Kill questions**

- **Who hurts?** The PPL administrator facing a hidden
  `indices:monitor/settings/get` failure; the security admin who finds
  `security_rest_api_access` works but grants too much; users reporting hours
  of permission trial-and-error.
- **Gap under gap:** The missing feature is not another role editor. The
  missing mechanism is compiling user-visible capabilities into underlying
  actions while preserving explicit data boundaries.
- **Layer or primitive?** Primitive. PPL, Dashboards, snapshots, ingest,
  monitoring, and future plugins can all supply representative workflows.

**3. Feasible version:** Stand on `perform_permission_check=true`, Security
audit records, exact error parsing, and the Security roles API. Keep the first
version deterministic and human-reviewed; do not invent a policy language or
automatic production deployment.

**4. Cheap probes, cheapest-to-kill first**

1. **Offline parse probe:** Feed real documented 403, `missingPrivileges`, and
   audit-record shapes into a parser. Kill if exact actions cannot be recovered
   reliably.
2. **Scope probe:** Compile two workflows using the same action but different
   index patterns. Kill if the compiler cannot prevent cross-index broadening.
3. **Negative-boundary probe:** Add a required search and forbidden delete.
   Kill if the generated role or validation lets delete pass.
4. **Live convergence probe:** On Docker OpenSearch, start with an empty test
   role, collect permission checks, apply the candidate manually, and verify
   positive and negative operations. Kill if the loop is not faster or clearer
   than manual debugging.

**5. Survival conditions**

- OpenSearch permission checks expose useful exact actions.
- Index scope can be declared and kept separate from action discovery.
- The agent never needs production admin credentials to discover permissions.
- The output remains portable and proprietary-dependency-free.
- The demo shows both productivity and a narrower security boundary.

If any fail: beautiful idea, wrong time, file it.

**Result:** Thickens hardest. Its hardest objection - "an agent might grant too
much" - improves the design by forcing deterministic evidence, negative tests,
explicit scope, and human application.

## Hackathon-weighted finalist score

Scores are decision estimates, not claims about judges. Each dimension is
scored 1-5 and weighted by the official rubric.

| Finalist | Innovation 25 | Utility 25 | Ops 20 | Portability 15 | Docs/demo 15 | Weighted /100 |
|---|---:|---:|---:|---:|---:|---:|
| Permission Compiler | 4.6 | 4.8 | 4.7 | 4.8 | 4.7 | **94** |
| Mapping Contract Compiler | 4.4 | 4.7 | 4.2 | 4.5 | 4.4 | 89 |
| Upgrade Invariant Runner | 4.3 | 4.7 | 4.1 | 4.4 | 4.3 | 87 |
| Disaster-Recovery Rehearsal | 4.1 | 4.8 | 4.4 | 3.9 | 4.6 | 87 |
| Relevance Regression Bisector | 4.6 | 4.5 | 4.0 | 4.4 | 4.2 | 87 |
| Hybrid Score Attribution Lab | 4.8 | 4.3 | 3.7 | 4.2 | 4.3 | 86 |
| Ingest Failure Flight Recorder | 4.3 | 4.5 | 3.9 | 4.3 | 4.2 | 85 |
| Snapshot Compatibility Linter | 4.0 | 4.4 | 4.2 | 3.8 | 4.2 | 83 |

## Selection

**Build OpenSearch Permission Compiler.**

It is the best combination of witnessed pain, an ugly OpenSearch-specific seam,
primitive-level reuse, safe cheap probes, production feasibility, and a
five-minute demo with an immediately visible before/after result.
