# LC4R9 Generator-Backed Contract Repair — Sprint Contract

Date: 2026-07-15

GPT Sol is Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator. DeepSeek V4 Flash/high through Claude Code
`--bare` owns one bounded implementation/test lane. Gemini 3.5 Flash through a
fresh Antigravity project owns the independent veto. DeepSeek Pro and Deep Code
are not authorized.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Protected boundary and incident containment

Use only the ordinary Silver/pending development corpus, the accepted LC4R8
redacted replay audit, and explicitly named development files. Do not open,
enumerate, search, import, run, regenerate, hash-check, or inspect protected
holdout v1 or any fixture, support module, seal, receipt, or report belonging
to it. Do not search the broad `tests/` tree.

Sol's source orientation accidentally exposed generic lines from protected
fixture paths and the LC4 support module. The incident is recorded in
`lc4r9-protected-search-incident.md`. Those outputs are quarantined and must
not inform the implementation, tests, report, worker, or review. LC4R9 remains
authorized because its exact repair selection was frozen from development-only
LC4R8 evidence before the incident. Holdout v1 may not be rerun or certified
without a later explicit reuse policy; a fresh holdout remains preferable.

No provider inference, T3.5 adapter, route/API, database, UI, deployment,
historical-diary, memory/RAG, confirmation, or write authority is permitted.
T3.1-T3.4 remain intact and blocked by default.

## Frozen repair selection

Repair exactly these 11 ordinary development surface scenarios:

- `lc4_dw1_dev_var_001_01`
- `lc4_dw1_dev_var_001_02`
- `lc4_dw1_dev_var_001_03`
- `lc4_dw1_dev_var_001_05`
- `lc4_dw1_dev_var_001_06`
- `lc4_dw1_dev_var_001_07`
- `lc4_dw1_dev_var_001_08`
- `lc4_dw1_dev_var_001_09`
- `lc4_dw1_dev_var_012_03`
- `lc4_dw1_dev_var_012_05`
- `lc4_dw1_dev_var_012_07`

Selection count is 11 and selection hash is `b88018991e49ffd5`. The canonical
pre-repair delta-line SHA-256 over sorted newline-joined
`scenario_id|create_requested|created` lines is
`14e3648ae8a98598bbc091ce16bf29f31fd5b2fdb92fe7d817ae86fb21837c69`.

Every selected record is an action `create` contract whose deterministic replay
and appointment delta already say `created`; LC4R8 proved only the expected
audit vocabulary differs. The repair changes only its expected audit delta from
`create_requested` to `created`, retaining `appointment_id: apt-001` and
`count: 1`. It does not change interpretation, replay, the comparator, or make
the two values globally equivalent.

Pre-repair development identities are:

- corpus hash `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`;
- group 001 hash `sha256:0874f6887020df0ae9abe0ca75a9ee60bc9eb0d55094701fbf5a48788cd71e5d`;
- group 012 hash `sha256:76a4a27c6d217dcfd0fa4a96ea42b1416201b31fdb87af39c4bb32040f7fb9b6`.

## Implementation contract

Add a source-level frozen allowlist in the authoritative development generator.
It must be fail-closed, accept only the selected surface IDs, assert the target
action is `create`, and pass an explicit audit-delta override into
`_build_scenario`. Do not change `_derive_audit_deltas` globally. Do not hand
edit generated JSON.

Regenerate the complete development fixture through
`generate_development_fixture`. The committed generated delta must be exactly:

- the 11 selected records' `expected_audit_deltas` and cascading variant hashes;
- the cascading group hashes in group 001 and group 012; and
- the cascading corpus/group references in the development manifest.

No other scenario payload, group fixture, manifest field, generator identity,
or historical report may change. A temporary full regeneration must reproduce
the committed corpus byte-for-byte.

Add a deterministic LC4R9 helper and tests which fail closed on selection,
source allowlist, pre/post vocabulary, non-selected scenario drift, file delta,
hash cascade, generator round-trip, composed result, semantic baseline, safety,
variance, and exit-count drift. The helper must use development-only entry
points and support `--check`.

Post-repair acceptance requires:

- all 11 selected scenarios pass complete composed component checks;
- semantic counts remain `880/814/628/101/300/782`;
- safety remains `1152/1152`;
- variance remains zero over 2,304 samples;
- generator-repair authorized/remaining count becomes zero;
- clarification blockers remain 53;
- replay contract-reconciliation blockers remain 40; and
- exit status becomes `blocked_pending_contract_reconciliation`.

LC4R7 and LC4R8 artifacts are historical evidence and must not be regenerated
or rewritten.

## Owned files

The worker may change or add only:

- `app/services/bernie/scale_corpus.py`;
- `tests/test_bernie_lc4r9_generator_contract_repair.py`;
- `scripts/bernie_lc4r9_generator_contract_repair.py`;
- `tests/fixtures/bernie_lc4_development/lc4_dw1_dev_group_001.json`;
- `tests/fixtures/bernie_lc4_development/lc4_dw1_dev_group_012.json`;
- `tests/fixtures/bernie_lc4_development/lc4_development_manifest.json`;
- `docs/bernie-lc4r9-generator-contract-repair.json`;
- `docs/bernie-lc4r9-generator-contract-repair.md`; and
- `orchestration/agent_inbox/codex/lc4r9-dw1-completion.md`.

Use `C:\Users\sarashera\emr4\.venv\Scripts\python.exe`. Commit the candidate
on the disposable worker branch, leave it clean, do not push, and return
`DECISION: pass` only after the focused tests, helper check, compilation,
round-trip regeneration, and `git diff --check` succeed.

Sprint engine state: continuing.
