# Ariadne agent error and correction register — revision 297

Date: 2026-08-15

Timestamp: 2026-08-15T22:21:42+10:00 (Australia/Brisbane)

Revision 297 records AER-0336. At this revision the register contains 336
bounded known incidents, all corrected or contained by an explicit control.

AER-0336 preserves the rejected terminal self-pass from the DeepSeek
delete-confirm scaffold worker. Candidate
`bc0b8adcdc9f1c11bb69abe1514677a92d17f9c7` was a clean child of
`d500f1f86a83695cee0c2aac93aa2e2735e8f799`, but mandatory command 3 exited 1:
the legacy status-scaffold suite reported 10 passed and one failed OpenAPI-hash
assertion. A required nonzero gate cannot be reconciled with `DECISION pass` by
qualifying prose.

The worker result and candidate remain revision-required, untrusted provenance.
No source admission, integration or acceptance followed. Future worker receipt
admission mechanically compares every mandatory command exit with the terminal
decision; any nonzero result overrides pass prose.
