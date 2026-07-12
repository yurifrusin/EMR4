# Review: S8 W2 Revision 1 — Diary Header Layout Regression

**Source:** `orchestration/agent_inbox/deepcode/deepcode-s8-w2-revision-1.md`
**Candidate branch:** `deepcode/s8-w2-affordances`
**Worker:** DeepSeek Flash via Deep Code (local mailbox bridge)

---

## Problem

`review/test_diary_smoke.py::test_bernie_stale_navigation_clearing` fails because
Playwright cannot click `#btn-today` — the new S8 W2 `#diary-search-input` element
intercepts pointer events over it at certain viewport widths.

## Root Cause

`.diary-actions` (the flex section containing the search input, toggle flow,
refresh, etc.) has `min-width: 0` in `diary.css`. This allows `.diary-actions` to
shrink below its natural content width when the three header flex sections
(`.diary-logo`, `.diary-date-nav`, `.diary-actions`) are on one line but the total
available width is tight.

When `.diary-actions` shrinks below its content width (~300px: search input 120px +
clear button + toggle-flow ~90px + refresh ~55px + gaps), the `overflow: visible`
(default) causes the `#diary-search-input` to overflow leftward into the adjacent
`.diary-date-nav` section, physically covering `#btn-today`.

## Fix

**File:** `docs/diary/diary.css`  (one line)

Changed `.diary-actions` from `min-width: 0` to `min-width: fit-content`.

This prevents `.diary-actions` from ever shrinking below its content width. When
the total flex-basis of the three header sections plus gaps exceeds the available
header width, the existing `flex-wrap: wrap` on `#diary-header` pushes the entire
`.diary-actions` section to its own line where it has full width and no overlap
can occur.

No responsive breakpoints were added or removed. The existing `@media (max-width:
520px)` and `@media (max-width: 300px)` breakpoints continue to work as before.

## Files Changed

| File | Change |
|---|---|
| `docs/diary/diary.css` | `.diary-actions` `min-width: 0` → `min-width: fit-content` |
| `docs/diary/diary.html` | Version cache-bust `diary.css?v=136` → `diary.css?v=137` |

## Verification Results

### Focused day-search tests (`review/test_diary_day_search.py`)
```
5 passed
```

### Full smoke suite (`review/test_diary_smoke.py`)
```
All passed (includes test_bernie_stale_navigation_clearing)
```

### Selection preservation (`review/test_diary_selection_preservation.py`)
```
3 passed
```

### JavaScript syntax
```
node --check docs/diary/diary.js → PASS
```

### Whitespace
```
git diff --check → clean
```

### Version check
```
diary.html:  diary.css?v=137, diary.js?v=184
```

## Permission Limitation

The current `askAll` permission profile denied the `mutate-git-log` side effect,
so the candidate changes (**diary.css**, **diary.html**) could not be committed
locally. The working tree contains the unstaged fix for the orchestrator to
review, stage, and commit as part of integration.

## Scope

This fix is strictly limited to the CSS layout regression. No JavaScript logic
was changed. No test assertions were weakened or bypassed. The existing S8 W2
day-search affordance (search input, highlights, clear, re-apply on refresh)
continues to function and is verified by the 5 focused day-search tests.

## STATUS: complete
