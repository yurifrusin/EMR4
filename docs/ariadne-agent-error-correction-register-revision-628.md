# Ariadne agent error and correction register — revision 628

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 628
incident_count: 1003
new_incident_ids: AER-1003
open_incident_count: 0
-->

## AER-1003 — Attempt 006 server start/attach exited while container remained created

Status: `closed_contained_then_escalated`

The sole occupied attempt-006 Docker start/attach process exited nonzero while
the exact captured server retained safe projected `created` state,
`running=false` and attached stdin remained open after credential delivery.
The closed harness therefore denied readiness and every transaction stage,
released no success or retry, removed all owned resources and preserved the
immutable negative terminal.

This is an observed Harness lifecycle failure, not a causal claim about Docker,
PostgreSQL or the wrapper. Before any repair or attempt 007, the accepted next
control is a provider-free read-only diagnosis of exact start/attach command
construction and CLI grammar with deterministic process fakes and a closed
sanitised host-process/OCI coordinate.
