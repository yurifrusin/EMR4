# Ariadne agent error and correction register — Revision 622

Date: 2026-08-22

Timestamp: 2026-08-22T19:05:50.6495370+10:00 (Australia/Brisbane)

Status: `accepted_closed_reading`

<!-- ariadne-agent-error-register-reading
revision: 622
incident_count: 978
new_incident_ids: AER-0977,AER-0978
open_incident_count: 0
-->

This revision records two bounded local orchestration errors from the
provider-free integrated-runner factory-subcoordinate diagnostic recovery.
Neither reached a Harness, worker, model or provider boundary, and neither is
open.

## AER-0977 — continuation receipt used an unregistered leverage value

The first post-compaction receipt used the descriptive value
`neutral_until_candidate` where the closed parallelism vocabulary admits
`neutral`. The preflight rejected it before dispatch. The corrected receipt
selects the exact registered value, and future receipts must select rather than
reconstruct this field.

## AER-0978 — fixture projected the package scope one level too high

The single authorised Node fixture selected `node_modules` instead of the
scoped `node_modules/@deepseek-ai` package root, so both emitted imports were
absent and the process stopped before `AgentRegistry.create`. The attempt is
consumed without retry. The distinct successor must prove both exact import
targets exist before its one process is admitted.

The corrections add no native Harness retry, worker/model/provider request,
product or data action, ordinary-practice enablement, production runtime,
deployment, release, Pages or protected-ref authority.
