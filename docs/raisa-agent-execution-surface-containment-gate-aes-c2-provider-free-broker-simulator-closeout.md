# Raisa AES-C2 provider-free inert broker simulator closeout

Date: 2026-08-11

Result: `raisa_agent_execution_surface_containment_gate_aes_c2_provider_free_broker_simulator_pass`

Reviewed source HEAD: `d54f0476448f1218cd55477d42b958721359eae8`

## Accepted result

AES-C2 passes as an authored-synthetic, provider-free, in-process inert broker
simulation beneath the exact accepted AES-C0 authority contract and AES-C1
admission evaluator. A broker-owned registry selects exactly one statically
bound pure function only after a fresh AES-C1 allow, exact registry and supply-
chain identity, a dispatch-time generation/authority/revocation/kill recheck,
and exact cumulative budget-after commit.

The exact 26-scenario catalogue resolves as two released `simulated` results,
four AES-C1 `not_dispatched` decisions and 20 terminal `stop` decisions. The
pure function is called exactly three times: once for each released simulation
and once for the deliberately malformed-result scenario, whose invalid result
is rejected and released nowhere. All other scenarios invoke it zero times.

The work-cell view contains only the closed candidate and proofreader result.
It receives no lease, registry, credential fixture or operation identity. The
operation, capability, adapter, implementation, destination, method and media
type all come from the one broker registry entry. The broker-private fixture is
explicitly an unusable authored-synthetic noncredential and neither its handle
nor value reaches an invocation, result, evidence or exception surface.

## Exact inherited and generated boundary

All five accepted AES-C1 artifact hashes remain exact. The inherited C1
`adapter_artifact_digest` remains `sha256:` plus 64 `f` characters; it is not
conflated with the separately recomputed C2 implementation-definition digest
`sha256:887429a4faee4eba7611ffbb8653fa8c9a730132446c9a7fc6e9ebab59efcb5d`.

The closed C2 artifacts have these exact SHA-256 values:

- contract: `530c9c3067725f6078785e846fa82c0ebb89f72d0a8feeb5c2916d567b5a4ccf`;
- schema: `895f1afc8c4d7f58ba0a8032f54f274496d93e1601e9ce40444d642d4bf0c175`;
- authored-synthetic scenarios: `6ccbf4947ad004535080fc6a75914e54618e44f5e483acc490deed0d02eb1d1c`.

All 18 generated hostile attempt/result mutations and all 14 nested contract
mutations fail closed with zero released simulated result.

## API Spine boundary

The API Steward classification remains unchanged. GraphQL stays read-only and
was not invoked. Committed events remain signals for fresh authorized reads and
were not consumed. Provider invocation remains a future backend-brokered Access
AI boundary and provider failure remains explicit `intelligence_unavailable`.
Product mutations remain separately authorized, human/policy-gated,
idempotent, audited and read-back REST/OpenAPI commands. AES-C2 adds no route,
tool, command or product authority.

## Deterministic and independent evidence

- all 26 canonical scenarios match their exact status, reason and actual pure-
  function invocation count;
- all 18 hostile attempt/result mutations and 14 hostile contract mutations
  reject without a released simulation;
- the final focused C2/C1/C0/API packet passes 95/95 tests;
- the final maintained Python 3.11 static packet passes 155/155 tests;
- the canonical fast profile passes 161/161 tests, Ruff, compilation of 202
  maintained Python source files plus 31 exact verification files, Diary
  JavaScript syntax and Git whitespace;
- the local Python 3.14 environment cannot truthfully run the separately
  version-pinned Python 3.11 `ci-correctness` profile, so that profile is not
  claimed; its maintained static test packet was run directly and passed; and
- a fresh Gemini 3.6 Flash/high exact-HEAD veto independently passes 95/95
  tests, Ruff, whitespace and unchanged-clean-worktree invariants.

Evidence mode is
`authored_synthetic_provider_free_in_process_inert_simulation`: three ordinary
pure Python calls, zero real adapter executions, runtime starts, provider
calls, network, database/source, filesystem, executable/tool or command
operations, and no patient or product data.

## Issues exposed and resolved

The first DeepSeek candidate incorrectly allowed an adapter-result override to
bypass the actual pure call while still reporting one invocation; a schema-
valid supplied result could therefore be released with zero real pure calls.
It also admitted an extra scenario-packet key and overstated closeout evidence.
Sol rejected that candidate. The one plan-permitted mechanical revision made
the pure call unconditional, required canonical packet equality, added actual-
call and closure regressions, corrected the evidence, and passed fresh Gemini
review.

Two Sol orchestration defects also failed closed before acceptance: an invalid
adapter-observation method in a post-compaction receipt and worker-only paths
in a primary error-register draft. They are preserved as AER-0250 and AER-0252.
AER-0251 preserves the rejected worker self-pass and its accepted correction.
No rejected candidate or refused receipt was admitted.

The first final maintained profile also caught that AES-C1's historical
continuity tests still assumed C1 must remain the current final graph node, and
that the new C2 baton row reached the compact handover's 500-line ceiling. The
tests now bind the preserved C1 node and journey independently of later
descendants, and one wrapped historical sentence was compacted without removing
content. The complete 161-test profile then passed.

## Claim and authority boundary

AES-C2 proves deterministic broker-owned identity selection, synthetic custody
non-disclosure, dispatch-time control-state recheck, budget commit and one
statically selected pure inert function call. It does not prove process or
container isolation, real credential custody, real adapter safety, concurrent
atomicity, provider behavior, product-data safety, command safety, deployment
or production readiness.

No protected evidence, historical Diary PHI, patient/clinical/product data,
licensed content, provider, real credential, IAM, metadata, network,
database/source, migration, watcher/listener, filesystem capability,
executable tool, command/write, deployment, production, release, Pages or
protected ref was opened or moved. User-owned `docs/branding/` and all unrelated
untracked files remain preserved and excluded.

## Next planned descendant

AES-C3 hostile containment rehearsal is dependency-satisfied next work. Its
narrow plan may use authored-synthetic, provider-free, unmounted or pure in-
process attacks only, covering local-file references, template/deserialization,
metadata/credential probing, arbitrary relay or encoded egress, cumulative
probing, stale lease and cross-generation replay. AES-C2 grants no C3 runtime,
real adapter, provider, data, credential, network, filesystem, database/source,
tool or command authority.
