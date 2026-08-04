# EMR4 model-required Bureau provider-free successor lanes

Date: 2026-08-04

Status: A1/A2, B1/B2, C1/C2 and dependency-open D1/D2 architecture/test
candidate; provider-free and non-executing

Source HEAD: `ef6d0e20d4fabaa922d95ce96853bacda7b50603`

Parent: `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`

## Decision

This tranche specializes the accepted Gate-zero contract without opening a
product or provider runtime. It freezes four closed, repository-local contract
families:

- Rayleen waiting-room context, deterministic projections, intent grammar and
  authored-synthetic proof fixtures (A1/A2);
- Davida practice-administration intent grammar and authored-synthetic proof
  fixtures (B1/B2);
- controlled-recovery technical anatomy/provenance and diagnostic candidate
  proofreading (C1/C2); and
- update-class separation plus signed provenance and semantic-delta proof
  (D1/D2), opened only because C1 freezes the shared observation vocabulary.

Every language case contains an authored-synthetic candidate so deterministic
evaluation can prove schema, grounding and policy behavior. It does not claim
that provider-free code performed intelligent natural-language interpretation.
An eventual named intelligent path still requires an admitted provider model.

## A1: WaitingRoomContextFrame and projections

`WaitingRoomContextFrame` is a minimized, practice-scoped, location-bounded,
revision- and expiry-bound read frame. Backend facts are separated from derived
display signals. The frame permits only operational identifiers/labels,
appointment state, scheduled and arrival time, waiting-area placement and
practitioner/location membership. It excludes demographics, contacts, national
identifiers, clinical text, notes and unrestricted history.

Deterministic projection kinds are closed to `current_arrivals`,
`waiting_state`, `waiting_area_group`, `practitioner_group`, `threshold_band`,
`longest_wait`, `flow_exception` and `selected_focus`. A projection may narrow
the authorized set; it cannot broaden practice, location, reader or freshness
scope. Elapsed wait and threshold bands are derived by typed code from backend
timestamps and policy, never supplied as authoritative model facts.

The future product read belongs in a named practice-scoped GraphQL read/context
field or an existing authorized REST read. A1 mounts no route and performs no
read. Events remain committed hints requiring a fresh authorized read.

## A2: Rayleen grammar and proof fixtures

Rayleen's grammar contains `read`, `explain`, `filter`, `group`, `focus`,
`clarify`, `check_in_proposal`, `status_proposal`,
`waiting_area_move_proposal` and `refuse`. The three proposal intents reuse the
shared Diary `check_in`, `status_change` and `waiting_area_move` action grammar.
They never become private Rayleen commands and never imply confirmation.

The evaluator reports linguistic candidate matching separately from projection
grounding, identity ambiguity, freshness/conflict, proposal/confirmation
separation and safe refusal. Stale context, ambiguous identity, cross-scope
references, direct-confirmation language and clinical content fail closed.

## B1/B2: Davida grammar and proof fixtures

Davida's grammar contains `read`, `explain`, `summarize`, `compare`, `validate`,
`dry_run`, `propose`, `clarify` and `refuse`. Initial resources are active
practitioners and locations only. The grammar has no patient or appointment
assumption and cannot convert `propose` into `confirm` or `administer`.

Authored-synthetic cases cover incomplete names, cross-location requests,
inactive resources, stale context, security-relevant changes, bulk wording,
negation, correction and attempts to delegate confirmation. Evaluation keeps
candidate interpretation, deterministic grounding and policy decisions as
three distinct results. Existing context-desk, advisory and dry-run contracts
remain authoritative; this tranche does not call or mutate them.

## C1: Technical anatomy and provenance vocabulary

The shared technical observation vocabulary is now frozen. A
`TechnicalAnatomyFrame` is version-bound and may contain only:

- service and component versions;
- deployment-manifest references and hashes;
- database schema head;
- dependency state;
- health and capacity signals;
- sanitized error classes;
- backup verification;
- configuration drift; and
- signed runbook-catalog references.

Every observation carries a stable identifier, source identity, collector id
and version, observation and expiry time, freshness, confidence class,
authorization decision, sanitization class and content digest. Credentials,
secrets, unrestricted logs, raw patient/clinical data and generic database
introspection are structurally forbidden. This exact vocabulary is the C1
dependency that opens D1/D2; it grants no collector or live read runtime.

## C2: Diagnostic candidate and deterministic proofreader

A `TechnicalDiagnosisCandidate` contains hypotheses, evidence links, missing
evidence, likely impact, urgency, an optional signed-catalog runbook candidate
and a bounded operator explanation. The deterministic proofreader rejects an
unsupported hypothesis, unknown evidence, stale anatomy version, unknown
runbook, empty missing-evidence disclosure where support is incomplete, and any
shell, SQL, URL, command, executable or success-claim field. Admission releases
only a read-only diagnosis candidate; it creates no plan authority or actuator.

## D1/D2: Update classes, provenance and semantic delta

Application/dependency builds, database migrations, reference datasets and
operational/clinical policy content use distinct contract and future command
families. No generic update command exists.

Every source manifest binds source identity, licence, SHA-256 checksum, schema
version, jurisdiction, issued/effective/expiry timestamps, supersession and
withdrawal state. Deterministic validation must produce a typed semantic delta,
compatibility decision and rollback candidate before a future provider explains
the change or forms an activation proposal. Download, licence acceptance,
import, migration, activation, deployment and production remain closed.

## API Spine and authority boundary

- GraphQL is scoped read/context only and has no mutation or provider field.
- State-changing, provider and external operations remain single-purpose
  REST/OpenAPI commands with actor, practice/environment scope, correlation,
  idempotency, freshness, confirmation/dual-review, audit and readback.
- Events are committed hints and manifests are declarative inputs, never
  command authority.
- Access AI remains closed. No prompt or response is transmitted or persisted.

## Evidence and closed gates

The only evidence label is
`provider_free_successor_lane_architecture_and_proof`. Provider calls, external
prompts, patient or product-derived data, live reads, runtime wiring, commands,
writes, actuators, shell/SQL/cloud/IAM, migrations, update activation,
deployment, production, release, Pages, protected refs and protected evidence
remain zero and closed. `docs/branding/` remains excluded.
