# Ariadne agent error and correction register — revision 380

Date: 2026-08-18

Timestamp: 2026-08-18T13:30:01.6997279+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 380 adds AER-0432. After resumption, Sol combined `git status`, four
protected-ref readbacks and two exact-file metadata readbacks in one
semicolon-composed PowerShell invocation. This repeated the readback form of
the AER-0429 control breach even though the combined process exited zero and
reported the expected values.

The output is retained as incident evidence but is not admitted as the
verifier gate. Every dispatch-critical readback is rerun independently before
Gemini launch. No product source, candidate, worktree, provider call or ref
changed.

## Population

- incidents: 432;
- corrected or explicitly contained: 432;
- open: 0;
- latest id: `AER-0432`.

No product data, deployment, release, Pages or protected-ref action occurred.
