# Ariadne agent error and correction register — revision 658

Date: 2026-08-24

Timestamp: 2026-08-24T07:17:32.9431546+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 658
incident_count: 1147
new_incident_ids: AER-1146,AER-1147
open_incident_count: 0
-->

## AER-1146

Two draft closeout bindings used manually expanded 40-character strings based
on abbreviated planning and empirical commit IDs. A prepublication
`git rev-parse` comparison rejected both before staging or publication. Every
occurrence was replaced with the machine-resolved full object ID.

The prevention control is mechanical: a closeout may not accept a caller-
constructed expansion of an abbreviated Git ID. Every Git-bearing field is
compared with repository resolution before clockwork admission.

## AER-1147

Post-run cleanup removed the private manifest, projection and owned Word
process but left the strict count-only progress sidecar. It contained no source
value and the first-use gate remained closed, but retention contradicted the
frozen cleanup boundary.

The exact ignored sidecar was removed without reopening historical content.
The cleanup routine now includes both Word process-control and count-only
progress paths, and all 190 provider-free historical-Diary controls pass.
