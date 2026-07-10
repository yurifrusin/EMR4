# Ariadne S3 Advisory Classifier

Date: 2026-07-10

S3 classifies observable changed-path artifacts against a policy supplied as
data. It does not read action titles, prompts, chat history, or an
orchestrator's claimed intent. It emits labels only and has no hook into agent
execution, git operations, runtime code, or release control.

The current EMR4 policy classifies `docs/`, `tests/`, `orchestration/`,
`orchestration_harness/`, `scripts/`, and `review/` as Green. It classifies
clinical/runtime paths such as `app/`, `alembic/`, `static/`, `EMR4 Sidebar/`,
and `docs/diary/` as Red and therefore `requires_user_approval`. `local_data/`
is Black and `blocked`. Unknown roots are Amber and `underspecified`.

The initial replay corpus contains 15 exact changed-path inventories from
historical EMR4 commits, including two runtime UI changes and thirteen
documentation/test/closeout changes. The test verifies both path inventory
integrity against local git history and the expected advisory label. This is a
calibration corpus, not a claim that the historical work lacked the approvals it
received at the time.

S3 remains advisory. Its next proof requirement is to classify proposed work
alongside ordinary EMR4 sprints and measure whether its labels match the
human-approved boundary decisions before any choke-point integration is
considered.
