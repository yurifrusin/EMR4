# Check-in prospective-redaction and typed-cleanup repair

Date: 2026-08-23

Timestamp: 2026-08-23T05:05:13.7520724+10:00 (Australia/Brisbane)

Yuri attention required: `no`

## Lay summary

The mechanism is genuinely closer to a ratchet. Before any future database run,
the harness now lays out the complete success record and feeds every field
through the same safety filter that will judge the final record. The previously
bad field name is gone without weakening the filter or opening the boundary.

Cleanup also now has a typed handover. If a final paperwork check fails after
cleanup, the wrapper receives the cleanup reading already taken by the base
harness instead of substituting “not started.” These two exact causes of the
last wasted occupied run can no longer recur in the same way.

The workflow around the repair was less satisfactory. Six test sessions used
the ordinary repository runner, which silently exercises the local synthetic
test database. That breached the no-database instruction. Those results were
discarded and replaced by clean no-conftest runs, but the incident remains
material and recorded. Several smaller command/form mistakes were also caught
and corrected. So the honest conclusion is: substantive engineering progress,
but further tightening of the verification control plane is justified.

## Technical summary

Exact implementation source is
`8a82a8184cc66efbe31769eda88e299887f798bc`. Static admission proves 67 exact
prospective/runtime paths, schema/redaction pass and 66 hostile rejections. The
base-owned frozen terminal type preserves `cleanup_verified` on late redaction
and schema failures; the historical wrapper projects it correctly. Canonical
evidence SHA-256 is
`47f422e7b8ad072c9f4912fe6269cfc85f44eb75808419182c75e19d41157eaa`.

The exact 83-test candidate profile and complete register suite passed through
the provider-free runner. Six ordinary-pytest results were excluded because
autouse conftest touched only the local authored-synthetic test schema. AER-1021
through AER-1027 record all seven process incidents, including the direct
canonical-register draft that was reverted before clockwork publication.

## Deliberately closed

No occupied attempt ran and attempt 008 remains closed. No ordinary-practice,
route/API/client, product-data, provider, production, deployment, release,
Pages or protected-ref authority opens. All unrelated untracked files,
especially `docs/branding/`, remain preserved.

## Next

The engine is continuing into a narrow workflow repair: when database authority
is closed, the command envelope must mechanically reject ordinary/serial pytest,
and tests must be typed as prepublication or postpublication. Once that gear is
accepted, we can decide whether a separately planned attempt 008 is warranted.
No decision from Yuri is needed.
