# Native analysis — Reception One selected-action-console progressive disclosure

Date: 2026-08-14

Timestamp: 2026-08-14T17:22:06+10:00 (Australia/Brisbane)

Source inspected: `67f203097507d5f8c976f716ff37f720f4ea6b73`

Disposition: `completed_read_only_positive_leverage`

## Implementation-seam result

The composition can remain confined to `docs/diary/meta-grid.js`,
`docs/diary/meta-grid.css` and the two asset cache references. The four bridge
methods in `docs/diary/diary.js` remain unchanged.

The exact implementation seam is one presentation-only
`activeSelectedAction`, explicit resets beside the four existing action-state
resets, one console renderer replacing the unconditional four-renderer block,
and an append target supplied to exactly one existing field renderer. The
summary must use `selectedStatusActionItem()` so requested state cannot
contaminate current truth.

Two additional fail-closed hazards were identified and added to acceptance:

- selecting another appointment while a field action is busy currently clears
  all four action latches, so busy reselection must be ignored; and
- blur or fresh event-driven projection replacement can preserve idle requested
  values, so provisional drafts must be cleared before changed truth can render.

No render may occur from an in-flight bridge callback because that would
replace the control retained for the existing confirmation dialog's focus
return. Workspace Escape remains unchanged.

## Test-seam result

The four current route-intercepted suites already provide strong status/update
proposal/confirm trace, raw-write absence, paired outcome, interruption,
focus/Escape and responsive evidence. Their opening helpers need small Sol-owned
adaptations to activate the appropriate palette button before waiting for the
unchanged field panel. Simultaneous-panel assertions become palette-lock and
one-active-editor assertions.

The narrowest separable DeepSeek package is one new file,
`review/test_reception_one_selected_action_console.py`, capped to a single
authored-synthetic fixture and seven cases:

1. collapsed native route-inert palette;
2. open/collapse/switch zero-or-one editor and zero routes;
3. four-field collapse/switch draft disposal;
4. four-field busy palette locking plus dialog preservation;
5. interruption teardown and fresh refresh;
6. exact field request traces plus fresh rebind/removal; and
7. accessibility and desktop/tablet/phone containment.

One polite live-region assertion is scoped to the shared editor because the
Diary correctly has other independent live regions. All worker browser evidence
is `route_intercepted_browser`; static guards are
`authored_synthetic_client_fixture`; neither is live evidence.

## Authority result

No source was edited by either native analyst. No route, backend, API Spine,
database, provider, product data, protected evidence, deployment or Git
authority was exercised. Sol retains plan, product, integration and acceptance
ownership.
