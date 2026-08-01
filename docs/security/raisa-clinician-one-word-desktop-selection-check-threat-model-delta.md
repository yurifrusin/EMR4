# Threat-model delta: Clinician One supervised Word desktop selection check

Date: 2026-07-31

Status: `active_provider_free_real_host_check`

Parent: `clinician_one_readonly_document_context_adapter_pass`

## New trust edge

One disposable local manifest loads the accepted taskpane in installed Word
desktop. One task-created unsaved document contains one authored-synthetic
fixture whose exact current selection may be read once.

## Threats and controls

### Existing document or account material is exposed

- Use one new unsaved blank document only.
- Do not inspect other Word windows, recent files, account, licence or tenant
  surfaces.
- Retain no filename, document identifier or Office account identifier.

### Manifest authority exceeds the adapter

- Request exactly `ReadDocument`.
- Use a distinct disposable product identifier and exact localhost flag.
- Add no command, backend, provider, microphone or write capability.
- Stop and remove the sideload after the check.

### Word reads beyond the selected fixture

- The accepted adapter calls only `context.document.getSelection()`.
- It loads only `text` on that range.
- Source tests prohibit body, paragraph, property and Custom XML access.
- The visible taskpane renders counts and typed provenance only.

### Synthetic text becomes durable evidence

- The task document remains unsaved.
- Evidence retains only a SHA-256 hash, character count, line count and typed
  labels.
- Computer-use screenshots are inspected transiently and not saved.
- Raw selection text is not copied into logs, evidence, taskpane DOM, backend
  or provider traffic.

### Sideload or listener persists

- The manifest is task-specific and local.
- The server binds only to `127.0.0.1`.
- Stop the debugging/sideload session and listener at cleanup.
- Independently check process, listener, temporary-log and manifest residue.

### Cleanup discards the wrong document

- Target only the uniquely observed task-created unsaved Word window.
- Do not close unrelated Word windows.
- Treat `Don't Save` as destructive UI action and request user confirmation at
  action time.

## Preserved boundaries

The frame remains minimal, source-labelled and non-authoritative. GraphQL stays
read-only and unchanged; no REST command or async event is introduced.
Provider, backend, database, credential, microphone, document-write,
diagnostic, prescribing, clinical-finalisation, appointment, production,
deployment and release gates remain closed.

## Residual risk

This exercise does not prove Office tenant identity, role authorization,
authenticated Word Online behavior or safety for real clinical text. It is one
provider-free authored-synthetic local desktop-host observation.
