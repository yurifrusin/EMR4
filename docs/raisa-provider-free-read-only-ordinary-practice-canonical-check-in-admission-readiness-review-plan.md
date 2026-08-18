# Provider-free read-only ordinary-practice canonical check-in admission-readiness review plan

Date: 2026-08-18

Timestamp: 2026-08-18T22:34:05.3641972+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `8fe889764e778c21bd051f30549f77c8db425e7c`

Accepted route source: `c82c3a741053a9c8da260aa62e1a968af22bb54e`

Target result:
`raisa_provider_free_read_only_ordinary_practice_canonical_check_in_admission_readiness_review_pass`

Reasoning level: Extra High for freezing the meaning of ordinary-practice
admission and its fail-closed successor. High is sufficient for the bounded
read-only evidence implementation, deterministic verification and closeout
while this classification contract remains unchanged.

## Objective

Determine whether the already accepted default-off canonical check-in command
is ready for a future ordinary-practice admission candidate. Inventory and
classify only its current feature posture, ordinary-practice admission control,
API Spine contract, authentication/authorization, tenant isolation,
idempotency, atomic rollback and unknown-commit posture, audit/event evidence,
rollout/disable controls, environment documentation, observability and the
separate client/waiting-area boundary.

This tranche changes no product source or configuration, enables no practice,
calls no route and opens no database. A passing review means the inventory and
verdict are exact; it does not mean ordinary-practice admission passes.

## Exact source boundary

After this freeze, evidence reads and hashes are limited to the following exact
non-protected text sources. The reviewer must decode strict UTF-8, normalize
CRLF to LF, reject remaining bare CR bytes and compare SHA-256 over canonical
LF bytes before classifying any dimension.

