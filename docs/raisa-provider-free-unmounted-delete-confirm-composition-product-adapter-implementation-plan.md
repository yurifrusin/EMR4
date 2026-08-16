# Provider-free unmounted delete-confirm composition and product-adapter implementation plan

Date: 2026-08-16

Timestamp: 2026-08-16T19:30:56.9386967+10:00 (Australia/Brisbane)

Source HEAD: `44a91b7239ac9f38510c10cb57729ac5312d32f9`

Status: `frozen`

Reasoning level: bounded implementation of accepted command-authority and public-response architecture / High

Risk classification: Tier 2 (`authority_or_security_contract`, `user_visible_behavior_contract`)

## Objective

Implement the accepted delete-confirm boundary in two new, unmounted product
service modules and prove it with provider-free authored-synthetic tests. The
implementation must:

1. accept only the exact existing delete proposal/confirmation model family;
2. derive practice, actor, role, positive authority generation and an HMAC
   session reference from authenticated server state;
3. bind the signed delete evidence signature to one positive appointment source
   version with `raisa.delete_proposal_version_binding.v1`;
4. repeat exact proposal admission against the locked appointment returned by
   `delete_confirm_locked_transaction`;
5. stage exactly one soft cancellation, one attributable delete audit and one
   complete private six-field receipt for a new command;
6. project both first delivery and replay from the validated private bytes into
   one byte-deterministic minimal public envelope; and
7. map every stopped or failed outcome to the accepted non-sensitive closed
   posture.

No router, schema, model, migration or API Spine file may change. No route may
import the modules in this tranche.

## Admission and continuation evidence

Fresh five-source rehydration, protected-ref verification and the mandatory
parallelism disposition are recorded in:

- `orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-implementation-preplanning-runtime-state.json`; and
- `orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-implementation-preplanning-receipt.json`.

The active latch is `in_progress` at exact source
`44a91b7239ac9f38510c10cb57729ac5312d32f9`. Local/origin `master` and
`handoff/current` remain protected at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. All unrelated untracked paths,
including `docs/branding/`, remain outside the tranche.

## Frozen canonical-LF input bindings

Text is strict UTF-8, CRLF is canonicalized to LF, bare CR is rejected, and
SHA-256 is compared before candidate admission.

| SHA-256 | Exact path | Purpose |
|---|---|---|
| `c5d77c82362fd767574cbef33adcdeb1a601010a6ff129eca0ced907ed78670d` | `docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-plan.md` | accepted implementation boundary |
| `ad4b440bd8a6a01194a32bc27ec0872993630505f4026626a5ba186598813197` | `docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md` | frozen semantics |
| `ffb8876efe954e399526bf5e1f41cfb7c2fb460e992428f4aeba7f3b91d2e0bb` | `docs/security/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-threat-model-delta.md` | inherited threat controls |
| `7a715d50dc7d997171c21ab0646923e82493b13571a3584bd3ef872f4c8e0c37` | `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture/architecture-contract.json` | machine-readable accepted contract |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | `app/services/appointment_delete_physical.py` | sole physical transaction and private receipt seam |
| `42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a` | `app/services/appointment_status_composition.py` | composition precedent only |
| `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` | `app/services/appointment_status_product_adapter.py` | product-adapter precedent only |
| `e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467` | `app/services/bernie_turn_evidence.py` | exact signed-evidence verifier and purpose |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` | exact idempotency-key hashing helper |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | `app/schemas/appointments.py` | existing delete input types; no edit |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` | exact private persistence fields; no edit |
| `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` | `app/models/tenancy.py` | server-owned user generation and role fields; no edit |

## Exact implementation contract

### Pure composition module

`app/services/appointment_delete_composition.py` owns:

- immutable `DeleteConfirmServerIngress`, `DeleteConfirmEffectResult` and
  `DeleteConfirmCompositionResult` records;
- exact validation of an admitted `raisa.delete_kernel_request.v1` whose
  `effect_authority` is always false;
- strict validation of the private six-field byte order, compact encoding,
  `Cancelled` status, null waiting area, dedicated reason code and canonical
  warning order;
- pure `raisa.delete_confirm_public_envelope.v1` projection with receipt schema
  `appointment.delete_confirmation_receipt.v1`, sorted-key compact UTF-8 JSON,
  the frozen warning registry and the three frozen audit labels;
- a typed blocked envelope with no receipt and generic issue text;
- composition through the injected transaction factory, defaulting only to
  `delete_confirm_locked_transaction`;
- identical first/replay public bytes derived only from validated private
  bytes; and
- the closed 200/403/404/409/503 outcome mapping.

The composition may inspect a locked appointment only while admitting/staging
a new command. It must not read current appointment state to construct a replay
or success response.

### Application-owned adapter module

`app/services/appointment_delete_product_adapter.py` owns:

- domain-separated bearer minimization bound to practice and actor;
- mint/verify functions for
  `raisa.delete_proposal_version_binding.v1`, covering exactly positive
  `source_version` and the signed evidence signature;
