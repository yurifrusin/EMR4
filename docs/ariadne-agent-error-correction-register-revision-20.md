# Ariadne agent-error register revision 20

Date: 2026-08-05

Status: AER-0026 contained and escalated to Sol recovery; no incident remains
open

## AER-0026 C4 bounded repair self-pass with residual authority races

The distinct DeepSeek V4 Flash/high C4 repair stayed within its six owned paths,
preserved the original failed commit and returned `DECISION: pass` after its
focused and inherited checks passed. It corrected the seven explicitly named
first-review findings, but that did not establish the shared transactional
semantics implied by the frozen plan.

Independent Sol/native audit reproduced three material residual failures. Any
non-empty reviewer role remained accepted after role revocation. The current-
authority store could be changed between its one snapshot and the simulated
effect without invalidating success. Two runtime instances sharing the same
evidence, state and audit stores could each admit the same one-use evidence
because their locks, idempotency state and attempt sequences were instance-
local.

The exact repair receipt and commit remain preserved as untrusted. The one
bounded same-lane Flash correction permitted by the active complexity rule is
exhausted. Sol now owns the narrow recovery lease: shared execution-store
coordination, authority-store locking for the full execution transaction and
an exact closed reviewer role, with adversarial regressions for each failure.

Acceptance still requires reproducible deterministic evidence, the focused and
inherited C4/API Spine suite, static checks and a fresh clean exact-head Gemini
3.6 Flash/high implementation veto. AER-0026 is an observed implementer
reasoning-claim error; it is not proof of a provider or transport cause.

Revision 20 contains 26 bounded incidents. AER-0025 and AER-0026 are contained
and escalated through the recorded correction path; no incident is open.
