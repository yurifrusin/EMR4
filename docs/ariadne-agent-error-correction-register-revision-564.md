# Ariadne agent-error and correction register — revision 564

Date: 2026-08-19
Timestamp: 2026-08-19T11:53:31.2243631+10:00 (Australia/Brisbane)

## Revision scope

Revision 564 preserves AER-0654, a recurrence of AER-0651. The corrected focused suite yielded after partial dots, but the orchestration wrapper again failed to expose the returned session identifier. The exact pytest processes later exited, but their final result could not be recovered and is not acceptance evidence.

The correction executes the focused file alone and makes the wrapper emit `session_id` and poll it to a final exit code if it yields. The register contains 654 incidents, all corrected or contained and none open.

Final end-to-end rehearsal and closeout cost is twenty-two reruns. The exact corrected Gemini input remains sixteen; all six post-review closeout reruns are reported separately. Projected clockwork-owned representative steady-state corrective reruns remain zero.

## Prevention

Every potentially yielding command wrapper emits output, session identifier and exit code. Any returned session is polled to a final exit before its result can support acceptance.
