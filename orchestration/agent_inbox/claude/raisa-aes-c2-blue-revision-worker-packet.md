# AES-C2 bounded DeepSeek blue revision packet

Date: 2026-08-11

Task ID: `raisa-aes-c2-blue-revision-001`

Worker: DeepSeek V4 Flash/high through Claude Code `--bare`

## Exact workspace

- Worktree: `C:\Users\sarashera\EMR4-worktrees\aes-c2-deepseek-blue`
- Branch: `codex/aes-c2-blue-deepseek`
- Required revision source HEAD: `52f1dbb10fd6e616d3190aa896e60d8facf5897d`
- Original corrected-plan source: `bd11333d462424b40f5f8f014b1c4a945b3a5133`
- Primary rejection/register source: `b20c301e416c4f5eb4a9e20821bea7d56e916c12`
- Clean exact-head preflight:
  `orchestration/agent_inbox/codex/raisa-aes-c2-blue-revision-worktree-preflight.json`
- Sol rejection:
  `C:\Users\sarashera\emr4\orchestration\agent_inbox\codex\raisa-aes-c2-blue-candidate-sol-rejection.md`
- Incident: AER-0251 at register revision 216.

This is the single mechanical same-lane revision permitted by the frozen plan.
It conveys no acceptance, recovery, integration, baton, push or protected-ref
authority. A failed revision ends this DeepSeek correction lane.

## Mandatory findings to correct

1. `_dispatch_adapter` currently returns `adapter_result_override` before calling
   `_pure_inert_render`. The frozen malformed-result scenario therefore reports
   one call while making zero, and a schema-valid supplied result can release a
   simulated result with zero actual calls. Make the sole pure adapter call
   unconditional exactly once after every preceding gate and before observing
   the exact negative result seam. Never add a second callable or dynamic
   selection path.
2. `validate_scenario_packet` accepts an undeclared top-level packet key and does
   not bind the committed scenario packet to the exact generated 26-scenario
   catalogue. Reject every extra/missing packet field and every noncanonical
   scenario value, including a schema-valid result override outside the one
   exact malformed-result scenario.
3. Add independent tests that instrument the actual `_pure_inert_render`
   callable and prove the malformed scenario executes it exactly once, prove a
   schema-valid override cannot bypass that actual call, and prove an extra
   packet key plus any noncanonical packet fail validation.
4. Regenerate the minimized evidence only after the corrected source and tests
   pass. Preserve exact 2 simulated / 4 not_dispatched / 20 stop accounting and
   three actual pure calls (two releases and one malformed result with no
   release).
5. Correct the worker closeout:
   - the revision source is exact `52f1dbb...`; because the closeout is committed
     in the candidate commit, write `candidate_commit: resolved_by_receipt`
     rather than guessing its self-referential final SHA;
   - name local `master`, local `handoff/current`, `origin/master` and
     `origin/handoff/current` as exact
     `2e34bdad732fdab32fbf778280b3d3c70d66d602`;
   - claim actual calls only after instrumented proof;
   - state that the synthetic fixture is supplied directly to the fixed pure
     adapter but never emitted, while its digest alone is compared for custody
     binding;
   - do not claim all 15 plan criteria are complete. State explicitly that Sol
     final review/adoption, broader maintained/canonical gates, fresh Gemini
     veto, integration, baton/continuity, Yuri mailbox and publication remain
     pending and outside worker authority.

## Exact owned paths

You may edit only these existing seven paths:

1. `orchestration/agent_inbox/claude/raisa-aes-c2-blue-implementation-closeout.md`
2. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/authored-synthetic-broker-simulator-scenarios.json`
3. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json`
4. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json`
5. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/provider-free-broker-simulator-evidence.json`
6. `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`
7. `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`

Do not add, delete or rename any path. Do not touch the plan, threat delta,
AGENTS.md, error register, C0/C1 artifact, API Spine, implementation plan, CI,
fast-profile configuration, docs/branding, unrelated untracked file or protected
ref.

## Required verification

Run serially from the exact worker root using the primary environment when
needed:

1. the corrected simulator script, confirming status `passed` and regenerated
   evidence;
2. focused C2 tests;
3. the exact serial C2 + C1 + C0 + API Spine packet used in the original
   closeout, with the corrected collected/pass count reported exactly;
4. Ruff check and Ruff format check for the two touched Python files;
5. compile/syntax for the C2 script and test;
6. `git diff --check` and an exact seven-path diff check against
   `52f1dbb10fd6e616d3190aa896e60d8facf5897d`.

Do not run protected fixtures, provider/model calls, network, database/source,
runtime broker/adapter, executable tool, command/write or product paths.

## Durable result

Commit the corrected seven-path candidate on `codex/aes-c2-blue-deepseek` and
leave the worktree clean. Return one closed JSON object with:

- `decision`: `pass` or `revision_required` for this bounded revision only;
- `source_head`;
- `candidate_head` (the actual `git rev-parse HEAD` after commit);
- `changed_paths`;
- `actual_adapter_calls`;
- exact scenario/mutation/test counts;
- `closeout_path`;
- `worktree_clean`;
- `protected_refs_unchanged`; and
- `unresolved_findings`.

A worker `pass` is candidate evidence only. Sol remains the sole acceptance and
integration owner, and fresh Gemini veto remains mandatory after deterministic
admission.
