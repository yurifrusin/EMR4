# C4 allowlisted-actuator simulator — DeepSeek implementation packet

Source HEAD: `b66b37a81120b1abd655ce65c42daf7518b8f7d5`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-c4-simulator`

Branch: `codex/worker-model-required-bureau-c4-simulator`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No model fallback is authorised.

## Mandatory source pass

Before editing, read `AGENTS.md` completely and state the exact five
rehydration sources. Read these files completely:

- `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md`
- `docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md`
- `docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c3-d3-closeout.md`
- `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`
- the C4 section of
  `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/agent_inbox/antigravity/model-required-bureau-c4-plan-review-receipt.json`

Verify the exact source, branch and clean worktree before editing. The Gemini
receipt is a passed veto, not implementation authority and not a design source
that may widen the frozen plan.

## Exact implementation task

Implement only the frozen C4 provider-free authored-synthetic in-memory
simulator and its deterministic acceptance evidence. The only forward runbook
is exact `restart-api-synthetic.v1` against exact
`isolated_authored_synthetic / service / synthetic:api-service`, with exact
empty parameters and pure `degraded -> healthy` state transition. The only
rollback runbook is exact `restore-api-synthetic-lkg.v1` to the immutable
last-known-good snapshot.

The runtime simulator must have no filesystem, process, shell, SQL, socket,
network, database, container, cloud, IAM, secret-store, product-route, provider
or external-event capability. It must not import production actuator code or
`app.main`. Acceptance/evidence tooling may read the owned schemas/examples and
write only the owned authored-synthetic evidence file; that tooling must remain
separate from the runtime simulator module.

Implement closed typed objects and closed Draft 2020-12 JSON schemas/examples
for exactly:

- immutable runbook catalog entry and reproducible catalog digest;
- server-held execution-evidence record plus opaque random one-use reference;
- backend-owned simulator command envelope;
- bounded simulator execution receipt; and
- bounded simulator denial receipt.

Unknown properties, duplicate-key input, non-canonical encoding, executable
content, command text, arbitrary callable names and unknown parameters must fail
closed before authority/state lookup. Do not persist or expose the raw opaque
reference in records, logs, receipts or denials; store/lookup a one-way digest.

The issuer must independently bind and validate canonical plan hash/revision,
exact C3 deterministic classification, current backend authority decision,
policy/catalog versions, exact target and revision, current actor and
`authorized_technical_operator` role, candidate-generator/reviewer separation,
fresh observations and digests, supersession, correlation, random nonce and the
earliest expiry. C3's `execution_authorized: false` remains unchanged. Evidence
cannot be renewed or patched and there may be at most one effective evidence
record for the same plan revision/supersession key.

The handler must use one explicit critical section and one fixed code-level
enum-to-callable map. It must never interpret a string, dynamically import,
reflect, use `eval`/`exec`, run subprocess/shell/SQL/templates/URLs/paths or
accept a generic function/callable from input.

The exact order is:

1. same-key/same-fingerprint stored replay;
2. same-key changed fingerprint or in-progress denial;
3. resolve and lock hashed opaque evidence;
4. reauthorize actor/role and revalidate every binding, expiry, target revision
   and fresh observation;
5. reject consumed evidence, including under a different key;
6. build the closed backend-owned envelope;
7. atomically seal idempotency, consume evidence and append immutable attempt
   evidence that can never be rolled back;
8. snapshot only simulated state/effect audit and invoke the fixed transition;
9. append effect audit;
10. perform a separately invoked fresh state-store read;
11. release success only on exact expected health/revision readback; otherwise
    invoke only exact rollback, freshly read again and distinguish verified
    rollback from inconclusive rollback; and
12. store the terminal bounded receipt.

Transition/effect-audit failure restores the simulated state/effect-audit
snapshot but never reopens evidence or attempt evidence. Verified rollback and
unverified rollback are terminal failures, never success. A new attempt needs a
complete new plan/decision/evidence chain.

Use stable denial reason codes from the plan and no attacker-controlled prose,
raw evidence, secret, stack trace or ambient state. Use explicit test-only fault
enums/state rather than injectable arbitrary callables. Expose deterministic
operation counters proving zero forbidden operations.

Add an OpenAPI-shaped declarative command document only if useful, and if added
mark it unambiguously `not_mounted`; it must not be imported by `app.main` or
claim an existing route. GraphQL remains read-only and no event is emitted.

## Owned paths

- `scripts/model_required_bureau_c4_simulator.py` (new)
- `scripts/model_required_bureau_c4_acceptance.py` (new)
- `tests/test_model_required_bureau_c4_simulator.py` (new)
- `orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator/**`
  (new closed schemas, canonical examples and authored-synthetic acceptance
  evidence only)
- `docs/api-spine/openapi/technical-control-simulator-commands.yaml` (optional,
  new, declarative and explicitly `not_mounted` only)

Do not edit any other path. In particular do not edit `AGENTS.md`, the frozen
plan/threat/review artifacts, any existing test, `app/**`, migrations, GraphQL,
provider configuration, deployment/workflows, Continuity/Compass global maps,
`docs/branding/**`, protected/historical evidence or another worktree.

## Acceptance coverage

Tests and the acceptance script must prove at least:

- all five schemas are valid and closed, examples validate, LF-byte hashes and
  catalog/canonical digests reproduce, and duplicate/unknown/non-canonical
  mutations reject;
- exact successful issuance and execution consume evidence once, change only
  the synthetic service, append exact attempt/effect audit, and release exact
  `simulated_effect_verified` only after a distinct fresh read;
- same-key replay, changed fingerprint, in-progress record, different-key
  evidence replay and concurrent single-winner behavior;
- unknown/tampered/expired/superseded evidence, mismatched plan/decision/catalog,
  wrong actor/role, invalid reviewer separation, stale observations, target
  revision drift, scope expansion and multiple-environment claims produce zero
  simulated effect;
- executable fields/content, shell/SQL/URL/path/cloud/template/module/callable
  names and non-empty/unknown parameters are structurally unreachable or
  adversarially rejected before lookup;
- transition failure, audit failure, false handler return, failed first
  readback, verified rollback and unverified rollback prove no false success,
  correct snapshots and permanently consumed evidence;
- source/import/runtime counters prove zero filesystem, process, network,
  socket, database, container, cloud, IAM, product, provider or external-event
  operation by the simulator; and
- no mounted route or `app.main` import change, no GraphQL mutation, and exact
  evidence label
  `provider_free_authored_synthetic_allowlisted_actuator_simulation`.

## Mechanics and forbidden claims

Use only bounded file editing within the owned paths. Run the owned acceptance
script, focused owned tests if the repository test lease is available, Ruff,
`py_compile`, JSON/YAML parsing, source checks and `git diff --check`. Do not
fetch, merge, rebase, switch, push, deploy or move protected refs. Stage only
owned paths by explicit pathname, verify no `docs/branding/` path is cached and
commit once to the worker branch.

This is local/provider-free/newly-authored-synthetic simulation only. It grants
no patient, clinical, product-derived, participant, protected or production
data; no provider product-runtime call; no real target/database/process;
no C5; no autonomous action; no deployment, release, Pages or protected-ref
authority. It does not establish live recovery or production readiness.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one `DECISION: pass` or `DECISION: revision_required`.
