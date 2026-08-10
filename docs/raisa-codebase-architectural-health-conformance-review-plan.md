# Raisa codebase architectural-health and conformance review plan

Date: 2026-08-11

Source HEAD: `95ce6b75723d57e672858619c3621d4a273c1f34`

## Purpose

Perform one bounded, repository-local, read-only pulse over the architecture
that has accumulated through the Reception One, shared authentication,
Bernie/Davida, model-required Bureau and Practice Context Fabric tranches. The
review asks whether the parts still form one coherent Raisa system and where
small preventive controls should be installed before further architectural
weight makes correction more expensive.

The review produces findings and proposed fitness functions only. It does not
perform a broad refactor or open any implementation, runtime, provider, data,
deployment or integration gate.

## Authoritative inputs

- `AGENTS.md`, including Current Baton, authority allocation, protected
  evidence and user-decision boundaries;
- `implementation_plan.md`;
- the accepted Context Fabric durability behavior/transaction closeout and Sol
  acceptance;
- `orchestration/api_spine_adr.md` and
  `orchestration/api_spine_programme.md`;
- current tracked source under `app/`, current API Spine contracts under
  `docs/api-spine/`, repository verification entry points and GitHub workflow
  definitions;
- the current Continuity graph and Compass map; and
- Hypatia's completed user-requested research on architectural-review value and
  cadence.

Protected holdouts, protected authoring/support surfaces and raw historical
diary material are not inputs and must not be enumerated, opened or searched.

## Review taxonomy

Every material component is classified as one of:

1. `mounted_current`: imported by the ordinary application or published client
   path and available under its existing default/feature posture;
2. `mounted_default_off`: mounted but inert unless the accepted default-off
   feature or authenticated path is explicitly selected;
3. `accepted_unmounted`: independently accepted architecture, contract,
   component or rehearsal that ordinary application composition does not mount;
4. `future_planned`: recorded direction or unopened gate without an accepted
   executable product path; or
5. `retired_historical`: superseded implementation direction retained only for
   provenance.

Acceptance evidence must not be relabelled as mounted product capability.

## Review questions

### System composition

- Do the ordinary FastAPI, GraphQL, native Diary and Office composition roots
  make current capability visible without accidentally mounting accepted-only
  descendants?
- Are large modules, duplicated adapters or cross-file invariants creating
  change-amplification risk?
- Do the master plan, live baton, Compass and source composition agree about
  what is current and what is next?

### API Spine and authority

- Does mounted GraphQL remain scoped and read-only with no provider, command or
  write authority?
- Do state-changing or external effects remain explicit REST/OpenAPI commands
  with practice scope, authorization, confirmation where required,
  idempotency, audit and deterministic readback?
- Do events remain committed signals that require a fresh authorised read and
  never become commands or truth?
- Do YAML and Context Fabric artifacts declare posture while typed backend code
  owns enforcement?

### Transactions and durability

- Are transaction ownership, commit/rollback, outbox/event publication,
  idempotency and readback responsibilities recognisable at the service and
  route boundaries?
- Does the accepted disposable PostgreSQL evidence remain correctly bounded
  from unapplied migration and ordinary runtime wiring?

### Verification topology

- Which architectural properties are mechanically checked today?
- Which important properties depend on prose, local sprint packets or manually
  selected tests?
- Do default pull-request workflows exercise ordinary Python correctness in
  addition to security scanning?

## Evidence methods

- tracked-file-only static inventory and source tracing;
- exact application composition and route inspection without starting a
  server, database, browser or provider;
- targeted deterministic tests already authorised by the repository;
- API Spine artifact validation, GraphQL schema inspection, repository
  verification-profile inspection and Git diff/ref checks; and
- line-addressable findings with explicit confidence and consequence.

No database migration, Docker container, external provider, product data,
patient/clinical data, browser runtime, networked service or deployment is
used.

## Severity and decision rule

- `P0`: present cross-tenant, clinical-safety, protected-evidence or destructive
  path requiring an immediate stop;
- `P1`: mounted authority or transaction-boundary defect with plausible serious
  consequence;
- `P2`: architectural drift or verification gap likely to produce future
  defects or materially impede safe change;
- `P3`: maintainability/documentation weakness with bounded current consequence;
  and
- `observation`: healthy property or longer-horizon improvement without a
  current defect.

The review may recommend a narrow corrective descendant, but it cannot apply
that correction. A finding is not authority to open a closed gate.

## Required outputs

1. an as-built state map covering composition roots and the principal
   Reception One, Bureau, Context Fabric and API Spine surfaces;
2. prioritised findings with exact file/line evidence;
3. a critical-path trace for reads, commands, committed events, model/context
   boundaries and the accepted durability slice;
4. a proposed small set of repository-owned architectural fitness functions;
5. a sustainable review cadence; and
6. a dual lay/technical closeout message in Yuri's repository mailbox.

## Acceptance

The tranche passes when the required outputs are internally consistent,
targeted deterministic checks pass or any failure is reported accurately, all
findings preserve evidence and authority boundaries, no code refactor or gate
opening occurs, and protected refs plus unrelated untracked files remain
unchanged.

The next planned construction sequence remains the Agent Execution Surface and
Containment Gate unless this review finds a P0/P1 condition that must be
resolved first.
