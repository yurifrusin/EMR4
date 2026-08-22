# Ariadne agent error and correction register — Revision 623

Date: 2026-08-22

Timestamp: 2026-08-22T19:27:57.8855998+10:00 (Australia/Brisbane)

Status: `accepted_closed_reading`

<!-- ariadne-agent-error-register-reading
revision: 623
incident_count: 979
new_incident_ids: AER-0979
open_incident_count: 0
-->

This revision records one bounded pre-process test-design lapse from the
provider-free factory import-path recovery. It was corrected before the only
Node attempt and is not open.

## AER-0979 — focused tests coupled to incidental forms and shared subprocess state

The first focused implementation collection contained literal URI and prose
assumptions, an over-broad shared-subprocess monkeypatch and one unused import.
Four tests and Ruff rejected before process admission. The corrected tests bind
to source-owned URIs, inspect the exact Node call site without monkeypatching
Git's subprocess use, and assert semantic boundaries rather than report prose.

No process identity, Harness, worker, model, provider, product, data,
deployment, Pages or protected-ref boundary was consumed by the rejected
collection.
