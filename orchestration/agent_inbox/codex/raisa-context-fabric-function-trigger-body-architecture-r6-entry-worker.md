# R6 coordinator and recovery-anchor worker result

- Source HEAD: `2b3798f8`
- Role: bounded R6A/R6B entry-program implementation worker; no acceptance or integration authority

## Paths changed

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
2. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-entry-worker.md`

## R6A summary

- Kept coordinator binding, barrier, generation, checkpoint, retained receipt and retained PRIMARY/CONFLICT evidence before route selection.
- Removed unconditional source-outbox, anchor, frame, watermark and pending-obligation selections from the shared prefix.
- Moved the exact source-position set/read behind the exact active PRIMARY route and moved anchor/frame/watermark/obligation reads behind the exact single-source branch that can apply or rebase from that evidence.
- Preserved conflict, `RECEIPT_REPLAYED` and `TERMINAL_REPLAYED` paths without inherited source, anchor, frame, watermark or obligation reads.
- Added literal-relation path walking that proves replay/conflict effect locality and rejects resealed hostile root hoisting of source or frame reads.

## R6B summary

- Added an exact revision-greater-than-zero `F_ANCHOR` gate, retained exact current-checkpoint revision matching, and selected exactly one lifecycle row at the requested revision.
- Added common generation/checkpoint state consistency and non-null seven-digest controls.
- Added DECISION proof branches with an exact immediately previous anchor and exact current audit:
  - zero-receipt rebase rederives `checkpoint_rebase_digest_v1`, proves zero receipt, prior-anchor continuity, unchanged checkpoint position/observation, generation digest continuity, rebase lifecycle/audit/checkpoint integrity and state;
  - receipt-bearing decision proves one receipt, one matching PRIMARY, zero CONFLICT, exact prior-anchor continuity, rederives `classified_receipt_digest_v1` and `checkpoint_apply_digest_v1`, and compares receipt, audit, lifecycle, checkpoint and controlling generation fields/digests.
- Added KEY_ROTATION proof with zero audit/receipt, exact lifecycle-named key interval, exact immediately previous anchor, `key_rotation_digest_v1` rederivation, unchanged checkpoint position/observation, prior-anchor continuity for unchanged generation digests, generation key-schedule binding and checkpoint integrity/state.
- Derived `recovery_anchor_digest_v1` only after a branch assigns one proof-gated trusted integrity digest.
- Made anchor creation time deterministically equal the proven lifecycle time, compared every stored anchor column on replay, rejected ambiguous anchor populations, and retained no checkpoint update or partial-repair path.
- Added resealed, candidate-independent focused checks for branch-local coordinator effects; omitted lifecycle/audit/receipt/PRIMARY/CONFLICT/key/prior-anchor evidence; wrong revision-zero gate, cardinality, lifecycle branch and digest profile; and replay-field substitution.
- No shared primitive was required; subtraction uses the existing typed `SUBTRACT` binary opcode.

## Ruff

Command:

`./.venv/Scripts/python.exe -m ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`

Result: `All checks passed!`

No pytest or generation command was run.

## Integration dependencies

- Reconcile the independent R6B anchor challenge and the R6C schema lane before acceptance.
- Regenerate contract/schema artifacts only after the combined source candidate is admitted.
- Run conductor-owned serial focused and broader pytest/semantic gates, builder check mode, path/effect readback and digest reconciliation.

## Boundary confirmation

Only the three packet-owned paths were modified. No builder, validator, schema source, generated artifact, existing test, plan/design/threat/AER, `docs/branding/`, app/API/Diary/migration file, SQL/DDL, database/source/provider/network/browser surface, patient/product data, runtime/credential/command/write surface, deployment/production/release/Pages surface or protected ref was touched. Nothing was staged, committed or pushed.

RESULT: candidate_ready
