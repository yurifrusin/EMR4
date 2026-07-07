# review-deepseek-sprint152-create-proposal-minlength-readiness

| Item | Value |
|---|---|
| Source Task | Sprint 152 client-readiness decision for create-proposal Idempotency-Key `minLength: 8` runtime enforcement |
| Reviewer | DeepSeek Flash adversarial lane |
| Files Inspected | `app/routers/appointments.py` (lines 1031-1041), `docs/api-spine/openapi/appointment-commands.yaml`, `orchestration/api_spine_appointment_idempotency_create_proposal_header_alignment.md`, `orchestration/api_spine_appointment_idempotency_proposal_only_preflight.md`, `orchestration/api_spine_appointment_idempotency_create_proposal_replay_model.md`, `tests/test_api_spine_create_proposal_header_alignment.py`, `tests/test_api_spine_create_proposal_idempotency_route_contract.py`, `tests/test_api_spine_appointment_openapi_drift_guard.py`, `orchestration/sprint_closeout.md`, `orchestration/phase_programmes.md`, `orchestration/protocol_alerts.md`, `AGENTS.md` |
| Commands Run | `rg -n` static-search over OpenAPI/FastAPI for `IdempotencyKey`, `proposeAppointment*`, `propose_*` route definitions, `minLength`, and companion test imports; `Get-Content` inspection of all documents listed above |
| Status | Integrated by Ariadne |

## Verdict

**Safer Sprint 152 outcome: defer-with-guard, not enforce-now.**

Enforcing `minLength: 8` on create-proposal alone creates wider API-spine
inconsistency than it closes, adds a new untested error code surface, and
requires client-side error handling for a route that has no known HTTP client
consumers yet. The current guard tests are sound; the preconditions for
enforcement need tightening before the decision resets.

## Concrete Client-Compatibility Risks

### 1. The other 3 proposal routes have zero Idempotency-Key enforcement

The OpenAPI spec declares `Idempotency-Key: required, minLength: 8` on **all
four** proposal operations (`proposeAppointmentCreate`, `proposeAppointmentUpdate`,
`proposeAppointmentStatus`, `proposeAppointmentDelete`). FastAPI only binds the
header on `propose_create_appointment`. The remaining three routes
(`propose_update_appointment`, `propose_status_update`,
`propose_delete_appointment`) have **no** header binding at all — they accept
requests with or without the key.

If create-proposal enforces `minLength: 8` now, a client that sends a 7-char
key gets `400` on create-proposal but `200` on update/status/delete proposals
with the same key. That asymmetry is documented in `x-emr4-proposal-header-posture`,
but a general-purpose API client or generated SDK that reads the OpenAPI
component definition and applies uniform validation would break on the create
route alone.

### 2. No proven external HTTP clients exist

There is no mobile app, third-party PMS, patient portal, or generated SDK that
has been tested against any proposal route. The "client readiness" trigger
defined in Sprint 149 (`all intended clients can send a non-blank key`) has no
specific event, deadline, or test protocol attached. This creates a perpetual
deferral risk where the decision never comes because "readiness" is unmeasured.

### 3. New error code and client-handler surface

The current normalizer returns `idempotency_key_required` for missing or blank
keys. Enforcing `minLength: 8` requires a second error code (e.g.,
`idempotency_key_too_short`). This means:

- The normalizer must report distinct codes for "key absent" vs "key too short",
  because a missing-key rejection is a different client bug than a short-key
  rejection.
- Clients need distinct error handling paths for both codes.
- The separation between `strip()` normalization and raw-header length must be
  defined: should `"  abc  "` (7 raw chars, 3 normalized) be rejected? This
  ambiguity is not yet resolved.

### 4. Precedent for the other 3 proposal routes

Enforcing on create-proposal now hardens a precedent that affects the remaining
proposal routes. The Sprint 151 guard explicitly recorded that update/status/
delete proposal idempotency remains out of scope. But if the programme's next
move is update-proposal header enforcement, the decision must either apply
uniformly (same `minLength: 8`, same error codes, same `x-emr4-proposal-header-posture`)
or explain why create-proposal requires 8-char keys but update-proposal doesn't.

## API-Spine Risks

### OpenAPI-runtime drift on non-create routes

The `test_api_spine_appointment_openapi_drift_guard.py` inventory lists the 4
canonical OpenAPI proposal paths (`/appointments/proposals/create`,
`/appointments/proposals/update`, `/appointments/proposals/status`,
`/appointments/proposals/delete`). It does not check per-operation header
alignment — only that the path set matches. So the existing drift guard would
not catch a scenario where create-proposal has `minLength: 8` enforcement and
the others accept bare requests.

**Recommendation before any enforcement:** Add a per-operation header-contract
guard to the drift test or the header alignment test that asserts each OpenAPI
proposal operation with `IdempotencyKey: required, minLength: 8` also has a
FastAPI `Header` binding with `minLength: 8` enforcement, or an explicit
`x-emr4-proposal-header-posture` annotation recording the deferral.

