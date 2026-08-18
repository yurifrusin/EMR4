# Provider-free read-only ordinary-practice canonical check-in admission-readiness review report

Date: 2026-08-18

Timestamp: 2026-08-18T22:34:05.3641972+10:00 (Australia/Brisbane)

Status: frozen evidence

Result: `raisa_provider_free_read_only_ordinary_practice_canonical_check_in_admission_readiness_review_pass`

Verdict: `not_ready_for_ordinary_practice_admission`

## Outcome

The accepted canonical check-in command core is not ready for ordinary-practice admission. Its typed API contract, dual Receptionist authorization, tenant-scoped transaction, idempotency/evidence, append-only audit/event and bounded client/waiting-area separation are present. Ordinary-practice admission control, selected-practice rollout/rollback and non-PHI observability are missing; runtime database-role, unknown-commit recovery and environment evidence remain unproved.

The authored-synthetic allowlist is not an ordinary-practice admission mechanism and cannot be repurposed. Default denial remains unchanged.

## Source boundary

All 28 strict UTF-8 canonical-LF (bare-CR rejected) SHA-256 bindings matched before classification.

| Path | SHA-256 |
|---|---|
| `app/config.py` | `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` |
| `app/database.py` | `2da2b2d584391755a1d9de4e274d59f05dcc24b6b5a3737a35efae49c7f6b117` |
| `app/dependencies.py` | `70574af69c73664a9f8ebda15b749bc5b5b25fe291a55be1f080096146bf47bc` |
| `app/services/auth_service.py` | `c7380e744bc42be006b34546769b76eb3b8f010b8602513a64f3865c76c1f33c` |
| `app/routers/appointments.py` | `8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08` |
| `app/schemas/appointments.py` | `ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90` |
| `app/services/appointment_check_in_product_adapter.py` | `ef6abdfef1b99737c527790be007ab07296bbc0422197858a5ae561012230570` |
| `app/services/appointment_idempotency.py` | `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` |
| `app/services/diary_committed_events.py` | `7a2caaa1fc862821cc9f8a666e945ddb5e5e837825978bcdcb5f7445cd7a219f` |
| `app/models/appointments.py` | `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` |
| `app/models/tenancy.py` | `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` |
| `app/models/diary.py` | `257960e5ac5222b0fef319f1c34cabbd55c785230a8697cc7f685484040b8e87` |
| `alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py` | `0836c40fe51e9aa3d908967f4875174dfd04edcff6a7aa88f1476c7b0398113b` |
| `alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py` | `a7e29785a7e2e8433fa9543b8ede9f35f75260a054d6302da6f8e0630e0c9a53` |
| `alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py` | `0cc6918aa6ae26de29b2cc9090e4efadb4e7b48433a5e00e12a36ae7502ff6f1` |
| `docs/api-spine/openapi/appointment-commands.yaml` | `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` |
| `orchestration/api_spine_adr.md` | `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` |
| `orchestration/api_spine_programme.md` | `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` |
| `orchestration/api_spine_appointment_command_alignment_inventory.md` | `c13a7edd91799a240f94f47729136022cc23789df22d7fd8bea0b82b57a52935` |
| `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-plan.md` | `e641ea24d1787ad5b971d7db6e1817d33fdb132be67bf79345ed736f1ca1b56d` |
| `docs/security/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-threat-model-delta.md` | `e894a308c94299e4242090b5862758959442ab98cc11e051be5237846ed9b961` |
| `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md` | `6ccdc05d5958b51eea87585e3c0d656cccc67de7137456daf6c88b9dc641fc3a` |
| `orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-sol-acceptance.md` | `72bf62e321ef1cd19887776bd98b51684efa4fca305690a3f13209daa66f188c` |
| `tests/test_model_required_bureau_a5_1_check_in_runtime.py` | `758bbcf786a0ee806b25fa5fae33480d3158605ea0594e2178b41b854cc3e5b5` |
| `tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py` | `666f0dbda7f41fb183059f6d9c5d0864001e33faf7ef5984175cb2c8b355241b` |
| `tests/test_api_spine_appointment_openapi_drift_guard.py` | `019a6eadcd4a57b414e8c0f8df000adebc57ea4ff397838132310aabee07b640` |
| `tests/test_api_spine_artifacts.py` | `01981b06e762b0fc044b962aba4d16c03ff3d407a19dbb13a81b0410bdbd2946` |
| `.env.example` | `c31eb51ece0eb8c49054ce76cee57f64c21fe50c07da716c112cdc01627a0ebe` |

## Dimension matrix

