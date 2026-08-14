# Reception One multi-change request atomicity orientation plan

Date: 2026-08-14

Timestamp: 2026-08-14T19:45:27+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_read_only_orientation`

Task baseline: `f362f0de378fdddb610a04ae61182aaae2c105c0`

Target result: `raisa_reception_one_multi_change_request_atomicity_orientation_pass`

Reasoning level: Extra High. This tranche freezes action vocabulary, atomicity
meaning and the future authority boundary between Raisa, human projections,
channel adapters and the backend command plane. It changes no runtime.

## Objective

Map the exact existing appointment update and status proposal/confirm contracts,
then select the narrowest safe semantics for a request containing more than one
change. Preserve the compact console's four-action vocabulary while making
clear that visible buttons are human presentation affordances, not provider-
model actuators.

Raisa and future email, SMS, voice or chatbot adapters may eventually nominate
typed inert action candidates. They may not click the UI, manufacture current
truth, confirm a mutation, call a write route or inherit the authority of the
human or application session that receives their words.

## Exact current contract to map

- `AppointmentUpdateProposalIn` accepts a closed optional patch containing
  several update-family fields.
- `propose_update_appointment` merges supplied fields over current appointment
  truth, checks the combined result and emits one full update command with
  signed freshness evidence without mutating.
- `confirm_update_proposal_route` serializes the appointment, rechecks current
  truth and signed evidence, recomputes the same full proposal, requires an
  exact command match and applies one update inside one command transaction.
- The current Reception One time, duration and practitioner controls each send
  one field through that shared update family; their UI does not yet compose a
  multi-field patch.
- Status uses a distinct status proposal/confirm family and cannot be described
  as atomic with an update-family change under the current contract.

This mapping is a factual orientation target, not a new API claim. Existing
tests must determine exactly which multi-field combinations and transaction
properties are already evidenced and which remain only structurally present.

## Frozen candidate semantics

1. A channel or provider interpretation produces only a typed, inert
   `AppointmentActionCandidate`; it is never a command or a confirmation.
2. Each candidate field belongs to exactly one backend command family:
   `status` or `update`.
3. A non-contradictory subset of `time`, `duration` and `practitioner` belongs
   to the existing update family and may be represented as one proposed patch,
   one review packet and one explicit confirmation. It must not be decomposed
   into an automatic sequence of single-field writes.
4. `status` remains the status family. A request combining status with any
   update-family field is `cross_family` and has no current atomic command.
5. A cross-family candidate may be displayed as a non-executable review plan,
   but the system must neither run it automatically nor imply rollback across
   its parts. If staff chooses separate actions, each is newly proposed and
   explicitly confirmed against fresh truth after the preceding result.
6. Contradictory values for one field, ambiguous targets, unsupported fields or
   missing authority produce clarification or a typed block, never precedence
   guessing.
7. A future complex button is a typed presentation macro over admitted action
   meaning. It receives no direct route, tool or write authority. Any future
   all-or-nothing cross-family button requires a separately designed and proven
   kernel-owned atomic command.
8. Human-visible confirmation remains mandatory. Adapter authentication,
   patient recognition and channel possession are separate future gates and do
   not themselves confer confirmation authority.

## Authorised surface

This tranche may add only:

- this plan;
- one read-only architecture and one threat-model delta;
- one closed typed architecture contract, schema and authored-synthetic
  examples;
- deterministic architecture, source-map and continuity tests;
- native read-only analyses, one Gemini review packet/receipt, Ariadne receipts,
  acceptance, continuity and closeout artifacts.

All product code, `docs/diary/**`, `app/**`, database/migrations, GraphQL,
OpenAPI, async/event contracts and manifests are read-only evidence.

## API Spine classification

- Candidate interpretation: typed non-authoritative context/proposal input.
- Rich current-state display: GraphQL or existing authorised reads only.
- Appointment mutation: explicit REST/OpenAPI proposal and confirm command.
- Committed change cue: event hint only, followed by a fresh authorised read.
- Adapter manifest: declarative policy only, never executable authority.

The architecture must retain practice scope, actor and confirmer distinction,
idempotency, signed evidence, current-source revalidation, audit and default
denial. No GraphQL mutation or model-to-database path is admissible.

## Acceptance matrix

The tranche passes only if repository-local evidence proves:

1. the exact closed update patch, full-command proposal and confirm-time
   revalidation path are mapped to source and tests;
2. evidenced existing multi-field atomic behavior is distinguished from merely
   structural support or a future UI claim;
3. status and update are classified as distinct command families;
4. same-update-family candidate composition is one proposal/confirmation, not
   several automatic writes;
5. cross-family candidates are non-executable and disclose the absence of
   all-or-nothing semantics;
6. provider output, Siri-like chatbot output, email, SMS and voice transports
   remain typed candidate inputs with no DOM, confirmation, route or write
   authority;
7. human action, authenticated principal, confirmer, current truth and command
   execution remain distinct facts;
8. contradictions, ambiguity, stale truth, unsupported fields and interrupted
   multi-step review fail closed;
9. the architecture preserves the four-button console, API Spine, source-owned
   truth, idempotency, audit and event-hint boundaries;
10. source hash guards prove no product/API/database surface changed;
11. focused architecture tests, API Spine invariants, latch/preflight tests,
    Ruff and Git whitespace pass; and
12. one fresh Gemini 3.6 Flash/high exact-candidate veto returns one decision at
    an unchanged clean review worktree.

Evidence is `repository_static_authored_synthetic`. It is not live adapter,
provider, browser, backend, database or usability evidence.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high — declined:** architecture and authority meaning are
  tightly coupled and no stable mechanical implementation package exists. The
  preceding test-only lane also had negative net economy.
- **Native subagents — planned read-only:** one exact update/status source and
  test map; one independent adapter-neutral action-authority and threat/options
  analysis.
- **Gemini 3.6 Flash/high — reserved:** one fresh exact-candidate architecture
  veto after deterministic admission.
- **Sol — serial authority owner:** source reconciliation, architecture
  selection, contract authoring, acceptance, continuity and Git.

Reassess at plan freeze, native return, material architecture revision,
pre-verifier admission and closeout.

## Stop and recovery conditions

Stop or narrow if the result would require a new request field, route, command,
UI behavior, adapter runtime, identity decision, patient/product data, provider
call, database proof, deployment or protected-ref movement. Contradictory source
evidence that changes the selected atomicity meaning requires Sol reconciliation
and a fresh veto before acceptance.

## Closed surfaces

No product implementation, API/OpenAPI/GraphQL/database/migration/RLS,
event/watcher, external patient or chatbot client, voice runtime, identity or
authentication change, provider/ADC, credential/IAM/network, patient/product/
clinical data, historical Diary/PHI, command/write, deployment, production,
release, Pages or protected-ref authority is opened. `docs/branding/` and every
unrelated untracked file remain preserved; staging is explicit-path only.
