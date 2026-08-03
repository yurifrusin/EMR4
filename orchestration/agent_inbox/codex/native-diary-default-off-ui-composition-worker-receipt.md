# Worker receipt: native-Diary default-off application-session UI composition

Date: 2026-08-03

Worker: native Codex bounded implementation worker

Source head: `e7d209e6652106c8f69036460223259a33af19c9`

Branch: `codex/native-diary-default-off-ui-composition`

Decision: `candidate_ready`

Candidate result:
`provider_free_native_diary_application_session_ui_composition_pass`

## Authority and rehydration

The worker read the worktree `AGENTS.md` completely at 438 lines, the exact
root-owned worker packet, the active composition/runtime/reconciliation plans,
designs, threat models, contracts and closeouts, and the API Spine ADR,
programme and relevant practitioner-directory artifacts. The EMR4 API steward
skill and its review checklist were applied.

A fresh Ariadne preflight passed with
`rehydrated_from_receipt=true`, settings fingerprint
`sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`,
and all five required sources:

- `live_handover_current_baton`
- `current_authority_allocation`
- `active_plan_and_acceptance`
- `protected_evidence_boundaries`
- `git_refs_and_worktree`

The isolated worktree and branch matched the packet at the exact source head.
At rehydration, local/origin `master` and `handoff/current` were aligned at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Implemented bounded candidate

- Published an LF-canonical copy of the accepted reconciler at
  `docs/diary/application-session-practitioner-reconciler.mjs` without editing
  the accepted source.
- Added an ES-module composition around exactly one injected no-argument fixed
  reader. Exact three-key bootstrap admission rejects incomplete, extra or
  authority-bearing enabled state before reading.
- Added strict latest-read-wins egress through the accepted reconciler,
  sanitized reader-failure handling, strict generation advance, invalidation
  and a sanitized immutable snapshot.
- Added the smallest native-Diary wiring: only exact boolean `true` selects the
  application-session branch; feature-off states retain the existing bearer
  GraphQL plus REST fallback. The two legacy fetch functions remain exact at
  the source head, and the enabled branch contains no legacy fallback.
- Added a recursively closed machine contract/schema, plan, threat-model delta,
  authored-synthetic Node harness and focused Python wrapper.
- Did not create the final evidence JSON; root retains acceptance execution and
  evidence ownership.

## Deterministic checks

- Node acceptance harness: 15/15 passed with exact evidence label
  `provider_free_default_off_ui_composition_harness` and
  `data_class=authored_synthetic`.
- Node syntax: published reconciler, composition module, `diary.js` and the
  acceptance harness passed.
- Ruff: the focused Python test passed.
- Serial pytest initial run: 192 passed and one test-only Windows decode check
  failed because `git show` used cp1252. No product/module assertion failed.
- Mechanical repair: the subprocess now decodes the repository blob explicitly
  as UTF-8.
- Serial pytest rerun: 193 passed, 0 failed in 57.5 seconds across the new test,
  composition/runtime/reconciliation parents, session practitioner-directory
  read bridge, practitioner REST and GraphQL reads, Bernie/Davida seam and API
  Spine artifacts.
- `git diff --check` and exact path/branding cache checks are required again at
  staging and were not delegated.

## Fail-closed repair after root review

Root required revision of candidate `c18c57947ea56f9546a9be57b82e4bc2fb541bfe`
before external review for two race/failure gaps. The repair remains inside the
same owned UI-composition paths and adds no authority:

- one bounded helper invalidates outstanding tickets and clears the cached
  composition/reader whenever bootstrap becomes disabled or malformed and
  before enabled invalid-bootstrap, changed-reader, invalid-generation or read
  failures leave the composition branch;
- every enabled-path failure is converted to one fixed generic marker and the
  existing enclosing practitioner-directory catch rethrows it, preventing a
  partial empty-directory Diary render;
- feature-off legacy non-401 failure swallowing remains unchanged;
- Node now drives the actual reset helper against an outstanding read for
  disabled, malformed and changed-reader transitions, and executes the actual
  call-site handler for both enabled rethrow and legacy swallowing.

Repair verification passed: Node acceptance 17/17, Ruff, all four Node syntax
checks, `git diff --check`, and 194 serial focused/parent/practitioner-directory/
seam/API-Spine pytest cases in 56.8 seconds. The shared PostgreSQL pytest slot
was explicitly released before the repair commit. The repair is committed
separately and does not amend or erase the original candidate history.

## API Spine and claims

This is a scoped read consumer. GraphQL remains read-only; no mutation, command
tunnel, REST surface, event actuator, manifest or write authority was added.
The candidate is provider-free, default-off and limited to authored-synthetic
static/UI harness evidence. It is not browser, route-intercepted, HTTP/backend,
PostgreSQL, mounted-backend, real-identity, patient/clinical/document,
usability, deployment, production or release evidence.

No `app/**`, migration, shared auth/router, accepted reconciliation source,
API Spine artifact, global Continuity/Compass map, harness setting, workflow,
protected evidence/ref or `docs/branding/**` path was edited. The worker did not
push, integrate, accept, deploy or release. Root Sol alone owns review and
acceptance.
