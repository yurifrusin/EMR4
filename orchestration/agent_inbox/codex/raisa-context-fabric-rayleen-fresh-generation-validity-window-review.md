# Independent veto — fresh-generation validity window

Date: 2026-08-06

Reviewed candidate: `3b4c34d54b737a339209a7b5b971a0dff8e3cbfe`

Decision: `revision_required`

The fresh native GPT Sol xhigh read-only veto found one decisive high-severity
candidate defect. The final proofreader and initial release gate checked only
the new frame-set and lease expiries. At `2026-08-06T03:01:31Z`, they released
although the predecessor reassembly requirement and instruction both expired
at `03:01:30Z`; the new frame/lease remained live until `03:02:00Z`. This
violated the frozen current-instruction, validity-window and expiry-blocking
conditions.

The machine suites were intentionally not run after the decisive semantic
failure. Before and after review, the isolated worktree was clean on
`codex/review-rayleen-fresh-generation-3b4c34d5` at the exact reviewed HEAD.
The reviewer changed no file, evidence, ref, commit or staging state.

This is an ordinary candidate defect, not an agent-error-register incident.
The repair must bind a sealed predecessor-validity trace into admission and
make both the initial and public proofreaders reject at either predecessor
expiry before a fresh independent veto.
