# Provider-free unmounted canonical check-in product-adapter extraction rehearsal plan

Date: 2026-08-18

Timestamp: 2026-08-18T08:58:42+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `852f6f26089cf081c205aff952dffcdecb80d63b`

Target result:
`raisa_provider_free_unmounted_canonical_check_in_product_adapter_extraction_rehearsal_pass`

Reasoning level: Extra High for this plan freeze because it crystallizes the
future canonical ordinary-arrival authority seam. High is sufficient for the
bounded implementation, deterministic admission and check-gated closeout while
this contract remains unchanged.

## Objective

Extract the deterministic check-in confirmation contract from the current
default-off A5.1 route-local implementation into one reusable, unmounted
application-owned adapter. Exercise it only with authored-synthetic in-process
objects and injected fakes. The existing route remains unchanged, uncalled and
behind its exact default-off Rayleen/authored-synthetic gate.

This tranche proves a reusable adapter seam, not an admitted product command.
It must not move either first-party client, change generic-status `Arrived`,
promote the action grammar or perform a real database write.

## Exact frozen inputs

All hashes are SHA-256 over canonical LF bytes at source HEAD.

| Existing read-only source | SHA-256 |
|---|---|
| `app/routers/appointments.py` | `87a67fd718ac9233f6b1e089d708969749afda0124713e8621d542939f5d605f` |
| `app/config.py` | `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` |
| `app/schemas/appointments.py` | `ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90` |
| `app/models/appointments.py` | `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` |
| `app/models/tenancy.py` | `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` |
| `app/models/diary.py` | `257960e5ac5222b0fef319f1c34cabbd55c785230a8697cc7f685484040b8e87` |
| `app/services/appointment_idempotency.py` | `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` |
| `app/services/diary_committed_events.py` | `7a2caaa1fc862821cc9f8a666e945ddb5e5e837825978bcdcb5f7445cd7a219f` |
| `app/services/appointment_status_product_adapter.py` | `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` |
| `docs/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review.md` | `056108b8cea82961f31c4cfc9296b2d65d63aecaecb813a33b147bff996302a3` |
| `docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md` | `81f5a60e45e6b272f186f032e8e1339a0cde18db8f0480789303c34ed219813c` |
| `docs/api-spine/openapi/appointment-commands.yaml` | `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` |

After freeze, the worker may read these exact files plus this plan, its threat
delta and the worker packet. It may not perform repository-wide discovery.

## Owned implementation package

DeepSeek V4 Flash/high owns exactly:

- `app/services/appointment_check_in_product_adapter.py`; and
- `tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`.

Sol owns plan/threat/continuity/evidence/acceptance artifacts, worker review,
recovery, integration and Git. Existing files are read-only. In particular,
the worker must not edit or import the adapter from
`app/routers/appointments.py`.

## Frozen adapter responsibilities

The module must expose one unmounted `compose_product_check_in` seam plus
bounded typed helper/result objects. Exact public symbol names other than
`compose_product_check_in` may be chosen mechanically, but the following
responsibilities are indivisible:

1. **A5-only gate excluded.** The Rayleen feature flag, authored-synthetic
   practice allowlist and Rayleen naming remain in the route layer. The adapter
   cannot enable a practice and does not read configuration.
2. **Authenticated current human authority.** Accept only a server-supplied
   actor, require active exact-practice `Receptionist`, reject client-selected
   practice/actor/role authority, and recheck the injected current actor inside
   the command session before effect composition.
3. **Closed confirmation envelope.** Accept only
   `AppointmentCheckInProposalConfirmationIn` carrying the dedicated
   `AppointmentCheckInProposalOut` / `AppointmentCheckInCommand` family,
   `confirmed=true`, a safe confirmation-required proposal, exact warning
   acknowledgement and non-empty opaque evidence.
4. **Stable idempotency and one-use evidence.** Derive the evidence hash without
   releasing the evidence; invoke the existing injected check-in claim before
   effect; return exact stored replay without a second lock/effect; classify
   conflict, in-progress and different-key evidence reuse fail closed.
5. **Locked current truth.** Load one exact practice-scoped appointment under
   the injected lock seam, require command/appointment identity and exact
   `Booked|Confirmed -> Arrived`, and reproduce the current A5.1 state payload,
   command payload and 32-character freshness calculation byte-for-byte.
6. **Opaque evidence verification.** Verify practice, current actor,
   appointment, source status, waiting-area before/target and freshness through
   the existing injected verifier at the injected UTC time. Invalid, expired,
   tampered, wrong-purpose or mismatched evidence produces no effect.
