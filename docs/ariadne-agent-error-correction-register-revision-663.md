# Ariadne agent error and correction register — revision 663

Date: 2026-08-24

Timestamp: 2026-08-24T12:55:43.0106995+10:00 (Australia/Brisbane)

Register revision: `663`

Incident count: `1156`

Open incidents: `0`

New incidents: `AER-1156`

<!-- ariadne-agent-error-register-reading
revision: 663
incident_count: 1156
new_incident_ids: AER-1156
open_incident_count: 0
-->

## AER-1156

An uncommitted closeout-evidence draft supplied a composed 40-character value
for the planning commit instead of Git's actual resolved object ID. The
mandatory full-object readback compared the draft with `git rev-parse`, caught
the mismatch before staging or publication, and replaced it with exact source
`6c5a49e1a80e2c651380b79a4f5b59d0bd93ee8c`.

The reviewed implementation source and every protected ref were already
correct. No fixture, archive, provider, product or runtime was touched, and no
implementation or occupied run was repeated.

Durable prevention: every authored Git binding in closeout evidence must be
resolved and compared by Git before explicit-path staging; a plausible-looking
40-character value is never accepted as its own proof.
