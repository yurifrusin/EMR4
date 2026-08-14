# DeepSeek V4 Flash/high bounded selected-action-console test packet

Date: 2026-08-14

Timestamp: 2026-08-14T17:25:10+10:00 (Australia/Brisbane)

Source HEAD: `46df6dd8db69d73dd672f5beb5c545510eeb3ecb`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\action-console-test-worker-d8dbe80a`

Assigned branch:
`codex/reception-one-action-console-test-worker-d8dbe80a`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact:
`review/test_reception_one_selected_action_console.py`. The completed file must
not exceed 800 source lines. You may read the exact allowlist below, create and
edit only that new file, run only the listed checks, stage that exact file and
make one worker commit. You have no existing-test edit, product implementation,
architecture, orchestration, acceptance, integration, push, protected-ref,
provider, database, runtime or deployment authority. Permission availability is
not authority.

Read `AGENTS.md` completely before acting. Then read only:

- `docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-plan.md`
- `docs/security/raisa-reception-one-selected-action-console-progressive-disclosure-composition-threat-model-delta.md`
- `orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-native-analysis.md`
- `review/harness.py`
- `review/test_reception_one_status_action.py`
- `review/test_reception_one_time_reschedule_action.py`
- `review/test_reception_one_duration_action.py`
- `review/test_reception_one_practitioner_reassignment_action.py`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `docs/diary/diary.html`
- `docs/diary/diary.js`

Use literal exact-path reads only. Do not use Glob, Grep, `rg`, recursive
search, directory listing, protected paths or any file outside that allowlist
and your new test artifact.

## Frozen product selectors

The parallel Sol implementation will supply these exact new stable selectors:

- `meta-grid-selected-action-console`
- `meta-grid-selected-action-summary`
- `meta-grid-selected-action-palette`
- `meta-grid-selected-action-editor`
- `meta-grid-action-choice-status`
- `meta-grid-action-choice-time`
- `meta-grid-action-choice-duration`
- `meta-grid-action-choice-practitioner`

The existing `meta-grid-status-*`, `meta-grid-reschedule-*`,
`meta-grid-duration-*`, `meta-grid-practitioner-*` and
`status-proposal-dialog` selectors remain unchanged. All four choice buttons
reference `meta-grid-selected-action-editor` through `aria-controls`; exactly
one may have `aria-expanded="true"`.

## Deliverable

Create one compact self-contained authored-synthetic provider-free pytest
browser contract. Reuse only minimum exact helpers from the allowlisted sibling
tests. Do not import mutable fixtures in a way that makes another test module's
collection or execution a hidden prerequisite.

Implement exactly seven focused test functions:

1. `test_palette_starts_collapsed_native_and_route_inert`
   - four real native buttons, no custom role or positive tabindex;
   - first button focused after appointment selection;
   - correct `aria-controls` and all `aria-expanded=false`;
   - no field panel initially;
   - patient-minimized summary contains status, time, duration and practitioner
     but no patient name; and
   - palette startup produces zero routes after fixture-startup traces clear.
2. `test_open_collapse_switch_keeps_zero_or_one_editor_and_zero_routes`
   - use visible Enter, Space and click activation;
   - open, collapse and switch through all four actions;
   - at every step zero or one existing panel is mounted; and
   - the intercepted route log remains empty.
3. `test_idle_collapse_and_switch_discard_each_field_draft`
   - parametrize status, time, duration and practitioner;
   - enter a non-current value, collapse or switch, reopen;
   - current/default truth is restored, review remains disabled, no route was
     sent and the announcer says no new Diary change occurred.
4. `test_each_busy_action_locks_all_four_choices_and_preserves_dialog`
   - parametrize all four fields with warning-confirmation cases;
   - while `status-proposal-dialog` is visible, all palette choices are
     disabled and only the active panel remains mounted;
   - Tab remains contained by the existing dialog; and
   - Escape returns focus to the active field's unchanged control.
5. `test_interruption_clears_draft_and_requires_fresh_refresh`
   - trigger window blur before any proposal;
   - no palette choice remains actionable, only the accepted refresh path is
     offered, no proposal/confirm route occurred;
   - after fresh list read the console is collapsed and the draft is gone.
6. `test_field_request_traces_and_fresh_rebind_or_removal`
   - parametrize four safe actions;
   - status trace is exactly status proposal then status confirm;
   - time/duration/practitioner traces are exactly update proposal then update
     confirm;
   - no raw PATCH/PUT or unexpected mutation occurs;
   - each proposal body changes only its intended field;
   - retained appointments keep the active action and fresh summary; and
   - one explicit removal outcome renders only its active action-specific
     terminal status.
7. `test_palette_editor_accessibility_and_containment`
   - parametrize viewports `(1280,720)`, `(768,1024)`, `(390,844)`;
   - all palette targets are at least 44 by 44 CSS pixels;
   - palette wraps with no document/host/editor horizontal overflow;
   - the editor is labelled; and
   - exactly one polite atomic status region exists inside the active editor.

Keep the evidence labels `route_intercepted_browser` and
`authored_synthetic_client_fixture` in the file. Never claim live product,
backend or database evidence. The product implementation is intentionally
absent at this source, so behavioral assertions may remain red until Sol's
parallel source lands. Do not weaken the contract to pass pre-implementation.

## Multi-field and authority guards

The test source must contain static or behavioral guards that reject:

- a generic action executor map or compound draft;
- automatic sequential execution of more than one field action;
- palette activation issuing any API request; and
- raw compatibility `PUT`/`PATCH` fallback.

Do not add product hooks or call page-internal execution functions. Drive all
authority-bearing behavior through visible controls and the existing explicit
confirmation dialog.

## Allowed checks

- `python -m py_compile review/test_reception_one_selected_action_console.py`
- a literal line-count command for that exact file
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_reception_one_selected_action_console.py`
- `git diff -- review/test_reception_one_selected_action_console.py`
- `git add -- review/test_reception_one_selected_action_console.py`
- `git diff --cached --check`
- `git commit -m "test(reception-one): specify selected action console"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree; Sol owns execution after admission.

## Terminal receipt

Return one compact result containing: status, exact changed file, final line
count, syntax-check result, expected-red behavioral status, commit hash,
boundary attestation and any genuine blocker. Do not claim acceptance.
