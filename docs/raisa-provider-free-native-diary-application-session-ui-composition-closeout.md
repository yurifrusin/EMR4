# Closeout: native-Diary default-off application-session UI composition

Date: 2026-08-03

Result: `provider_free_native_diary_application_session_ui_composition_pass`

## Accepted result

The native Diary now contains a default-off static UI composition for the
accepted fixed application-session active-practitioner read. Exact boolean
`true` plus the closed three-key bootstrap selects one injected no-argument
reader. The accepted reconciler remains the sole row egress, with strict row
admission, latest-read-wins, generation/invalidation, replay and callback
controls. When the feature is off, the pre-existing bearer GraphQL and REST
fallback functions remain unchanged.

An enabled failure cannot fall through to the bearer path or be swallowed as
an empty practitioner directory. Disabled, malformed and changed-reader
transitions invalidate outstanding reads and clear the cached composition. The
enclosing Diary load rethrows one generic composition marker before rendering
can continue, while ordinary feature-off non-401 failure handling is preserved.

## Evidence, repair and verification

- Native bounded implementation produced initial candidate
  `c18c57947ea56f9546a9be57b82e4bc2fb541bfe`.
- Root review found two fail-closed race gaps: enabled failures could be
  swallowed by the enclosing practitioner catch, and bootstrap transitions did
  not invalidate the cached reconciler. Separate repair
  `bb79a5dbbb1841a7472d007061791dbf08b14252` closed both and added executing VM
  transition/handler tests.
- Root-generated evidence candidate
  `1578ef693c733a7ce63953d37048793575891f1d` records 17/17 authored-synthetic
  cases. Its final task-branch replay is `2ce689f6` after implementation replay
  `1eae1023` and repair replay `2b4da653`.
- Fresh Gemini 3.6 Flash/high reproduced 194 serial tests, Ruff, four Node
  syntax checks, diff/ref/path checks and returned one exact `pass` while
  leaving the review worktree clean and unchanged.
- The integrated pair passed 289 serial tests. The evidence reproduced
  byte-for-byte at SHA-256
  `072943cb0cf88fb50577dfe172a97806f337961ceddb9930733f85e44f4e31c2`;
  Ruff, Node syntax and `git diff --check` passed.

## Claims not made

The evidence remains `provider_free_default_off_ui_composition_harness` over
authored-synthetic values. It does not establish browser, route-intercepted,
HTTP/backend, PostgreSQL, real-session injection, DOM/usability, default-on,
real-identity, patient/clinical/document, provider/model, command/write,
deployment, production or release behavior.

Protected refs/evidence and `docs/branding/` remained untouched. The product
Continuity/Compass map remains 206/187 because this is default-off static UI
composition without a live browser/backend result.

## Next bounded lane step

The next safe candidate is a provider-free, authored-synthetic,
route-intercepted browser rehearsal of the exact default-off composition. It
may prove real module loading, injected fixed-reader behavior, failure
rethrow/no-partial-render and feature-off legacy preservation in a disposable
local harness. It must not mount `app.main`, use real identity/data, become
default-on, or claim production/release authority.
