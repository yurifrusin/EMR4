# Reception One cancellation command-path readiness review plan

Date: 2026-08-15

Timestamp: 2026-08-15T11:19:48+10:00 (Australia/Brisbane)

Status: `frozen_for_repository_static_execution`

Task baseline: `c4e28ad03bb22516bd40d110021ac2de9ead1ec8`

Target result: `raisa_reception_one_cancellation_command_path_readiness_review_pass`

Reasoning level: Extra High. Cancellation is a destructive appointment command
family, and this review selects the architecture prerequisite that must precede
any Reception One exposure. Execution remains provider-free and read-only.

## Objective

Inventory and reconcile the exact existing appointment cancellation surfaces:
the dedicated delete proposal/confirm family, the ordinary Diary's optional
delete-to-status fallback, the raw compatibility delete, the OpenAPI/API Spine
contract and Reception One's present absence of a cancellation bridge. Freeze
the narrowest fail-closed prerequisite before any cancellation UI composition.

The review changes no product or runtime behavior.

## Boundary classification

- API Spine class: destructive REST/OpenAPI appointment command mutation.
- Present evidence class: `repository_static_authored_synthetic`.
- Principal path under review: authenticated practice staff only.
- Required pattern: proposal, deterministic backend checks, typed evidence and
  freshness, explicit human confirmation, confirm command, atomic current-truth
  and current-authority revalidation, idempotent commit, audit and fresh readback.

GraphQL remains read-only. Events remain acceleration hints and do not supply
cancellation authority or confirmation evidence.

## Exact evidence sources

Read only:

1. `AGENTS.md`, the accepted post-combined-editor orientation chain and the
   current active-operation latch;
2. `orchestration/api_spine_adr.md`,
   `orchestration/api_spine_programme.md`,
   `orchestration/bernie_release_gates.md`, the current appointment alignment
   inventory and compatibility-write deprecation map;
3. `docs/api-spine/openapi/appointment-commands.yaml` and its drift guards;
4. appointment router, schemas, Diary action grammar/route contracts and the
   conditional-command status reference implementation;
5. the ordinary Diary cancellation client, Reception One bridge/presentation
   sources and their focused tests; and
6. current cancellation, reason-code, audit, idempotency and stale-evidence
   tests.

Protected holdouts, historical Diary/PHI, live product/database state, provider
output and external channel state are ineligible.

## Questions this review must answer

1. Which mounted routes can propose, confirm or directly perform cancellation?
2. Does every ordinary product-client cancellation require explicit destructive
   human confirmation and signed evidence before mutation?
3. Does the dedicated confirm path preserve cancellation text and reason code,
   reject stale/tampered evidence, provide idempotent replay and append audit?
4. Does it lock and recheck appointment truth and current actor authority inside
   the mutation transaction, as required by the accepted conditional-command
   reorientation?
5. What meaning changes when the native Diary falls back from delete to status?
6. Which OpenAPI/backend route and schema differences are deliberate, guarded,
   stale or unresolved?
7. Can Reception One safely compose the existing family unchanged, or must a
   bounded delete-family convergence tranche precede it?

## Acceptance

The tranche passes only if it:

1. inventories the exact delete proposal, delete confirm, raw compatibility
   delete, status fallback and Reception One reach;
2. separates mounted compatibility behavior from the preferred API Spine path;
3. records confirmation, signed-evidence, freshness, idempotency, audit,
   reason-preservation and fresh-readback behavior with exact source evidence;
4. explicitly tests the accepted in-transaction lock/current-authority
   requirement against the current delete path;
5. identifies OpenAPI/backend path and payload drift without changing either;
6. classifies each finding by severity and proves no vulnerability broader than
   repository evidence supports;
7. selects exactly one narrow prerequisite or proves unchanged reuse safe;
8. changes no product, API, OpenAPI, route, schema, database, UI, event or
   runtime source;
9. passes focused static review, API Spine, cancellation and canonical fast
   checks; and
10. receives one fresh Gemini 3.6 Flash/high read-only exact-candidate veto
    after deterministic admission.

## Expected decision rule

Unchanged reuse is admissible only if one dedicated cancellation family owns
the product meaning and its confirm transaction already provides:

- explicit human confirmation;
- signed actor/practice/command/current-state evidence;
- a locked current appointment read;
- current authority rechecked inside that same mutation transaction;
- reason-code and cancellation-text preservation;
- atomic mutation, audit and idempotency completion; and
- fresh authoritative readback.

If any item is absent, freeze the smallest provider-free, unmounted
delete-family conditional-command convergence architecture/rehearsal before UI
composition. Do not repair product code inside this review.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high — declined:** the evidence set is small but its
  delete-versus-status meaning and authority classification are tightly
  coupled; there is no stable mechanical implementation package.
- **Gemini 3.6 Flash/high — reserved:** one fresh exact-candidate veto will
  challenge route completeness, severity, claim boundary and the selected
  prerequisite.
- **Native subagents — declined:** no bounded package has positive leverage
  after briefing and reconciliation cost.
- **Sol — serial owner:** evidence reconciliation, plan, report, acceptance,
  continuity and Git.

Reassess at report freeze, pre-verifier admission and closeout.

## Stop and recovery

Correct stale citations, omitted mounted routes, mistaken severity or test
coverage inside this read-only tranche. Stop for Yuri only if repository
evidence reveals a genuinely non-inferable product-policy choice between
materially different cancellation meanings. A missing architecture safeguard
does not itself require a pause: select the narrowest fail-closed prerequisite.

## Closed surfaces

No cancellation control, product behavior, route, OpenAPI/GraphQL/schema,
database/source, watcher/event runtime, command/write, provider/ADC,
credential/IAM/network, patient/product/clinical/protected data, external
channel, deployment, production, release, Pages or protected-ref action is
authorised. Preserve `docs/branding/` and every unrelated untracked file; use
explicit-path staging only.
