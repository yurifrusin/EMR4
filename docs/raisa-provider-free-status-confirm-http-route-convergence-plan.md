# Provider-free status-confirm HTTP route convergence plan

Date: 2026-08-13

Timestamp: 2026-08-13T12:24:35+10:00 (Australia/Brisbane)

Status: frozen

Revision: 3

Task HEAD: `43ccca7cf6585724a5a06c795d9ffdffcdd78e39`

Accepted database-integration source: `553d38c37af86ceefc7b4315b8eaa171d405ab95`

Reasoning level: authenticated user-visible write-boundary convergence — Extra High

## Objective

Converge the existing authenticated appointment status-confirm HTTP family
onto the accepted product adapter and disposable-PostgreSQL transaction seam.
The canonical endpoint becomes
`POST /api/v1/appointments/proposals/status/confirm`; the existing
`/api/v1/appointments/proposals/status-confirm` spelling remains mounted as a
compatibility alias over the same handler and no longer owns a write path.

The non-mutating status proposal carries one opaque, server-minted HMAC binding
between its signed evidence and the database-owned appointment generation.
The client may transport that object but receives no authority to select,
increment or replace the generation. Both successful first delivery and
completed-receipt replay return the exact canonical bytes stored by the
accepted physical seam.

This is the last backend seam before visible native Diary status-confirm
wiring. It does not reopen CF-D2: durable event/cue delivery remains a later
observability-first extension because the atomic command already rechecks
current database truth and authority at commit time.

## Frozen source boundary

After this freeze, existing-source reads, imports and hashes are limited to the
following exact non-protected files. Only the files marked `editable` may
change. No repository-wide or directory-wide discovery is permitted.

| Existing source | Posture | SHA-256 |
|---|---|---|
| `app/routers/appointments.py` | editable | `59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb` |
| `app/dependencies.py` | editable | `d44f777f742074f0ee4717d599d7ee71dd6343c7096c87793149c727c1c4b0a9` |
| `app/schemas/appointments.py` | editable | `d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d` |
| `app/services/diary/confirm_actions.py` | editable | `7b37dce383b5f36fa831e6b3221d5cd897bc24bb0c6fd9637b11a7a6bc9b2561` |
| `docs/api-spine/openapi/appointment-commands.yaml` | editable | `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` |
| `tests/test_appointment_status_mutations.py` | narrow compatibility repair permitted | `bdd3c67a53dd3eedbc6ac9c214503972e86c9079bb673ab889b9f6f5b570252b` |
| `tests/test_reason_code_backend.py` | narrow compatibility repair permitted | `16c608d988d95d14c94b55cf3599185e7b36540bcd717f0e1fcf05b0c2d6591c` |
| `tests/conftest.py` | narrow accepted-version-trigger fixture repair permitted | `76346e1858482bdad47ccd6ab3ac570147fcdab45e8c60a0c74c29c3f055dab9` |
| `tests/test_api_spine_appointment_openapi_drift_guard.py` | narrow canonical-alias assertion repair permitted | `635acc3b15819696a8df42de62c02910bb8e8b2d47fa178c0cd2e387133b6cc5` |
| `tests/test_api_spine_openapi_backend_alignment.py` | narrow canonical-alias assertion repair permitted | `75261435b82408143200fbe1f4fe4098b89e0044c0846c671ddd856aa3c85730` |
| `tests/test_api_spine_confirmation_contract_matrix.py` | narrow adapter-mode assertion repair permitted | `4881bde300c6c62a061518aec8a1ddfc5e7b185e0c1cd4f86c490c5fef2c6ef6` |
| `tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py` | narrow required-binding helper repair permitted | `06e540c3dc6d3f4a1f3f8ff41561c473fe1bfa7aa4ddfd44bc143f0869cde4f4` |
| `tests/test_api_spine_appointment_command_alignment_inventory.py` | narrow canonical-route assertion repair permitted | `43f224d63d3f1a34e1ad71d47f42d4acf5223a516adb250a628fbb99e9ae6e75` |
| `tests/test_api_spine_appointment_idempotency_gap.py` | narrow adapter-owned status-confirm assertion repair permitted | `e88ea7107c84423d511916fa6204bbfff1d18b93601e1bc5564eb173ce7a134b` |
| `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` | narrow adapter-owned status-confirm assertion repair permitted | `798f79587c5b884b9467c077eb3ff98d910e6283de0d714e960d1abf7cfa8982` |
| `tests/test_api_spine_appointment_idempotency_route_integration_preflight.py` | narrow adapter-owned status-confirm assertion repair permitted | `fd145d8530e1a52e678c993edab90b9e2870e00bf0ca451af925a407dc21abc0` |
| `tests/test_api_spine_status_confirm_idempotency_preflight.py` | narrow adapter-owned status-confirm assertion repair permitted | `cc5d5c4b3c4dcd081a58b35f1441e5230daa6bc436f36cbdfc2e0e02080d9e1a` |
| `tests/test_api_spine_status_confirm_idempotency_route_contract.py` | narrow canonical adapter contract repair permitted | `0ecc5b2bff0853d3f9797163b979f575f9604c6ba0895cf5bd36c165664eb8af` |
| `tests/test_api_spine_idempotency_audit_metadata.py` | narrow adapter-owned metadata assertion repair permitted | `1667887406e274d788b40f1bfccb19704db462485ce501c8dffc0c212338353f` |
| `tests/test_api_spine_proposal_only_idempotency_preflight.py` | narrow UUID-route assertion repair permitted | `8b8c8961f5cc2fe5c3293aa87f1a58d5b39b977c9f6597fde4ce5a9c9b41d3ce` |
| `tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py` | narrow shared-static status-confirm assertion repair permitted | `ea87d82f8f51cd2d2333676b08a1a1d4c56bece24a63317878de9eb39f243b5e` |
| `orchestration/api_spine_appointment_command_alignment_inventory.md` | editable canonical-alias inventory | `5b97c22ead511a3b72a49fa9fd36a7db2455429185095883d60fcad3e414e818` |
| `app/database.py` | read-only | `2da2b2d584391755a1d9de4e274d59f05dcc24b6b5a3737a35efae49c7f6b117` |
| `app/services/appointment_status_product_adapter.py` | read-only | `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` |
| `app/services/appointment_status_composition.py` | read-only | `42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a` |
| `app/services/appointment_status_physical.py` | read-only | `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` |
| `app/services/bernie_turn_evidence.py` | read-only | `e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467` |
| `app/config.py` | read-only | `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` |
| `app/main.py` | read-only | `0e0f42290688943bc9dd7d5711826acf10430133be0b309eae94bad15da46ca2` |
| accepted PostgreSQL integration rehearsal script | read-only reusable lifecycle helper | `f5af625924cd7287db006014db10df21af0e9dc4fd92475f1ed7bad6ab5b5ffb` |

