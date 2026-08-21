# DeepSeek native Harness post-sentinel exit-coordinate diagnosis

Date: 2026-08-21
Timestamp: 2026-08-21T17:06:22.152214+10:00 (Australia/Brisbane)

## Result

- Verdict: `unique_supported_exit_coordinate`
- Narrowest supported coordinate: `headless_startup.apply.missing_task_program_error_to_app_exit_one`
- Exact source-chain links: `8 / 8`
- Retained events: `sentinel_activated`
- Retained exit / readiness / retry: `1` / `false` / `0`
- Node / Harness / broker / worker / model / provider / network activity: `0 / 0 / 0 / 0 / 0 / 0 / 0`

## Reading

The frozen launch passed no inner task argument. The exact headless bundle kept
its startup provider mounted even though the user patch disabled the one-shot
runner. After the sentinel activated, headless startup therefore took its
mandatory empty-task rejection branch. The exact command-line adapter routed
Commander's default failure code through `ctx.appExit`, and profile shutdown
disposed the tree with that same code before HMR registered both watched patch
paths.

This source chain is sufficient to explain the retained post-sentinel exit-one
terminal. It was derived without executing JavaScript and without reconstructing
or guessing the destroyed stderr text, stack, path, environment or stream.

## Claim boundary

A unique result identifies the exact empty-task startup rejection and shutdown path sufficient to explain the observed post-sentinel exit; it does not reconstruct stderr, prove later HMR readiness, authorize a repair, or authorize another native process.
