# Ariadne agent error and correction register — revision 587

Date: 2026-08-21
Timestamp: 2026-08-21T13:48:50.6623983+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 587
incident_count: 776
new_incident_ids: AER-0773,AER-0774,AER-0775,AER-0776
open_incident_count: 0
-->

## AER-0773 — repair runner omitted direct-script import bootstrap

The first direct CLI invocation could not import the repository `scripts`
package because the new runner did not place the repository root on
`sys.path`. It exited before evidence, Node, Harness or provider activity. The
standard repository-root bootstrap was added and direct execution passes.

## AER-0774 — dead-local guard searched beyond its owned function

The corrected runner initially rejected a legitimate `proof` local in the
separate attempt-preparation function. The invariant concerns only
`profile_patch`, so the guard now slices that exact function body before
checking the removed local. The repaired evidence then passes.

## AER-0775 — no-database wrapper received an unsupported pytest option

The first widened command supplied `--deselect` to
`scripts.ariadne_provider_free_pytest`, whose closed CLI accepts test paths
only. Argument parsing rejected the invocation before collection. The corrected
serial command uses direct pytest and names each deselection explicitly.

## AER-0776 — widened run selected frozen source-binding equality checks

The first direct widened run selected two controller-convergence tests that
bind its accepted pre-repair component hash. Both correctly returned
`accepted_component_drift`. Their frozen artifacts were not regenerated or
weakened. The successor selection note deselects those two current-artifact
checks, retains every behavioral peer, and the corrected 56-test run passes.

All four incidents are corrected or contained and none remains open.
