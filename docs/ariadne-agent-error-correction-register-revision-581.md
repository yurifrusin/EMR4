# Ariadne agent error and correction register — revision 581

Date: 2026-08-21

Timestamp: 2026-08-21T10:15:26.7935902+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 581
incident_count: 749
new_incident_ids: AER-0744,AER-0745,AER-0746,AER-0747,AER-0748,AER-0749
open_incident_count: 0
-->

## AER-0744 — candidate Git object repeated in receipt prose

The first preexecution runtime state put the full candidate object into the
free-form Git evidence sentence even though exact objects belong only to the
machine snapshot. The receipt rejected before native launch. The rejected
receipt is preserved, the prose now names only the active candidate, and the
corrected five-source receipt passes with zero manual objects.

## AER-0745 — malformed composite prelaunch PowerShell reading

The first composite prelaunch command embedded a semicolon inside an invalid
parenthesized expression and failed in the parser. It started no process and
changed no file. The reading was decomposed into explicit assignments; the
deterministic check, candidate ancestry, zero-output, Node identity and four
protected refs then passed before the only native launch.

## AER-0746 — inadmissible pytest selector in checkpoint manifest

The checkpoint manifest supplied `-k` to the provider-free pytest wrapper,
which deliberately accepts only literal repository-relative test files. The
post-terminal command was rejected before pytest collection and changed no
evidence. The exact acceptance set was rerun as five whole admitted files,
including the materialisation fixture once, and all 64 tests passed. Future
provider-free manifests use literal file paths only unless the wrapper first
gains a separately reviewed typed-selection contract.

## AER-0747 — noncanonical clockwork incident stage

The first closeout intent labelled two prelaunch observations
`preexecution`, which is not a member of the clockwork's closed incident-stage
vocabulary; that phase is represented as `dispatch`. The read-only check
rejected before transaction preparation, command execution or publication.
The observations now use the engine-owned value and the unchanged transaction
is rerun.

## AER-0748 — successor latch omitted canonical closed-surface token

The first published successor latch retained the closed ordinary-practice
meaning but omitted the exact
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`
token required by baton consistency. The postpublication suite rejected it.
The uncommitted clockwork generation was rolled back byte-exactly, the token
was added to the typed intent, and the corrected bundle is republished.

## AER-0749 — rollback lease not bound before replacement dry-run

Clockwork rollback restored canonical and metadata bytes but correctly
incremented its monotonic pointer lease. The first replacement dry-run was
attempted before that lease change was committed and rejected with
`tick_pointer_physical_drift`. Only the clockwork-owned pointer was then
committed; replacement publication now starts from that durable rollback
lease.

All six incidents are corrected or contained. None remains open. The native
Harness attempt ran exactly once, no DeepSeek provider call occurred, and no
product, data, deployment, protected evidence or protected ref was affected.
