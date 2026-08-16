# Provider-free unmounted delete-confirm response-compatibility and product-adapter architecture plan

Date: 2026-08-16

Timestamp: 2026-08-16T16:33:54.6870685+10:00 (Australia/Brisbane)

Source HEAD: `f0c98682568784441991b080681f9beb3b9354c2`

Status: `frozen`

Reasoning level: material command-authority and public-response architecture / Extra High

Risk classification: Tier 2 (`authority_or_security_contract`, `user_visible_behavior_contract`)

## Objective

Freeze the narrowest off-route architecture that closes the six blockers from
the accepted delete-confirm route review without mounting or calling a route:

1. derive all command identity, session, authority generation and capability
   meaning from authenticated server state;
2. bind one opaque proposal generation to signed delete evidence and re-admit
   the exact proposal against the locked current appointment;
3. compose the accepted authority-first physical transaction seam and its
   atomic appointment/audit/private-receipt write set; and
4. project the stored six-field private receipt into one versioned,
   byte-deterministic full public success envelope without reconstructing a
   larger appointment from mutable post-commit truth.

This tranche defines architecture and authored-synthetic contract evidence
only. It does not implement an adapter, edit a schema or route, run a database,
or open product runtime authority.

## Admission and five-source rehydration

The fresh runtime state and corrected passing receipt are:

- `orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-preplanning-runtime-state.json`; and
- `orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-preplanning-corrected-receipt.json`.

They name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`; machine-resolve exact source
`f0c98682568784441991b080681f9beb3b9354c2`; and record DeepSeek, Gemini and
native-subagent dispositions. The first receipt's invalid leverage-vocabulary
result is preserved and grants no authority.

At freeze, local/origin task are exact source. Local/origin `master` and
`handoff/current` remain exact protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. The tracked tree was clean before
the active-latch transition. All 637 unrelated untracked paths, including
`docs/branding/` and the predecessor pre-push pair, remain preserved.

## Frozen canonical-LF input bindings

Every text input is strict UTF-8, CRLF is canonicalized to LF, and bare CR is
rejected before SHA-256 comparison.

| SHA-256 | Exact path | Purpose |
|---|---|---|
| `6b146f64a715738ff4729588bb77f9fb3c7edfcf04edba272888ad2972f50b6f` | `docs/raisa-provider-free-read-only-delete-confirm-route-convergence-review.md` | six-blocker decision |
| `2e2941e5bbe8574dd044067140d66bc8ded2b49215376763ed53716423ed6713` | `docs/raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution-closeout.md` | predecessor claim boundary |
| `fcd9e11be52b3c4bf261f944e196a4cb32f142be1c302b37e76b060381c8eab2` | `orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-sol-acceptance.md` | accepted next direction |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | `app/services/appointment_delete_physical.py` | accepted six-field receipt and locked seam |
| `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` | `app/services/appointment_status_product_adapter.py` | application-owned adapter precedent |
| `42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a` | `app/services/appointment_status_composition.py` | dual-admission/composition precedent |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | `app/schemas/appointments.py` | current public delete envelope |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` | private receipt persistence boundary |
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | `app/routers/appointments.py` | current proposal/evidence/legacy route behavior |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` | canonical operation and public contract |
| `4988e5c694d6b9a4ad07b31d619088a1f7b216d4e6b91f63215a82a5a0dc0704` | `docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-plan.md` | analogous adapter controls |
| `ff975620aa9dc531b04389f89963759a5decc0e80ab853d6688e5501924e3366` | `docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-closeout.md` | analogous accepted boundary |
| `584405db5d49a56e18061f80fcd1faa72c278cf0d4975cf95febc86783609019` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-closeout.md` | minimized-receipt privacy decision |
| `8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91` | `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md` | abstract admission meaning |

No bound product source may change in this architecture tranche. Review and
validation may inspect only these exact inputs plus owned outputs.

## Frozen architecture decisions

### 1. Two-layer response contract

The accepted `response_body_canonical_bytes` remains the sole persisted command
truth: exactly six patient-minimized fields in its existing order. The adapter
must never store or later reconstruct `AppointmentOut`, patient, practitioner,
notes, reason, schedule or other mutable projection fields in order to answer a
retry.

The future public success response is instead
`raisa.delete_confirm_public_envelope.v1`: a complete, versioned envelope whose
only outcome object is `appointment.delete_confirmation_receipt.v1`, containing
the same six fields. Its warnings and audit-evidence labels come from frozen
registries. A pure projection validates the stored private bytes and produces
canonical sorted-key UTF-8 JSON. Both initial delivery and replay project from
the same stored bytes and therefore return byte-identical public bodies.

The current development response's full `appointment: AppointmentOut` is
deliberately retired for this command family when a later route/schema tranche
is admitted. Success must not expose both shapes, and canonical and compatibility
aliases must not diverge. This is a prerelease privacy and replay correction,
not route authority in this tranche.

### 2. Server-owned ingress

- operation and route family are constants
  `confirmAppointmentDeleteProposal` / `delete-confirm`;
- practice, actor, role and positive authority generation come only from the
  authenticated server-loaded user;
- the raw bearer token is minimized to a domain-separated HMAC session
  reference before the command session opens;
- the client supplies no role, generation, capability or session authority;
- `appointment.cancel.confirm` remains a physical-seam constant and its grant
  is checked twice under the accepted lock plan; and
- the command uses a distinct server-owned session factory that the adapter
  closes, never the request-scoped authentication session.

