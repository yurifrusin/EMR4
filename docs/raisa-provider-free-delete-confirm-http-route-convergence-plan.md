# Provider-free delete-confirm HTTP route convergence plan

Date: 2026-08-17

Timestamp: 2026-08-17T04:36:29.1514011+10:00 (Australia/Brisbane)

Status: frozen

Source HEAD: `d4a360640b2a50ae7c26ff5d020eca68c60c4533`

Reasoning level: Extra High — authenticated command-transport and public/private receipt boundary

## Objective

Close exactly the five route-transition gaps accepted at Continuity 307 /
Compass 289. Mount one canonical
`POST /api/v1/appointments/proposals/delete/confirm` handler, retain historical
`/api/v1/appointments/proposals/delete-confirm` as a hidden alias over that
same handler, carry one server-minted opaque appointment-version binding, pass
only server-owned authentication/session/secret dependencies into the accepted
delete product adapter, expose the minimal public receipt schema and serialize
canonical public-envelope bytes for both first delivery and replay.

This tranche removes the route-local confirmation write implementation. It
does not call the resulting route against a database, execute the physical
transaction, provision authority, or converge the separate raw compatibility
`DELETE /api/v1/appointments/{appointment_id}` route.

## Frozen source boundary

After this freeze, existing-source reads, imports and hashes are limited to the
exact non-protected files below. Hashes are strict UTF-8 canonical-LF SHA-256
with bare-CR rejection. Only files explicitly marked `editable` may change.

