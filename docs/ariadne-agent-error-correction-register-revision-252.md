# Ariadne agent error and correction register — revision 252

Date: 2026-08-12

Revision 252 records and contains AER-0284. The register now contains 284
bounded known incidents with none open.

CF-D2 recovery diagnostic attempt 001 isolated the failing participant to
`cfd2_r01_append_anchor_2`. Repository reconciliation then found a real
numeric inconsistency: the harness supplied lifecycle revision two while the
checkpoint was at revision one. Sol corrected that inconsistency but promoted
it too far, describing it as the sole cause even though the minimized terminal
envelope did not distinguish the anchor entry point's later internal
assertions.

The correction passed deterministic gates and a genuinely fresh exact-HEAD
review. Immutable diagnostic attempt 002 nevertheless failed at the same
coordinate. This proves that the correction was insufficient and falsifies
the sole-cause claim. It does not prove which later anchor invariant failed.
There were zero `SIGKILL`, restart, retry, provider, product or external-
network operations, and exact cleanup passed.

The recovery plan is now exhausted. Attempt 003 and every further CF-D2
runtime are ineligible; CF-D2 remains unproved. The preventive control is to
require a discriminator table before spending a correction: a coordinate is
not an assertion, and a source-visible inconsistency is not an exclusive cause
when multiple viable internal assertions collapse into the same evidence
envelope. Yuri's authorised independent workflow-incident diagnosis follows
the stopped closeout.
