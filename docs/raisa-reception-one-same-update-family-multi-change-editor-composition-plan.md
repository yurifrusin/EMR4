# Reception One same-update-family multi-change editor composition plan

Date: 2026-08-15

Timestamp: 2026-08-15T01:55:57+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_implementation`

Task baseline: `e417eca0e1871a7ce5ed90c5e9223b8f86982b20`

Target result: `raisa_reception_one_same_update_family_multi_change_editor_composition_pass`

Reasoning level: High. The accepted atomicity orientation and M1-M7 kernel
rehearsal already freeze command-family meaning and transactional behavior.
This tranche composes only the bounded visible Reception One client over that
exact existing update route.

## Objective

Let an authorised receptionist progressively draft any non-empty combination
of appointment practitioner, local start time and duration, then submit exactly
one existing update-family proposal, review one complete proposed command and
perform one explicit human confirmation. Preserve the four-button Reception
One semantic keyboard and keep status in its distinct command family.

The composition must not auto-sequence field commands, add a new backend
command, turn a palette action into a write or let requested values appear as
current Diary truth before a fresh authoritative read.

## API Spine classification

- The current projection and exact appointment read are authorised reads.
- The shared draft is local, typed and non-authoritative.
- `POST /api/v1/appointments/proposals/update/{appointment_id}` remains the
  sole update proposal command.
- The proposal-supplied allowlisted
  `POST /api/v1/appointments/proposals/update/confirm` remains the sole update
  confirmation command.
- The existing signed evidence, freshness, actor/practice scope, idempotency,
  audit and confirm-time revalidation remain backend owned.
- GraphQL remains read-only; status remains on its separate status proposal and
  confirmation family.

No OpenAPI or backend contract change is required. The new client bridge entry
is a presentation adapter over the existing `handleMoveResize` command path,
not a second command surface.

## Authorised implementation surface

Product changes are limited to:

- `docs/diary/meta-grid.js`;
- `docs/diary/diary.js`;
- `docs/diary/meta-grid.css` only if a visible shared-draft summary needs
  bounded responsive styling;
- cache references for changed Diary assets in `docs/diary/diary.html`;
- mechanical adaptations to the existing Reception One time, duration,
  practitioner and selected-action-console route-intercepted browser tests;
- the existing two-projection truth-parity helper only if its Reception One
  interaction must acknowledge the new explicit confirmation; and
- one new bounded route-intercepted combined-editor browser contract plus
  tranche-local plan, threat, evidence, acceptance, continuity and closeout
  artifacts.

`app/**`, migrations, database schema, OpenAPI, GraphQL, async/event contracts,
manifests and every non-Diary product surface are read-only controls.

## Frozen interaction contract

1. The console retains exactly four native buttons: status, time, duration and
   practitioner. It still mounts zero or one field editor and uses ordinary
   keyboard order and native button semantics.
2. Time, duration and practitioner are three views into one appointment-update
   draft. The activated button selects and focuses that field's existing
   control; switching among those three buttons preserves every valid pending
   update-family value and issues no route.
3. The visible update editor includes a patient-minimized shared-draft summary
   derived from current projection truth plus locally entered values. It names
   only changed dimensions and never presents them as committed truth.
4. Activating the already open update action collapses the editor and discards
   the complete unsubmitted update draft. Switching between update and status
   also discards the outgoing draft because cross-family atomicity does not
   exist. Status retains its present isolated draft behavior.
5. Appointment reselection, root/projection replacement, window blur,
   visibility interruption and fresh event-driven replacement discard any idle
   update draft. None may resurrect a value against newer truth.
6. Each update field starts from current selected-appointment truth. A review
   button is disabled until at least one supported field differs and the
   complete proposed start/duration/practitioner combination is locally valid.
   A single changed field remains a valid special case of the shared draft.
7. Review passes all three effective values to one bounded Diary bridge entry.
   That bridge validates the same-day 15-minute time/duration constraints and
   exact unique active practitioner, computes one start delta, one duration
   delta and one target column, and calls `handleMoveResize` exactly once.
8. One click on Review may issue exactly one update proposal. It never issues a
   confirm request. Even a safe/no-warning proposal opens the existing
   confirmation dialog with the full before/after appointment meaning.
9. Only the visible `Confirm & Save` control may cause exactly one update
   confirm request. Cancel, Escape or a blocked proposal causes zero confirm
   requests and no client truth promotion.
10. While proposal, dialog or confirmation work is active, every palette
    button, field control, appointment reselection and draft transition is
    locked. Existing focus containment and Escape return target remain intact.
11. Every terminal result uses the existing exact appointment/current
    projection refresh path. A committed value becomes current truth only after
    fresh reconciliation; cancelled, blocked, stale or failed results retain
    current truth and never promote draft values.
12. If the appointment leaves the current projection after commit, one
    update-family terminal outcome replaces the editor. It must not render
    separate partial time, duration or practitioner outcomes.

## Accessibility and responsive contract

- The four palette controls remain native 44-by-44-pixel-or-larger buttons
  with `aria-controls` and exactly one active `aria-expanded=true` value.
- The shared update draft remains inside the one labelled editor region.
- Exactly one polite atomic live-status region is mounted inside the active
  editor.
- The draft summary and field-specific editor wrap without horizontal overflow
  at desktop, tablet and phone widths.
- The existing confirmation dialog remains the only focus-contained layer;
  Escape returns focus to the field whose Review control opened it.

## Acceptance matrix

The tranche passes only if deterministic and rendered evidence proves:

1. four semantic buttons and zero-or-one mounted field editor remain;
2. update-family switching preserves a multi-field draft while collapse,
   status crossover, reselection and interruption discard it;
3. palette and draft-only activity performs zero requests;
4. one combined practitioner/time/duration review emits one and only one
   proposal body containing the three effective values;
5. the safe proposal stops before confirmation, and only visible explicit
   `Confirm & Save` emits one confirm request;
6. Cancel/Escape, blocked, stale and transport-failure paths perform no partial
   truth promotion and no raw compatibility write;
7. status cannot enter the update draft or its request, and crossing command
   families discloses/discards rather than implying atomicity;
8. fresh terminal reconciliation updates all current-truth summary dimensions
   together or renders one update-family removal outcome;
9. busy/dialog/stale/interruption locks and appointment-reselection exclusion
   remain effective;
10. current single-field Reception One behaviors remain valid as one-field
    instances of the shared update draft;
11. native keyboard, focus return, one live region, 44-pixel targets and
    no-overflow checks pass at desktop, tablet and phone widths;
12. source guards prove exactly one `handleMoveResize` call, one update
    proposal family, one allowlisted confirm family, no update loop and no
    `PUT`, `PATCH`, GraphQL mutation or status-plus-update payload;
13. focused browser/API Spine tests, canonical fast-profile checks, JavaScript
    syntax, Ruff, compilation, JSON and Git whitespace pass; and
14. one fresh Gemini 3.6 Flash/high exact-candidate veto passes at an unchanged
    clean review worktree after deterministic admission.

Browser evidence is labelled `route_intercepted_browser` and authored-
synthetic. It is not a live backend, database, patient, provider or production
claim.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high — planned:** after this freeze, author only one new
  isolated route-intercepted combined-editor test module in a disposable
  worktree. It receives no product-source, existing-test, acceptance or Git
  integration authority.
- **Gemini 3.6 Flash/high — reserved:** perform one fresh read-only exact-
  candidate veto after the deterministic and rendered packet passes.
- **Native subagents — declined:** the product state, bridge and existing
  browser fixtures are tightly coupled, and no independent bounded package
  remains beyond the external test-only lane.
- **Sol — serial authority owner:** implement product source, adapt existing
  tests, admit or recover worker output, run rendered evidence, accept, update
  continuity and use Git.

Reassess at worker pre-dispatch/return, any scope or candidate failure,
pre-verifier admission and closeout.

## Stop and recovery conditions

Stop or narrow if acceptance would require a new backend route, request field,
command family, OpenAPI/GraphQL/database change, cross-family transaction,
provider/model call, product or patient data, external channel identity,
deployment or protected-ref movement. A rejected test worker receives at most
one bounded same-lane correction; conceptual authority or UX defects transfer
to Sol recovery before a fresh independent veto.

## Closed surfaces

No backend, API/OpenAPI/GraphQL, schema/migration/RLS, event/watcher, model or
provider/ADC, credentials/IAM/network, external patient/channel runtime,
delegated-assistant authority, patient/product/clinical data, deployment,
production, release, Pages or protected-ref authority is opened.
`docs/branding/` and every unrelated untracked file remain preserved;
staging is explicit-path only.
