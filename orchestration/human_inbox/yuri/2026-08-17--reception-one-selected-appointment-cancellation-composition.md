# Reception One selected-appointment cancellation composition

Date: 2026-08-17

Timestamp: 2026-08-17T15:49:00.1044374+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

## Lay summary

Reception One can now cancel a selected appointment through the same contained
truth-first pattern as its other actions. Staff choose an administrative
reason, review the consequence and must explicitly confirm. The appointment is
not removed merely because the command appeared to succeed: Reception One
reads the Diary again and displays what the backend now says is true. If that
check cannot be completed, every action is disabled and no uncertain claim is
made.

This also records an important architectural point. Our native screen is one
reference client, not the only permissible Raisa experience. A future creative
display engine may reshape the interaction, and Siri or another external client
may own the presentation entirely. They can be creative about how meaning is
shown, but not about the meaning itself: facts, consequences, warnings,
confirmation, authority checks and receipts remain fixed by Raisa.

## Technical summary

- Exact accepted source: `856ebc3d832d5b64ce65c2e0732eaa63d926c600`.
- The fifth action uses only
  `POST /api/v1/appointments/proposals/delete/{appointment_id}` and canonical
  `POST /api/v1/appointments/proposals/delete/confirm`.
- There is no raw `DELETE`, status-cancellation fallback, new route/schema or
  optimistic appointment mutation.
- Strict public-envelope/receipt validation and fresh reconciliation cover
  success, staff cancellation, blocking, stale authority, malformed responses,
  transport ambiguity, interruption and replay.
- 15 dedicated and 84 combined browser cases, 43 focused checks and the
  canonical 200-test profile pass, along with syntax, Ruff, compilation,
  whitespace and three responsive viewport inspections.
- One fresh Gemini 3.7 Flash/high exact-candidate veto passed cleanly.
- DeepSeek's first transport non-result, two rejected pre-verifier drafts and
  one stopped pytest sequencing recurrence are preserved and corrected in
  AER-0382 through AER-0384. Register revision 337 contains 384 incidents with
  none open.

## Deliberately closed

No live backend/database proof, product/patient/clinical data, external adapter,
provider call, ADC/credential/IAM change, executable model tool, raw
compatibility write, migration, deployment, production, release, Pages rebuild
or protected-ref movement was opened. `docs/branding/` and every unrelated
untracked file remain preserved.

## Place in Raisa

The complete selected-action console now spans status, time, duration,
practitioner and cancellation while keeping presentation subordinate to the
same database-backed authority kernel. It is a stronger reference client and a
concrete proof that other human-facing adapters can vary their UX without
acquiring semantic or command authority.

## Planned next tranche

The sprint engine will continue with a provider-free read-only ordinary Diary
cancellation compatibility-consumer convergence review. Its purpose is to map
the older `deleteBooking()` / `applySignedDeleteProposal()` dual-family fallback
onto the canonical delete-only seam, initially without editing or calling any
route. Yuri's attention is not required.
