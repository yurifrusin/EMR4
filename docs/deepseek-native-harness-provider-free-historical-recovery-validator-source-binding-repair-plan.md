# DeepSeek native Harness provider-free historical recovery validator source-binding repair plan

Date: 2026-08-21

Status: `frozen`

Source HEAD: `9c49b436fda682b1ba06e3b29ce52d60ba9c95e3`

Operation:
`deepseek-native-harness-provider-free-historical-recovery-validator-source-binding-repair`

Target result:
`deepseek_native_harness_provider_free_historical_recovery_validator_source_binding_repair_pass`

Reasoning level: Extra High freezes the historical-evidence, Git-object and
zero-process boundaries. High is sufficient for the narrow deterministic
implementation, focused verification and clockwork closeout while this plan
remains unchanged.

## Objective

Repair one historical validation defect without changing the accepted recovery
result. The accepted pre-HMR startup-terminal recovery evidence recorded seven
source hashes at exact reviewed Git commit
`12d8758fee2504435ca2b4ccf6225b9d7a86a6a1`. Its validator later recomputed
those hashes from the evolving working tree. Legitimate descendant changes
therefore made two predecessor tests fail even though the immutable historical
evidence and its exact Git source remained intact.

The repair must:

1. project the accepted seven source hashes as immutable historical facts in
   the old subprocess-free validator;
2. independently resolve the full 40-character historical commit, prove it is
   an ancestor of current `HEAD`, read each exact Git blob and match all seven
   recorded hashes;
3. prove the accepted historical contract, schemas, evidence, report, efficacy
   reading and boundary receipt remain byte-identical; and
4. restore both predecessor checks with zero Harness, worker, model or provider
   activity.

## Causal floor

- Accepted recovery source:
  `12d8758fee2504435ca2b4ccf6225b9d7a86a6a1`.
- Accepted recovery evidence SHA-256:
  `a90ffbc5669c612ef44617724916c4e65d039f28c145dcfa5446bdfbf08075e0`.
- Accepted recovery report SHA-256:
  `25d2a3f6e7a5f602e705bd4be051e7d4593859775eeb1bbd59abfdbbd8e0ba7b`.
- Current accepted structured-diagnostic controller closeout input source:
  `7a681e1688c7b7cfa71a8856bb7db1c84c346be4`.
- Current task-branch publication source:
  `9c49b436fda682b1ba06e3b29ce52d60ba9c95e3`.
- Local/origin `master` and `handoff/current` remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The old recovery evidence, report, contract, schemas, efficacy reading,
boundary receipt, attempt-001 baseline and consumed attempt-002 artifacts are
immutable. No historical attempt may be retried, resumed, overwritten,
reclassified or reconstructed.

## Frozen design

The old validator receives one pure `historical_source_sha256()` projection
whose values are copied from the accepted evidence. It does not invoke Git,
start a subprocess or consult mutable descendant files for those historical
coordinates. All other existing behavioral, schema, immutable-attempt and
controller-ordering checks remain active.

A separate provider-free repair checker owns the Git proof. It accepts only the
full lowercase 40-character commit frozen in the contract, resolves it exactly
as a commit, proves ancestry to `HEAD`, reads each frozen path with local
`git show <full-object>:<exact-path>`, and hashes the returned blob bytes. A
missing object, abbreviated object, wrong type, absent path, non-ancestor or
single hash mismatch fails closed.

The separation is deliberate: the predecessor test monkeypatches the shared
Python `subprocess` module to forbid `run` and `Popen` while it calls the old
validator. Git verification therefore belongs to the new checker, not the old
historical validation path.

## Fixed acceptance matrix

1. `HSBR-S01` — the contract and evidence schemas are closed and reject an
   abbreviated or substituted source commit, path, hash or extra field;
2. `HSBR-S02` — the historical source commit resolves exactly to the frozen
   full 40-character commit and is an ancestor of current `HEAD`;
3. `HSBR-S03` — all seven Git blobs match their accepted SHA-256 values;
4. `HSBR-S04` — all eight named immutable recovery artifacts retain their exact
   bytes and hashes;
5. `HSBR-S05` — the old validator's historical source projection is independent
   of mutable current-source hashing;
6. `HSBR-S06` — the old validator passes when both `subprocess.run` and
   `subprocess.Popen` are forbidden;
7. `HSBR-S07` — the two previously failing predecessor tests pass unchanged;
8. `HSBR-S08` — hostile wrong commit, path and hash mutations fail closed;
9. `HSBR-S09` — focused and broader native-Harness controller regressions pass;
10. `HSBR-S10` — Harness, broker, worker, session, prompt, tool, model and
    provider-request counts remain zero; only bounded local Git object-reading
    subprocesses are admitted in the separate repair checker; and
11. `HSBR-S11` — clockwork closeout, paired Yuri summary and the usual non-PHI
    Pushover notification pass.

## Explicit parallelism assessment

- **DeepSeek:** `not_applicable`. The subject is the provider-free historical
  validator around the DeepSeek Harness; invoking the model or Harness would
  violate the active latch and add no evidence to an exact Git/hash proof.
- **Gemini:** `not_applicable`. This is a fully deterministic local Git-object,
  JSON-schema and predecessor-test invariant; provider review cannot improve
  the exact reading.
- **Native subagents:** `declined`. Current developer policy does not authorise
  proactive delegation, and the one old-validator seam plus its independent
  Git proof is intentionally serial.

No lane receives implementation, acceptance, integration or protected-ref
authority. Reassess at pre-verifier and closeout.

## Owned paths

This tranche may change only:

- this plan and its threat-model delta;
- the old recovery validator source, solely to replace mutable source hashing
  with the frozen historical projection;
- one new deterministic repair checker and focused tests;
- `orchestration/continuity/deepseek-native-harness-provider-free-historical-recovery-validator-source-binding-repair/`;
- required Ariadne receipts; and
- closeout, Sol acceptance, paired Yuri summary, clockwork and Pushover receipt.

The accepted historical recovery directory is read-only. No product source,
configuration, API, database, route, adapter, feature flag, allowlist, action
grammar, first-party client or waiting-area path may change.
The exact ordinary-practice boundary remains
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.

## Fail-closed and continuation rule

Any Git resolution, ancestry, blob, hash, immutable-artifact, schema,
subprocess prohibition or predecessor-test mismatch stops acceptance. This
repair proves historical validator stability only; it does not prove Harness
reliability, identify deleted attempt-002 output, authorize an occupied run or
admit ordinary-practice use.

After successful closeout, continue under Yuri's standing uninterrupted-
development authority to the narrowest dependency-satisfied successor unless
a genuine user-attention fork arises. Preserve `docs/branding/` and every
unrelated untracked file. Stage explicit paths only; `git add .` and
`git add -A` are forbidden.
