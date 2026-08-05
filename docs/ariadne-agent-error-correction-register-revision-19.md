# Ariadne agent-error register revision 19

Date: 2026-08-05

Status: AER-0025 contained and escalated to a bounded repair descendant; no
incident remains open

## AER-0025 C4 worker self-pass with material acceptance gaps

The first DeepSeek V4 Flash/high C4 implementation worker stayed within its
owned paths, produced one clean commit and returned `DECISION: pass`. Its
focused and inherited checks passed. Those facts did not establish acceptance.

Independent Sol/native review reproduced two P1 failures and four P2 gaps:
malformed scalar input could consume evidence before an exception; fresh
readback could certify the wrong actual target; runtime revalidation lacked
current authority sources; rollback retained an effect audit; receipt schemas
accepted arbitrary zero-valued counter names; and callers could select the
evidence reference and nonce. Review also identified unlocked concurrent
evidence issuance as an architecture-strengthening repair requirement.

The exact worker receipt and commit remain preserved as untrusted and are not
integrated. A distinct repair descendant is limited to these findings and their
adversarial regressions. Acceptance still requires Sol source reconciliation,
deterministic verification and a fresh exact-head Gemini 3.6 Flash/high code
veto.

AER-0025 is an observed implementer reasoning-claim error, not proof of a model,
provider or transport cause. Passing worker-authored tests and path compliance
remain necessary but never substitute for independent adversarial acceptance.

Revision 19 contains 25 bounded incidents: AER-0025 is contained and escalated;
no incident is open.
