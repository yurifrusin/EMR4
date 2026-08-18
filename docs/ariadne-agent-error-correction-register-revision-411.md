# Ariadne agent error and correction register — revision 411

Date: 2026-08-18

Timestamp: 2026-08-18T19:05:40.5243540+10:00 (Australia/Brisbane)

Status: incomplete correction representation; superseded by revision 412

Reasoning level: high

Revision 411 preserves rejected revisions 409 and 410 and records AER-0480
and AER-0481. Revision 409 used a non-canonical register stage. Revision 410
then gave the Docker transport terminal and the later local conditional-read
mistake one shared attempt identity despite different transports. The
conditional read now has its own attempt identity and the invalid peer links
are cleared.

The revision also records AER-0473 through AER-0479 from the exact-tool-view
provider-free recovery. Both isolated Harness composition errors stopped
before any request. The corrected fresh Linux-native run used an internal
Docker network and emitted one local capture request containing exactly
`edit`, `glob` and `read`; it made zero external/provider calls. Its disposable
containers, volumes and network are absent, while the exact disposable profile
root was sent to the Windows Recycle Bin and remains recoverable until that bin
is emptied.

The register schema and pattern generation passed, but the complete focused
suite found one case-sensitive literal error in the new AER-0480 assertion.
Revision 412 preserves this incomplete representation, records AER-0482,
corrects the assertion and reruns the complete suite. Revision 411 is not the
accepted register state.
