# Ariadne agent-error register revision 13

Date: 2026-08-04

Status: AER-0020 contained; corrected fresh verifier attempt required

## AER-0020: terminal decision repeated after a background notification

The first independent review of the A3/B3 request-contract recovery ran in a
fresh clean worktree at exact HEAD
`ec1eb702b778a0ebf6c969d8967bb52708f2be79`. Gemini completed the requested
acceptance, 210 tests, Ruff and Git checks and reported no finding. It emitted
one detailed terminal `pass`, then emitted a second `pass` in a follow-up after
the background pytest completion notification. The Antigravity wrapper counted
two exact terminal markers, rejected the entire envelope and wrote no worker
receipt. The candidate and worktree remained unchanged and clean.

This is the fourth preserved occurrence of
`verifier.multiple_terminal_decisions`. It is an output-contract observation,
not evidence about model/provider quality. No candidate verdict is admitted.

## Narrow control

The corrected packet must require the verifier to consume every pending
background-command notification before finalizing, emit no terminal marker in
an intermediate/progress response, send one final response only after all
commands are complete, and send no follow-up after its single terminal marker.
The exact-single-decision wrapper remains unchanged and fail closed. Recovery
uses a fresh Antigravity project and a fresh exact clean non-protected review
worktree at the new candidate HEAD.

Revision 13 contains 20 bounded incidents and no open incident. AER-0020
remains contained until one corrected fresh review produces an admissible
single-decision receipt. Candidate-runtime provider calls remain zero.
