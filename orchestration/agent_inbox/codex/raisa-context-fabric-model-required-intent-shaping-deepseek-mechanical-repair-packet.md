# Context Fabric model-required intent shaping — bounded DeepSeek mechanical repair

Planning source HEAD: `5ddc052fae16298436d8873312e48464d52a9567`

Rejected worker candidate HEAD:
`d0d7584ff02df0d311b3f71d556cb95333292a82`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\context-fabric-model-intent-shaping`

Branch: `codex/context-fabric-model-intent-shaping-worker`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
This is the single same-lane mechanical revision allowed by the Flash
correction-loop rule. No model, transport or implementation fallback is
authorised.

## Authority and rehydration

Read `AGENTS.md` completely and restore the five named sources before editing:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Read the frozen intent-shaping plan, design and threat
delta, the original worker packet and this repair packet. Verify exact clean
HEAD `d0d7584ff02df0d311b3f71d556cb95333292a82` before editing.

GPT Sol has rejected the first candidate after read-only review. The following
are mechanical implementation defects; the frozen architecture, provider,
authority, acceptance meaning and clinical/product boundaries must not change.
The worker may repair and test only the named owned files. GPT Sol retains
acceptance, recovery, integration, provider execution and protected-ref
authority.

## Required repairs

1. **Immutable release after zeroisation.** The sealed release currently keeps
   the same mutable `ModelIntentCandidateEnvelope` object later cleared by the
   broker. Make the final release own immutable/deep-copied nested material so
   broker zeroisation cannot change the release or invalidate its digest. Add a
   regression test that mutates/clears the original envelope after admission
   and proves the released envelope, release digest and nested body remain
   intact and valid.

2. **Schema-invalid provider body reaches the eligible correction path.** A
   JSON object that fails the closed provider-body schema currently raises from
   `wrap_provider_body`, bypassing the structured proofreader and therefore the
   one allowed `provider_body_schema_invalid` correction. Refactor the bounded
   broker path so an invalid object is hashed/discarded, releases nothing, and
   returns a structured proofreader rejection with exactly
   `provider_body_schema_invalid` and `correction_eligible: true`. Do not retain
   unexpected provider field names or values in audit/evidence; any field-label
   telemetry must use a fixed allowlist plus bounded counts. Add a direct
   regression test for this path.

3. **Positive-thinking failure is terminal and ledger-accountable.** Missing,
   non-integer or non-positive provider-reported `thoughtsTokenCount` in live
   mode must release nothing and become a structured terminal pre-proof
   `positive_thinking_evidence_required` result after the provider call has
   consumed its single-use ledger. It must not raise only after a release has
   been created or strand the tranche cost ledger before reconciliation. It is
   not correction-eligible. Provider-free dry-run remains eligible with zero
   thinking tokens. Add focused tests of live zero/missing/invalid counts and
   dry-run zero.

4. **Exact clean source-veto binding.** Add the acceptance generator to the
   reviewed-source hash set. Bind a passing review receipt to exact equal
   `head_before`/`head_after`, `dirty_after: false`, and the current candidate
   HEAD. At occupied validation, also require the current tracked worktree to
   be unchanged from HEAD while permitting unrelated preserved untracked
   receipt/evidence files. Add tests proving wrong HEAD, dirty review, tracked
   drift, missing acceptance hash and stale hashes fail closed. This binding is
   what prevents an unreviewed accepted-parent or transport edit from entering
   the occupied run.

5. **Canonical cue ordering prompt.** Without changing the frozen output
   contract, state explicitly in the provider prompt that `cue_codes` must be
   returned in the displayed canonical `CUE_CODES` order. Keep the existing
   exact-order proofreader and test the instruction is present.

## Owned files

- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance.py`
- `tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py`

Do not edit schemas unless a focused test demonstrates that one of the exact
repairs above cannot be represented by the already frozen closed schema; if so,
stop with `revision_required` rather than changing it. Do not edit any plan,
design, threat model, accepted parent, `AGENTS.md`, `implementation_plan.md`,
`app/**`, `docs/diary/**`, `docs/branding/**`, API Spine, harness setting,
Continuity/Compass global map, credential, historical evidence, protected
evidence or ref.

## Verification and stop rule

Do not call a provider, inspect credentials, run Docker, run repository pytest,
open a database, push, deploy or alter a protected ref. You may run direct pure
tests, Ruff, compile checks, schema validation and `git diff --check`. Use
explicit-path staging only; never `git add .` or `git add -A`.

Commit only the owned repair files. Return the five-source statement, exact
commit/files/checks and exactly one terminal `DECISION: pass` or
`DECISION: revision_required`. If any required repair remains incomplete, or a
new conceptual issue appears, return `revision_required`; no second same-lane
repair is authorised.
