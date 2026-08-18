# Ariadne agent error and correction register — revision 376

Date: 2026-08-18

Timestamp: 2026-08-18T13:17:00+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 376 adds AER-0428. Sol used the descriptive but non-admitted lane
disposition `contained_transport_non_result` in the first candidate-precommit
runtime state. The local preflight returned
`parallelism_lane_disposition_invalid:deepseek_flash` before commit, dispatch
or provider action.

The state now uses admitted disposition `completed`, retains a bounded work
package describing preservation/closure of the transport non-result and emits
a distinct corrected receipt with status `passed`. The failed receipt remains
immutable evidence; the product candidate did not change.

## Population

- incidents: 428;
- corrected or explicitly contained: 428;
- open: 0;
- latest id: `AER-0428`.

No source admission, provider call, product data, deployment or protected-ref
movement occurred under the rejected receipt.
