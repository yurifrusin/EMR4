# Provider-free unmounted legacy-route convergence and kernel-interface plan

Date: 2026-08-12

Source HEAD: `4af9966928b9d453eed372f158e566185aaad5da`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Define one backend-owned appointment conditional-command interface and map the
four raw create/update/status/delete compatibility writes plus their existing
proposal/confirm replacements onto it. This tranche is a static design and
authored-synthetic contract rehearsal only. It changes no route, client,
database, command or product behavior.

## Boundary classification

This is a REST/OpenAPI command-plane design under the mixed API Spine:

- GraphQL remains read/context only;
- proposal routes prepare evidence and never enter the mutating kernel;
- confirm routes are the preferred mutation ingress;
- raw routes remain visible compatibility surfaces, not trusted bypasses;
- events remain acceleration hints and never enter the command evidence set;
- Context Frames remain non-authoritative; and
- the owning appointment service alone may eventually serialize and commit.

## Frozen interface

The abstract kernel consumes a closed `ConditionalAppointmentCommand` carrying:

- schema version, canonical operation id and command digest;
- practice, actor, session and purpose bindings;
- nullable target appointment plus the applicable conflict domain;
- backend precondition evidence and current-source comparison inputs;
- separate confirmation evidence when policy requires it;
- idempotency identity, canonicalization version and request digest;
- correlation identity and minimized audit attribution; and
- one route-adapter identity that cannot change operation semantics.

It returns exactly one of `committed`, `idempotent_replay`,
`stale_precondition`, `schedule_conflict`, `authority_revoked`,
`confirmation_required`, `validation_rejected` or `idempotency_conflict`.
Only `committed` may describe a first effect. Replay references the original
receipt and never produces a second mutation audit.

## Fail-closed compatibility decision

The current raw routes do not carry a proven backend confirmation artifact,
conditional precondition token or uniformly enforced command idempotency key.
This design therefore records each raw route as `not_kernel_eligible_now`.

No adapter may convert the fact that an authenticated request arrived into
separate confirmation evidence. No same-transaction current read may be called
proof that the user acted on a current view. No route name, HTTP verb, Context
Frame or event may supply missing authority.

This does not change current compatibility behavior. It identifies the exact
controls that a later route-by-route migration must add or avoid by first
moving the consumer to the existing proposal/confirm path.

## Migration order

The contract freezes this dependency order:

1. freeze this static map and pure kernel interface;
2. rehearse pure authored-synthetic route adapters with no application imports;
3. if separately authorised, add default-off non-enforcing shadow comparison;
4. prove ordinary clients use proposal/confirm paths with equivalent outcomes;
5. converge raw status after its confirmation/precondition/idempotency ingress
   is complete;
6. converge raw delete under the same rules and explicit destructive-action
   confirmation;
7. converge raw update with schedule-domain plus appointment serialization;
8. separately select and prove the database-owned create schedule fence;
9. converge raw create only after that fence and all ingress controls pass;
10. consider header-mode deprecation only after all four families converge and
    observability/rollback evidence exists; and
11. retire a raw route only through a separate release gate with all remaining
    system/import/recovery consumers explicitly replaced.

The order goes from single-existing-row mutations to cross-schedule mutations.
Create remains last because it has no target row and its production fence is
not selected by this tranche.

## Owned files

- `docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-plan.md`
- `docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-design.md`
- `docs/security/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/contract.json`
- `orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/contract.schema.json`
- `scripts/raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py`
- `tests/test_raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py`
- exact receipts, register correction, closeout, acceptance, Yuri mailbox,
  Continuity/Compass updater and lifecycle test if the tranche passes.

## Forbidden surfaces

- no import, edit, alias, wrapping or execution of an application route;
- no database, source, watcher, event, migration, model or transaction;
- no live or product-derived payload and no patient, clinical or financial data;
- no provider call, credential, IAM, metadata, network or external worker;
- no executable capability exposed to a Bureau and no command or write;
- no client switch, deprecation-mode change, deployment, production, release,
  Pages rebuild or protected-ref movement; and
- no broad Git staging, `docs/branding/`, protected evidence or unrelated
  untracked file.

## Acceptance

The tranche passes only when:

1. one closed schema validates one exact source-hashed contract;
2. exactly four operation families bind every raw route and all named
   proposal/confirm replacements;
3. proposal routes are non-mutating and confirm routes map to one canonical
   operation per family;
4. all raw routes remain explicitly ineligible for kernel execution today;
5. confirmation, freshness, idempotency and audit remain distinct and all are
   required before a raw adapter becomes eligible;
6. the accepted eight outcomes, authority-first disclosure precedence and
   canonical lock order are exact;
7. create alone requires the schedule-domain fence without a target row;
8. the migration graph is acyclic and no raw route can converge, emit default
   deprecation headers or retire before its dependencies;
9. at least twenty independent hostile mutations fail closed;
10. focused API Spine tests, canonical repository checks and Git whitespace
    pass; and
11. protected refs and all unrelated untracked files remain unchanged.

## Recovery and next work

A mechanical schema, fixture, validator or assertion defect may receive one
bounded correction without changing the frozen interface or migration meaning.
A need to grandfather raw confirmation, weaken current-authority ordering,
change the eight outcomes or select a production create fence is conceptual and
must stop this tranche.

After acceptance, the next safe candidate is the provider-free unmounted pure
route-adapter differential rehearsal. It may transform authored-synthetic raw
and confirm envelopes into the frozen kernel request and prove semantic
equivalence or exact fail-closed gaps, but it still may not import or execute an
application route, database, source, provider, event or command.
