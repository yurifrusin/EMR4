# Provider-free visible native Diary status-confirm wiring plan

**Date:** 2026-08-13
**Timestamp:** 2026-08-13T15:13:59+10:00 (Australia/Brisbane)
**Status:** Frozen for execution
**Task baseline:** `2a407a8300560406f5311db4a4a54ebcf38a1e0e`
**Accepted backend source:** `b414eb256853c301099d9cf7797a69cd3ec077c5`
**Interaction-foundation source:** `17d9da1844e59406eecda44b5029e839b2e8a573`

## Purpose

Make the already accepted appointment-status proposal/confirm path visibly and
accessibly usable from the native Reception One Diary. This is a staff-only,
authored-synthetic, provider-free interaction tranche. It does not create a
new command, authority boundary, patient client or backend route.

Target flow: a receptionist changes an authored-synthetic appointment status
through the existing native Diary selector; a routine safe change proceeds
without an extra dialog, a warning or terminal change asks for explicit
confirmation, and cancellation or current-truth rejection leaves the existing
status unchanged with clear feedback and focus returned to the initiating
control.

## Frozen narrow implementation

1. Continue to obtain the signed status proposal and commit only through the
   accepted canonical status-confirm family. Retain the hidden compatibility
   alias only as already accepted; introduce no raw `PATCH` fallback.
2. Give the existing Diary status surface an accessible polite-live contract.
   Report checking, confirmation-required, saving, cancellation, committed
   outcome and fail-closed non-change in administrative language without
   adding patient details.
3. Keep routine safe transitions on the accepted no-extra-dialog path.
   Warnings, blocks and terminal statuses continue through the existing
   confirmation dialog.
4. Make that dialog name and describe itself, state the proposed status
   transition and the final current-Diary recheck, contain keyboard focus,
   close on Escape without committing, and restore focus to the initiating
   control.
5. Disable and mark the initiating selector busy while its transaction is in
   progress. On cancellation or failure restore its prior visible status; on
   success reload authoritative Diary truth and report the committed status.
6. Keep the surface legible at existing desktop, tablet and phone breakpoints.
   No wider Diary redesign is in scope.

## Acceptance

- A safe non-terminal change performs proposal then signed confirm without an
  extra dialog and without any raw appointment mutation.
- A warning or terminal proposal exposes one labelled confirmation dialog with
  the old and requested status plus the current-truth recheck boundary.
- A blocked proposal never offers a commit action.
- Cancel and Escape commit nothing, restore the previous selection, clear the
  busy state and restore focus.
- A signed confirm rejection or stale/current-authority failure commits
  nothing, restores the selector and says that the status was not changed.
- A successful confirm reloads the Diary and reports the committed status.
- Keyboard and responsive browser evidence covers desktop, tablet and phone;
  intercepted evidence is labelled `route_intercepted_browser`, never `live`.
- Existing route, API-spine, security-header, ordinary/fallback and canonical
  fast-profile tests remain green.
- All evidence is authored-synthetic and patient-free. No provider call,
  credential, IAM change, external network, product database/source, deploy,
  release, Pages or protected-ref action occurs.

## Protected boundaries

The tranche authorises changes only to the native Diary status interaction,
its exact tests/evidence, and its plan/security/closeout/continuity records.
Other appointment command families, GraphQL/OpenAPI, database schema or
migrations, external patient clients or channels, real identity, providers,
patient/clinical/product data and CF-D2 durability remain closed.
`docs/branding/` and every unrelated untracked file remain preserved and
excluded from staging.
