# Raisa Clinician One read-only document-context adapter plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_provider_free_development`

## 1. Authority and predecessor

This is the first Clinician One operation behind the accepted
`raisa_dual_host_foundation_pass`.

It reuses the immutable Office host profile and the API Spine consultant
context-frame concept:

- frame: `current_consult_note`;
- authority label: `staff_selected`;
- maximum scope: `active_document_selection`;
- data classification: `authored_synthetic`; and
- operation: one explicit read from the current Word selection.

The operation is available only through an exact localhost, default-off
development flag and an exact authored-synthetic fixture grant. It does not
claim production authentication, role authorization or clinical-data safety.

## 2. Boundary classification

This is a typed, client-local, non-authoritative context-frame adapter.

It is not:

- a GraphQL read;
- a REST command;
- an Access AI or provider invocation;
- a backend or database read;
- a patient-context read;
- a clinical-record mutation;
- a document write; or
- an autonomous agent action.

GraphQL remains read-only and unchanged. No REST command is added because the
adapter performs no external or irreversible action.

## 3. Exact operation

The request contract is
`emr4.clinician-one-document-context-request.v1`.

It permits only:

- `read_selected_authored_synthetic_text`;
- `current_word_selection`;
- one explicit clinician click;
- a single-use request identifier;
- at most 1,200 characters;
- at most 40 lines; and
- the local authored-synthetic clinician-fixture grant.

The adapter must:

1. verify the closed request;
2. verify the exact local fixture grant;
3. require the accepted Office host profile and
   `clinician_one.workspace=host_ready`;
4. admit only desktop or web Word hosts;
5. consume the request identifier before attempting the read;
6. call `Word.run` once and read only `context.document.getSelection().text`;
7. normalize line endings and reject empty, oversized or over-line-limit
   selections without truncation; and
8. emit a deeply immutable typed response.

The adapter never reads `context.document.body`.

## 4. Typed response

The response contract is
`emr4.clinician-one-document-context-response.v1`.

An admitted response contains one in-memory frame:

- `frame_type=current_consult_note`;
- `authority_label=staff_selected`;
- `source_scope=active_document_selection`;
- `source_label=word_current_selection`;
- `data_classification=authored_synthetic`;
- exact selected text;
- exact character and line counts;
- `truncated=false`;
- exact host kind and platform; and
- `single_use=true`.

The selected text is transient context only. It must not be written to logs,
screenshots, evidence, storage, the backend or a provider.

The taskpane may display only the disposition, source label, host kind,
character count and line count.

A blocked response contains no context frame and one allowlisted reason:

- invalid request;
- grant denied;
- unsupported or unavailable host;
- already consumed;
- empty selection;
- character or line limit exceeded; or
- sanitized selection-read failure.

## 5. API Spine and authority controls

- The context frame is source-labelled and non-authoritative.
- Host capability does not establish product authorization.
- The local fixture grant does not establish real authentication.
- Patient context and broad document reads remain false.
- Provider, network, microphone, command, write and document-write counts
  remain zero.
- No model, clinician, UI or adapter may treat the frame as diagnostic,
  prescribing, finalisation or mutation authority.

## 6. User experience

An exact localhost query flag,
`clinician_one_context_demo=true`, reveals one compact Clinician One card.

The card tells the user to select authored-synthetic text, then press
`Check selected text`. It never shows the selected text. Missing host
capability disables the control with a plain-language explanation.

The existing consultation, scribe and Reception One interfaces remain
unchanged.

## 7. Acceptance gates

### Contract and deterministic behavior

- Request and response schemas are closed and valid.
- Desktop and web Word fixtures admit one bounded selection.
- Mobile, unknown and missing Word-runtime fixtures fail closed.
- Reuse of a request identifier fails before another document read.
- Empty, oversized, over-line-limit and read-error cases fail closed.
- Outputs are deeply immutable.

### Source inspection

- The adapter contains no `fetch`, provider, storage, microphone, body-read,
  insertion or command path.
- The only document access is current selection text.
- Taskpane rendering never copies selected text into the DOM or logs.
- Source and published copies are byte-identical.

### Regression and evidence

- Run the focused Clinician One, Raisa foundation, Word companion, Word
  desktop/online and API Spine suites.
- Run JavaScript syntax, taskpane build, JSON/schema validation, Python
  compilation, continuity/Compass validation and `git diff --check`.
- Record only hashes, counts, reason codes and fixture labels in durable
  evidence.
- Remove all task-owned browser, listener, process and temporary residue.

## 8. Closed boundaries

No existing document, patient record, real/product-derived/health/clinical
data, provider, Access AI, backend, database, network, microphone, audio,
document write, clinical command, appointment command, production, deployment,
release or public rename is authorised.

There is no provider call and no document write in this increment.

Authenticated Word Online execution remains unproven. An ordinary browser or
dependency-injected web fixture is not authenticated Word Online evidence.

## 9. Candid evidence limit

A pass proves only that one repository-local adapter can read a bounded
authored-synthetic current-selection fixture under an exact local grant and
emit a typed, non-authoritative in-memory frame. It does not prove real Office
identity, role enforcement, safety for clinical text, Word Online tenant
behavior, provider readiness, clinical correctness or production fitness.
