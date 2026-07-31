# Raisa Clinician One read-only document-context closeout

Date: 2026-07-31

Result: `clinician_one_readonly_document_context_adapter_pass`

## Outcome

The first Clinician One operation now sits behind the accepted Office host
foundation. One exact local authored-synthetic fixture request can read the
current Word selection once and emit a closed, deeply immutable
`current_consult_note` frame.

The adapter:

- checks the accepted host profile without treating it as authorization;
- requires a separate exact local fixture grant and explicit click;
- supports desktop and web Word host fixtures only;
- reads only `context.document.getSelection().text`;
- rejects empty, oversized and over-line-limit selections without truncation;
- consumes a request identifier before attempting the read;
- sanitizes Office read failures to one allowlisted reason; and
- grants no diagnostic, prescribing, clinical-finalization, patient-context,
  provider, network, document-write, command or write authority.

## Taskpane behavior

An exact localhost `clinician_one_context_demo=true` flag reveals a compact
Clinician One card. It requires an authored-synthetic acknowledgement and
displays only source, host, character count and line count after admission.
Selected text is never rendered by the card.

In an ordinary browser, the card rendered correctly and remained disabled
after acknowledgement with the exact message that the Word host was not
ready. It made no document read. This is fail-closed browser evidence only.

## Verification

- Closed request and response JSON schemas: passed.
- Desktop and web dependency-injected selection reads: passed.
- Single-use replay: blocked before a second read.
- Mobile, unknown and missing Word host: blocked before read.
- Invalid grant/request, empty, oversized, over-line and read-error cases:
  blocked with typed reasons.
- Deep immutability and zero non-read authority: passed.
- Source inspection prohibits whole-document, write, provider, network,
  storage and microphone paths: passed.
- Source and published copies: byte-identical.
- Focused Clinician One, Raisa foundation, Hybrid, compact companion, Word
  desktop/online and continuity suite: 118 passed.
- Relevant API Spine contract suite: 65 passed.
- Repository-only Ariadne verifier: 266 passed.
- JavaScript/Python syntax and taskpane development build: passed.
- Browser, listener, process, container, network, image, temporary-log,
  credential and raw-selection residue: absent.

Continuity graph revision 174 and Compass map revision 155 bind the result.
The broader historical continuity audit retains its two previously documented
contract gaps; neither belongs to or is changed by this descendant.

## Evidence boundary

Durable evidence contains hashes, counts, fixture labels and reason codes only.
It contains no raw selected text, document body, Office error, patient context,
provider material or credential.

This result does not prove a real installed-Word selection, authenticated Word
Online, Office identity, role enforcement, clinical-data safety, provider
readiness, clinical correctness, production deployment or release.

## Recommended next descendant

Run one supervised provider-free installed-Word exercise using a task-created
blank document containing authored-synthetic text. Verify the exact selection,
single-use response, counts-only UI and complete cleanup without opening
backend, provider, patient, clinical or write authority.