Protected evidence paths remain excluded and must not be enumerated.

## Exact implementation

1. Add a dependency that returns the configured command-session factory. The
   request authentication session remains request-scoped; the command adapter
   receives a distinct fresh session that it alone closes.
2. Move the signed token's practice context establishment in
   `get_current_user` before the RLS-protected user lookup. The practice comes
   only from the verified JWT; the loaded user's practice must still match it.
3. Derive five domain-separated SHA-256/HMAC keys from the configured backend
   secret for status evidence, proposal generation, authenticated-session
   minimisation, idempotency and stored-session binding. No new environment
   variable, credential store or client-visible secret is introduced.
4. Mint signed status evidence with the status evidence key, then mint the
   opaque proposal-version binding from its signature and the current positive
   `appointment_state_version`. Return both in the proposal and its prepared
   confirmation payload.
5. Require the binding in `AppointmentStatusProposalConfirmationIn`. The
   accepted adapter verifies it before constructing a command session and
   rechecks the same generation under the database lock.
6. Mount the canonical `/proposals/status/confirm` route in generated OpenAPI.
   Retain `/proposals/status-confirm` with `include_in_schema=False` as a
   compatibility alias over the exact same handler. Change the Diary action
   descriptor and newly prepared proposal payloads to the canonical endpoint.
7. Invoke only `compose_product_status_confirm`. Remove the route-local claim,
   evidence, state mutation, audit, receipt and commit implementation.
8. For `committed` and `replay`, return `Response` over the adapter's exact
   `stored_response_bytes`; for typed blocked/error outcomes, return a
   `JSONResponse` with the adapter status and body.
9. Preserve status-only admission. A waiting-area proposal submitted to either
   alias receives the adapter's typed `unsupported_status_confirm_variant`
   block and cannot fall back to the legacy route-local write.

The legacy raw `PATCH /appointments/{appointment_id}/status` compatibility
route and every other command family remain unchanged and outside acceptance.

## Exact owned outputs

- this plan and its threat-model delta;
- the five editable application/API files above;
- one closed route-convergence contract, schema, evidence schema and released
  evidence under the matching continuity directory;
- `scripts/raisa_provider_free_status_confirm_http_route_convergence.py`;
- focused route-convergence, plan and continuity tests;
- only the narrow existing-test repairs needed for canonical endpoint and
  required binding carriage; and
