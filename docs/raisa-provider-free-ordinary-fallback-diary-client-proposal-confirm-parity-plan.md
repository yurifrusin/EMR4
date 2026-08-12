# Provider-free ordinary/fallback Diary client proposal-confirm parity plan

Date: 2026-08-12

Source HEAD: `d08b32db3f7cfbfb2307f3b03b8b83ec3d017f34`

Status: `frozen_for_bounded_implementation`

## Purpose

Move the native Diary's remaining ordinary and fallback appointment writes
inside the existing proposal plus signed-confirm envelope. The four raw
compatibility route families remain mounted and behaviorally unchanged for
unidentified external, recovery or migration consumers.

## Frozen inventory

The source-bound inventory is
`orchestration/continuity/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity/native-diary-raw-call-site-inventory.json`.
It records exactly seven native raw call sites:

1. create-modal missing-evidence fallback to raw `POST`;
2. edit-modal missing-evidence fallback to raw `PUT`;
3. drag/resize missing-evidence fallback to raw `PUT`;
4. edit-modal post-update raw status `PATCH`;
5. create-modal post-create raw status `PATCH`;
6. status/waiting-area missing-evidence fallback to raw status `PATCH`; and
7. delete-modal missing-evidence fallback to raw `DELETE`.

The accepted end state is zero raw appointment mutation calls in
`docs/diary/diary.js`, not removal of the backend routes.

## Frozen implementation

### Proposal admission

- Every native create, update, status, waiting-area and delete proposal request
  sends a non-empty client-generated `Idempotency-Key`.
- A booking-modal proposal key is stable across its warning-confirmation
  re-proposal and resets when the edited intent changes or the modal closes.
- Drag/resize, status/waiting-area and delete allocate one proposal key per
  user gesture.
- Delete's bounded 404 compatibility branch may request the existing status
  proposal with the same per-gesture key. It may not call raw delete.

These headers identify a proposal attempt only. They add no proposal replay,
reservation or new server write semantics.

### Fail-closed proposal handling

- Every fresh proposal is checked for blocks, including the second booking-
  modal click after warnings were shown.
- A changed warning-code set must be shown again; an earlier confirmation does
  not confirm newly returned warnings.
- A safe proposal that lacks an allowlisted confirm endpoint or confirm payload
  fails closed with no raw fallback.
- A confirm response must remain `safe=true`, `autonomy_tier=confirmed_write`
  and contain the expected appointment result.

### Status after create or update

The existing two-step booking behavior remains two-step, but its second write
uses the status proposal and signed status-confirm family. Routine safe status
changes follow the same no-extra-dialog policy as the existing status control.
Warning-bearing, blocked or terminal proposals use the existing status proposal
dialog. If the second step is blocked, cancelled or fails, the already
confirmed base create/update remains committed and the modal reports that the
booking details were saved but the selected status was not applied. The client
must never conceal that partial outcome or retry through raw `PATCH`.

## Authored-synthetic evidence

Evidence must prove:

1. the frozen inventory contains exactly seven unique pre-tranche call sites;
2. `docs/diary/diary.js` contains no raw appointment `POST`, `PUT`, status
   `PATCH` or `DELETE` mutation call;
3. all native proposal families send a non-empty idempotency header;
4. a blocked second-click re-proposal performs no confirm or raw write;
5. changed warnings require renewed review;
6. missing create/update/status/delete signed evidence fails closed;
7. edit and create status side-writes use status proposal plus signed confirm;
8. routine status, waiting-area, drag/resize and delete paths preserve their
   ordinary behavior through signed confirm;
9. rejected confirms perform no raw fallback;
10. the four backend raw compatibility routes remain mounted, retain their
    handlers/signals and keep the default `audit` mode; and
11. API Spine inventory records native-client parity without claiming external
    consumer, route-retirement, deployment or production readiness.

## Owned files

- this plan, design and threat-model delta;
- the exact inventory/schema under the tranche continuity directory;
- bounded edits to `docs/diary/diary.js`;
- bounded Diary route-intercepted tests and API Spine inventory tests;
- API Spine readiness/deprecation declarations describing the accepted client
  state without changing route behavior; and
- exact acceptance, continuity, closeout and Yuri mailbox artifacts.

## Forbidden surfaces

- no removal, rename, blocking or behavioral change to raw compatibility routes;
- no `appointment_raw_compat_mode` change or raw-route idempotency expansion;
- no backend command-kernel convergence or create fence;
- no database/source/watcher/event, observer, sink or persistence work;
- no provider call, model, patient/product dataset or live external consumer;
- no new appointment command authority or GraphQL mutation;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated untracked
  file.

## Acceptance and recovery

The tranche passes only if route-intercepted browser evidence, focused API
Spine/backend preservation tests, JavaScript syntax/static checks and the
canonical fast profile pass with zero native raw writes and unchanged protected
refs. One bounded mechanical correction may repair a client helper, fixture,
inventory assertion or declaration. A need to alter a backend compatibility
route, add a command, access product truth outside existing APIs or infer an
external consumer's readiness is conceptual and stops this tranche.

After acceptance, raw-route kernel convergence remains a later, separate gate.
The next tranche must be selected from the updated Compass only after this
client parity result is continuity-bound.
