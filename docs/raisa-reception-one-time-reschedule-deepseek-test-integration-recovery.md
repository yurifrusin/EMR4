# Reception One time-reschedule DeepSeek test integration recovery

Date: 2026-08-14

Timestamp: 2026-08-14T08:59:31+10:00 (Australia/Brisbane)

Status: `recovered_candidate_pass`

Worker commit: `180fd34ef19981650c32b9cbbe6cfc2342503c8d`

Integration parent: `34bfcd7187fac3fe12a752525402f3b696fddeb5`

## Preserved worker result

DeepSeek V4 Flash/high returned exactly one new file,
`review/test_reception_one_time_reschedule_action.py`, from its isolated clean
worktree. It performed only syntax and whitespace checks, explicitly labelled
the browser behavior expected-red until Sol's parallel product implementation
landed, and made no acceptance claim.

The first integrated full-file run reached the outer 180-second bound because
the artifact's pre-implementation selector vocabulary did not match the final
product's `meta-grid-reschedule-*` vocabulary. The bounded run emitted no
passing claim. Sol treated the file as an untrusted candidate under the
orchestrator recovery lease.

## Exact Sol amendments

1. Rebound the four provisional test ids to the final selected-reschedule
   panel, time input, submit button and feedback region.
2. Corrected the HTML time-input step assertion from minutes (`15`) to the
   standard seconds value (`900`).
3. Changed the no-op case to prove the submit button is disabled instead of
   attempting to click a disabled control.
4. Added deterministic waits for post-dialog focus return and for the
   committed Reception One coordinate, avoiding observation of the intentional
   intermediate `committed` phase before fresh reconciliation finishes.
5. Compared interruption truth against the rendered appointment coordinate,
   leaving the input value correctly classified as provisional staff intent.
6. Bound the duration guard to the exact bridge call whose third argument is
   literal zero.
7. Repaired one product reconciliation race exposed by the independent
   matrix: after a committed scoped refresh, Reception One now applies the
   bridge's exact fresh appointment read so its selected card cannot briefly
   retain the prior coordinate.

## Result

All nine recovered tests pass, including twelve route-intercepted browser
traces over the six paired conventional-grid/Reception One outcomes, invalid
and no-op denial, interruption, dialog keyboard/focus/Escape, three responsive
viewports and the no-second-write-path source guard.

This recovery proves only authored-synthetic `route_intercepted_browser` and
`authored_synthetic_client_fixture` behavior. It opens no backend, database,
provider, product-data, deployment or protected-ref authority.