| SHA-256 | Posture | Exact source |
|---|---|---|
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | editable | `app/routers/appointments.py` |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | editable | `app/schemas/appointments.py` |
| `9c7afeea930ce349edfc22dc2a1cd38fedf52c8cd8ae96be9c56e2deb634ec86` | editable | `app/services/diary/confirm_actions.py` |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | editable | `docs/api-spine/openapi/appointment-commands.yaml` |
| `10b71418a8d0c492def5c412d7aae1b79d69ea93e8566f3ce67408172fdfe8ea` | editable | `orchestration/api_spine_appointment_command_alignment_inventory.md` |
| `8c93542ede5a1de55375990d742762c6010f97aec8c08b7e16c90dc07675a1fa` | narrow test repair | `tests/test_appointment_proposals.py` |
| `4429c35d459ca9510e93a837eb9e0dcb0bbfbac86442d9efd372b5035f6dd3fe` | narrow test repair | `tests/test_bernie_signed_confirmation_evidence.py` |
| `3325395af8b10d655a8298307b54cc5dc95b02603040c3370a707cb3152806ea` | narrow test repair | `tests/test_diary_confirm_actions.py` |
| `2afc312a1c59a321ce758ca59a8865e61761811da731cd6f0233703db19ab4a3` | narrow test repair | `tests/test_api_spine_appointment_openapi_drift_guard.py` |
| `94b03d5060e8099570e58bc4317b853be20e5579fba6c126a1b58131102726aa` | narrow test repair | `tests/test_api_spine_openapi_backend_alignment.py` |
| `d2ce888ad107ce018dc051862fd320c1f8d285dd22840ede0c4e690c76b5b6d7` | narrow test repair | `tests/test_api_spine_confirmation_contract_matrix.py` |
| `57b4b690adc5631439845a04c8be59eed9bf8309d6d303c6c8ce6c88bbf3873c` | narrow test repair | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `c7413bcb4f3c01251b6aa9bf65805d58d4ab2ccbdce683b089058bcec4170995` | narrow test repair | `tests/test_api_spine_appointment_idempotency_route_integration_preflight.py` |
| `0c89fea55bb3904fb9e2126b7b60a0702cb021ed82709aa0ccf28c0c3595cb73` | narrow test repair | `tests/test_api_spine_appointment_command_alignment_inventory.py` |
| `ba8a6d796ac19d39083e9ead0ddf3f2ef5cf45d637abdcb362d2e831628c7fd5` | narrow test repair | `tests/test_api_spine_appointment_idempotency_gap.py` |
| `ea932d6ef0aeadc94b42461353f3798d7d9585e04e895ac90090d88c4280c909` | narrow test repair | `tests/test_api_spine_delete_confirm_idempotency_preflight.py` |
| `157e911c84b97916b9cb7f03f351e3036f2b395418d52cd0de43368e2412675c` | narrow test repair | `tests/test_api_spine_delete_confirm_idempotency_route_contract.py` |
| `b770a061f94ea5ce4bf56f46b5114c4418b39ebcc5fcd80f7ba27c2e39321445` | narrow test repair | `tests/test_api_spine_proposal_only_idempotency_preflight.py` |
| `961f449a525e2e88298b751fe9558f7e3ec1c1d776849043564d0c4dc3824e5c` | narrow test repair | `tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py` |
| `084c7064183b5b1fa7f8f15a39916fee24709470b3ebdc93fa86afd45605e643` | narrow test repair | `tests/test_appointment_audit.py` |
| `8ed7983208fddfb4d94f2d932c7613b6232da33a4effa1dd0658c70f2bf8e7fd` | narrow test repair | `tests/test_reason_code_backend.py` |
| `302e01da34b8b55934f0bfbac6357d84b2e43a23073aea0ffefad6cb22ed5874` | narrow test repair | `tests/test_appointment_status_mutations.py` |
| `a7e1702c61258acfb51f634883086ad5993c8ab63989eace9cfa1102b2532c59` | read-only accepted adapter | `app/services/appointment_delete_product_adapter.py` |
| `ed6a5e705808c71ecf4edcec837c6be2ec790660bf32a85357bda68c2159aa15` | read-only accepted composition | `app/services/appointment_delete_composition.py` |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | read-only accepted physical seam | `app/services/appointment_delete_physical.py` |
| `e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467` | read-only evidence primitive | `app/services/bernie_turn_evidence.py` |
| `70574af69c73664a9f8ebda15b749bc5b5b25fe291a55be1f080096146bf47bc` | read-only server dependency | `app/dependencies.py` |
| `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` | read-only server configuration | `app/config.py` |
| `9629f593629133b8f8a5ed178ccb474ff2ccd824859bb1f3f4bb0d4504e064c0` | read-only acceptance | `docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-closeout.md` |
| `59c7c84177a38c76d0606183736af1843cce6481a72a19d8710d7a992b6a039f` | read-only contract | `orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.json` |
| `e60101a4d60019daee4471088d1fcdc48b7a28e9320ead00eaea6899b4765ded` | read-only evidence | `orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-report.md` |
| `27f7f033b20db36e06bad285bd0318f5f41e7c5d849ba786e6f3aae1363b3db5` | read-only pattern | `docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md` |
| `ad4b440bd8a6a01194a32bc27ec0872993630505f4026626a5ba186598813197` | read-only architecture | `docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md` |

No repository-wide search is permitted after freeze. Protected evidence paths
remain excluded and must not be enumerated.

## Exact implementation

1. Derive delete-confirm evidence, proposal-version, authenticated-session,
   idempotency and stored-session-binding keys from the configured backend
   secret with distinct `emr4.delete-confirm.<purpose>.v1` domains. Introduce
   no new environment variable or client-visible secret.
2. Mint signed delete evidence with the delete evidence key, then mint
   `raisa.delete_proposal_version_binding.v1` from the evidence signature and
   current positive database-owned `appointment_state_version`. Carry it in
   the proposal and prepared confirmation payload; require it in the
   confirmation input.
3. Mount canonical `/proposals/delete/confirm` in generated OpenAPI and retain
   `/proposals/delete-confirm` with `include_in_schema=False` over the exact
   same handler. Point the Diary action descriptor at the canonical endpoint.
4. Give that handler only the normalized idempotency key, authenticated bearer,
   authenticated current user, distinct command-session factory and five
   domain-separated secrets. Invoke `compose_product_delete_confirm` exactly
   once. Remove all route-local claim, read, evidence verification, mutation,
   audit, receipt, commit and fallback behavior.
