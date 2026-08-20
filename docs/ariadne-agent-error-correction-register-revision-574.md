# Ariadne agent error and correction register — revision 574

Date: 2026-08-20

Timestamp: 2026-08-20T18:37:08.3978047+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 574
incident_count: 698
new_incident_ids: AER-0695,AER-0696,AER-0697,AER-0698
open_incident_count: 0
-->

This revision records three corrected independent-review control incidents and
one post-terminal checkpoint-test defect in the preset-row service-path
recovery. None contacted DeepSeek, accessed product data or moved protected
refs. None remains open.

## AER-0695 — the first semantic-review manifest wrote tracked evidence

One review command regenerated a tracked fixture containing an
environment-dependent credential-removal count. The exact HEAD was preserved,
but the isolated worktree became dirty, so Antigravity correctly admitted no
decision.

Correction: preserve the failed worktree and receipt, replace artifact-writing
commands with non-writing function validation, and rerun the review in a fresh
exact-candidate worktree. The corrected semantic veto passed cleanly.

## AER-0696 and AER-0697 — exact command-result retranscription failed egress

Two executor-review transports exited zero with non-empty output, no stderr and
unchanged clean candidates, but neither produced an envelope that could pass
the exact locally enforced command-results contract. Restating JSON-only output
did not cure the recurrence, so the retranscription retry lane closed.

Correction: split the evidence gate. The shell-free deterministic validation
runner now owns and seals the twelve exact argv/results; Gemini owns only the
independent semantic decision and review. The deterministic ledger passed all
twelve commands, the fresh split semantic veto passed, and the later one-shot
native confirmation completed successfully. This demonstrates the intended
clockwork principle: models judge; deterministic gears transcribe exact facts.

## AER-0698 — the negative checkpoint test captured an import-time path

After the real checkpoint was published, the fail-before-process test exposed
that `load_native_checkpoint()` had captured the original path in its default
argument. Monkeypatching the module path therefore no longer selected a missing
checkpoint. This did not affect the already consumed runtime call, but it made
the post-publication negative test ineffective.

Correction: resolve the module checkpoint path at call time when no explicit
path is supplied. The focused post-terminal suite now exercises the intended
missing-checkpoint boundary without rerunning the consumed native process.
