# Ariadne agent error and correction register — revision 410

Date: 2026-08-18

Timestamp: 2026-08-18T19:05:40.5243540+10:00 (Australia/Brisbane)

Status: rejected correction representation; superseded by revision 411

Reasoning level: high

Revision 410 preserves rejected revision 409 and records AER-0480. The prior
representation used non-canonical stage `cleanup` for AER-0479; the register
schema rejected it before pattern generation. AER-0479 is now represented at
canonical stage `closeout`.

The revision also records AER-0473 through AER-0479 from the exact-tool-view
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

This representation was not accepted: AER-0477 and AER-0478 shared one
attempt identity and peer linkage while declaring different transports. The
semantic validator rejected the split identity before pattern generation.
Revision 411 preserves this failure, separates the conditional capture read
into its own attempt, clears the invalid peer linkage and records AER-0481.
