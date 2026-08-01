# Threat model delta: Reception One Word compact companion shell

Date: 2026-07-31

Status: `accepted_closed`

Parent boundaries:

- Reception One integrated Bureau baseline;
- Bureau post-admission runtime hardening;
- Word Hybrid contextual launch; and
- EMR4 API Spine read/context and command separation.

## Assets

- Office session token already used by the native Diary dialog;
- authored-synthetic companion request;
- zero-authority launch context;
- deterministic native Diary projection;
- generic returned summary; and
- request/correlation freshness bindings.

## New trust edges

1. Word taskpane to native Diary: one separately typed request after the
   existing auth and zero-authority launch messages.
2. Native Diary to Word taskpane: one separately typed generic status summary.

Neither edge is a backend command, provider invocation, patient-context grant,
appointment-context grant or write grant.

## Threats and controls

### Request smuggled into launch or authentication

Threat: free text or authority fields are placed in the launch context, auth
message or dialog URL.

Controls:

- retain the unchanged closed launch schema;
- retain a separate auth message;
- use a separately closed request schema;
- permit only the non-sensitive local capability marker in the dialog URL; and
- test that request text, correlation, names and token are absent from the URL.

### Word patient file silently becomes request context

Threat: the open Word document or loaded patient banner is treated as verified
patient identity for the Diary request.

Controls:

- request contract sets patient-context and appointment-context authority
  false;
- taskpane request construction reads neither `currentPatient` nor document
  content;
- no patient identifier or appointment identifier field exists; and
- detailed identity resolution remains inside the existing native Diary
  projection.

### Cross-message confusion or replay

Threat: a request is paired with the wrong launch, date or response.

Controls:

- exact correlation id and reference-date equality;
- fresh cryptographic request id;
- native single-consumption set;
- date navigation completion awaited before request execution; and
- Word accepts a summary only for its pending request/correlation pair.

### Untrusted detail returned to Word

Threat: the Diary sends names, request text, appointment records, raw draft,
provider text or arbitrary status copy to Word.

Controls:

- closed summary schema with no free-text field;
- locally generated Word copy from allowlisted summary codes;
- explicit false detail-release flags;
- exact key validation in both windows; and
- tests for unknown, sensitive and authoritative field rejection.

### Stale or malformed projection described as ready

Threat: Word says work is ready when the native projection is stale, blocked,
unsupported or carries command authority.

Controls:

- native deterministic summary proofreader;
- exact allowed family/state pairings;
- `freshness.stale === false`;
- zero command and appointment-write authority;
- `human_gate` for clarification and `edge_abort` for blocked/malformed
  results; and
- no unverified draft release.

### Capability accidentally enabled outside development

Threat: the authored-synthetic shell becomes available in hosted or production
Word.

Controls:

- hidden by default;
- taskpane enablement requires loopback plus the exact query capability;
- native acceptance requires loopback plus the same capability;
- provider and backend paths remain absent; and
- source/published parity tests preserve the same fail-closed gate.

### Provider or command escalation

Threat: companion text reaches a provider or write endpoint.

Controls:

- fixed deterministic planner mode;
- provider authority and command authority false in both schemas;
- no Access AI/provider client or command route added;
- network acceptance blocks unexpected external hosts; and
- evidence requires zero provider calls, credential reads, database writes and
  appointment commands.

## Protected evidence boundary

Protected holdout fixture paths, historical Diary material, real or
product-derived patient/health/clinical data, raw provider material,
credentials and hidden reasoning remain excluded. Only explicit current files
and authored-synthetic examples may be used.

## Residual risk

The browser harness stubs Office dialog transport and local Diary reads. It
cannot prove authenticated Word Online dialog behavior or live backend
authorization. Natural-language fixtures can resemble real receptionist
utterances; their synthetic status is an evidence classification, not a
content detector. A later live or real-data increment must introduce backend
entitlement, audit, tenancy, privacy and data-classification controls rather
than relying on this local shell.
