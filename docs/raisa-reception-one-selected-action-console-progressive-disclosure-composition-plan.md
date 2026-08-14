# Reception One selected-action-console progressive-disclosure composition plan

Date: 2026-08-14

Timestamp: 2026-08-14T17:06:54+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_implementation`

Task baseline: `67f203097507d5f8c976f716ff37f720f4ea6b73`

Target result: `raisa_reception_one_selected_action_console_progressive_disclosure_composition_pass`

Reasoning level: High. The preceding Extra High orientation already froze the
user-visible architecture and authority meaning; this tranche implements and
verifies that exact bounded contract.

## Objective

Replace the four permanently stacked selected-appointment editors with one
compact current-truth summary, four native action buttons and exactly zero or
one existing field-specific editor. Preserve every status, time, duration and
practitioner renderer, executor, bridge, request shape, proposal/confirmation
route and fresh-reconciliation path.

Multi-field intent remains an inert provisional concept only. The client must
not automatically execute several single-field commands, construct a compound
dispatcher, imply atomic multi-field behavior or claim a compound-update
contract that has not received its own backend proof.

## Authorised surface

Implementation is limited to:

- `docs/diary/meta-grid.js`;
- `docs/diary/meta-grid.css`;
- the `meta-grid.js` and `meta-grid.css` cache references in
  `docs/diary/diary.html`;
- the four existing route-intercepted selected-action browser test files and
  one narrowly bounded action-console test artifact if useful; and
- tranche-local plan, threat, typed evidence, acceptance, continuity and
  closeout artifacts.

`docs/diary/diary.js`, every bridge, backend, API Spine artifact, request
payload, route and database surface are read-only controls in this tranche.

## Frozen interaction contract

1. `activeSelectedAction` is presentation-only and exactly one of `null`,
   `status`, `time`, `duration` or `practitioner`.
2. Selecting an eligible appointment resets the enum to `null`, renders a
   patient-minimized current-truth summary and four native buttons, and focuses
   the first button without opening an editor.
3. A button activation performs zero HTTP requests and only opens its existing
   field-specific renderer in one shared labelled editor region.
4. Activating the open action collapses it and returns focus to its button.
5. Idle switching resets the outgoing field's unsubmitted provisional state
   from current truth, announces that no new Diary change occurred and opens
   the requested editor. No concealed draft survives.
6. Collapse or switch is disabled while any action is busy, the existing
   confirmation dialog owns focus, the projection is stale/interrupted or
   fresh reconciliation is required.
7. The active renderer remains mounted through proposal and confirmation, so
   existing Escape and field-specific focus return remain unchanged.
8. A terminal result leaves the same action open. If the appointment leaves
   the projection, that action's existing terminal outcome replaces the editor;
   requested values never appear as current truth.
9. Window-blur or visibility interruption keeps the existing refresh-only
   safety gate and clears any unsubmitted draft before another action can open.
10. The summary is derived only from the selected fresh projection: status,
    start/end time, duration and practitioner display. It contains no patient
    name, command evidence or provisional value.
11. Appointment reselection is ignored while an action is busy or confirmation
    owns focus, so selecting another card cannot erase an in-flight action
    latch. Fresh event-driven projection replacement also clears any idle
    provisional draft before it could reappear against changed truth.

## Accessibility and responsive contract

- Palette choices are ordinary `button` elements in document tab order with
  `aria-expanded` and `aria-controls`; there is no tablist, toolbar or roving
  tabindex.
- The shared editor has one stable labelled region and contains exactly one
  existing action-specific polite atomic live region.
- Palette buttons have at least 44-by-44 CSS-pixel targets.
- The palette wraps without horizontal scrolling at desktop, tablet and phone
  widths; the one editor remains full width beneath it.
- The existing confirmation dialog remains the only focus-contained layer and
  retains Escape ownership.

## API Spine preservation

This is a presentation composition over existing REST/OpenAPI commands.
GraphQL remains read-only. Status continues through the existing status
proposal/confirm family. Time, duration and practitioner continue through
their field-specific bridges to the update proposal/confirm family. Palette
activity is not a command-style read and must issue no route. No raw
compatibility `PUT`, `PATCH` or other second write path may appear.

## Acceptance matrix

The tranche passes only if deterministic and rendered evidence proves:

1. no editor initially and exactly zero or one action editor thereafter;
2. zero API routes on open, collapse and idle switch;
3. outgoing draft disposal across every supported switch;
4. all palette transitions disabled during four-way busy, stale,
   interruption and confirmation states;
5. unchanged status and update proposal/confirm request traces and zero raw
   compatibility writes;
6. unchanged confirmation focus containment, Escape and field focus return;
7. exact fresh rebind or action-specific removal outcome after every terminal
   result;
8. one active polite live region, native keyboard semantics, 44-pixel targets
   and no horizontal overflow at desktop, tablet and phone widths;
9. busy appointment reselection cannot replace the selected action, and fresh
   externally driven projection replacement cannot resurrect an idle draft;
10. source guards forbidding a generic command object, automatic multi-command
   sequencing or a compound-update claim;
11. relevant focused tests, API Spine invariant tests, canonical fast-profile
    checks, JavaScript syntax, Ruff, compilation and Git whitespace; and
12. one fresh Gemini 3.6 Flash/high exact-candidate veto at an unchanged clean
    review worktree after deterministic admission.

Route-intercepted Playwright evidence is labelled
`route_intercepted_browser`; it is not live backend or database evidence.
Rendered in-app Browser inspection is fixture/local visual evidence unless an
explicit non-intercepted backend boundary is separately proven.

## Parallelism-efficacy allocation

- **Native subagents — dispatched read-only:** one exact JavaScript/CSS
  implementation-seam audit and one existing browser-fixture, selector,
  route-count and responsive-validation audit.
- **DeepSeek V4 Flash/high — planned after this freeze:** one tightly capped
  test-only package over the four existing route-intercepted selected-action
  test files, with no product-source, architecture, acceptance or Git authority.
- **Gemini 3.6 Flash/high — reserved:** one fresh read-only exact-candidate veto
  after deterministic and rendered passage.
- **Sol — serial authority owner:** reconcile analyses, implement product
  source, admit or recover worker artifacts, run browser verification, accept,
  update Continuity and use Git.

Reassess at native return, DeepSeek pre-dispatch and return, material recovery,
pre-verifier admission and closeout.

## Stop and recovery conditions

Stop or narrow if the accepted result would require a new bridge, route,
request field, combined command, backend/API/database change, language intent
execution, product/patient data, provider, protected evidence, deployment or
protected-ref movement. A rejected mechanical worker artifact receives at most
one bounded same-lane correction; a conceptual authority defect transfers to
Sol recovery without another Flash loop.

## Closed surfaces

No backend, API/OpenAPI/GraphQL, database/migration/RLS, event/watcher,
provider/ADC, credential/IAM/network, product/patient/clinical data, historical
Diary/PHI, language execution, compound update, deployment, production,
release, Pages or protected-ref authority is opened. `docs/branding/` and every
unrelated untracked file remain preserved; staging is explicit-path only.
