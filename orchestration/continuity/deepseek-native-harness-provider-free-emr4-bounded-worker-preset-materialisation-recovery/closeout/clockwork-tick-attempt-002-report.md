# Governance clockwork tick — rejected attempt 002

Status: **rejected after postpublication compatibility failure**

Operation:
`deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery`

Source: `76c00987d70de782cc490197e5b76ad981186050`

Generation:
`gen-9369f5151e7e1ad2f6713282c2417c241df8d0f76280dedd543762b5d01c789b`

Lease sequence: 55

The corrected execution-envelope control retained session `38278` and polled
it to an exact terminal result. The postpublication suite returned exit code
one. The sole failure was the register compatibility test that still required
the yielded-session recurrence pattern to contain only `AER-0651` and
`AER-0654`; canonical incident intake correctly added `AER-0666` to that same
recurrence signature.

This is a stale governance-test expectation, not a candidate or clockwork
derivation failure. The generation is preserved here and must be rolled back
byte-exactly before the expectation is updated to include the newly derived
incident and the closeout is republished through incident intake.