### 3. Opaque proposal-generation binding and locked re-admission

The non-mutating proposal later carries
`delete_proposal_version_binding`, an opaque server HMAC over the exact signed
evidence signature and positive appointment state version. The client may
return it unchanged but cannot select, increment or replace its generation.

Before opening the command session, the adapter validates exact proposal type,
operation, confirmation, idempotency presence, warning acknowledgement, signed
evidence purpose/binding, freshness and opaque generation. Inside the physical
transaction, it rebuilds current delete state from the locked appointment and
repeats the same admission. Any target, version, status, waiting-area, reason,
warning, evidence or freshness mismatch stops without effect.

### 4. Physical composition and effect staging

Only the accepted `delete_confirm_locked_transaction` may classify a new
command or replay. A `new_command` stages exactly one cancellation, one
attributable delete audit and one complete private receipt before the physical
seam validates the entire write set. `replay` validates stored receipt integrity
and performs no effect. No route-local claim, audit, commit or fallback exists
in the architecture.

### 5. Closed outcome mapping

| Internal outcome | Future HTTP status | Public posture |
|---|---:|---|
| `committed`, `replay` | 200 | exact canonical public-envelope bytes projected from stored six-field receipt |
| proposal/admission stop | 200 | typed blocked envelope; no effect and no success receipt |
| missing/blank idempotency or binding conflict | 409 | stable non-sensitive error code |
| current authority unavailable | 403 | stable non-sensitive error code |
| target unavailable/cross-practice | 404 | indistinguishable unavailable result |
| in-progress or legacy non-replayable receipt | 409 | no body from partial/legacy state |
| wait budget, scaffold, integrity or projection failure | 503 | no stored or current appointment disclosure |

No error mapping may reconstruct the full appointment or disclose whether a
cross-practice row exists.

### 6. Compatibility isolation

Raw `DELETE /appointments/{id}` remains a separately governed legacy ingress.
It cannot call, import, emulate or inherit the dedicated adapter, capability,
receipt, idempotency or replay contract. A later canonical
`/appointments/proposals/delete/confirm` path and hidden
`/appointments/proposals/delete-confirm` alias must share one handler and one
public v1 envelope if and only if route convergence is separately admitted.

## Exact outputs and ownership

Sol-owned semantic outputs:

- this plan;
- `docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md`;
- `docs/security/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-threat-model-delta.md`; and
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture/architecture-contract.json`.

DeepSeek V4 Flash/high receives only the post-freeze mechanical package:

- `architecture-contract.schema.json` and provider-free evidence schema/data in
  that continuity directory;
- `scripts/raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py`; and
- `tests/test_raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py`.

Sol alone owns worker reconciliation, receipts/latch, register, final report,
closeout, acceptance, Yuri summary, Continuity/Compass and Git publication.

## Verification and acceptance

Pass only if:

1. all five rehydration sources and fourteen canonical-LF input hashes match;
2. the contract and architecture preserve the exact physical six-field byte
   receipt as sole persisted command truth;
3. public success contains the versioned minimal receipt and cannot contain or
   reconstruct `AppointmentOut` or mutable patient/practitioner/schedule data;
4. initial and replay public bytes are identical pure projections of the same
   validated private bytes, including fixed warning and audit registries;
5. no client field can supply role, session, generation or capability;
6. opaque proposal generation, signed evidence, freshness, warnings and delete
   state are checked before the command session and against the locked target;
7. physical effect, audit and private receipt are one validated write set and
   all stopped/replay/error paths have no write fallback;
8. every internal outcome maps to exactly one closed HTTP posture and cross-
   practice absence is non-disclosing;
9. raw DELETE remains isolated and no route/schema/product source changes;
10. at least 100 hostile semantic mutations fail closed;
11. focused architecture, plan, API Spine, current-baton/latch/register tests,
    Ruff, compilation, one post-freeze canonical profile and whitespace pass;
12. one fresh Gemini 3.7 Flash/high exact-candidate veto passes after
    deterministic admission and leaves the review worktree unchanged; and
13. protected refs, `docs/branding/` and every unrelated untracked path remain
    unchanged.

## Parallelism efficacy

- Sol owns the material response and authority decisions and freezes them
  before dispatch.
- DeepSeek V4 Flash/high is reserved for one bounded mechanical validator,
  schema, evidence-fixture and hostile-test package. It may not revise meaning,
  product source or acceptance.
- Gemini 3.7 Flash/high is reserved for one final Tier-2 veto after the exact
  candidate and deterministic profile pass.
- Native subagents are declined under the current developer constraint.

Reassess on plan freeze, worker pre-dispatch, material recovery,
pre-verifier acceptance and closeout.

## Recovery and next direction

One mechanical DeepSeek defect may receive one bounded same-lane correction.
Any disagreement about public response meaning, persistence, authority,
locked-state semantics or user-visible compatibility is conceptual and moves
immediately to Sol's recovery lease; no worker decides it.

Passing this architecture permits only a separately frozen provider-free
unmounted delete-confirm composition and product-adapter implementation. It
still does not permit route/schema edits, database execution or product runtime.

## Forbidden surfaces

No product source edit; route edit/mount/call; HTTP transport; database,
Docker, migration or SQL execution; capability provisioning; product command;
patient, clinical, product-derived, historical-diary or protected data;
provider, ADC, credential, IAM, browser or external network; UI, deployment,
production, release, Pages or protected-ref movement. Preserve
`docs/branding/` and every unrelated untracked file. Stage explicit paths only.