| Order | Dimension | Classification | Source citations | Markers |
|---:|---|---|---|---|
| 1 | `current_default_off_and_empty_ordinary_posture` | `satisfied` | `.env.example`; `app/config.py`; `app/routers/appointments.py` | feature_flag_defaults_false; synthetic_allowlist_defaults_empty; flag_denial_precedes_route_work; ordinary_practice_setting_absent |
| 2 | `ordinary_practice_admission_control` | `blocking_gap` | `.env.example`; `app/config.py`; `app/routers/appointments.py` | gate_is_explicitly_synthetic_only; gate_names_only_the_synthetic_allowlist; only_named_check_in_allowlist_is_synthetic; separate_ordinary_admission_control_missing |
| 3 | `api_spine_contract_and_route_identity` | `satisfied` | `app/routers/appointments.py`; `app/schemas/appointments.py`; `docs/api-spine/openapi/appointment-commands.yaml`; `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md` | canonical_confirm_path_documented; operation_id_documented; typed_request_documented; typed_response_documented; mounted_operation_id_exact; accepted_adapter_delegated_once; route_convergence_exactly_accepted |
| 4 | `authentication_and_dual_receptionist_authorization` | `satisfied` | `app/dependencies.py`; `app/routers/appointments.py`; `app/services/appointment_check_in_product_adapter.py`; `app/services/auth_service.py` | route_requires_receptionist; token_user_practice_match_required; active_user_required; adapter_rechecks_ingress_receptionist; transaction_actor_reloaded; revoked_authority_stops |
| 5 | `tenant_isolation_and_runtime_database_role` | `operational_evidence_gap` | `.env.example`; `alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py`; `alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py`; `app/database.py`; `app/dependencies.py`; `app/routers/appointments.py` | request_sets_transaction_practice; appointment_queries_are_practice_scoped; appointments_and_idempotency_forced_rls_helper; idempotency_rls_policy_applied; audit_forced_rls; event_forced_rls; ordinary_runtime_role_attestation_absent |
| 6 | `idempotency_evidence_and_replay` | `satisfied` | `alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py`; `app/services/appointment_check_in_product_adapter.py`; `app/services/appointment_idempotency.py`; `tests/test_model_required_bureau_a5_1_check_in_runtime.py` | dedicated_check_in_claim; practice_actor_operation_key_identity; different_key_evidence_reuse_rejected; same_key_replay_classified_before_effect; invalid_stored_replay_fails_closed; database_unique_evidence_constraint |
| 7 | `atomic_effect_rollback_and_unknown_commit_recovery` | `operational_evidence_gap` | `.env.example`; `app/config.py`; `app/routers/appointments.py`; `app/services/appointment_check_in_product_adapter.py`; `tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py` | precommit_stops_rollback; commit_uncertainty_releases_no_success; readback_uncertainty_releases_no_success; uncertain_outcome_is_explicit; commit_failure_regression_present; ordinary_unknown_commit_runbook_and_alert_absent |
| 8 | `append_only_audit_and_committed_event` | `satisfied` | `alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py`; `alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py`; `app/services/appointment_check_in_product_adapter.py`; `app/services/diary_committed_events.py` | audit_append_only_trigger; event_append_only_trigger; one_command_bound_audit_staged; one_committed_event_staged; patient_free_event_payload; patient_free_receipt_enforced |
| 9 | `ordinary_rollout_kill_switch_and_rollback_runbook` | `blocking_gap` | `.env.example`; `app/config.py`; `app/routers/appointments.py` | existing_global_synthetic_kill_switch_defaults_off; existing_allowlist_is_synthetic_not_ordinary; ordinary_rollout_state_kill_switch_and_runbook_missing |
| 10 | `non_phi_observability_and_alerting` | `blocking_gap` | `.env.example`; `app/config.py`; `app/routers/appointments.py`; `app/services/appointment_check_in_product_adapter.py`; `app/services/diary_committed_events.py` | audit_evidence_exists_but_is_not_telemetry; committed_event_exists_but_is_not_monitoring; non_phi_metrics_and_alerts_missing |
| 11 | `environment_manifest_and_operational_secret_posture` | `operational_evidence_gap` | `.env.example`; `app/config.py`; `app/database.py` | non_dev_default_secret_fails_closed; environment_is_documented; database_url_is_documented; secret_key_is_documented; a5_settings_and_runtime_role_evidence_absent |
| 12 | `client_cutover_and_waiting_area_separation` | `satisfied` | `app/routers/appointments.py`; `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md`; `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-plan.md` | waiting_area_move_remains_blocked; waiting_area_assignment_and_preservation_bounded; plan_keeps_first_party_client_closed; plan_keeps_waiting_area_movement_closed; accepted_closeout_keeps_client_cutover_separate |

## Counts and gaps

Satisfied: 6; blocking gaps: 3; operational-evidence gaps: 3.

Blocking gaps:

- `ordinary_practice_admission_control`
- `ordinary_rollout_kill_switch_and_rollback_runbook`
- `non_phi_observability_and_alerting`

Operational-evidence gaps:

- `tenant_isolation_and_runtime_database_role`
- `atomic_effect_rollback_and_unknown_commit_recovery`
- `environment_manifest_and_operational_secret_posture`

## Narrowest successor

`raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture`

That successor is architecture-only and remains default-off. It may specify separate ordinary versus authored-synthetic admission controls, non-PHI observability, runtime-role evidence, kill-switch and rollback prerequisites. It may not enable a practice or edit product code/configuration.

## Hostile mutation suite

Rejected 128 deterministic hostile contract mutations (minimum 120).

## Closed boundaries

| Boundary | Value |
|---|---|
| app_imported | False |
| route_called | False |
| database_opened | False |
| docker_used | False |
| sql_executed | False |
| browser_opened | False |
| provider_called | False |
| network_opened | False |
| product_code_changed | False |
| practice_enabled | False |

No `app` module was imported; no route, database, Docker, SQL, browser, provider or network surface was opened. No practice was enabled and no product source changed.
