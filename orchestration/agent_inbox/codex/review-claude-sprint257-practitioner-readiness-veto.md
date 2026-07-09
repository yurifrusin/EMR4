# Claude Sprint 257 — Practitioner Directory Readiness/Safety Veto Review

| Item | Value |
|---|---|
| Reviewer | claude (Sonnet 4.6) |
| Sprint | 257 |
| Date | 2026-07-09 |
| Source packet | `orchestration/agent_inbox/claude/claude-sprint257-practitioner-readiness-veto.md` |
| Branch | `claude/current` |
| Target route | `GET /api/v1/practice/practitioners` |
| Readiness flag under review | `rest_route_ready` (currently `false`) |
| Recommendation | **NO-GO** — do not ask Yuri to approve `rest_route_ready=true` at this time |

---

## Recommendation Summary

The implementation is solid and the security dimensions directly tied to the route
(authentication, tenancy, sensitive-field exclusion, anti-enumeration, pagination) are
well-evidenced. However, **five of the thirteen Sprint 255 required criteria are not met
or not documented**, and the approval payload required for the readiness flag flip is
absent. Blocking the readiness flag change now protects the sprint engine from
outrunning its own evidence framework.

---

## Evidence Sources Reviewed

| Source | Sprint | Decision recorded |
|---|---|---|
| `docs/api-spine/practitioner-directory-approved-gate.json` | Yuri 2026-07-08 | `approved_for_rest_route_first_slice` |
| `docs/api-spine/practitioner-directory-post-implementation-readiness-review.json` | 235 | `implemented_rest_slice_reviewed_readiness_blocked` |
| `docs/api-spine/practitioner-directory-runtime-evidence-refresh.json` | 254 | `runtime_evidence_refreshed_readiness_blocked` |
| `docs/api-spine/practitioner-directory-readiness-criteria.json` | 255 | `criteria_defined_readiness_not_approved` |
| `docs/api-spine/practitioner-directory-consumer-contract-check.md` | 256 | `consumer_contract_checked_readiness_blocked` |
| `tests/fixtures/api_spine_practitioner_directory/consumer_contract_report.json` | 256 | OpenAPI introspection snapshot |
| `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json` | — | `rest_route_ready: false` (and all adjacent gates false) |
| `app/routers/practice.py`, `app/schemas/practice.py`, `app/services/practice/practitioner_directory_read.py` | 235 | Direct source read |
| `tests/test_practitioner_directory_route.py` | 254 | 25-test matrix |
| `orchestration/sprint_257_practitioner_directory_worker_readiness_block.md` | 257 | Sprint block plan |

---

## Criteria Mapping (Sprint 255 Required Before `rest_route_ready=true`)

