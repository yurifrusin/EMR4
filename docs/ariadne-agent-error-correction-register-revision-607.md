# Ariadne agent error and correction register — revision 607

Date: 2026-08-22

Status: **three corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 607
incident_count: 897
new_incident_ids: AER-0895,AER-0896,AER-0897
open_incident_count: 0
-->

## AER-0895

The first runner-bridge preplanning state used the shorthand continuation event
`pre_plan`, which is outside the orchestrator profile's registered vocabulary.
Preflight rejected it before implementation. The rejected receipt was preserved
and the fresh state used `pre_sprint_planning`.

## AER-0896

While reading the accepted source-coordinate evidence, the orchestrator again
derived a physical directory from a logical operation name. The read-only path
failed; repository inventory resolved the actual accepted artifact before any
implementation or fixture process. This is a recurrence of the path-resolution
family recorded in AER-0892.

## AER-0897

The first post-execution selected suite found that one focused test asserted
only the preexecution `fresh` artifact state. The deterministic checker had
correctly advanced to `accepted`. The test was made phase-aware and now asserts
the exact additional accepted fields; the 90-test collection passed without a
second Node process.

## Control reading

Closed vocabulary, repository-owned path resolution and state-machine-aware
tests are three distinct typed-input problems. Each was caught before it could
broaden authority or consume a prohibited retry. The recurrence in AER-0896
remains visible for efficacy measurement rather than being merged away.
