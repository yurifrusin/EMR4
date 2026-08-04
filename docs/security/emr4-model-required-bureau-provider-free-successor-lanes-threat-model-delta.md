# Threat-model delta: provider-free Bureau successor lanes

Date: 2026-08-04

Status: architecture/schema prototypes; provider-free and non-executing

Parent: `docs/security/emr4-model-required-bureau-gate-zero-threat-model-delta.md`

## New assets and boundaries

The new assets are a minimized waiting-room frame, Rayleen and Davida intent
fixtures, a versioned technical-anatomy frame, diagnosis candidates, signed
update provenance and semantic deltas. All remain authored-synthetic repository
artifacts. The Gate-zero model/proof/authority/execution separation remains
unchanged.

## Threats and controls

### Waiting-room context becomes a patient dump

Controls: closed operational fields; practice/location/reader scope; short
expiry; backend-fact and derived-signal separation; no contacts, identifiers,
clinical text, notes or history; projections only narrow an authorized set.

### Rayleen creates a private write vocabulary

Controls: proposal intents map exactly to shared Diary `check_in`,
`status_change` and `waiting_area_move`; candidates have proposal-only
authority; direct confirmation and mutation wording is refused; future writes
remain backend-owned REST/OpenAPI commands.

### Davida turns harmless wording into administrative authority

Controls: active practitioner/location resources only; interpretation,
grounding and policy results remain separate; inactive, stale, cross-location,
bulk, negated and delegated-confirmation cases fail closed; `propose` never
means `confirm` or `administer`.

### Technical observations leak secrets or clinical data

Controls: closed observation kinds and value shapes; source/collector/time/
freshness/confidence/authorization/sanitization/digest required per item;
credential, secret, unrestricted-log, patient/clinical and generic database
introspection fields are forbidden.

### Diagnostic prose becomes executable recovery

Controls: evidence ids must exist in the bound fresh anatomy frame; runbook ids
must exist in its signed catalog; unsupported hypotheses reject; strings are
data; shell, SQL, URLs, command fields, executable instructions and success
claims reject; no actuator exists.

### Update classes collapse into one privileged path

Controls: four distinct classes and future command families; generic update is
forbidden; source identity, licence, checksum, jurisdiction and lifecycle
metadata are mandatory; semantic delta, compatibility and rollback are
deterministic prerequisites; activation remains separately closed.

### Provider-free evidence is inflated

Controls: authored candidates are explicitly fixture inputs, provider call and
external prompt counts remain zero, and the claim stops at
`provider_free_successor_lane_architecture_and_proof`.

## Residual closed risks

These schemas do not prove a live read, collector, provider model, proofreader
service, update importer, migration runner or actuator. Product/provider data,
patient-facing Rayleen, command/write authority, recovery execution, external
updates, cloud/IAM, deployment, production, release, Pages, protected refs and
protected evidence remain closed. Any broader field, observation kind, command
family or bridge is a material security fork.