### 5-char correlation asymmetry

The OpenAPI `CorrelationId` parameter has `minLength: 8` (optional). If a client
sends a 3-char correlation ID with a compliant 8-char idempotency key, the
create-proposal route would accept it despite the spec contradiction. This is
a minor separate issue but adds noise to the enforcement surface.

## Test/Run Recommendations for Ariadne

### Existing guard tests to run first

```powershell
.venv\Scripts\python.exe -m pytest `
  tests/test_api_spine_create_proposal_header_alignment.py `
  tests/test_api_spine_create_proposal_idempotency_route_contract.py `
  tests/test_api_spine_appointment_openapi_drift_guard.py `
  tests/test_api_spine_create_proposal_replay_model_decision.py `
  tests/test_phase_programmes_current_checkpoint.py `
  tests/test_sprint_closeout_protocol.py -q
```

These should all pass. They prove the current deferral guard works.

### New tests to add before enforcement

If the decision is "defer-with-guard", add:

1. **`test_openapi_shared_idempotency_key_referenced_on_all_proposal_routes`**
   in `test_api_spine_appointment_openapi_drift_guard.py`:
   Assert that OpenAPI `proposeAppointmentCreate`, `proposeAppointmentUpdate`,
   `proposeAppointmentStatus`, and `proposeAppointmentDelete` all reference
   `#/components/parameters/IdempotencyKey`. This documents the shared commitment
   and catches accidental spec drift.

2. **`test_fastapi_header_binding_gap_documented`** in
   `test_api_spine_create_proposal_header_alignment.py`:
   Assert that `propose_update_appointment`, `propose_status_update`, and
   `propose_delete_appointment` do NOT have `Idempotency-Key` header bindings,
   and that this gap is recorded in the alignment document. This prevents someone
   from silently adding a header binding to one route without documenting the
   asymmetry.

3. **Client-readiness precondition check** in the header alignment doc: define
   concrete preconditions such as:
   - A specific test client (e.g., `tests/test_client_readiness_proposal_headers.py`)
     that sends keys of every length from `1..8` on all 4 proposal routes.
   - A documented client event (e.g., "after the first deployment that includes
     the Appointments SPA create-proposal dialog" or "after a specific consumer
     SDK version is published and tested").
   - A `minLength: 8` enforcement test that is skipped-by-default (e.g., `pytest.mark.skip(reason="awaiting client-readiness precondition X")`)
     until that precondition is met.

If the decision is "enforce-now", add:

1. A distinct error code (`idempotency_key_too_short`) in `_normalize_create_proposal_idempotency_key`.
2. Updated reaction tests: the one-character-key acceptance test must become a rejection test.
3. A per-operation header alignment guard across all 4 proposal OpenAPI operations.
4. A correlation-Id/minLength inconsistency note (optional but recommended).

## Dissent / Risks

- **Perpetual deferral is the real risk, not early enforcement.**
  The current guard uses "until a client-readiness decision" as the trigger but
  defines no concrete preconditions. Without a measurement or event, the next
  Ariadne will see "deferred" and skip the sprint because there is no protocol
  for deciding readiness. If Sprint 152 chooses defer, it must add concrete
  preconditions so that Sprint 153 or the next Ariadne-initiated intersection
  can make an informed call.

- **The other 3 proposal routes are the bigger API-spine gap.**
  Even after Sprint 150, the OpenAPI spec says all 4 proposal routes require
  `Idempotency-Key: required, minLength: 8`. Only 1 of 4 has any header binding,
  and that binding is non-blank only. The API-spine consistency question
  ("which proposal routes actually require the key?") is more important than
  the fine-grained length question. A programme decision to enforce headers on
  all 4 routes uniformly (starting with non-blank on update/status/delete)
  would produce a more consistent surface than tightening one route to `minLength: 8`.

- **Error code naming and structure.** If enforcement happens later, consider
  whether `idempotency_key_required` is the right family namespace for length
  violations. A `400` with `"code": "idempotency_key_required"` for a present
  but too-short key is semantically wrong. A separate `"code": "idempotency_key_invalid"`
  or `"code": "idempotency_key_too_short"` is clearer but multiplies the client
  error-handling surface.

## Summary for Ariadne

| Question | Answer |
|---|---|
| Enforce `minLength: 8` now? | No. Defers with tightened preconditions. |
| Concrete client-compatibility risk? | 3/4 proposal routes have zero header binding; enforcement on 1 route creates uneven surface. No tested external clients. |
| API-spine risk? | Existing drift guard does not check per-operation header alignment. Gap between OpenAPI spec and runtime is wider than create-proposal alone. |
| Safer outcome? | Defer-with-guard, but add concrete precondition tests and a per-operation header inventory guard. |
| Next sprint if deferred? | Either add the precondition tests (low risk, tight guard), or preflight update-proposal non-blank header enforcement (bigger risk but closes the wider gap). |

