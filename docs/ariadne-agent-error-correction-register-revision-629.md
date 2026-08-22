# Ariadne agent error and correction register — revision 629

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 629
incident_count: 1005
new_incident_ids: AER-1004,AER-1005
open_incident_count: 0
-->

## AER-1004 — Diagnosis validation mixed preterminal and postterminal lifecycles

Status: `closed_corrected`

The first broad diagnosis validation selection included two attempt-006 tests
whose contract requires an empty preexecution terminal namespace and one
earlier repair-plan test whose exact historical harness hash is intentionally
superseded. All three failed before closeout publication because the current
repository correctly contains the consumed attempt-006 terminal and its
accepted descendant harness.

The selection was replaced by a current-lifecycle manifest. Fifty-eight
diagnosis, postterminal, repaired-lifecycle and created-state lineage tests
then passed. No Docker object, database run, provider request or canonical
publication was repeated. The prospective control is to generate validation
manifests from terminal-state and artifact-lifecycle tags rather than filename
adjacency.

## AER-1005 — Diagnosis postterminal assertions overtreated safe literals

Status: `closed_corrected`

Two first-draft postterminal assertions treated the safe typed
`<container_id>` source placeholder as if it were a retained dynamic object
identity and compared one Markdown sentence with incidental case sensitivity.
Focused pytest rejected both assertions before candidate publication.

The tests now reject prohibited raw field names while admitting the schema's
closed placeholder and normalize document text before semantic comparison.
The resulting current-lifecycle suite passes. The durable control is to prefer
schema-structural evidence assertions and normalized document predicates over
unscoped substring tests.
