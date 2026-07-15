# LC4R9 Sol Acceptance

Date: 2026-07-15

## Authority and provenance

GPT Sol remained Conductor, sprint planner, architecture/acceptance owner,
recovery owner, and protected integrator. DeepSeek V4 Flash/high ran through
Claude Code `--bare` as the bounded implementation/test worker. DeepSeek Pro
and Deep Code were not used. Gemini 3.5 Flash/High ran through a fresh
Antigravity worktree as the independent veto reviewer.

Worker commit `e446a44f` correctly implemented the source-level repair but
failed acceptance evidence. Its bounded revision then confused corpus-wide raw
failures with the frozen LC4R8 populations, reported 338/719 instead of 53/40,
temporarily wrote two unauthorized root helpers, and claimed a clean committed
branch while leaving five files uncommitted. Sol preserved those failures and
adopted the useful source only as an untrusted candidate under the Ariadne
recovery lease. Every Sol amendment is recorded in
`lc4r9-sol-recovery-amendment.md`.

This experience produced a user-authorized workflow rule, committed at
`69206154`: conceptual Flash acceptance failures move directly to Sol recovery;
mechanical defects may receive at most one bounded revision; any failed
revision ends the external correction loop. The machine-readable operating
model and deterministic tests enforce that rule. It is an error-shape routing
decision, not a general capability verdict based only on tokens or elapsed
time.

## Accepted generator repair

The authoritative development generator now contains exactly the frozen 11
surface-scenario allowlist, selection hash `b88018991e49ffd5`. Each target is a
`create` contract and receives a fresh expected audit delta with
`change_type: created`, `appointment_id: apt-001`, and count 1. The global
`_derive_audit_deltas("create")` behavior remains `create_requested`; no global
equivalence or scorer relaxation was introduced.

The complete corpus was regenerated through `generate_development_fixture`.
Only group 001, group 012, and the manifest changed, and only through the 11
target audit deltas plus their deterministic hash cascade. Frozen identities
are:

- pre-repair group 001:
  `sha256:0874f6887020df0ae9abe0ca75a9ee60bc9eb0d55094701fbf5a48788cd71e5d`;
- pre-repair group 012:
  `sha256:76a4a27c6d217dcfd0fa4a96ea42b1416201b31fdb87af39c4bb32040f7fb9b6`;
- pre-repair corpus:
  `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`;
- post-repair group 001:
  `sha256:b1e33767b127856e25095c907b14a40a6f88e6522af0cc1841e9baa3bdeff6d7`;
- post-repair group 012:
  `sha256:90d321501e51df4e1b91aa94997e3470b3d26c2678ca61045ad8c6c63abdc5c0`;
- post-repair corpus:
  `sha256:f11e98f9bc61b962da0e816fbb918d7f722d3f82c57dfde18a5e323c1b24e9e1`.

Reversing only the 11 deltas reconstructs every pre-repair identity, and a
temporary full generation reproduces all 97 committed fixture files
byte-for-byte.

## Accepted evidence and exit

All 11 repaired cases pass the complete deterministic interpretation, replay,
and composed score path. Two-repeat development evidence preserves semantic
counts `880/814/628/101/300/782` per repeat, safety 1,152/1,152 per repeat, and
zero variance over 2,304 samples.

Exit evidence uses the accepted redacted LC4R8 populations rather than raw
corpus totals. Frozen hashes are clarification `9496e23c6f339603`, replay-all
`2e45f30f714568ef`, repaired `b88018991e49ffd5`, and remaining replay
`defe4c59877753e9`. The accepted post-LC4R9 result is:

- generator-backed repair remaining: 0;
- clarification contract blockers: 53;
- replay contract-reconciliation blockers: 40; and
- status: `blocked_pending_contract_reconciliation`.

No parser or replay integration remediation is authorized by this result.

## Verification

Sol's recovered focused LC4R9 suite passed 54/54, the helper returned
`LC4R9 CHECK PASSED`, compilation succeeded, the report comparison was
read-only and fail-closed, generator round-trip was byte-identical, and diff
hygiene was clean.

Gemini independently reviewed exact recovered source head
`a8f46cea8a96f15860d578e114e33cc8146ac2ab`, repeated 54 focused passes plus
handover and operating-model checks, and returned `DECISION: pass` in
`lc4r9-antigravity-independent-review.md`.

The final single-process preservation gate selected 275 nodes covering the T1
scenario laboratory, T3.1-T3.4 provider-free shadow contracts, adversarial
corpus guards, LC4 scale corpus, LC4R9, handover integrity, and Ariadne routing.
It completed with 273 passes, one expected xfail, and one established skip.
The gate deliberately deselected only
`TestNegativeRejectedDefects::test_non_mutating_check`, whose historical LC4
development report freezes the pre-LC4R9 corpus hash and must not be
regenerated. All other selected nodes passed.

## Protected boundaries and continuation

During Sol's initial source orientation, two overly broad searches exposed
generic lines from protected fixture paths and the LC4 support module. The
content exposure and containment are recorded in
`lc4r9-protected-search-incident.md`. The frozen repair authorization predates
the incident, no exposed output informed the implementation or reviews, and
protected holdout v1 was not run, imported, regenerated, or certified. It must
not be reused for certification without a later explicit user-approved policy;
a fresh holdout remains preferable.

LC4R9 changes no runtime interpreter, core scorer/replay, provider/T3.5
adapter, route/API, database, UI, deployment, historical diary, memory/RAG,
confirmation, or write authority. T3.1-T3.4 remain intact and blocked by
default.

The next ordinary development tranche is a Sol-planned LC4R10 contract-quality
reconciliation of the remaining 53 clarification and 40 replay populations.
It must keep corpus engineering separate from parser remediation and may only
authorize parser work from a new frozen surface-supported subset. Holdout
reuse/v2 and T3.5 remain user decision boundaries.

LC4R9 is accepted.
