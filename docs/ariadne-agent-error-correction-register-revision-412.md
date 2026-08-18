# Ariadne agent error and correction register — revision 412

Date: 2026-08-18

Timestamp: 2026-08-18T19:05:40.5243540+10:00 (Australia/Brisbane)

Status: incomplete correction representation; superseded by revision 413

Reasoning level: high

Revision 412 preserves rejected revisions 409 and 410 plus incomplete revision
411. Revision 409 used a non-canonical stage; revision 410 split one attempt
identity across different transports; revision 411 passed schema and pattern
generation but its new focused test used a case-mismatched literal. AER-0480
through AER-0482 record and correct those representations.

The revision also records AER-0473 through AER-0479 from the exact-tool-view
provider-free recovery. Both isolated Harness composition errors stopped
before any request. The corrected fresh Linux-native run used an internal
Docker network and emitted one local capture request containing exactly
`edit`, `glob` and `read`; it made zero external/provider calls. Its disposable
containers, volumes and network are absent, while the exact disposable profile
root was sent to the Windows Recycle Bin and remains recoverable until that bin
is emptied.

The register schema and pattern generation passed, but the complete focused
suite found a second imprecise new literal: the test searched for `split
identity` while the canonical phrase was `split attempt identity`. Revision
413 preserves this incomplete representation, records AER-0483, corrects the
literal and reruns the complete suite. Revision 412 is not the accepted state.
