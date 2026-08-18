# Ariadne agent error and correction register — revision 394

Date: 2026-08-18

Timestamp: 2026-08-18T16:09:20.8230251+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 394 adds AER-0452 and AER-0453 before the first monitored occupied
native-Harness EMR4 dispatch.

AER-0452 corrects a manually expanded plan-source SHA in the live latch. The
only admitted identity is the standalone `git rev-parse HEAD` output
`bb6d9c65910c2464dd1cfb5bfe087984f3d8a583`. The incorrect full identity did
not control a dispatch, provider request, candidate adoption or ref movement.

AER-0453 corrects the stronger boundary claim in the frozen native-Harness
plan. Exact rc.7 package source states that its filesystem sandbox fences
mutations while every mode permits reads, and that same-UID model tools can
read locally held credentials. Sparse checkout plus workspace-write was
therefore not technical read or credential isolation. No occupied call had
occurred. The recovery freezes a no-direct-egress Harness container that sees
only the sparse worktree and no provider credential, plus a separate
authenticated broker sidecar that holds the provider key and shares no mount.
The first trial also removes model-facing shell authority; Sol runs the tests.

These corrections preserve the original two-path worker package, prepaid
monetary boundary, zero retry/fallback, single session, 15-minute wall clock,
protected refs and all product/data prohibitions.

## Population

- incidents: 453;
- corrected or explicitly contained: 453;
- open: 0;
- latest id: `AER-0453`.