7. **Waiting-area policy.** A supplied non-null area may assign only when none
   exists. Omitted/null preserves an existing area. Move/removal is forbidden.
   Assigned or preserved areas must be exact-id, active, same-practice and at
   the same non-null appointment location. An unresolved lookup fails closed.
8. **Ordered atomic effect composition.** Only after admission, stage exactly
   status `Arrived`, the permitted area assignment/preservation, one
   command-bound attributable audit, one patient-free
   `diary.appointment_checked_in.v1` event, one bounded private
   `appointment.check_in_receipt.v1`, idempotency completion, one commit and one
   bounded fresh readback. Injected failure at any pre-commit member rolls back
   the entire fake session and releases no successful receipt.
9. **Patient-free release.** The adapter result, audit evidence, event plan and
   receipt may contain only the already accepted command/correlation fields.
   Patient name, identifier, reason, note, clinical text and raw token/key are
   forbidden.
10. **No route/runtime ownership.** The adapter may use injected fakes and
    existing typed models/services, but must not import FastAPI routers,
    settings, `SessionLocal`, start a server, connect to a database or expose a
    generic executor.

The adapter may use a dependency object of exact callbacks rather than own a
database session. That keeps the rehearsal executable without giving this
tranche a live command or database capability.

## Deterministic acceptance

Authored-synthetic tests must prove at least:

- Booked and Confirmed success with no area, new compatible assignment and
  compatible existing-area preservation;
- exact current-state, command-payload, target-area and freshness parity with
  the frozen route-local contract;
- replay returns the stored result and performs no lock, audit, event, complete
  or commit callback;
- key conflict, in-progress and evidence reuse stop before effect;
- inactive/wrong-role/wrong-practice current actor and authority revocation
  stop before effect;
- false confirmation, unsafe/blocked proposal, missing evidence, command/path
  identity mismatch, stale freshness and every evidence-verifier failure stop;
- invalid source, already arrived and terminal source stop;
- cross-practice, foreign-id, inactive, locationless, location-mismatched,
  move and removal waiting-area cases stop;
- success orders claim, lock, reauthorization, validation, audit, event,
  completion, commit and readback with exactly one effect each;
- injected failures at audit, event, completion, commit and readback never
  release a false successful receipt and pre-commit failures roll back;
- event/receipt/result remain patient-free and contain no raw idempotency key
  or signed evidence; and
- at least 60 hostile contract mutations reject with zero successful effect.

The route, config, schemas, models, idempotency/event services, manifests and
all other existing inputs must remain hash-exact. Focused tests, relevant A5.1
and API Spine regression tests, the canonical fast profile, latch/baton checks,
Ruff, maintained-source compilation and Git whitespace must pass. One fresh
Gemini 3.7 Flash/high exact-candidate veto is mandatory after deterministic
admission.

## API Spine classification

- This is an application-owned adapter under an existing single-purpose
  REST/OpenAPI scheduling command; GraphQL remains read-only.
- The adapter accepts server-authenticated identity and a human-confirmed typed
  proposal. Neither proposal, model provenance, client role assertion nor event
  is authority.
- Current human authority and database truth remain transaction-time checks.
- The event is a committed acceleration hint, not current truth, authority or
  a receipt.
- OpenAPI, async manifests and route source remain unchanged because the
  adapter is unmounted.

## Parallelism allocation

- **Sol:** plan, acceptance, worker review/recovery, integration, continuity and
  Git.
- **DeepSeek V4 Flash/high:** positively selected for the exact two-file
  implementation/test package in a disposable worktree after pre-dispatch
  receipt.
- **Gemini 3.7 Flash/high:** reserved as required independent exact-candidate
  veto after deterministic admission.
- **Native subagents:** declined because current developer policy prohibits
  proactive native delegation.

The lanes are serial at their authority boundaries: plan freeze precedes
DeepSeek; Sol admission precedes Gemini; Sol alone accepts and integrates.

## Claim boundary and closed surfaces

Passing proves only an authored-synthetic, in-process, unmounted adapter over
injected fakes. It does not prove an HTTP route, ordinary-practice admission,
real PostgreSQL/RLS/transaction behavior, concurrency, restart, unknown commit,
client behavior, external adapter conformance, deployment or production.

No existing route/config/schema/model/service/manifest/migration/client file,
feature flag, generic-status `Arrived`, action grammar, route contract, waiting-
area move/remove command, live route/database/source/watcher, product/patient/
clinical/historical/protected data, provider/ADC/credential/IAM/network/tool,
deployment, production, release, Pages or protected ref may change. Preserve
`docs/branding/` and every unrelated untracked file; stage explicit paths only.