| # | Criterion | Status | Evidence / Gap |
|---|---|---|---|
| 1 | `runtime_test_matrix_passes_in_isolated_run` | ⚠️ PLAUSIBLE | 25 tests exist covering all approved-gate matrix items. No recorded isolated-run pass result in any evidence document. A pass record from `pytest tests/test_practitioner_directory_route.py -q` should be committed before flipping. |
| 2 | `api_spine_artifact_tests_pass` | ⚠️ PLAUSIBLE | `test_route_does_not_change_readiness_snapshot` and source-guard tests exist. No confirmed pass record documented. |
| 3 | `openapi_contract_snapshot_matches_runtime_route` | ⚠️ PARTIAL | Consumer contract report (`consumer_contract_report.json`) records the OpenAPI snapshot. No explicit assertion or test confirming the snapshot was generated from the live running route (i.e., not manually authored). Confidence is high based on the `source: fastapi_openapi_introspection` field, but no committed snapshot-match test exists. |
| 4 | `authn_authz_tenancy_review_current` | ✅ MET | Runtime evidence refresh confirms: `authn_checked`, `invalid_token_checked`, `inactive_user_denied`, all roles can read, inactive scope admin/owner only, `practice_scoping_checked`. Tests: `test_auth_denial_returns_401`, `test_invalid_token_returns_401`, `test_inactive_user_denied`, `test_all_authenticated_roles_can_read_active_directory`, `test_active_only_false_requires_admin_or_practice_owner`, `test_practice_scoping_never_returns_other_practice_practitioners`. |
| 5 | `anti_enumeration_review_current` | ✅ MET | Runtime evidence confirms `anti_enumeration_checked=true`. Tests: `test_no_practitioner_detail_route_or_idor_surface`, `test_no_cross_practice_existence_leak` (also asserts practitioner name and UUID absent from response body). |
| 6 | `sensitive_field_exclusion_review_current` | ✅ MET | Runtime evidence confirms `sensitive_fields_excluded=true`. Test `test_response_excludes_sensitive_practitioner_fields` asserts against a comprehensive `SENSITIVE_KEYS` set (provider_number, prescriber_number, ahpra_number, hpi_i, email, phone, address fields, password_hash, credentials, schedules) and checks that raw sentinel strings are absent from the serialized response. |
| 7 | `pagination_and_error_contract_review_current` | ✅ MET | Runtime evidence confirms `pagination_bounds_checked=true`. Tests: `test_limit_default_and_maximum` (default 50, max 200), `test_invalid_limit_and_offset_return_422`. |
| 8 | `rate_limit_or_deferred_rate_limit_decision_recorded` | ❌ MISSING | No rate-limit decision or deferral decision found in any evidence document reviewed. The approved gate, post-implementation review, runtime evidence refresh, and consumer contract check are all silent on rate limiting. |
| 9 | `deployment_surface_explicitly_named` | ❌ MISSING | No deployment surface named in any evidence document. The approved gate explicitly keeps `deployment_or_production_readiness_allowed: false`. A deployment surface decision (Cloud Run, internal-only, etc.) must be recorded before flipping. |
| 10 | `rls_or_rls_equivalent_gap_recorded` | ❌ MISSING | No RLS gap record found in any practitioner-directory evidence document. AGENTS.md §8 notes that tenancy is enforced by manual `practice_id` filters and that PostgreSQL RLS is the recommended defense-in-depth for this gap. The practitioner directory currently relies solely on the query filter `Practitioner.practice_id == current_user.practice_id`. This gap must be explicitly acknowledged in a practitioner-directory-specific gap document. |
| 11 | `field_encryption_gap_recorded` | ❌ MISSING | No field encryption gap record found. The `Practitioner` model holds `provider_number`, `prescriber_number`, `ahpra_number`, and `hpi_i` in plaintext columns. Whether these require field-level encryption (or whether deferral is accepted) must be explicitly documented before the readiness flag changes. |
| 12 | `external_client_exposure_decision_recorded` | ⚠️ PARTIAL | `external_patient_client_ready: false` is recorded consistently across all artifacts. The consumer contract check explicitly states this check "does not approve external patient-client exposure." However, no decision document specifically states when/how external client access will eventually be opened or whether it is permanently internal-only. A brief external-client scope decision note is needed. |
| 13 | `separate_yuri_approval_payload_exists` | ❌ MISSING | `practitioner-directory-approved-gate.json` records Yuri's approval for the **REST first slice implementation**. It does not constitute approval for setting `rest_route_ready=true`. The criteria require a separate approval payload specifically for the readiness flag flip. The approved gate even explicitly states `readiness_flag_changes_allowed: false`. |

**Score: 4 fully met, 3 partially met/plausible, 5 missing (criteria 8, 9, 10, 11, 13, with 12 borderline).**

---

## Safety Observations

### Positive findings

- The route is read-only; no writes to Practitioner, Appointment, AuditLog, or any
  other table occur on a GET request.
- Sensitive practitioner fields (AHPRA, provider number, prescriber number, HPI-I,
  email, phone, address) are cleanly excluded at the Pydantic schema layer.
  `PractitionerOut` exposes only: `id`, `displayName`, `roleLabel`, `active`,
  `defaultLocation` (id + name only).
- The `inactive_scope` gate correctly restricts `activeOnly=false` to Admin and
  PracticeOwner roles; other roles receive 403 without leaking inactive practitioner names.
- Tenancy isolation is enforced at the query level (`practice_id == current_user.practice_id`).
- No practitioner detail route (`GET /practitioners/{id}`) is present; attempts
  return 404/405 without leaking existence.
- Cross-practice existence leak test (`test_no_cross_practice_existence_leak`) confirms
  that even the practitioner ID and name are absent from responses for other practices.
- No provider, Access AI, RAG, GraphRAG, H15/H-series, or historical diary material
  imports are present in the route or service layer.
- No write side effects; the `test_get_route_does_not_write_database_state` and
  `test_read_does_not_create_appointment_audit_log` tests provide explicit regression
  coverage.
- The blocked readiness snapshot (`blocked_readiness_status.json`) is confirmed `false`
  for all adjacent gates and is covered by `test_route_does_not_change_readiness_snapshot`.

### Concerns / gaps

**RLS gap (criterion 10):** The service relies entirely on `Practitioner.practice_id == current_user.practice_id` as a WHERE clause filter. This is correct and the test matrix covers it, but if a future ORM query bypasses the filter or a new route variant omits it, there is no database-level backstop. This is a known EMR4-wide gap (noted in AGENTS.md). It does not block the route from being _used_, but it must be acknowledged in a practitioner-directory gap record before `rest_route_ready=true`, per criterion 10.

