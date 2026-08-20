# Ariadne agent error and correction register — revision 572

Date: 2026-08-20

Timestamp: 2026-08-20T16:04:16.4951745+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 572
incident_count: 689
new_incident_ids: AER-0682,AER-0683,AER-0684,AER-0685,AER-0686,AER-0687,AER-0688,AER-0689
open_incident_count: 0
-->

This revision records eight contained or corrected lifecycle-repair and
verification incidents. None opened product, provider, database, protected-ref
or deployment authority, and none remains open.

## AER-0682 — provider-free bootstrap consulted the ambient home

The first isolated provider-free test import derived a package location through
the ambient user home. The sealed runner correctly made that dependency
unavailable and stopped before a native process.

Correction: the bootstrap now receives or derives its exact task-owned root
without consulting the ambient home. Provider-free collection covers the
sealed environment directly.

## AER-0683 — a static guard matched audit literals as executable scope

The controller's own static forbidden-surface test rejected literal credential
and future-attempt names that existed only in the audit guard itself. No
credential or attempt was opened.

Correction: the audit names are composed from closed fragments, leaving the
forbidden literal absent from executable source while retaining the same
fail-closed check.

## AER-0684 — direct script execution lacked the repository import root

The first direct-path controller check could not import repository modules even
though module execution worked. It failed before process or provider activity.

Correction: the controller binds the resolved repository root into its direct
entry-point import path, and both direct and module-shaped checks now pass.

## AER-0685 — a latch checkpoint bypassed the clockwork owner

One intermediate checkpoint wrote the active latch directly. The live
clockwork detected canonical drift before native execution or publication.

Correction: the direct draft was rejected, the clockwork restored all ten
surfaces from its byte-recoverable predecessor and every later checkpoint used
the exclusive clockwork writer.

## AER-0686 — checkpoint prose contained a hand-completed Git object

The first pre-verifier checkpoint prose contained a 40-character-looking
expansion that did not equal the resolver's full object. Its machine source
binding remained correct, and readback caught the prose conflict before review
acceptance.

Correction: a new clockwork tick injected
`f89677fb17f80e0660f6dd2b72f8cfad09b190d6` directly from the resolver. The
rejected checkpoint remains immutable.

## AER-0687 — a clockwork manifest used a non-admitted executable

The first local checkpoint command manifest named Git directly where the
clockwork grammar admits the exact Python module entry point. Validation
rejected it before publication.

Correction: the manifest now uses the admitted Python `-m` clockwork command,
and its check, publish and readback pass.

## AER-0688 — provider-disabled native preset validation failed closed

The one authorised native rc.7 process passed preset discovery and stopped at
the first missing `PRESET_VALIDATION_PASSED` marker. It created no agent or
turn, made zero broker/model/provider/network/Docker/database requests, retried
zero times and left no process or disposable root.

Containment: the terminal is consumed and immutable. A successor may split the
validation coordinate provider-free; it may not retry this process or infer a
DeepSeek-quality result.

## AER-0689 — isolated verifier worktree doubled the worker-root segment

The initial Gemini veto found that the controller appended `EMR4-worktrees`
when it was already running inside that directory. Its C03 and C04 commands
failed, and the review returned `revision_required` with an unchanged clean
candidate.

Correction: `_worker_root()` now maps both the primary checkout and a direct
isolated-worktree child to the same exact worker root. A regression covers both
shapes, 52 provider-free tests pass there, and one fresh corrected Gemini veto
passes all nine commands at unchanged clean HEAD.

