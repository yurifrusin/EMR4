# Closeout: Davida default-location proposal-to-confirm command boundary

Date: 2026-08-03

Worker result: `candidate_ready`

Candidate architecture result:
`davida_practice_administration_default_location_command_boundary_pass`

Acceptance owner: GPT Sol

## Candidate result

A separate documentation-only OpenAPI artifact now freezes one future
backend-owned practitioner default-location proposal-to-confirm boundary. The
proposal is a non-mutating deterministic re-evaluation and returns a signed
self-contained opaque proposal reference with no proposal store. Practice,
actor and role authority comes only from the authenticated application session;
body values are exact-match binding assertions.

Only the proposed future contract roles `practice_manager` and
`practice_owner` may confirm. That role list is not a claim about current
permission-matrix runtime grants. Davida remains proposal-only and cannot mint
confirmation evidence, confirm, call or apply the command. The confirmation
request carries only an opaque backend-issued server-held one-use evidence
reference.

The future confirmation contract defines expected aggregate version and
before-state revalidation; durable scoped idempotency; exact safe-retry,
idempotency-conflict and cross-key evidence-replay behavior; and one atomic
confirmation unit covering evidence consumption, idempotency, aggregate change,
version increment, immutable audit, transactional outbox and bounded receipt.
All members roll back together and outbox publication is after commit only.

## API-steward checklist

- Boundary: REST/OpenAPI command plane; GraphQL remains read-only and unchanged.
- Proposal: typed, practice-scoped, non-mutating, expiring, deterministic and
  non-reserving.
- Confirmation: authenticated human, current practice/action/resource
  authorization, reauthorization before write, expected version, durable
  idempotency and closed receipt/rejection schemas.
- Audit/event: immutable audit and transactional outbox are in the same future
  transaction; events publish only after commit and never carry authority.
- Manifests: unchanged and declarative only.
- Closed gates: no route, runtime, provider, database, GraphQL mutation,
  arbitrary API, real data, deployment or release gate opened.

No blocking API-steward finding remains in the candidate.

## Verification

- 31/31 focused architecture tests passed in the root-granted serial slot.
- 36/36 API Spine artifact tests passed serially afterward.
- Ruff, JSON/YAML parsing and exact-path `git diff --check` passed.
- The earlier concurrent rerun is explicitly inadmissible and preserved at
  `orchestration/agent_inbox/codex/davida-default-location-command-boundary-pytest-collision-receipt.json`;
  the clean serialized replacement supersedes it for candidate verification.

## Unresolved implementation risks and gates

The following are intentionally unresolved because implementation is not
authorized: proposal-reference signing-key lifecycle; server-held confirmation
evidence schema/retention; authorization policy/runtime integration; durable
idempotency schema/retention; transaction isolation and locks; practitioner
aggregate version migration; append-only audit schema; transactional outbox and
dispatcher; rate limiting and anti-enumeration operation; and error/receipt HTTP
implementation.

Actual command implementation, any current permission grant, database migration
or administrative apply/write authority remains a material Yuri-owned gate.
Provider/model, memory/RAG, real identity/data, patient/clinical/document data,
arbitrary API access, cloud/IAM, deployment, production, release, protected
evidence/refs and `docs/branding/` remain closed.