**No isolated test run record:** The 25-test matrix covers every item in the approved gate's `required_runtime_test_matrix`. Confidence is high that they pass. But the criteria require a confirmed isolated run pass, not just the existence of tests. A committed `pytest tests/test_practitioner_directory_route.py -v` output or a CI badge reference is the right artifact.

**`displayName` derivation for edge cases:** `_display_name()` strips whitespace and joins non-empty parts. If both `first_name` and `last_name` are `None` or blank, `displayName` returns an empty string `""`. This is not a security risk but is an ergonomic gap for data-quality edge cases not covered by the existing test matrix.

---

## Adjacent Gates Confirmed False

The following must remain false regardless of any readiness flag change:

| Gate | Current value | Source |
|---|---|---|
| `graphql_resolver_ready` | false | blocked_readiness_status.json, approved-gate.json, all review docs |
| `external_read_model_runtime_ready` | false | blocked_readiness_status.json |
| `runtime_or_memory_ready` | false | blocked_readiness_status.json |
| `provider_or_directory_runtime_ready` | false | blocked_readiness_status.json |
| `write_authority_ready` | false | blocked_readiness_status.json |
| `deployment_ready` | false | blocked_readiness_status.json |
| `production_ready` | false | blocked_readiness_status.json |
| `external_patient_client_ready` | false | blocked_readiness_status.json, consumer contract check |

All adjacent gates are confirmed false and no evidence document reviewed changes any of them.

---

## Explicit Blockers Before `rest_route_ready=true`

1. **Rate-limit or deferred rate-limit decision not recorded.** A practitioner-directory-specific document must either specify a rate-limit plan or explicitly defer it and record the accepted risk.

2. **Deployment surface not explicitly named.** The route must be associated with a named deployment surface (e.g., Cloud Run internal endpoint, internal-only VPC, specific ingress rule). No such record exists.

3. **RLS or RLS-equivalent gap not recorded.** A practitioner-directory-specific gap acknowledgment must state that the route currently relies on application-layer tenancy filtering rather than PostgreSQL RLS, and record whether RLS will be added before or after the readiness flag.

4. **Field encryption gap not recorded.** The Practitioner model holds sensitive identifiers (AHPRA, provider number, prescriber number, HPI-I) unencrypted. Even though these fields are excluded from the API response, the gap must be explicitly documented.

5. **Separate Yuri approval payload for `rest_route_ready=true` does not exist.** The existing gate approves the implementation slice, not the readiness flag flip. A new approval payload shaped per `approval_packet_shape` in the criteria document must be created and approved before the flag is changed.

---

## Non-blocking Recommendations (for the next sprint)

- Commit a recorded pytest isolated-run result for the 25-test matrix.
- Add an explicit snapshot-match test asserting the `consumer_contract_report.json`
  was generated from the live FastAPI OpenAPI schema (or add a generation step to CI).
- Add an external-client scope decision record (even if just one sentence confirming
  permanent internal-only access for this route).
- Add a test for the `displayName=""` edge case (both name parts blank).

---

## What to Do in the Next Sprint

If Ariadne agrees with this no-go:

1. Create a **blocker-closure sprint** with four narrow deliverables:
   - a rate-limit/deferred-rate-limit decision note for this route
   - a deployment surface naming record
   - an RLS gap acknowledgment record (practitioner-directory-scoped)
   - a field encryption gap acknowledgment record (practitioner-directory-scoped)
2. After those four documents exist, create the **separate Yuri approval payload** for `rest_route_ready=true` (shaped per `approval_packet_shape` in the criteria JSON).
3. Only after Yuri signs the separate payload should a later sprint flip `rest_route_ready` in `blocked_readiness_status.json` and verify all adjacent gates remain false.

---

## Files Changed in This Review

None. This is a read-only review artifact. No route code, schemas, services, tests,
fixtures, readiness flags, or deployment config were modified.

## Verification Run

```
git status --short --branch
# On branch claude/current, nothing to commit
```

Static review only per task specification. No tests run.

## Remaining Risks

- If Ariadne and DeepSeek reviewers surface additional blockers not visible in the source
  files reviewed here (e.g., a route variant, a SDL stub, or an import I missed), those
  should be treated as additive blockers.
- The "separate Yuri approval payload" requirement is the hardest gate to skip: even if
  all four documentation gaps are closed, the readiness flip must wait for a new Yuri
  approval payload targeting `rest_route_ready=true` specifically.
