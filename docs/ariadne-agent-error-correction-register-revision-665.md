# Ariadne agent error and correction register — revision 665

Date: 2026-08-24

Timestamp: 2026-08-24T15:21:43.2895486+10:00 (Australia/Brisbane)

Register revision: `665`

Incident count: `1159`

Open incidents: `0`

New incident: `AER-1159`

<!-- ariadne-agent-error-register-reading
revision: 665
incident_count: 1159
new_incident_ids: AER-1159
open_incident_count: 0
-->

## AER-1159

Four small prepublication verification-control lapses were contained. One
privacy test used a substring that also matched an admitted aggregate field;
Ruff then found one unused test import; and a later PowerShell conditional
mistook an output-silent successful `git diff --quiet` for failure instead of
checking its native exit code. The semantic clockwork check then required the
conventional tranche-local `efficacy-reading.json` path in addition to the
already complete typed evidence and report.

The assertion was narrowed to the exact singular row-level JSON keys, the
unused import was removed, the Git gate was repeated with an explicit
`LASTEXITCODE` check, and a compact efficacy projection was added without new
claims. Thirteen exact-HEAD focused tests and the full 337-test combined profile
then passed. No historical fixture, local control, archive, provider, product
runtime or protected ref was touched.

Durable prevention: privacy assertions distinguish aggregate schema keys from
row-level keys exactly; Ruff runs in the focused precommit loop; output-silent
native commands are always followed by an explicit exit-code test; and each
tranche emits the clockwork's conventional efficacy projection before semantic
closeout checking.
