# Ariadne agent-error register revision 39

Date: 2026-08-06

Status: two-sided observation-clock recovery pending fresh veto

## AER-0047 open

The first Sol recovery for AER-0046 passed 221 deterministic checks but a
second genuinely fresh independent veto found that the clock-domain correction
covered only one timestamp ordering. Admission intentionally accepts absolute
source-to-backend clock skew up to the frozen bound. Mapping still required the
source timestamp to be no later than the backend observation timestamp, so a
contract-valid nine-second positive skew admitted and then failed mapping.

Sol kept the existing recovery lease active, made mapping apply the same exact
absolute-skew rule as admission while retaining independent observation-expiry
validation, and added a positive-skew admission-to-mapping test. AER-0046 and
AER-0047 remain open until another genuinely fresh exact-head veto passes.

Revision 39 contains 47 bounded incidents: 35 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
Two incidents remain open. Counts remain workflow-improvement signals only and
do not establish model, provider, transport or role causation.