- timestamped closeout, Sol acceptance, Yuri lay/technical summary,
  receipt/state pairs and Continuity/Compass updater/test.

No migration, database model, adapter, composition, physical transaction,
frontend, generated Pages or deployment source may change.

Revision 2 admits only the mechanical predecessor repairs exposed by the first
regression pass: the shared ORM-table test setup must install the already
accepted database-owned adjacent-version function/trigger, and static API
tests/inventory must recognize the canonical route and adapter-owned
idempotency/audit seam. This adds no application behavior or new authority.

Revision 3 records the exact further predecessor tests exposed by the wider
API regression pass. Repairs are limited to carrying the now-required opaque
version binding, recognizing the UUID-qualified proposal route and asserting
that status-confirm idempotency, metadata and mutation ownership reside in the
accepted product adapter. Historical waiting-area route-write expectations
must become explicit unsupported-variant/no-mutation assertions; they may not
restore that closed write path.

## Disposable HTTP/PostgreSQL rehearsal

Reuse the accepted cached `postgres:16-bookworm`, internal-network, no-port,
tmpfs, bounded-resource, fixed-loopback-relay and exact-ID cleanup lifecycle.
Install the accepted scaffold and forced-RLS application-role surface. Run the
real FastAPI route through `TestClient`, overriding only the normal database
and new command-session-factory dependencies with fresh sessions bound to that
owned server. Authentication uses locally minted JWTs for fixed
authored-synthetic users. No provider, browser, external service or product
database is called.

## Frozen serial scenarios

| ID | Required proof |
|---|---|
| `HRC-S01` | authenticated proposal is non-mutating and carries canonical endpoint, signed evidence and one valid opaque database-version binding |
| `HRC-S02` | canonical confirm commits one status mutation, adjacent version, correlated audit and complete v1 receipt and returns the exact stored canonical bytes |
| `HRC-S03` | compatibility alias reaches the same adapter/transaction behavior with no second implementation |
| `HRC-S04` | simulated lost first response followed by same-key retry returns byte-identical HTTP body bytes and no second effect |
| `HRC-S05` | missing/blank/conflicting idempotency keys fail with exact typed status/code and no effect |
| `HRC-S06` | missing, invalid, inactive or non-mutating authentication fails before any effect |
| `HRC-S07` | cross-practice target returns the closed unavailable result with no row disclosure or effect |
| `HRC-S08` | absent, malformed, tampered or stale proposal-version binding fails closed; tamper stops before command-session construction |
| `HRC-S09` | waiting-area proposal submitted to either alias receives `unsupported_status_confirm_variant` and cannot mutate |
| `HRC-S10` | missing or altered required warning acknowledgement blocks the terminal transition atomically |
| `HRC-S11` | forced projection/receipt failure maps to 503 and rolls back appointment, audit and receipt |
| `HRC-S12` | canonical OpenAPI, hidden compatibility alias, dynamic Diary descriptor and unchanged raw compatibility route inventory remain aligned |

## Acceptance

Pass only if all frozen hashes initially match; all twelve scenarios pass;
the canonical and compatibility endpoints share one handler; there is no
route-local write fallback; exact replay HTTP bytes match the stored receipt;
tenant context is transaction-local; all mutations/audit/receipt effects are
atomic; at least 100 hostile contract mutations fail closed; and focused,
API-Spine, authentication, current-lineage, canonical fast-profile, Ruff,
maintained-source compilation, Diary JavaScript, Git whitespace and exact
cleanup checks pass.

Evidence may retain only fixed scenario IDs, decisions/codes, counts, versions,
hashes, endpoint names, containment booleans and cleanup results. It must not
retain JWTs, HMACs, request/response bodies, SQL, connection URLs, passwords,
runtime IDs, synthetic row values or unrestricted database output.

## Claim and recovery boundary

Passing proves only authored-synthetic local HTTP convergence of one existing
status-confirm family over one disposable PostgreSQL 16 server. It does not
prove visible Diary behavior, other appointment commands, durable event/cue
delivery, concurrency beyond the accepted transaction locks, restart,
unknown-commit recovery, performance, deployment or production.

Mechanical failures may receive a narrow evidence-backed repair within these
owned files and scenarios. A need to change the accepted adapter/physical
contract, reopen waiting-area write authority, alter user-visible command
meaning, access product/protected data or choose a deployment/runtime posture
is a material fork and stops.

No patient/clinical or operational product data, provider/ADC, credential/IAM
change, external network, browser automation, filesystem/tool capability,
deployment, production, release, Pages or protected-ref movement is
authorised. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.
