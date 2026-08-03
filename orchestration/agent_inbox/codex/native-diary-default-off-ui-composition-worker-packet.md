# Worker packet: native-Diary default-off application-session UI composition

Date: 2026-08-03

Authority: bounded implementation and focused tests only

Source head: `e7d209e6652106c8f69036460223259a33af19c9`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\native-diary-default-off-ui-composition`

Branch: `codex/native-diary-default-off-ui-composition`

Target result:
`provider_free_native_diary_application_session_ui_composition_pass`

## Frozen boundary

Implement Diary lane step 3 only. Add a browser-published copy of the accepted
pure reconciler, an ES-module composition that uses that reconciler around one
trusted injected fixed-read function, and the smallest `diary.html`/`diary.js`
wiring. The application-session path is enabled only by one exact strict-true
bootstrap flag. Undefined, false, malformed or incomplete bootstrap state keeps
the existing bearer-authenticated GraphQL-with-REST-fallback path unchanged.

When enabled, the composition must fail closed if the injected reader or
generation is absent/invalid. It must never fall back to bearer/REST after an
application-session attempt. The injected reader owns HTTP/cookie/CSRF details;
the UI composition accepts no cookie, token, CSRF, practice, principal, role,
policy, action or arbitrary query value. Its only data egress is the accepted
reconciler. Expose bounded lifecycle controls to invalidate or strictly advance
generation and a sanitized snapshot only.

The published reconciler copy must be canonical-LF byte-equivalent to
`orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/client-reconciler.mjs`,
with a deterministic parity test. Do not weaken or edit the accepted source.

This tranche is mounted in static UI assets but remains default-off and has no
browser/live/backend evidence. Evidence label:
`provider_free_default_off_ui_composition_harness`; data class:
`authored_synthetic`.

## Owned paths

- `docs/diary/application-session-practitioner-reconciler.mjs` (new)
- `docs/diary/application-session-practitioner-directory.mjs` (new)
- `docs/diary/diary.html` (minimal script/version edit)
- `docs/diary/diary.js` (minimal default-off branch only)
- `docs/raisa-provider-free-native-diary-application-session-ui-composition-plan.md` (new)
- `docs/security/raisa-provider-free-native-diary-application-session-ui-composition-threat-model-delta.md` (new)
- `orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition/ui-composition-contract.json` (new)
- `orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition/ui-composition-contract.schema.json` (new)
- `scripts/raisa_provider_free_native_diary_application_session_ui_composition_acceptance.mjs` (new)
- `tests/test_raisa_provider_free_native_diary_application_session_ui_composition.py` (new)
- `orchestration/agent_inbox/codex/native-diary-default-off-ui-composition-worker-receipt.md` (new, durable worker receipt)

Do not create the final evidence JSON; root runs the acceptance script after
review.

## Acceptance cases

- default missing/false/malformed bootstrap takes the unchanged legacy path;
- strict true plus exact injected reader/generation uses only the application-
  session composition;
- enabled incomplete bootstrap fails closed before a read and never falls back;
- latest read wins, stale generation, supersession, invalidation, replay,
  malformed/authority-bearing response and callback failure remain suppressed;
- generation advance is strict and invalidation suppresses outstanding work;
- no reader, response row, secret or authority material is retained or emitted
  in the snapshot;
- published/canonical reconciler parity is exact after LF normalization;
- new modules contain no direct fetch, cookie/localStorage/sessionStorage,
  bearer, CSRF, network, provider, model, command or write implementation;
- `diary.js` retains the exact existing GraphQL and REST functions and falls
  back only inside the feature-off legacy branch;
- contract validates recursively closed and every authority-bearing mutation
  fails;
- existing practitioner-directory, parent runtime/reconciliation, seam and API
  Spine tests pass serially.

## Forbidden paths and claims

Do not edit `app/**`, `alembic/**`, existing accepted reconciliation files,
GraphQL/OpenAPI/manifests, `AGENTS.md`, Continuity/Compass global maps, harness
settings, workflows, `docs/branding/**`, protected evidence or any other lane.
No `app.main` mount, backend route, provider/model, real identity, patient/
clinical/document data, product write, default-on, browser/live evidence,
deployment, production, release or protected-ref action.

## Worker mechanics

Use `apply_patch` only. Run focused Node/Python/static checks serially. Stage
only owned paths by exact pathname, assert no `docs/branding/` path is cached,
commit to the task branch, and return the exact commit plus one terminal
`candidate_ready` or `revision_required`. Do not push.
