# Ariadne agent error and correction register — revision 582

Date: 2026-08-21

Timestamp: 2026-08-21T10:54:16.4878045+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 582
incident_count: 752
new_incident_ids: AER-0750,AER-0751,AER-0752
open_incident_count: 0
-->

## AER-0750 — direct controller edit crossed a historical source binding

The first local implementation placed the structured gear directly into the
consumed bounded-worker controller. Focused predecessor tests showed that the
controller is itself a byte-bound input to historical recovery evidence. The
uncommitted edit was removed exactly; the historical controller returned to its
tracked bytes, and the integration was implemented as a descendant adapter
whose fixtures preserve all consumed evidence. No occupied process or provider
request occurred.

## AER-0751 — pre-verifier receipt generated before candidate push

The first pre-verifier preflight ran after the candidate commit but before its
task-branch push, so the machine snapshot correctly reported the local branch
ahead of origin. The receipt was not used for acceptance. The candidate was
pushed, the same runtime state was rerun, and the canonical receipt passes with
local/origin alignment, protected-ref alignment and zero manual Git objects.

## AER-0752 — incident tranche exceeded the clockwork bound

The first read-only closeout check supplied the full long operation identifier
as each incident's tranche label, exceeding the clockwork's 120-character
bounded vocabulary. The clockwork rejected before transaction preparation,
command execution or publication. Both observations now use the concise unique
tranche label `structured-diagnostic-bounded-worker-controller-convergence-rehearsal`.

All three incidents are corrected or contained. None remains open. The accepted
historical controller, all three consumed attempts, product/data surfaces and
protected refs were unchanged.
