# S8 W3 - Independent Review of W1

Role: independent review/veto
Resource: `deepseek-flash-workers` instance 3
Model: `deepseek-v4-flash` / high
Candidate: `12bac6c9a98928c4ed65c2ae1b88023762f3f59c`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-s8-w1-independent-review.md`

Review the candidate against the Fable S8 plan and W1 packet. Do not edit code,
tests, or candidate artifacts. Inspect the complete diff and rejected-attempt
history. Run the focused test with the shared main venv, JavaScript syntax, and
whitespace checks.

Veto for test weakening, incorrect URL resolution, unbounded 12007 retry,
inaccessible or misleading failure UI, Command Centre regression, shared
harness modification, scope/gate expansion, or any mismatch between artifact
claims and observed evidence. Check Word Online behavior conservatively.

Write a review artifact containing observed branch/HEAD, candidate SHA, exact
commands/counts, findings, residual risks, and one canonical final marker:
`DECISION: pass` or `DECISION: revision_required`. Finish the turn normally.

No code edits, Git mutation, push, or integration authority.
