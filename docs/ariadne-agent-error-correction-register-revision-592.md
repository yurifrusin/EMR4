# Ariadne agent error and correction register — revision 592

<!-- ariadne-agent-error-register-reading
revision: 592
incident_count: 804
new_incident_ids: AER-0802,AER-0803,AER-0804
open_incident_count: 0
-->

This revision note binds three corrected observations to the prospective
clockwork-projected register. The canonical JSON register and pattern report
remain clockwork-owned.

## AER-0802

The first static source-chain predicate required `forceExitOnce(code)` to occur
exactly once even though the pinned shutdown controller deliberately calls the
same helper from several branches. Focused tests stopped before canonical
evidence. The predicate now distinguishes a unique causal coordinate from
non-unique helper presence and requires at least one exact call.

## AER-0803

The first raw-stream safety test prohibited the word `stderr` anywhere in the
serialized evidence, including inside the claim boundary that explicitly says
stderr was not reconstructed. Focused tests stopped before evidence generation.
The test now asserts the structural absence of stream and stderr-digest fields
while permitting precise non-reconstruction prose.

## AER-0804

Two widened verification selections rediscovered four immutable historical
assertions that bind pre-source-repair controller/sentinel digests and verdicts.
Their expected retained failures changed no candidate. The final applicability
set names the four exclusions explicitly; 37 current and applicable predecessor
tests pass. Successors should consume a generated applicability manifest rather
than reconstructing negative selectors from memory.
