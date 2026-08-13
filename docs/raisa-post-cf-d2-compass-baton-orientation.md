# Post-CF-D2 Compass and baton orientation

Date: 2026-08-13

Timestamp: 2026-08-13T21:18:59+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_acceptance`

Result: `raisa_post_cf_d2_compass_baton_orientation_pass`

## Orientation result

The next dependency-satisfied visible product tranche is a **provider-free
Reception One selected-appointment status-action composition**.

Reception One already renders current appointment cards and their status in
its modeless intent-projected workspace. The ordinary native Diary now has an
accepted visible status selector backed exclusively by the existing
appointment-status proposal/confirm family. The missing seam is narrow and
observable: Reception One's bridge exposes reads, availability, create
proposal handoff and date navigation, but no status action; its appointment
card displays status as read-only text.

The successor should let staff select one current appointment in Reception
One, choose one existing status transition and pass that intent through a
small bridge to the same status interaction already used by the ordinary
Diary. It must not add a second command implementation or raw fallback. The
ordinary command path retains proposal admission, exact warnings/blocks,
terminal confirmation, provisional-identity safeguards, command-time current
authority/source-truth recheck, idempotency, audit, receipt and fresh reload.

## Why this is the narrowest useful successor

- It advances the accepted conversation-first/product-projection direction:
  a routine staff task becomes possible from the focused Reception One view
  without searching the full Diary.
- It reuses an already accepted command family and visible interaction instead
  of creating new backend authority.
- It needs no event delivery. CF-D2 remains an optional payload-free
  acceleration layer for changes made elsewhere, not a prerequisite for the
  staff-initiated command.
- It is provider-free and can be proven with authored-synthetic responsive,
  keyboard, cancellation, warning, blocked, stale and success evidence.
- It preserves the modeless Diary relationship and explicit distinction
  between current fact, staff selection, proposal and committed result.

## Exact successor boundary to freeze

The next tranche should be limited to:

1. an action affordance on a single selected Reception One appointment card;
2. the existing status vocabulary only;
3. a bridge method that resolves the exact current appointment from the
   authoritative client snapshot and delegates to the existing
   `setAppointmentStatus` interaction;
4. the existing safe/warning/terminal/provisional-identity behavior;
5. busy, cancel, blocked, stale/failure and committed feedback inside the
   modeless Reception One surface;
6. fresh Diary reload and selected-card reconciliation after success; and
7. desktop, tablet, phone, keyboard, focus-return and interruption evidence.

No change to FastAPI, GraphQL, OpenAPI, PostgreSQL, the status proposal/confirm
contract, the status vocabulary, current authority, event/cue runtime or
provider behavior is eligible.

## Alternatives retained but not selected

| Direction | Disposition |
|---|---|
| Representative Stage 3B sessions | Deferred; Yuri must reopen execution and nominate or schedule the cohort. |
| First external patient channel | Future programme; identity topology, provider/channel choice, recovery and hosting remain unsettled. |
| Another Diary event family | Candidate only; Compass requires a fresh Yuri value/family decision. |
| Operational CF-D2 watcher or restart work | Later extension; runtime, source, persistence and restart authority remain closed. |
| Another appointment command family | Not selected; the present authority closes other command families. |
| General visual polish | Lower leverage than composing one already-secured routine task into Reception One. |

## Programme position

CF-D2 has done enough for the present horizon: its five serial protocols have
honest database evidence while command correctness remains independent of
delivery. The programme can therefore return to visible Reception One work
without either abandoning future durable cues or making UI progress wait for a
watcher runtime.

The chosen tranche is the smallest bridge from the secured status command into
the accepted projection-console experience. It does not start patient-facing
work, expand event coverage or turn Reception One into an authority boundary.

## Claim boundary

This is a repository-local orientation result. It changes no product behavior
and proves no runtime. Protected evidence, historical Diary/PHI,
patient/product/clinical data, external patient clients/channels, real identity,
source/watcher/persistence, provider/ADC, credentials/IAM/network, new
commands/writes, deployment, production, release, Pages and protected refs
remain closed.
