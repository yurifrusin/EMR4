# Ariadne agent-error and correction register — revision 565

Date: 2026-08-19
Timestamp: 2026-08-19T11:53:31.2243631+10:00 (Australia/Brisbane)

## Revision scope

Revision 565 preserves AER-0655, a recurrence of the bounded-checkpoint failures AER-0460 and AER-0512. The first terminal closeout summary was 525 characters, exceeding the active-operation schema's 500-character maximum and causing every latch-dependent surrounding test to reject before reaching its own invariant.

The correction reduces the terminal summary below the schema bound, restores the exact Current Baton protected-ref movement phrase and admits the AER-0651/AER-0654 yielded-session recurrence in the generated pattern fixture. The register contains 655 incidents, all corrected or contained and none open.

Final end-to-end rehearsal and closeout cost is twenty-four reruns. The exact corrected Gemini input remains sixteen; all eight post-review closeout reruns are reported separately, including correction of AER-0655's recurrence resource to the pattern reducer's exact composite key. Projected clockwork-owned representative steady-state corrective reruns remain zero.

## Prevention

Generate and validate the terminal latch projection before running surrounding suites. No hand-authored checkpoint summary is admitted without its exact schema-length reading.