- exact delete command, current-state, freshness and signed-payload builders;
- the one-warning registry admission rule;
- pre-command and locked-state server-ingress construction;
- a default-deny admission adapter producing a digest-bound
  `raisa.delete_kernel_request.v1` with no client authority fields;
- a distinct server-owned command session closed after use;
- a UUID-bound wrapper around the accepted physical transaction; and
- effect staging for exactly appointment cancellation, the v1 attributable
  delete audit and the complete private receipt.

The adapter must use the authenticated user's current positive
`authority_generation`; the physical seam remains the sole capability/grant
checker and checks current authority twice under lock.

### Closed response details

Private receipt fields remain ordered exactly:

1. `appointment_id`;
2. `status`;
3. `status_reason_code`;
4. `cancellation_reason`;
5. `waiting_area_id`; and
6. `warning_codes`.

Public success contains only `schema_version`, `intent`, `safe`,
`requires_confirmation`, `autonomy_tier`, `summary`, `receipt`, `warnings`,
`blocks` and `audit_evidence`. It contains no `appointment`, patient,
practitioner, notes, reason, schedule, audit identity or live projection.

## Exact outputs and ownership

Sol owns:

- this plan and the machine contract;
- the continuous harness repair-and-resume policy/test addition requested by
  Yuri;
- worker reconciliation, deterministic admission, independent review,
  receipts, register changes if an incident qualifies, closeout, acceptance,
  Yuri summary, Continuity/Compass and Git publication.

DeepSeek V4 Flash/high owns exactly one post-freeze work package:

- `app/services/appointment_delete_composition.py`;
- `app/services/appointment_delete_product_adapter.py`;
- `tests/test_appointment_delete_composition.py`; and
- `tests/test_appointment_delete_product_adapter.py`.

It may not edit the plan, contract, route, schema, model, migration, API Spine,
latch, AGENTS, harness policy or any existing product source.

## Verification and acceptance

Pass requires:

1. all twelve machine bindings match strict canonical-LF hashes;
2. exact pure private-to-public projection rejects malformed UTF-8/JSON,
   noncanonical bytes, wrong order/fields/constants, unknown/duplicate/reordered
   warnings and any private/public disclosure field;
3. first and replay public bytes are identical and replay performs no effect;
4. every client attempt to select practice, actor, role, generation, session or
   capability is ignored or rejected;
5. evidence, proposal generation, freshness, target, status, waiting area,
   reason, cancellation text and warnings are checked before the command
   session and again against the locked appointment;
6. new-command staging completes the exact appointment/audit/private-receipt
   write set expected by the physical seam;
7. all closed outcome mappings are exact and non-disclosing;
8. the raw DELETE and both proposal/confirmation routes remain byte-unchanged
   and import none of the new modules;
9. focused provider-free tests pass only through
   `python -m scripts.ariadne_provider_free_pytest`;
10. Ruff, compilation, existing physical tests, architecture tests, API Spine
    tests and canonical provider-free profile pass in risk-proportional scope;
11. the continuous harness repair-and-resume policy test passes;
12. one fresh Gemini 3.7 Flash/high exact-candidate veto passes and leaves its
    review worktree unchanged; and
13. protected refs, `docs/branding/` and all unrelated untracked paths remain
    unchanged.

## Parallelism efficacy

- Sol freezes semantics and owns integration/recovery.
- DeepSeek V4 Flash/high has positive leverage for the separable four-file
  implementation/test package and receives one bounded attempt plus at most one
  mechanical correction.
- Gemini 3.7 Flash/high owns one serial final veto after deterministic
  admission; it is not a co-implementer.
- Native subagents are declined under the current developer constraint.

The serial dependency is plan/contract freeze, then DeepSeek candidate, then
Sol reconciliation and deterministic tests, then Gemini veto, then Sol
acceptance/publication. Reassess at material recovery, pre-verifier and
closeout.

## Recovery and next direction

A mechanical worker defect may receive one bounded same-lane correction. A
conceptual change to response meaning, persistence, authority, locked-state
admission or compatibility moves directly to Sol recovery. The accepted active
operation resumes after any qualifying narrow harness repair without a Yuri
pause unless an existing user-attention condition is met.

Passing this tranche permits the next dependency-satisfied provider-free
read-only route-mounting readiness review. It does not itself permit route or
schema edits, database execution, capability provisioning, runtime mounting,
UI, deployment, release, Pages or protected-ref movement.

## Forbidden surfaces

No route edit/mount/call or HTTP transport; no schema/model/migration/API Spine
edit; no database, Docker or SQL execution; no capability provisioning or
product command; no patient, clinical, product-derived, historical diary or
protected data; no provider, ADC, credentials, IAM, browser or external
network; no UI, deployment, production, release, Pages or protected-ref
movement. Preserve `docs/branding/` and every unrelated untracked file. Stage
explicit paths only.
