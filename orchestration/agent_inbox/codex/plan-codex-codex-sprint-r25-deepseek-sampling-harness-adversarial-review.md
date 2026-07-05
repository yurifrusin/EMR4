# plan-codex-codex-sprint-r25-deepseek-sampling-harness-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-r25-deepseek-sampling-harness-adversarial-review` |
| Status | integrated |
| Created | 2026-07-05 23:49 +1000 |
| Source HEAD | `1d6183d` |

## Plan Summary

Independent adversarial review of default-disabled no-write provider sampling harness

## My Understanding

R24 provides a deterministic fake-provider-only manifest eval gate with frame shape validation, write-authority/PHI/bypass detectors, and receptionist scenario gates. R25 proposes a default-disabled no-write sampling harness that can feed configured provider-style sample outputs through the R24 gate without making live calls in tests. This is a safety-critical addition: the harness must be structurally incapable of accidental live calls, PHI logging, write authority, provider metadata spoofing, or sample-evaluation bypass.

## Intended Surface / Boundary

app/services/ai/evals/ (new sampling harness module), focused tests in tests/, the R24 manifest_eval.py consumption path. No changes to: Diary UI, taskpane, Word integration, route/builders, DB/schema, live Gemini provider, secrets/credentials.

## Out Of Scope

Actual live Gemini/Vertex calls, production prompt wiring, Diary UI/taskpane changes, appointment mutations, secrets/service-accounts, route changes, database migrations, frontend assets.

## Files I Expect To Edit

app/services/ai/evals/provider_sampler.py (new, if accepted), tests/test_provider_sampler_adversarial.py (new review artifact, if accepted), orchestration/docs/ if needed for review artifact

## Implementation Steps

1. Understand R24 manifest_eval gate structure and the R24 receptionist scenario fixture/seam. 2. Review the proposed harness scaffold for five bypass classes: accidental live calls, write authority, PHI logging, metadata spoofing, sample-evaluation bypass. 3. Produce adversarial review artifact or non-overlapping focused tests. 4. Verify py_compile and run focused tests if tests are added.

## Visual / Behavioural Acceptance Checks

Ariadne receives an independent adversarial review of the no-write sampling scaffold without overlapping the scaffold implementation unnecessarily. At minimum: a structured document covering all five bypass classes with concrete test scenarios or code assertions demonstrating each risk.

## Risks / Ambiguities

1. Harness default-disabled toggle could be misconfigured upstream and enable live calls if wiring assumes enabled-by-default. 2. Scripted provider metadata (model name, provider ID, version) could be confused with real Gemini output in downstream consumers. 3. Provider sample fixtures with writes_authorized=True could be accidentally promoted into runtime eval if the fixture/response seam is not clearly typed. 4. Sample-evaluation bypass: if the harness configures samples that skip R24 frame-shape validation. 5. PHI-indicative keys in sample fixtures could be logged through the eval path and persist in test artifacts. 6. The scaffold implementation worker and this adversarial review worker may independently reach the same module, creating conflicts or duplicate coverage.

## Codex Plan Review

- Review result: Accepted and integrated after Ariadne cleanup.
- Required changes before implementation: use the actual `provider_sampling_harness.py` filename, remove stale/NUL artifact text, and convert the `allow_write=True` risk into a deterministic failing test plus manifest gate hardening.
- Approved to proceed: yes; completed and integrated in Sprint R25.