| SHA-256 | Exact source |
|---|---|
| `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` | `app/config.py` |
| `2da2b2d584391755a1d9de4e274d59f05dcc24b6b5a3737a35efae49c7f6b117` | `app/database.py` |
| `70574af69c73664a9f8ebda15b749bc5b5b25fe291a55be1f080096146bf47bc` | `app/dependencies.py` |
| `c7380e744bc42be006b34546769b76eb3b8f010b8602513a64f3865c76c1f33c` | `app/services/auth_service.py` |
| `8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08` | `app/routers/appointments.py` |
| `ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90` | `app/schemas/appointments.py` |
| `ef6abdfef1b99737c527790be007ab07296bbc0422197858a5ae561012230570` | `app/services/appointment_check_in_product_adapter.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `7a2caaa1fc862821cc9f8a666e945ddb5e5e837825978bcdcb5f7445cd7a219f` | `app/services/diary_committed_events.py` |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` |
| `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` | `app/models/tenancy.py` |
| `257960e5ac5222b0fef319f1c34cabbd55c785230a8697cc7f685484040b8e87` | `app/models/diary.py` |
| `0836c40fe51e9aa3d908967f4875174dfd04edcff6a7aa88f1476c7b0398113b` | `alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py` |
| `a7e29785a7e2e8433fa9543b8ede9f35f75260a054d6302da6f8e0630e0c9a53` | `alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py` |
| `0cc6918aa6ae26de29b2cc9090e4efadb4e7b48433a5e00e12a36ae7502ff6f1` | `alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py` |
| `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |
| `c13a7edd91799a240f94f47729136022cc23789df22d7fd8bea0b82b57a52935` | `orchestration/api_spine_appointment_command_alignment_inventory.md` |
| `e641ea24d1787ad5b971d7db6e1817d33fdb132be67bf79345ed736f1ca1b56d` | `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-plan.md` |
| `e894a308c94299e4242090b5862758959442ab98cc11e051be5237846ed9b961` | `docs/security/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-threat-model-delta.md` |
| `6ccdc05d5958b51eea87585e3c0d656cccc67de7137456daf6c88b9dc641fc3a` | `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md` |
| `72bf62e321ef1cd19887776bd98b51684efa4fca305690a3f13209daa66f188c` | `orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-sol-acceptance.md` |
| `758bbcf786a0ee806b25fa5fae33480d3158605ea0594e2178b41b854cc3e5b5` | `tests/test_model_required_bureau_a5_1_check_in_runtime.py` |
| `666f0dbda7f41fb183059f6d9c5d0864001e33faf7ef5984175cb2c8b355241b` | `tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py` |
| `019a6eadcd4a57b414e8c0f8df000adebc57ea4ff397838132310aabee07b640` | `tests/test_api_spine_appointment_openapi_drift_guard.py` |
| `01981b06e762b0fc044b962aba4d16c03ff3d407a19dbb13a81b0410bdbd2946` | `tests/test_api_spine_artifacts.py` |
| `c31eb51ece0eb8c49054ce76cee57f64c21fe50c07da716c112cdc01627a0ebe` | `.env.example` |

No repository-wide search is permitted after freeze. The deterministic reviewer
must not import any `app` module or execute application, route, database,
Docker, SQL, browser, provider or network surfaces.

## Frozen classification

The machine contract owns these twelve ordered dimensions and exactly three
classifications:

- `satisfied`: the current prerequisite is present and accepted at the bound
  source, while conferring no admission authority;
- `blocking_gap`: a missing admission-control, rollout or observability design
  must be supplied by a later default-off tranche before an ordinary-practice
  enablement candidate can exist; and
- `operational_evidence_gap`: the safety design exists or is partially present,
  but its ordinary-practice runtime, role, recovery or environment evidence is
  absent and cannot be inferred from authored-synthetic tests.

The expected matrix is:

| Order | Dimension | Classification |
|---:|---|---|
| 1 | `current_default_off_and_empty_ordinary_posture` | `satisfied` |
| 2 | `ordinary_practice_admission_control` | `blocking_gap` |
| 3 | `api_spine_contract_and_route_identity` | `satisfied` |
| 4 | `authentication_and_dual_receptionist_authorization` | `satisfied` |
| 5 | `tenant_isolation_and_runtime_database_role` | `operational_evidence_gap` |
| 6 | `idempotency_evidence_and_replay` | `satisfied` |
| 7 | `atomic_effect_rollback_and_unknown_commit_recovery` | `operational_evidence_gap` |
| 8 | `append_only_audit_and_committed_event` | `satisfied` |
| 9 | `ordinary_rollout_kill_switch_and_rollback_runbook` | `blocking_gap` |
| 10 | `non_phi_observability_and_alerting` | `blocking_gap` |
| 11 | `environment_manifest_and_operational_secret_posture` | `operational_evidence_gap` |
| 12 | `client_cutover_and_waiting_area_separation` | `satisfied` |

Expected counts are six `satisfied`, three `blocking_gap` and three
`operational_evidence_gap`. Any non-satisfied dimension requires the verdict
`not_ready_for_ordinary_practice_admission`. A contrary readiness verdict must
fail closed.

The narrowest dependency-satisfied successor is frozen as
`raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture`.
It may specify only a still-disabled ordinary-practice admission state machine,
separate ordinary versus authored-synthetic controls, non-PHI observability,
runtime-role evidence, kill-switch and rollback prerequisites. It may not edit
product code/configuration or enable a practice.

## Exact owned outputs

GPT Sol owns the serial review and may create or update only:

- this plan and its threat-model delta;
- a machine contract and JSON Schema under the tranche Continuity directory;
- one provider-free deterministic reviewer and its focused tests;
- one source-bound evidence JSON and paired technical report;
- the current tranche latch plus the narrow current-latch transition fixture;
- qualifying closed incident-register evidence and generated revision/report;
- closeout, Sol acceptance, Yuri summary, Continuity updater/test, live baton and
  Compass/Continuity position; and
- required Ariadne runtime states and receipts.

No existing application, configuration, schema, migration, API Spine, runtime
or product test source is editable.

## Deterministic acceptance

Pass requires:

1. all 28 canonical-LF source hashes match before classification;
2. all twelve dimensions appear once, in exact order, with exact source
   citations and marker evidence;
3. the exact 6/3/3 count and
   `not_ready_for_ordinary_practice_admission` verdict are emitted;
4. the evidence explicitly proves default flag `False`, empty synthetic
   allowlist default and zero ordinary-practice admission setting;
5. the evidence distinguishes accepted command-core safety from missing
   ordinary rollout/observability/operational proof;
6. the reviewer performs no `app` import, route call, database/Docker/SQL,
   browser, provider or network operation;
7. at least 120 hostile contract mutations fail closed;
8. the initial successor-latch transition fixture failure is preserved and the
   fixture is narrowed to accept this exact in-progress operation without
   weakening predecessor assertions;
9. focused reviewer/plan tests, API Spine tests, both latch suites, baton,
   register, compilation, Ruff and `git diff --check` pass; and
10. local/origin `master` and `handoff/current` remain exact protected source,
    while `docs/branding/` and every unrelated untracked file remain preserved.

## API Spine posture

The route remains one typed REST/OpenAPI command with an authenticated current
human, Receptionist confirmation, server-owned practice, exact tenant locks,
idempotency before effect, opaque evidence, freshness, atomic mutation, one
append-only audit, one patient-free committed event and bounded receipt.
GraphQL remains read-only. This review changes no path, operation id, schema,
status mapping, event, manifest or runtime.

The absence of ordinary-practice admission and observability controls cannot be
repaired by reusing the authored-synthetic allowlist, weakening default denial,
calling the route, changing generic status or advancing a client.

## Parallelism assessment

- **DeepSeek:** declined. This is a serial read-only authority classification
  with no implementation package. Native-Harness occupied work is paused until
  a separate provider-free HMR boot proof; Claude Code is not a silent fallback.
- **Gemini:** declined. There is no candidate or material conceptual fork; exact
  source bindings and deterministic classification provide the needed review.
  Reassess on conflicting evidence and before any later admission candidate.
- **Native subagents:** declined under current developer policy and because one
  latch and one evidence contract form a serial transition.

No external worker receives implementation, review, acceptance, integration or
protected-ref authority.

## Claim, recovery and closed surfaces

Passing proves only a provider-free repository-static inventory and a
fail-closed not-ready verdict. It does not prove an ordinary practice, live
identity or database role, operational monitoring, real rollback, external
concurrency/restart, deployment or production.

No ordinary-practice enablement, product code/configuration/live-route/database
change, generic-status `Arrived`, action grammar, first-party client,
waiting-area movement, product/patient/clinical/historical/protected data,
provider/Harness retry, credential/IAM/network, production runtime, deployment,
release, Pages or protected-ref movement is authorised. Preserve
`docs/branding/`; stage explicit paths only.
