# Raisa local-only historical Diary access boundary convergence — plan

Date: 2026-08-24

Timestamp: 2026-08-24T02:20:53+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-local-only-historical-diary-access-boundary-convergence`

Planning source HEAD: `9d5b72fa2000163f86c661d542d17366872bf1da`

Reasoning level: Extra High. This tranche changes the typed authority vocabulary
that the live governance clockwork copies into the next operation latch. It must
make one useful local research probe expressible without turning a narrow Diary
exception into general historical-data authority.

## Decision and objective

The accepted privacy gate is useful now. Before that gate may read even one
historical Diary file, the clockwork will distinguish a default historical-data
denial from one exact, contract-bound local Diary privacy subgate.

This tranche changes only governance-clockwork validation and its deterministic
tests. It does not open, list, search, sample, hash, parse or otherwise inspect
the historical archive. It does not bind a real archive path.

## Closed typed vocabulary

The validator will admit exactly three historical-data modes.

1. `legacy_full_denial` retains the already-published compound token
   `no_product_patient_appointment_clinical_historical_or_protected_data`.
   This is a compatibility reading for existing latches only and grants no
   access.
2. `typed_full_denial` requires both
   `no_product_patient_appointment_clinical_or_protected_data` and
   `no_historical_data_access`.
3. `bounded_local_diary_probe` requires the typed product/patient/appointment/
   clinical/protected denial plus every member of the following closed set:

   - `allow_local_only_historical_diary_snapshot_measured_privacy_probe`;
   - `historical_diary_privacy_subgate_contract_sha256_e312d58d7743b9b4d79d8a947b765732eea142f47586e0bd1f4e738047802615`;
   - `historical_diary_access_one_leaf_root_one_dense_day_nonrecursive_maximum_80_files`;
   - `historical_diary_access_maximum_134217728_total_bytes_and_8388608_per_file`;
   - `historical_diary_access_read_only_no_symlink_or_reparse_traversal`;
   - `historical_diary_access_new_ignored_output_root_ephemeral_in_memory_key_and_failure_cleanup`;
   - `historical_diary_access_no_network_provider_model_prompt_telemetry_clipboard_or_external_release`;
   - `historical_diary_access_no_raw_text_identity_filename_timestamp_key_or_mapping_commit`;
   - `historical_diary_access_strongest_result_locally_restricted_candidate_without_downstream_authority`; and
   - `historical_diary_access_no_fixture_memory_rag_product_runtime_route_api_client_database_or_configuration`.

The SHA-256 token binds the exception to the accepted data-free
`real-access-subgate-contract.json` bytes. A deterministic repository test must
read that committed contract and prove the digest, schema, non-executable state,
absence of a real path and every limit represented above. Altering the contract
therefore requires an explicit code-and-test change rather than a descriptive
boundary rewrite.

The three modes are mutually exclusive. The validator rejects an exception
combined with either denial token, a partial exact set, any unknown boundary
containing `historical`, any substitute digest, any broader file/byte/root
allowance and any absence of the product/patient/appointment/clinical/protected
denial.

## Implementation

Refactor `orchestration_harness/governance_clockwork_tick.py` so all ordinary
and user-decision closeout paths call one typed historical-boundary validator.
Keep the stable non-data boundary floor unchanged. Export immutable vocabulary
constants so the deterministic tests construct exact states instead of copying
free-form strings.

Update `tests/test_ariadne_governance_clockwork_tick.py` with hostile cases for
all three admitted modes and every rejection class. Update
`tests/test_current_baton_consistency.py` so it validates the active latch
through the same typed control rather than requiring the retired compound token
forever. The accepted subgate contract remains byte-unchanged.

## Acceptance

Pass requires:

1. the fresh five-source Ariadne receipt and valid in-progress latch;
2. the recorded DeepSeek, Gemini and native-subagent serial dispositions;
3. exactly three admitted historical-data modes and rejection of incomplete,
   contradictory, unknown or overbroad variants;
4. byte-exact binding to the accepted non-executable access contract;
5. no historical archive enumeration or content access;
6. unchanged product, patient, appointment, clinical, protected, provider,
   runtime, deployment, Pages and protected-ref denials;
7. passing focused and complete governance-clockwork verification;
8. clockwork closeout, paired lay/technical Yuri summary and non-PHI Pushover
   notification; and
9. unchanged protected refs and preservation of every unrelated untracked file.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The native harness remains
  paused pending its separate boot proof, the authority vocabulary is one
  tightly coupled change, and no silent Claude Code fallback is allowed.
- **Gemini:** not applicable with neutral leverage. This tranche forbids
  provider, network and model execution, so no live verifier is dispatched.
- **Native subagents:** declined with negative leverage. There is no separately
  owned work package independent of the central validator and its latch tests.
- **GPT Sol:** owns plan, implementation, deterministic review, acceptance,
  clockwork publication and the next-latch decision.

## Closed surfaces

Provider-free, local-only and unmounted. No archive open/list/search/sample/
hash/parse and no real path binding; no patient, appointment, clinical, product
or protected data; no provider, network, model prompt, telemetry, clipboard or
external release; no product runtime, route, API, client, database or
configuration change; no fixture, memory, RAG or GraphRAG promotion; no
ordinary-practice enablement; no production, deployment, release, Pages or
protected-ref movement. Local/origin `master` and `handoff/current` remain
exactly `2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve
`docs/branding/` and every unrelated untracked file. Stage explicit paths only.
