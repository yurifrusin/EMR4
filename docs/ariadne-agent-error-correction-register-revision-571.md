# Ariadne agent error and correction register — revision 571

Date: 2026-08-20

<!-- ariadne-agent-error-register-reading
revision: 571
incident_count: 680
new_incident_ids: AER-0676,AER-0677,AER-0678,AER-0679,AER-0680
open_incident_count: 0
-->

This revision records five contained or corrected workflow incidents from
check-in relay-free recovery attempt 005. The prospective canonical machine
register contains 680 incidents and none is open.

## AER-0676 — hand-entered full Git object was wrong

The first native-worker controller draft contained a 40-character-looking Git
identifier that did not equal the current machine-resolved HEAD. Controller
prepare rejected it before a worker, provider or model request.

Correction: the controller was rebound to the exact `git rev-parse HEAD`
reading. Future builders must receive Git objects directly from the resolver;
the orchestrator must not transcribe even a full-length identifier.

## AER-0677 — sparse worker packet omitted an admitted dependency

The first worker packet omitted one base focused test named by its command
manifest. Controller prepare rejected the incomplete packet before dispatch.

Correction: the exact dependency was added and the packet closure passed.
Future sparse packets must be generated from the admitted manifest's resolved
file closure rather than maintained as a parallel hand-authored list.

## AER-0678 — native Harness preset mount failed before provider dispatch

The sole rc.7 worker process reached broker and HMR readiness, then failed at
`EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`. Provider requests, model
steps, tool calls and edits remained zero; cleanup passed and the attempt is
consumed without retry. The sanitized coordinate collapses all preset-mount
subcauses, so the retained evidence cannot identify the exact mount stage.

Containment: preserve the terminal and continue the frozen adapter/test package
under Sol. Before another occupied worker, run the identical full-profile
`agents.create` mount path provider-disabled, split safe mount coordinates and
derive changed paths from before/after hashes.

## AER-0679 — historical source-pin test entered a descendant manifest

An expanded candidate manifest included the server-repair plan-freeze test,
which intentionally binds the pre-repair harness bytes and therefore rejects
the accepted repaired descendant. The first deterministic runner failed before
candidate commit; no source or authority changed.

Correction: preserve the rejected receipt and exclude that immutable-history
test from descendant acceptance. Future compatibility selection must come from
machine-readable descendant metadata rather than filename proximity.

## AER-0680 — checkpoint prose exceeded its schema bound

The first database-checkpoint check rejected `completed_stage` because the
hand-authored text exceeded the 500-character schema limit. No command,
generation or canonical write occurred.

Correction: the same facts were rendered in 458 characters and the separate
check, publication and idempotent readback passed. Future transition prose must
be produced through a schema-backed bounded-text builder that reports length
before the clockwork command is invoked.

All five incidents have contained or accepted correction states. They do not
reclassify the failed database attempt, authorise a worker or database retry,
or change any product, data, production, deployment, Pages or protected-ref
boundary.
