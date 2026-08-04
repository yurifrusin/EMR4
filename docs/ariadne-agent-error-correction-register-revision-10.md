# Ariadne agent-error register revision 10

Date: 2026-08-04

Status: Review 7 duplicate terminal decision contained; fresh exact-HEAD
independent veto pending

## AER-0018: Review 7 emitted two terminal decisions

The fresh Gemini 3.6 Flash/high Antigravity review ran against clean exact
candidate HEAD `e22c7991495e8c1301c803d919ad6711d1b3afc7`. Its transport returned
successfully and the read-only worktree remained clean and unchanged, but the
raw verifier response contained two terminal decision markers. The wrapper's
existing exact-cardinality control rejected the whole response and wrote no
worker receipt. No candidate finding or decision was admitted.

This is the third bounded incident with the full
`verifier.multiple_terminal_decisions` classification composite. The recurrence
is an operational control signal only; it does not establish model or provider
causation or say anything about candidate quality. The failure receipt retains
only sanitized cardinality, exact candidate/worktree state and the zero
candidate-runtime-call boundary. Raw verifier output is not retained.

The incident is contained because the fail-closed wrapper prevented acceptance
and the candidate remained unchanged. The bounded recovery is a fresh
Antigravity project and fresh exact clean non-protected worktree with a shorter
non-echo terminal contract. AER-0017 remains separately open until an
admissible fresh independent veto reviews the terminal reconciliation.
