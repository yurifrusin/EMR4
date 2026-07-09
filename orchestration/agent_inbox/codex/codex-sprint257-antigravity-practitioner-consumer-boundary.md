# codex-sprint257-antigravity-practitioner-consumer-boundary

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint257-practitioner-consumer-boundary` |
| Status | reviewed |
| Created | 2026-07-09 13:40 +1000 |

## Executive Summary

As the Antigravity worker, we performed a comprehensive review of the `GET /api/v1/practice/practitioners` REST endpoint to evaluate its consumer ergonomics, schema designs, pagination behaviors, tenancy isolation, and external-client boundaries.

**Verdict: PASS.** The endpoint design is well-formed, safe, and meets all consumer expectations for an internal staff-facing practitioner directory. It returns only public-facing / display-safe metadata, maintains strict tenancy boundary enforcement, excludes all sensitive fields, and presents zero risk of exposure to external patient-client surfaces. All adjacent scope boundaries (GraphQL resolvers, database writes, provider/AI integrations, H-series/H15 imports) remain fully isolated.

---

## Detailed Findings

### 1. OpenAPI Shape & Response Semantics
* **Resource Route**: `GET /api/v1/practice/practitioners`
* **Response Model**: `list[PractitionerOut]`
* **Schema Fields**:
  * `PractitionerOut`:
    * `id`: `uuid.UUID` (Required)
    * `displayName`: `str` (Required)
    * `roleLabel`: `Optional[str]` (Optional specialty label)
    * `active`: `bool` (Required)
    * `defaultLocation`: `Optional[PractitionerDefaultLocationOut]` (Optional default location metadata)
  * `PractitionerDefaultLocationOut`:
    * `id`: `uuid.UUID` (Required)
    * `name`: `str` (Required)
* **Ergonomics Evaluation**: The schema is clean, minimal, and tailored for simple list rendering (e.g., selection dropdowns, schedule grids). Display name derivation is handled cleanly at the service level, joining and trimming non-empty name parts correctly.

### 2. Query Parameters and Defaults
* **`activeOnly` (boolean, default: `true`)**:
  * Scopes the directory list to active practitioners by default.
  * Role-based access check: Only users with `Admin` or `PracticeOwner` roles can query inactive practitioners (`activeOnly=false`). GPs, Receptionists, and Nurses are rejected with a `403 Forbidden` error when trying to fetch inactive practitioners.
* **`limit` (integer, default: `50`, min: `1`, max: `200`)**:
  * Protects the application from resource exhaustion attacks while allowing flexible batch sizes.
* **`offset` (integer, default: `0`, min: `0`)**:
  * Standard zero-indexed pagination offset.
* **Ergonomics Evaluation**: All pagination and default parameters are enforced via FastAPI's Query validators, returning standard `422 Unprocessable Entity` errors for out-of-bounds parameters (e.g., negative offset or limit > 200).

### 3. Tenancy Isolation & Security
* **Authentication**: Gated behind `get_current_user` dependency (validates JWT and active user status). Inactive users are denied access with `401 Unauthorized`.
* **Tenancy Filtering**: Strict tenancy constraint is enforced via `Practitioner.practice_id == current_user.practice_id`.
* **Location Scope**: Default locations are outerjoined but strictly scoped to the same tenant via `PracticeLocation.practice_id == current_user.practice_id` and must be active (`PracticeLocation.is_active == True`). If a practitioner's default location belongs to another practice or is inactive, it returns `null` in the payload.
* **Deterministic Sorting**: Results are consistently ordered by `last_name.asc()`, `first_name.asc()`, and `Practitioner.id.asc()`, preventing pagination drift.

### 4. Sensitive-Field Isolation and Anti-Enumeration
* **Sensitive Field Exclusion**: Private practitioner details such as:
  * `provider_number`, `prescriber_number`, `ahpra_number`, `hpi_i`
  * `email`, `phone`, physical address details, and password hashes
  are completely absent from `PractitionerOut` and `PractitionerDefaultLocationOut`.
* **No Detail Route / IDOR Surface**: There is no individual detail route (`GET /api/v1/practice/practitioners/{id}`). Requests trying to access individual IDs return standard `404 Not Found` or `405 Method Not Allowed`, preventing direct object reference enumeration or path-based probing.

### 5. External Patient-Client Boundary
* The directory is located under the `/api/v1/practice/` router, which is dedicated to internal clinical practice management.
* No patient-facing endpoints, schemas, or patient client systems consume this endpoint. It remains strictly internal.

### 6. Adjacent Scope Verification
We verified that the implementation does not leak into any adjacent restricted domains:
* **GraphQL**: No SDL modifications or resolver code exists for this route.
* **Providers / AI**: No imports or integrations with Access AI, Gemini, Vertex, or other LLM providers.
* **Historical Diary (H15/H-series)**: No imports of troves, H-series profiles, or synthetic semantic fixtures.
* **Writes**: Read-only query; does not write to the database or create appointment audit logs.
* **Readiness Flags**: The readiness flag `rest_route_ready` in `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json` remains strictly `false`.

---

## Blockers & Go/No-Go Recommendation

* **Blockers**: None. The REST route is ergonomically sound, secure, and ready for internal consumers.
* **Recommendation**: **GO** for first-slice REST readiness.
* **Next Steps**: Pause and await Yuri's explicit approval. Only after approval should a future sprint flip the readiness flag in `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`.
