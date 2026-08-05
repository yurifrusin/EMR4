# C4 allowlisted-actuator simulator — bounded DeepSeek repair packet

Untrusted source candidate:
`c56267d23c24dd9e4fe642df85e74cc95de07a6e`

Source parent:
`b66b37a81120b1abd655ce65c42daf7518b8f7d5`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-c4-simulator`

Branch: `codex/worker-model-required-bureau-c4-simulator`

Model/transport: exact DeepSeek V4 Flash/high through a fresh Claude Code
`--bare` process. No fallback is authorised.

## Mandatory source and incident pass

Read `AGENTS.md` completely and repeat the exact five rehydration sources. Read
the frozen C4 plan and threat-model delta, the passed plan-review receipt, the
original worker packet, your preserved original worker receipt, and
`orchestration/agent_inbox/codex/model-required-bureau-c4-worker-independent-review.md`
completely. Verify exact clean source `c56267d23c24dd9e4fe642df85e74cc95de07a6e`
before editing.

The original `DECISION: pass` is rejected. Passing worker-authored tests and
owned-path compliance do not establish acceptance. Repair only the exact
findings below and their necessary regression evidence; do not redesign or
widen C4.

## Exact repairs

### 1. Fail-closed scalar admission before lookup or consumption

`parse_request` must validate all required scalar and nested field types,
closed enums/formats and non-empty/bounded values before constructing a request.
At minimum cover idempotency key, correlation id, actor id/role, evidence
reference, runbook, target strings/revision, plan id/revision/hash, decision
id/hash/policy, catalog version/digest, supersession key and readback values.
Boolean must not satisfy integer fields. Invalid inputs return a stable denial;
they must never reach `fingerprint()`, authority lookup, idempotency sealing,
evidence consumption or audit. Add adversarial type mutations for every field,
including the reproduced numeric-idempotency-key case, and assert zero state,
evidence, idempotency and audit change.

### 2. Read back the exact actual target

Success and rollback verification must compare the full actual state tuple:
environment, target kind, target id, revision and health. A state store seeded
with any wrong environment/kind/id/revision must fail closed before or during
revalidation with zero false success. The success receipt must derive its target
from the verified fresh readback, never module constants. Add the exact
`synthetic:wrong-service` regression and every other target component.

### 3. Add genuine current authority sources at execution time

Add one closed in-memory current-authority state/store that the runtime reads
fresh inside the critical section. It must contain and revalidate at least:

- current canonical plan id/revision/hash and non-superseded state;
- current decision id/hash/policy, authority class, expiry and closed C3
  non-execution lineage;
- current immutable catalog entry/version/digest/runbook/rollback/target;
- current actor id/role/expiry;
- current reviewer id/role/expiry and separation from generator/actor; and
- current observation ids, content digests, observation/expiry timestamps.

The evidence record remains a snapshot/binding, not the current source. Runtime
must reject catalog replacement, plan or decision drift/supersession, role loss,
actor/reviewer expiry, reviewer separation loss, observation-content drift,
observation replacement/staleness and missing current records. Use stable
denials and zero simulated effect. Do not add a database, file, network or
generic authority provider.

### 4. Retain effect audit only for verified success

An effect audit may be prepared before readback if needed, but it must not
remain in the durable in-memory effect log unless the exact full fresh readback
verifies success. Every transition/audit/readback/rollback failure path restores
the effect-audit snapshot. The monotone attempt audit and consumed evidence must
remain. Verified and unverified rollback remain distinct terminal failures.
Update acceptance evidence so all denial/rollback cases have zero retained
effect records; success has exactly one.

### 5. Close exact counter-property schemas

Both execution and denial receipt schemas must enumerate and require all 18
exact named zero-capability counters, forbid additional counter properties and
reject missing, renamed or non-zero counters. Add schema mutations replacing
the names with `arbitrary_0`…`arbitrary_17`, omitting each name and adding one
extra name.

### 6. Make entropy non-caller-selectable

Remove caller-supplied reference and nonce arguments from the production
`EvidenceIssuer.mint` interface. Production issuance must always call
`secrets.token_hex` (or stronger equivalent) for both. Deterministic acceptance
may monkeypatch the module entropy function only inside test/acceptance tooling;
do not expose a runtime deterministic mode or injectable entropy callable. Add
tests proving the production signature has no reference/nonce parameters and
two unpatched issuances produce different values/digests.

### 7. Make issuance uniqueness concurrency-safe

Protect the complete check-and-insert sequence for the one effective
`(plan_revision, supersession_key)` evidence record with an issuer-owned lock.
Add a concurrent barrier test in which exactly one mint succeeds and every
other contender receives the stable stale/superseded denial, with exactly one
record and one issued key.

## Owned paths

Edit only the original C4 worker-owned paths:

- `scripts/model_required_bureau_c4_simulator.py`
- `scripts/model_required_bureau_c4_acceptance.py`
- `tests/test_model_required_bureau_c4_simulator.py`
- `orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator/**`
- `docs/api-spine/openapi/technical-control-simulator-commands.yaml` only if its
  schemas must align; keep it explicitly `not_mounted`.

Do not edit `AGENTS.md`, plans/threats/review/receipt files, any existing test,
`app/**`, migrations, GraphQL, provider configuration, deployment/workflows,
global Continuity/Compass, `docs/branding/**`, protected evidence or another
worktree.

## Required verification and commit

Regenerate the owned provider-free evidence and prove `--check`
reproducibility. Run all owned tests plus inherited C4 plan, C3/D3, Gate-zero
and API Spine tests, Ruff, `py_compile`, Bandit, JSON/YAML parsing and
`git diff --check`. Mechanically verify the exact changed-path set and no
`docs/branding/` cached path. Commit once as a new repair commit on the existing
worker branch; do not amend or erase `c56267d2`.

No fetch, merge, rebase, switch, push, deployment or protected-ref movement.
No product/runtime provider call, patient/product/protected data, real target,
database, process, C5, deployment, release or production claim.

Return exact changes/tests/blockers and finish with exactly one terminal
`DECISION: pass` or `DECISION: revision_required`.
