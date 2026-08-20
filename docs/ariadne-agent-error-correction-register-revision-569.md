# Ariadne agent-error and correction register — revision 569

Date: 2026-08-20

Timestamp: 2026-08-20T11:05:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 569 records one low-severity orchestration recurrence from the
DeepSeek native Harness provider-free emr4-bounded-worker preset
materialisation recovery.

The first postpublication compatibility chain yielded after partial pytest
output. The tool caller projected only stdout and discarded the returned
unified-session identifier, repeating the already corrected failure pattern in
AER-0421, AER-0651 and AER-0654. Process inspection proved that the chain
reached its final clockwork check and exited, but the pytest terminal exit was
not recoverable and was not admitted.

One unchanged observed rerun emitted the full execution envelope, retained
session `42419`, polled it to terminal exit code zero and passed the complete
suite to 100%. The candidate, provider boundary and protected refs were
unchanged. The otherwise-valid lease-53 clean publication is preserved as a
rejected closeout attempt and rolled back byte-exactly at lease 54 so this
recurrence can enter canonical incident intake before final publication.

The clockwork derives the incident identifier, revision, origin, status,
counts and pattern report from the semantic observation in the closeout
intent. This explanatory note does not replace the canonical register under
`orchestration/continuity/ariadne-agent-error-register/`.

## Prevention

Every local command that can exceed the initial tool yield is dispatched as a
dedicated call whose complete result envelope—`output`, `session_id`,
`exit_code` and `chunk_id`—is emitted before control returns. A nonterminal
result is polled through that retained identifier to a final exit. Long test
suites are not placed in a multi-command shell chain whose earlier exit could
become unobservable.
