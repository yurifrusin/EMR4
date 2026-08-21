# Native Harness attempt 005 readiness — lay and technical summary

Date: 2026-08-21
Timestamp: 2026-08-21T18:25:14.5439157+10:00 (Australia/Brisbane)
Yuri attention required: **no**

## Lay summary

The repaired native DeepSeek Harness setup is now coherent enough to prepare
one new tightly controlled worker attempt. Nothing was launched during this
decision: there was no DeepSeek call, cost, worker, network activity or product
change. The next attempt still has to pass its own fresh checkpoint before its
single allowed run.

The gate also measured its own friction. Three kinds of local procedural rerun
occurred—PowerShell inventory syntax, a self-check that initially matched its
own words, two historical tests tied to the controller before the accepted
repairs, and a clockwork authority-opening draft in the wrong shape. They are
corrected or explicitly bounded, and none wasted a Harness or provider attempt;
the clockwork draft was rejected before publication.

## Technical summary

Decision:
`ready_for_one_separately_checkpointed_occupied_attempt_005` at candidate
`48d7d457bc5768f3f4b4f52fced7c7fd6452a8cc`.

- 7 legacy consumed artifacts and 15 attempt-004/startup artifacts bound;
- 16 current component digests and 22 absent future output paths verified;
- exact initial sentinel-only and changed sentinel-plus-runner profiles pass;
- focused 9/9 and applicable widened 75/75 tests pass;
- zero Node/Harness/broker/worker/model/provider/network activity;
- readiness clockwork reading is explicitly non-reusable;
- AER-0810 through AER-0813 contained; 813 total, none open.

Still closed: occupied execution until its new checkpoint; retries, resumes,
fallbacks and second workers; ordinary-practice/product/data/runtime/
deployment/Pages/protected-ref changes.

Next: create the fresh attempt-005 latch and checkpoint, then—only if every
preexecution gate passes—consume its sole one-process/one-request worker lease.
This advances the harness from repaired startup evidence toward the first
traceable bounded DeepSeek development attempt without weakening EMR4's
product or evidence boundaries.