5. Replace successful `AppointmentOut` delivery with the exact versioned
   minimal public envelope: top-level schema version, command metadata,
   receipt, warnings, blocks and bounded audit labels. No patient,
   practitioner, schedule, note, mutable appointment or identity field enters
   the success body.
6. For `committed` and `replay`, validate and serialize `result.body` only with
   `canonical_delete_confirm_envelope_bytes` and return those public bytes.
   `result.stored_response_bytes` is private command truth and may be checked
   only as the adapter's success invariant; it is never used as HTTP content.
   Typed blocked/error outcomes use their adapter status/body unchanged.
7. Update API Spine and alignment tests to describe the canonical route,
   hidden alias, required opaque binding, adapter-owned command semantics and
   minimal public response. Preserve every other command family and raw
   compatibility route unchanged.

## Provider-free scenarios

| ID | Required proof |
|---|---|
| `DHC-S01` | safe proposal is non-mutating and carries canonical endpoint, signed evidence and one opaque positive-version binding |
| `DHC-S02` | canonical handler forwards only server-owned identity/session/secrets and calls the accepted adapter exactly once |
| `DHC-S03` | historical alias resolves to the same handler and is absent from generated OpenAPI |
| `DHC-S04` | committed and replay results return byte-identical canonical public-envelope bytes while private stored bytes differ and are never delivered |
| `DHC-S05` | minimal public schema admits the exact receipt envelope and rejects appointment, patient, practitioner, schedule, notes and extra fields |
| `DHC-S06` | absent, blank, malformed, tampered or evidence-mismatched version bindings fail closed before a command session can be constructed |
| `DHC-S07` | invalid authentication, inactive user, non-mutating role or missing server secret remains a closed adapter outcome with no fallback |
| `DHC-S08` | missing/blank/conflicting idempotency inputs preserve the adapter's closed status/code mapping |
| `DHC-S09` | warning acknowledgement and stale source-version checks remain owned by the accepted adapter/locked seam, not the route |
| `DHC-S10` | projection or canonical-public serialization failure releases no private bytes and yields no route-local write |
| `DHC-S11` | API Spine, backend inventory, schema and Diary descriptor agree on canonical identity and hidden alias |
| `DHC-S12` | raw `DELETE /{appointment_id}` and all non-delete command families are byte-for-byte outside this change |

Route tests use an in-memory accepted-result stub and dependency overrides;
they may not open a database session or execute SQL. Accepted adapter,
composition and physical behavior evidence is consumed without rerun.

## Exact owned outputs and parallelism

Sol owns this plan, threat delta, contract/schema, source admission,
integration, recovery, acceptance, Continuity/Compass and publication.

DeepSeek V4 Flash/high owns the five editable application/API sources, only
the listed narrow test repairs, and exactly these new implementation outputs:

- `scripts/raisa_provider_free_delete_confirm_http_route_convergence.py`;
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py`;
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence_plan.py`;
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/provider-free-route-convergence-evidence.json`; and
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-report.md`.

Gemini 3.7 Flash/high is reserved for one fresh exact-candidate veto after
deterministic admission. Native subagents remain declined by developer policy.

## Acceptance

Pass requires all frozen hashes before edits; all twelve scenarios; one handler
for canonical and alias paths; one accepted-adapter call; no route-local write
fallback; required proposal-version carriage; exact public schema; identical
canonical public bytes for committed/replay; proof that private receipt bytes
cannot be returned; raw DELETE isolation; at least 100 hostile contract
mutations rejected; focused/provider-free API Spine tests; Ruff, maintained
source compilation, whitespace and one clean fresh Gemini veto.

No database, Docker, SQL, source watcher, provider, ADC, credential, IAM,
browser, external network, patient/clinical/product/protected data, UI,
deployment, production, release, Pages or protected-ref movement is
authorised. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.

## Recovery boundary

One mechanical worker defect may receive one bounded same-lane correction.
A need to edit the accepted adapter/composition/physical contract, execute a
database, change raw DELETE behavior, add capability authority, change product
meaning or cross a protected/provider/deployment boundary stops the candidate
for Sol diagnosis; it does not silently broaden this plan.
