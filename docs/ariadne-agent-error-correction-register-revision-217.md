# Ariadne agent error and correction register — revision 217

Date: 2026-08-11

Revision 217 closes the pending correction evidence for AER-0251 and retains
the register at 252 bounded incidents.

## AER-0251 — accepted fixed-call and packet-closure correction

The first AES-C2 worker candidate remains rejected and immutable evidence. Its
reported malformed-result invocation had bypassed the actual fixed pure
function, a schema-valid supplied result could be released after zero real pure
calls, and an undeclared scenario-packet field was accepted.

The one plan-permitted same-lane revision made the fixed pure call
unconditional, restricted result substitution to the exact malformed-result
scenario, required canonical scenario-packet equality, and added actual-call
and packet-closure regressions. Sol independently reproduced three actual pure
calls across the 26 scenarios, with the malformed result releasing nothing. A
fresh exact-head Gemini 3.6 Flash/high veto then passed before AES-C2
acceptance.

The correction status therefore advances from
`control_implemented_pending_acceptance` to `corrected_fresh_attempt`. No
incident is removed or reattributed, the incident count and recurrence data are
unchanged, and no protected or external capability was opened.
