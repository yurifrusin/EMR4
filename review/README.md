# `review/` — cost-conscious sprint-review harness

A starter template for taking the model **out of the review execution loop**. Instead
of Ariadne driving a browser step-by-step (each step a paid model round-trip with
screenshots), the deterministic checks live here as code, run free under `pytest`,
and emit a JUnit report Ariadne reads only when something fails.

> Status: Initial diary smoke harness ratified by Ariadne and wired into CI.

## What's here

| File | Purpose |
|---|---|
| `harness.py` | Reusable Playwright primitives (`count`, `min_count`, `text_count`) + a static-file server and an `office.js` stub. Model-agnostic library code. |
| `checks_diary.json` | Data-driven check table for the diary grid. **Add a check = add a row** — no Playwright code to write. |
| `test_diary_smoke.py` | Pytest spec: serves `docs/`, loads `diary.html?smoke=true`, parametrizes over the table so every check is a named case in the report. |

## Why it's deterministic

It targets the diary's built-in **`?smoke=true`** mode, which renders the grid from
embedded fixtures — **no backend, no auth, no DB seeding**. `office.js` is stubbed so
`Office.onReady` fires offline. Same input every run → stable assertions.

## Run it

```bash
pip install -r review/requirements.txt
playwright install chromium          # one-time browser download
pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q
```

A green run prints nothing of interest; `review/diary-review.xml` carries per-check
pass/fail. Ariadne reads that and engages only on failures.

## What the diary checks prove

Expectations match the **embedded `FALLBACK_TEMPLATE` + smoke fixtures** in `diary.js`,
which `?smoke=true` renders — these are intentionally heterogeneous (to exercise
per-column breaks/intervals) and differ from `diary_template.json`:

- 3 room columns + 1 time column render.
- **LUNCH** appears in all 3 columns; **MORNING TEA** in 2 (Room 3 has none); **BRUNCH**
  only in Room 2 — locking the per-column break shape.
- Room 1 / Dr Alex Shera column header renders.
- Lifecycle classes `appt-booked` and `appt-arrived` render. **Cancelled** appointments
  are deliberately excluded from the grid (`shouldRenderAppointment`) — they belong in
  the flow panel's Cancelled section, so there is no grid `appt-cancelled` to assert.

> Note: asserting "breaks in *all* columns" per the canonical `diary_template.json`
> (the real product rule that was once buggy) needs a **backend-backed** check — the
> real API returning that template — not smoke mode. That's a good next harness to add.

## Extending it (the pattern)

1. **Explore once** — for a new surface, do one exploratory pass to find selectors/state.
2. **Crystallize** — add rows to a `checks_*.json` table (or a new one); reuse the
   primitives in `harness.py`. Add a new primitive only for a genuinely new assertion shape.
3. **Run free forever** — every later sprint runs the suite with no model in the loop.

## Recommended hardening (for Codex/Ariadne)

- Add stable `data-testid` attributes to the diary DOM so checks don't break on
  restyling — this is what keeps the model out of the *repair* loop.
- CI runs the diary smoke review through `.github/workflows/ui-review.yml` when
  `docs/diary/**`, `review/**`, or the workflow itself changes.
- For backend-only facts (e.g. cancellation_reason persistence) prefer a direct HTTP
  probe over a browser check — cheaper still.
- Selectors/expectations here were derived by reading `docs/diary/diary.js` and
  `diary_template.json`; the authoritative validation is a live `pytest` run with
  Playwright installed.
