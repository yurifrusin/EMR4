# Ariadne agent error and correction register — revision 583

Date: 2026-08-21

Timestamp: 2026-08-21T11:28:18.5222638+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 583
incident_count: 755
new_incident_ids: AER-0753,AER-0754,AER-0755
open_incident_count: 0
-->

## AER-0753 — local Git subprocess boundary was imprecise in the frozen plan

The first frozen acceptance row used the generic phrase “process counts remain
zero” even though its design explicitly admits bounded local Git object-reading
subprocesses in the separate repair checker. The same plan also preserved the
ordinary-practice boundary semantically without repeating its exact closed
token in prose. Before candidate acceptance, the row was corrected to separate
the nine admitted Git reads from zero Harness/broker/worker/model/provider
activity, and the exact token was restored. A focused plan test now binds both
requirements.

The initial focused test correctly rejected the missing token, after which the
unchanged candidate passed. No Harness, worker, model or provider process was
started; no historical evidence, product surface, data or protected ref moved.

## AER-0754 — closeout manifest supplied two node relationships

The first read-only clockwork check supplied both the controlling `builds_on`
parent and a descriptive repair relation. The transactional manifest contract
admits exactly one node relationship, so clockwork rejected with
`node_relationship_invalid` before transaction preparation, command execution
or publication. The intent now retains only the controller-convergence parent;
the relationship to the older recovery remains explicit in prose and evidence.
Future closeout construction checks relationship cardinality before its first
clockwork reading.

## AER-0755 — incident stage used an unadmitted planning value

After the relationship correction, the second read-only clockwork check reached
the incident validator and rejected the first observation's `planning` stage.
The closed vocabulary instead admits `deterministic_verification` for the
focused plan-test detection. The observation now uses that exact value, and the
complete intent is validated directly against the live clockwork contract
before another CLI reading. Rejection occurred before transaction preparation,
commands or publication.

All three incidents are corrected or contained and none remains open.
