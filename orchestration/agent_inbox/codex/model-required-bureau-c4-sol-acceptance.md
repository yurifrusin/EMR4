# Sol acceptance: Bureau C4 allowlisted-actuator simulator

Date: 2026-08-05

Decision: `model_required_bureau_c4_allowlisted_actuator_simulator_pass`

Accepted source HEAD: `955b6a566f7097f58929dcb2fa9c4ed0aaad8b29`

## Acceptance basis

- The frozen C4 plan and threat-model delta permit only one local in-memory
  authored-synthetic forward transition and its exact rollback.
- Closed schemas, examples, generated evidence and 31 focused tests cover
  admission, authority, one-use evidence, idempotency, concurrency, audit,
  readback, rollback and zero-capability receipts.
- Sol's recovery lease closes the original seven findings and the repair's
  three residual authority/concurrency findings without widening C4.
- The widened inherited suite, evidence reproduction, Ruff, compilation,
  Bandit, JSON and whitespace checks pass.
- Fresh Gemini 3.6 Flash/high reviewed exact source HEAD
  `955b6a566f7097f58929dcb2fa9c4ed0aaad8b29`, passed 389 tests, found no
  material defect, emitted exactly one pass and left the worktree clean and
  unchanged.

## Decision

Accept C4 only as
`provider_free_authored_synthetic_allowlisted_actuator_simulation`. The fixed
callable map, backend-owned current authority, shared evidence transaction,
monotone attempt record, exact fresh readback and fail-closed rollback are
authoritative. Model text, plan text, reviewer text and the OpenAPI-shaped
artifact carry no execution authority.

AER-0025 and AER-0026 remain immutable rejected-worker evidence and become
corrected only through the completed named recovery lease and independent veto.

No product/runtime provider call, patient or product-derived data, real target,
database, mounted route, external effect, C5 action, production, deployment,
release, Pages, protected evidence or protected ref is accepted.

The next dependency-satisfied action is to freeze C5's narrowest disposable
live-development-recovery plan. Standing programme authority permits planning
without another ceremonial handback; no live action begins until that exact
plan's own deterministic and independent gates pass.
