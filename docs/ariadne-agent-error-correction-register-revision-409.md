# Ariadne agent error and correction register — revision 409

Date: 2026-08-18

Timestamp: 2026-08-18T19:05:40.5243540+10:00 (Australia/Brisbane)

Status: rejected correction representation; superseded by revision 410

Reasoning level: high

Revision 409 records AER-0473 through AER-0479 from the exact-tool-view
provider-free recovery: one invalid Windows `rg` glob form, one unnormalised
Markdown assertion, one unsupported Docker inspect template, two fail-closed
container-enclosure composition errors, one expected-absent capture read and
one policy-rejected nonrecoverable cleanup form.

Both isolated Harness composition errors stopped before any request. The
corrected fresh Linux-native run used an internal Docker network and emitted
one local capture request containing exactly `edit`, `glob` and `read`; it made
zero external/provider calls and its disposable containers, volumes, network
and profile root were then removed. The profile root was sent to the Windows
Recycle Bin and remains recoverable until that bin is emptied.

This representation was not accepted: AER-0479 used non-canonical stage
`cleanup`, and the register schema rejected it before pattern generation.
Revision 410 preserves this failed representation, reclassifies AER-0479 at
canonical stage `closeout`, records AER-0480 and performs the complete
validation. No authority or evidence claim derives from revision 409.
