# Provider-free unmounted status-confirm route-convergence composition rehearsal plan

Date: 2026-08-12

Status: frozen

Source HEAD: `83db576fc2c95f513de38ae57d5b4b1ac6fe5027`

## Purpose

Build and rehearse the narrowest unmounted composition callable that joins the
accepted status-only admission adapter, server-owned authority/session facts,
the accepted physical transaction seam and a closed transport-result mapper.
The rehearsal is authored-synthetic and in-memory. It does not mount or call an
application route or connect to a database.

## Pre-composition contract reconciliation

The route-mounting review named a closed public-response mapper as a blocker.
Exact source inspection now proves why: the current mounted route and API Spine
return `AppointmentConfirmStatusProposalOut`, including the current appointment
projection, while the unmounted physical helper describes its five-field status
projection as the complete public response. A five-field buffer cannot be
mapped into the larger current envelope on replay without consulting mutable
appointment state, which would violate stored-result replay.

The narrow correction is frozen before composition:

- receipt v1 remains private, unmounted and schema-compatible;
- `response_body_canonical_bytes` contains deterministic canonical JSON for the
  complete current `AppointmentConfirmStatusProposalOut` payload;
- `response_body_json` must equal the parsed canonical bytes and
  `response_body_hash` must equal their lowercase SHA-256 digest;
- the five status fields remain a required, validated projection derived from
  the envelope's appointment and warning objects, not a second response body;
- initial success and replay release the exact same stored bytes;
- no current route, API Spine schema, model, migration or database constraint is
  changed; and
- any incomplete, mismatched or corrupt receipt fails closed without a body.

This corrects an unmounted representation before first use. It adds no data
category: the current idempotency service already stores the same full response
payload in `response_body_json`.

## Exact accepted inputs

| Path | SHA-256 |
|---|---|
| `app/routers/appointments.py` | `59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb` |
| `app/schemas/appointments.py` | `d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d` |
| `docs/api-spine/openapi/appointment-commands.yaml` | `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` |
| `app/services/appointment_idempotency.py` | `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` |
| `app/services/appointment_status_physical.py` | `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` |
| `app/models/appointments.py` | `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` |
| `scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py` | `a45b601a375c7dec7ee08e46be53e23991542cf9699a9ac75798c2e70d2865d8` |
| `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md` | `aa2eab6fddc0f8394ea3950965d525222917506a04b0ef10ab22999e2e442363` |
| `docs/raisa-provider-free-read-only-status-confirm-route-mounting-admission-review-closeout.md` | `cfc63d42c16de0c62ee19a6df7d29a374479c890bb52e7fd0c7398739a5fb933` |

## Frozen composition order

1. accept transport data only through the exact status-only adapter;
2. take practice, actor, role, current-authority and opaque session identity
   only from server-owned inputs;
3. derive the HMAC idempotency-key binding, canonical request digest and
   domain-separated session digest;
4. enter the exact physical transaction seam;
5. for `new_command`, revalidate locked version, warnings, evidence and terminal
   policy before invoking one injected status effect;
6. stage one mutation/audit/completed-receipt set or roll back completely;
7. for `replay`, return exact stored canonical bytes without another effect;
8. map conflict, incomplete legacy/in-progress/corrupt receipt, revoked
   authority and unavailable target to closed non-disclosing outcomes; and
9. never rebuild a successful response from current mutable appointment state.

## Frozen scenarios

The rehearsal covers clean execute, same-digest replay, different-digest
conflict, incomplete scaffold rollback, authority revocation, unavailable
target, waiting-area discrimination, warning mismatch, stale generation,
terminal transition deferral, corrupt stored bytes and post-commit response
loss followed by replay.

## Acceptance

Pass only if:

1. all nine accepted-input hashes match;
2. the complete-envelope reconciliation is deterministic and fails closed on
   missing, extra or inconsistent response fields;
3. initial success and replay return byte-identical stored envelopes;
4. every non-success outcome releases no stored success body;
5. one execute produces one effect and replay/conflict produce none;
6. authority and target checks precede receipt disclosure;
7. at least 50 hostile mutations fail closed;
8. focused, status-confirm lineage, canonical and whitespace gates pass;
9. the mounted route and database are neither edited nor executed; and
10. protected refs and all unrelated untracked files, including
    `docs/branding/`, remain unchanged.

## Non-authority

No route edit/mount/call, real database/source/watcher/event access, patient or
product data, provider call, credential/IAM/network access, executable external
tool, product command, deployment, production, release, Pages or protected-ref
movement is authorised.

On acceptance, the next safe candidate is a read-only route-mounting readiness
re-review against the composed source. Mounting remains separately closed.
