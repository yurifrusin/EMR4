# Raisa Clinician One supervised Word desktop selection check plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_provider_free_real_host_check`

## 1. Authority and predecessor

Yuri authorised continuation from
`clinician_one_readonly_document_context_adapter_pass`. Its recommended next
descendant is one supervised installed-Word exercise using a task-created blank
document containing authored-synthetic text.

This descendant may:

- use the existing installed Microsoft Word desktop application;
- create one new unsaved blank document;
- type one short authored-synthetic fixture into that document;
- select only that fixture text;
- temporarily sideload one disposable repository-local manifest;
- serve the existing taskpane from HTTPS loopback on `127.0.0.1:3000`; and
- press the existing `Check selected text` control exactly once.

It may not inspect an existing document, Office account, tenant, licence,
credential, filename or document identifier. It grants no product-derived,
patient, health or clinical-data authority.

## 2. API Spine classification

This is real-host evidence for the accepted typed, client-local,
non-authoritative `current_consult_note` context-frame adapter.

It is not:

- a GraphQL read;
- a REST command;
- a backend or database operation;
- an Access AI or provider invocation;
- a clinical-record or document mutation;
- a microphone operation; or
- a diagnostic, prescribing, finalisation or autonomous-agent action.

The selected text is labelled `staff_selected`,
`active_document_selection`, `word_current_selection` and
`authored_synthetic`. It remains transient in memory. GraphQL, REST, async
contracts and backend state remain unchanged.

## 3. Disposable Word boundary

- The task manifest has a product identifier distinct from the canonical and
  prior Reception One development manifests.
- It requests `ReadDocument`, not `ReadWriteDocument`.
- Its taskpane URL is exactly the HTTPS loopback taskpane with
  `clinician_one_context_demo=true`.
- The development listener binds only to `127.0.0.1`.
- The existing trusted localhost certificate is reused; no certificate,
  Trust Center, tenant, catalogue, privacy or security setting is changed.
- Only one newly created unsaved blank document may be used.
- The adapter may read only the exact current selection in that task document.
- Existing Word windows and documents must not be inspected or changed.

## 4. Exact exercise

1. Start the task-owned HTTPS loopback development server.
2. Temporarily sideload the disposable manifest in Word desktop.
3. Create or verify one new unsaved blank task document.
4. Type one short authored-synthetic two-line fixture.
5. Select exactly that fixture text.
6. Open the disposable Clinician One taskpane.
7. Check the authored-synthetic acknowledgement.
8. Press `Check selected text` exactly once.
9. Require the counts-only taskpane disposition:
   - selection ready;
   - exact character count;
   - exact line count;
   - `word_current_selection`; and
   - desktop host.
10. Retain only hash, counts, typed labels and zero-authority observations.
11. Stop the sideload and listener and discard the unsaved task document only
    after the required action-time user confirmation.

No raw selected text, screenshot, account identifier, document identifier,
Office error or filename is durable evidence.

## 5. Acceptance gates

### Gate A - rehydration and preservation

- The five mandatory Ariadne sources pass.
- HEAD and the four protected refs are verified.
- Every unrelated worktree change is preserved.

### Gate B - manifest and static contract

- The disposable manifest is XML/schema valid.
- Every task URL is HTTPS loopback.
- The requested permission is exactly `ReadDocument`.
- Source inspection still proves current-selection-only access and no body,
  write, provider, backend, storage or microphone path.

### Gate C - real installed Word

- Exactly one task-created unsaved blank document is used.
- Exactly one authored-synthetic selection read is requested.
- The taskpane reports the expected count, line, source and desktop-host
  metadata without rendering the selected text.
- No existing document or Office account material is inspected.

### Gate D - authority and evidence

- Provider, credential, backend, database, microphone, diagnostic, clinical
  action, command and document-write counts remain zero.
- Durable evidence contains no raw selected text.
- The result is labelled installed Word desktop evidence, not Word Online,
  production or clinical-data evidence.

### Gate E - cleanup and verification

- The disposable sideload, development listener, temporary logs and task-owned
  processes are removed.
- The task-created unsaved document is discarded only with user confirmation.
- Run the focused Clinician One/Word/API Spine tests, repository-only Ariadne
  verifier, manifest, JSON, Python, JavaScript, Compass/continuity and
  `git diff --check` gates.

## 6. Stop conditions

Stop without weakening the boundary if Word requires:

- account, tenant, catalogue, IAM, Trust Center, privacy or security changes;
- a new certificate;
- access to an existing document;
- product-derived, patient, health or clinical data;
- provider, backend, database, microphone, document-write or command access; or
- production, deployment or release authority.

## 7. Candid evidence limit

A pass proves only that the accepted adapter can read one bounded
authored-synthetic exact current selection in the installed Word desktop host
through a disposable local sideload and show counts-only metadata. It does not
prove authenticated Word Online, Office identity or role enforcement, safety
for clinical text, backend or provider integration, clinical correctness,
production fitness, deployment or release.
