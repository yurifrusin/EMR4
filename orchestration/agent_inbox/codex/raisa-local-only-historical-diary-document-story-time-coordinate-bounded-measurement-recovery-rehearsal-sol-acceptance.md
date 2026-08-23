# Sol acceptance — historical Diary bounded story-coordinate measurement recovery

Date: 2026-08-24

Timestamp: 2026-08-24T07:14:21.5476552+10:00 (Australia/Brisbane)

Exact reviewed source: `5df44bd28ae60db773b6fd833d0d8cdecca45611`

Empirical source: `54eb390e0b0007c13cfb28615e4c9041db41696a`

Decision: `accept_revision_required`

I accept the sole empirical run as a correctly bounded and useful negative
result. It completed all 80 documents with exact process cleanup, zero leakage,
zero provider calls and no retry. It falsifies the complete-main-story-time-
anchor hypothesis for this slice: zero anchors means no coordinate mapping or
interval claim is admissible.

I also accept the contained cleanup repair. The residual progress sidecar was
strictly count-only, but its retention contradicted the frozen plan. It was
removed from the exact attempt root, the normal cleanup now removes control and
progress state, and all 190 provider-free controls pass. No historical content
was reopened.

The nonzero internal uniqueness/linkage diagnostics are not accepted as a
probability that a real identity can be reconstructed. They preserve the need
for candidate-specific first-use review. Here no reusable candidate exists;
the first-use gate remains closed.

DeepSeek was declined with negative leverage because private content could not
leave the serial Word run and the native harness remains paused. Gemini was not
applicable with neutral leverage because provider transmission was forbidden.
Native subagents were declined with negative leverage because the bind,
process, progress and terminal state were indivisible. GPT Sol owned the run,
cleanup, acceptance, Git and closeout.

The dependency-satisfied successor is provider-free and authored-synthetic
only. It may prove a strict leading explicit time token at the start of one
table-cell segment, but it may not access historical data or authorize a new
measurement.
