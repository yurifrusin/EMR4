# Ariadne agent error and correction register — revision 573

Date: 2026-08-20

Timestamp: 2026-08-20T17:18:14.3713624+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 573
incident_count: 694
new_incident_ids: AER-0691,AER-0692,AER-0693,AER-0694
open_incident_count: 0
-->

This revision records four contained or corrected preset-validation recovery
and workflow incidents. None opened product, provider, database, protected-ref
or deployment authority, and none remains open.

## AER-0691 — a closeout binding used a hand-completed Git object

The predecessor closeout draft expanded a seven-character abbreviation into a
40-character-looking value that was not the reviewed Git object. The ordinary
object resolver would have rejected it before acceptance, but the narrative
still depended on operator transcription.

Correction: Git-ref narratives now reject every manually supplied object ID.
Only the machine-generated `git_refs_snapshot` owns ref values; focused tests
cover both nonexistent objects and valid-but-role-wrong manual IDs.

## AER-0692 — the first independent veto preceded the native runner

The first Gemini veto correctly reviewed the deterministic/package candidate,
but the no-agent native runner was authored afterwards. Treating the first
receipt as covering the later runner would have left the executable candidate
without independent review.

Correction: the plan now permits one fresh veto per materially distinct exact
candidate. The first receipt remains accurately scoped, while a separate clean
Gemini 3.7 Flash/high veto reviewed the exact runner and passed all twelve
commands before its checkpoint.

## AER-0693 — native preset-row discovery failed closed

The sole checkpoint-bound provider-disabled rc.7 process reached
`PRESET_ROW_DISCOVERY_ENTERED` but not `PRESET_ROW_FOUND`. It created no agent
or turn, made zero broker/model/provider/network/Docker/database requests,
retried zero times and left no process or disposable root.

Containment: the terminal is consumed and immutable. The successor may explain
the native `agentPresets` service-path discrepancy provider-free; it may not
retry this process or claim native preset-validation or DeepSeek success.

## AER-0694 — latch checkpoints again bypassed the clockwork owner

Several intermediate latch readings in the resumed operation were committed by
direct file edits. The live canonical-owner check reported drift before
closeout acceptance. The native terminal and other evidence were unaffected,
but the previously accepted exclusive-writer invariant was breached again.

Correction: restore the latch byte-for-byte from the active generation, commit
the immutable terminal evidence against that clean baseline, and publish the
terminal checkpoint through the exclusive clockwork writer. Canonical readback
then reports ten owned surfaces, zero dual ownership and zero drift. All future
checkpoint and closeout latch movement remains clockwork-only.
