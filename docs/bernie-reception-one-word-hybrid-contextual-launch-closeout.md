# Reception One Word Hybrid contextual-launch foundation closeout

Status: **accepted provider-free local development result**
Closed: 2026-07-31
Result: `reception_one_word_hybrid_contextual_launch_pass`

## Outcome

The first Hybrid increment passes.

- Word remains the clinical workspace.
- The Word taskpane now exposes a distinct compact `Reception One — Open in
  Diary` action while preserving the ordinary Diary action.
- Reception One detailed work still opens in the full native Diary/Bureau
  window.
- The taskpane sends one closed, typed, non-authoritative navigation context
  only after the existing child-ready handshake.
- Authentication remains a separate message. The context contains no token,
  patient, appointment, request or command payload and is absent from the URL.
- The native Diary revalidates the exact context, verifies the requested Diary
  date and only then opens Reception One.
- The request textarea now supports clear one- and two-line text at desktop
  and phone widths, grows only to its bounded maximum and then scrolls
  internally.

The later compact conversational Reception One companion inside Word remains
future work; this tranche establishes its safe native-window handoff only.

## Evidence

The route-intercepted Chromium exercise passed:

- exact messages: separate `auth`, then
  `reception_one_launch_context`;
- exact 12-field zero-authority context;
- context absent from the launch URL;
- initial Diary date `2026-07-27`;
- admitted launch date `2026-07-31`;
- `diary_read_complete` observed before `projection_open`;
- responsive 52–96 px request-input bounds;
- zero provider calls;
- zero credential reads;
- zero database reads or writes; and
- no console error or unexpected external host.

Durable evidence:

- `orchestration/continuity/reception-one-word-hybrid-contextual-launch/browser-acceptance-evidence.json`
- `orchestration/continuity/reception-one-word-hybrid-contextual-launch/word-companion-launcher.png`
- `orchestration/continuity/reception-one-word-hybrid-contextual-launch/contextual-launch-desktop.png`
- `orchestration/continuity/reception-one-word-hybrid-contextual-launch/contextual-launch-narrow.png`
- `orchestration/continuity/reception-one-word-hybrid-contextual-launch/word-launch-context.schema.json`

The final focused and relevant integration suite passed 128 tests across the
Hybrid contract, integrated Bureau, UI wiring, post-admission hardening,
overflow, availability reconciliation, functional/live-local meta-grid, API
Spine artifact and Compass gates.

## Security and authority disposition

No live provider call, ADC access, API key, patient/product-derived/clinical
data, historical Diary material, backend mutation, appointment confirmation,
database write, voice input, participant session, deployment, production or
release occurred.

The plan records one protected-evidence handling incident: an over-broad
read-only pre-plan search entered a protected fixture path. The search was
stopped, the content was not analysed or reused, and all implementation and
acceptance work thereafter used explicit non-protected paths and newly
authored-synthetic evidence. No historical node was revised.

## Candid limit

This proves the provider-free local Word taskpane contract using a stubbed
Office host and the native Diary in Chromium. It does not prove an authenticated
Word Online dialog, tenant popup policy, real cross-window focus restoration,
provider behavior, production fitness or safety with patient, appointment,
clinical or product-derived data.

## Next bounded increment

The recommended next increment is the compact Word companion shell: a small
natural-language entry surface and concise proofreader-admitted summary that
hands detailed work to this now-typed native Diary path. Its patient-context,
provider and product-data policies require a fresh plan before use.
