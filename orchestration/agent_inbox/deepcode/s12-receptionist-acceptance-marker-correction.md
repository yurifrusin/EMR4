# S12 W1 correction: canonical completion marker

This is a format-only same-lane correction. The prior attempt wrote useful
evidence but used the literal `STATUS: complete` in a table before its final
line. The PTY completion parser rejects a non-unique marker, so that artifact
was preserved and is not accepted.

Do not modify code, tests, documentation other than the required artifact, Git
history, branches, or remote state. Review only the evidence already described
in the earlier S12 packet. Terra owns all deterministic test execution.

Write the replacement review to exactly:
`orchestration/agent_inbox/codex/review-deepseek-s12-receptionist-acceptance.md`

Use `DECISION: pass` or `DECISION: revision_required`. Do not use the literal
completion marker anywhere in headings, prose, tables, or code blocks. The
last non-empty line, and the only occurrence of the completion marker, must be
exactly:

`STATUS: complete`
