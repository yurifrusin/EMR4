# Threat-model delta: Clinician One read-only document context

Date: 2026-07-31

Status: `active_provider_free_development`

Parent: `raisa_dual_host_foundation_pass`

## New surface

One default-off localhost adapter may read the current Word selection after an
explicit click and return a typed authored-synthetic context frame in memory.

It adds no backend route, provider path, microphone operation, document write
or command.

## Threats and controls

### Whole-document overread

Threat: a bounded selection operation silently reads the body, neighbouring
paragraphs, metadata or Custom XML.

Controls:

- the adapter uses only `context.document.getSelection()`;
- it loads only `text` on that range;
- source tests prohibit body, paragraph, property and Custom XML access; and
- empty selection fails closed.

### Host capability becomes document authority

Threat: `clinician_one.workspace=host_ready` is treated as permission to read.

Controls:

- the accepted host profile retains `document_read=false`;
- a separate exact single-use local fixture grant is required;
- the request requires an explicit click;
- the adapter labels the resulting frame `staff_selected`; and
- the local grant makes no real authentication or role claim.

### Oversized or hidden context escapes

Threat: large, multiline or silently truncated content leaves the document.

Controls:

- exact 1,200-character and 40-line ceilings;
- rejection rather than truncation;
- no network or provider path;
- the UI renders counts and provenance only; and
- durable evidence excludes raw selection text.

### Replay causes repeated reads

Threat: a request identifier is reused to read a changed selection.

Controls:

- request identifiers are consumed before document access;
- the ledger is in-memory and instance-local;
- replay returns `already_consumed`; and
- replay performs zero further document reads.

### Read error leaks host detail

Threat: raw Office errors reveal document, account, path or tenant details.

Controls:

- the response retains only `selection_read_failed`;
- raw error text is neither returned nor logged;
- evidence records only the allowlisted reason; and
- existing document or Office-account identifiers are not inspected.

### Synthetic gate is mistaken for clinical readiness

Threat: fixture success is used with real clinical text or described as
authenticated Word Online evidence.

Controls:

- the request accepts only `authored_synthetic`;
- the exact grant is named `local_authored_synthetic_fixture`;
- ordinary browser and injected desktop/web results are labelled fixtures;
- real/product-derived patient, health and clinical data remain closed; and
- authenticated Word Online remains a separate platform/deployment gate.

## Preserved API Spine controls

- GraphQL remains read-only and unchanged.
- No REST command or async event is introduced.
- The frame is minimal, source-labelled and non-authoritative.
- Frontends do not call providers.
- Clinical writes still require an explicit doctor-confirmed audited command.
- Broad patient context and autonomous clinical mutation remain blocked.

## Residual risk

Dependency-injected fixtures do not prove Word selection semantics, tenant
identity or role enforcement in every desktop and web host. A future
supervised real-host exercise must use a task-created synthetic document and
its own exact authority.
