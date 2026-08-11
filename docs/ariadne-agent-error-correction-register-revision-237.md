# Ariadne agent error and correction register — revision 237

Date: 2026-08-11

Revision 237 adds AER-0271. The register now contains 271 bounded known
incidents.

## AER-0271 — CF-D1 failure telemetry was not actionable

Attempt 002 failed closed on `result_marker` before completing `CFD1-C01` and
cleaned up its exact disposable container. The minimized evidence did not name
the failing leader/replay coordinate or closed expected/observed marker list,
and its static twelve-participant count was not actual-attempt accounting.

The bounded correction adds only closed diagnostic coordinates and actual
started-transaction counters, keeps historical failure evidence valid, consumes
attempt 002 and reserves attempt 003. It requires a fresh exact-HEAD veto before
another disposable run.
