# Ariadne agent error and correction register — revision 413

Date: 2026-08-18

Timestamp: 2026-08-18T19:05:40.5243540+10:00 (Australia/Brisbane)

Status: accepted correction update

Reasoning level: high

Revision 413 preserves rejected revisions 409 and 410 plus incomplete
revisions 411 and 412. AER-0480 through AER-0483 record and correct the invalid
stage, split attempt identity and two imprecise new focused-test literals.

The revision also records AER-0473 through AER-0479 from the exact-tool-view
provider-free recovery. Both isolated Harness composition errors stopped
before any request. The corrected fresh Linux-native run used an internal
Docker network and emitted one local capture request containing exactly
`edit`, `glob` and `read`; it made zero external/provider calls. Its disposable
containers, volumes and network are absent, while the exact disposable profile
root was sent to the Windows Recycle Bin and remains recoverable until that bin
is emptied.

The canonical register contains 483 bounded incidents, all corrected or
explicitly contained and none open. This correction does not broaden the
frozen tool-view plan, model route, data boundary, broker allowlist,
occupied-call authority or protected-ref authority.
