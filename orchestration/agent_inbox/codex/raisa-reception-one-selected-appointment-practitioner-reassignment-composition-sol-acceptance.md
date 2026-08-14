# Sol acceptance — Reception One practitioner reassignment

Date: 2026-08-14

Timestamp: 2026-08-14T13:38:04+10:00 (Australia/Brisbane)

Decision: accept

Accepted source: `f085fc98ead21a3e7929ee9adbda81abfc7542c9`

Result: `raisa_reception_one_selected_appointment_practitioner_reassignment_composition_pass`

## Acceptance reasoning

The exact candidate satisfies the practitioner-only boundary. Reception One
admits one distinct current active-directory target, re-reads the exact
appointment and directory, binds the admitted identity, fixes time and
duration deltas at zero and delegates once to existing `handleMoveResize`.

The existing update proposal/confirm family remains the only command path. A
changed target must be active in current same-practice database truth, and
confirmation re-runs that test before writing. Visible staff confirmation,
opaque signed evidence, idempotency, audit and atomic commit remain owned by
the ordinary Diary path. No new route or schema is introduced.

The twelve paired traces prove the exact proposal/confirm matrix: safe `[1,1]`,
cancelled `[1,0]`, blocked `[1,0]`, stale `[1,1]`, failed `[1,0]` and committed
`[1,1]`. All eight normalized truth fields agree between renderers; raw and
unexpected mutation counts are zero. Directory failure, target disappearance,
invalid/duplicate targets and interruption remain fail closed.

DeepSeek's test lane was useful but uneconomical, the native seam review drove
two material client repairs, and Gemini returned `pass` with 80/80 tests at an
unchanged clean candidate. Gemini's narrative misstated two route counts; the
passing source-bound test matrix above is controlling evidence.

## Authority finding

No patient/product data, product or Vertex call, live database/source read,
real database write, new command route, deployment, release, Pages or
protected-ref movement occurred. `docs/branding/` and all unrelated untracked
files remain outside the candidate.

The next safe descendant is a read-only selected-action-console consolidation
orientation before another appointment field is added. Standing authority
applies and no user-attention fork is present.
