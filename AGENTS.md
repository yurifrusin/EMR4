# EMR4 Centaur — Live Agent Handover

> **Purpose:** This compact file is the authoritative starting point for every human or AI agent working in EMR4. Read it completely. It controls current authority, protected boundaries, baton state, and next work. Historical detail lives in the indexed ledgers and immutable snapshot below.

## 1. Project

EMR4 Centaur is an AI-native, open-source General Practice management system for Australia. FastAPI/PostgreSQL owns clinical and diary truth. Microsoft Word with an Office.js add-in is the clinical workspace, and the native browser Diary is the scheduling surface. The full phase and architecture blueprint is [`implementation_plan.md`](implementation_plan.md).
## 2. Mandatory Rehydration

At a new session, after conversation compaction/restoration, after a model/provider change, and before a new sprint plan or dispatch:

1. Read this file completely.
2. Read the active acceptance/plan documents named in the Current Baton.
3. Restore the protected-evidence and user-decision boundaries in sections 5 and 6.
4. Verify `git status`, `HEAD`, `master`, `handoff/current`, `origin/master`, and `origin/handoff/current`.
5. Generate a fresh Ariadne orchestrator receipt naming all five sources: `live_handover_current_baton`, `current_authority_allocation`, `active_plan_and_acceptance`, `protected_evidence_boundaries`, and `git_refs_and_worktree`.

A conversation summary is a continuity aid only. It is never authoritative for model allocation, provider transport, holdout rules, write authority, or user decision boundaries. `rehydrated_from_receipt: true` without the five named sources is insufficient and must return `revision_required`.

Use a fresh chat context for each named tranche by default. The new context must repeat this full rehydration before acting; prior-chat memory never substitutes for the five sources. Durable decisions that must survive the handoff belong in this file and the active plan/evidence documents. The outgoing tranche must name its exact result, artifacts, unresolved gates, next tranche, and reasoning level.

## 3. Current Baton

| Item | Current value |
|---|---|
| Current protected-integration result | On 2026-08-02 Yuri explicitly authorised PR 74 integration and exactly one consequent public GitHub Pages rebuild. PR 74 rebase-merged at protected master `09a661cfa83559b13c438f45734403f33d1e3bbb`; Pages run `30719055657`, Node/Office security run `30719055642`, Python security run `30719055679` and CodeQL run `30719055649` all passed. CodeQL alerts 546-548 are natively `fixed` without dismissal and their bot review conversations are resolved. The repository-local outcome receipt is `orchestration/agent_inbox/codex/raisa-real-identity-microsoft-federation-protected-integration-receipt.json`. No-`docs/**` baton PR 75 then merged at `2e34bdad732fdab32fbf778280b3d3c70d66d602`; its PR and default-branch Node/Office, Python-security and CodeQL runs all passed, it triggered no Pages run, and local/origin `master` plus `handoff/current` aligned. No further Pages rebuild is authorised. |
| Mode | Parallel-capable Ariadne workflow; protected single-track integration |
| Baton ref | `handoff/current` |
| Active development worktree | `C:\Users\sarashera\emr4` on `codex/ariadne-bernie-davida-parallel-seam`; protected integration remains closed and single-track through `master` |
| Worker worktree root | `C:\Users\sarashera\EMR4-worktrees\` |
| Required Git relation | The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted native Diary proposal-confirm parity at exact source `78cbcca756476fddfd0fda4b4d1241f195b21ab6`, the accepted globally-disabled runtime-instrumentation scaffold at exact source `410ea6dbbe28b94cfaa83ac5f6b586910c77aa6a`, the accepted default-off runtime-instrumentation architecture at exact source `ed52950f451af88892a8f469157ecf8c8567da81`, the authored-synthetic shadow-comparison rehearsal at exact source `47b5f09ecf35225da25812ba87bb656a1094fc7e`, the default-off shadow-comparison architecture at exact source `e1dca1c6dc5d3f3e241548f80a226e5bb776417f`, the pure route-adapter differential rehearsal at exact source `beb4e65cddf72437948d72e08dd18c2ea4f0c609`, the legacy-route convergence design at exact source `47e08eada878d8f6dd2a9b100e706404d3594e5a`, the conditional-command admission rehearsal at exact source `f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c`, the source-owned-truth reorientation at reviewed source `037eed060d4519f2f3d6721135143ecb6f70e358`, the accepted CF-D1 closeout, both original immutable CF-D2 stop artifacts, the stopped recovery descendant and the accepted workflow-fluidity repair as descendants of CF-D1 runtime source `fed81847b4155d49cf997905e79cf31808ceb017`, original CF-D2 attempt-002 source `28cd0ce6639fd831960c57d5289b08f3d36ca3fb`, recovery diagnostic attempt-002 source `fe8313d224a92115aa31bea14f0cd3b14e4c9967`, exact workflow source `018099dd6c5f0502121360732feb602252eb34cc`, required resumed HEAD `648c8ec9805af63729264ea9c22fd695f062a741` and published conformance source `01d355f42df5981341196f3aa0caec2cccce7a2d`. Local/origin `master` and `handoff/current` remain aligned at protected `2e34bdad732fdab32fbf778280b3d3c70d66d602`; no protected ref movement is authorised. User-owned untracked `docs/branding/` and all unrelated untracked files remain preserved and excluded. |
| Conductor/integrator | GPT Sol |
| Implementation/test worker | DeepSeek V4 Flash/high through Claude Code `--bare` |
| Independent worker/reviewer | Gemini 3.6 Flash/high through a fresh Antigravity project |
| Active Ariadne descendant | Historical DeepSeek, Terra/Gemini, Gemini Developer API and Sydney Vertex failure nodes retain their immutable recorded results and consumed ledgers. Yuri subsequently authorised evidence-backed diagnose-repair-rerun cycles in the exact `gemini-2.5-flash` Sydney Vertex lane until success or bounded-option exhaustion, without changing the USD 1, provider, model, project, identity, keyless ADC, region, authored-synthetic, isolation, audit, no-fallback or no-product boundaries. The first repaired Sydney call still returned bounded HTTP 400. The next request removed the unsupported enum from the INTEGER field and used exact numeric bounds while the deterministic proofreader retained the exact integer release contract. A provider-free relay-readiness race was repaired with a connection-refused-only pre-connect retry and a distinct zero-call ledger. Occupied attempt `gemini-25-repair-002` then passed through `australia-southeast1-aiplatform.googleapis.com` using the exact Bernie impersonated ADC: HTTP 200, 1108 ms, 176 prompt tokens, 50 candidate tokens and 226 total tokens. The proofreader released exactly four grounded authored-synthetic fields with no repair. Every opened ledger is consumed, no call followed success, no fallback or external mutation occurred, and cleanup is complete. The terminal result is `ariadne_vertex_sydney_gemini_25_occupied_rehearsal_pass`, bound by Continuity graph revision 49 and Compass map revision 36. This proves the configured and observed Sydney locational request path and bounded typed release, not Australian physical or sovereign processing, production suitability, or authority for product-derived, patient, health or clinical data. |
| Active product track | Yuri accepted the strategic transition review and paused the provider lane without retry. Stages 1 and 2 passed the local synthetic provider-free appointment-create vertical and its durable authority/security foundation through protected PRs 36-39. Yuri then accepted the intent-projected, committed-event-aware conversational Diary north star and refined its fluid UX direction as a tablet-first portable projection console: conversation scopes the view, touch selects within it, and button or conversational confirmation converges on one backend-owned command path. Stage 3A passes its Yuri-only, typed, local, authored-synthetic, provider-disabled formative study. On 2026-07-20 Yuri removed the named-model dependency and authorised the bounded provider-neutral in-house meta-grid concept tranche, which passed with the typed projection grammar and implementation handoff. The bounded functional native Diary client, provider-free live-local integration, and exact combined patient/practitioner/time/duration proof all pass with desktop/tablet/phone, keyboard, privacy, interruption and ordinary-fallback evidence. On 2026-07-21 Yuri explicitly authorised the bounded committed-event runtime changes. That vertical now passes: the existing signed update-confirm path atomically appends one patient-free `diary.appointment_rescheduled` event with appointment truth, audit and idempotency completion; a default-off authenticated practice-scoped feed drives fresh authorized reads and one quiet controllable Reception One cue. Its authorised availability descendant also passes: the same signal triggers a fresh exact active-practitioner slot search, preserves a still-valid selection/proposal with fresh candidate data, clears invalid selection/proposal and stale Back history, and remains silent for other-practitioner or no-consequence changes. Reception One remains the leading provisional user-facing name while meta-grid remains the architectural/product term: many views and page-like focuses belong to one authoritative Diary. The candidate public hierarchy is explanatory `electronic medical records`, distinctive `RECEPTION ONE™`, concise umbrella `EMR`, and quiet technical/version `v4`; EMR4 remains internal nomenclature. This context grants no rename, artwork or trademark authority. Yuri then authorised Ariadne Compass Increment 2 to restore programme orientation. It passes as a revision-bound, repository-local, read-only map of the current Reception One journey, present capability, candidate directions and Yuri-owned decisions; it has no workflow-executive authority. On 2026-07-22 Yuri authorised Ariadne's first real continuity fork. The sandbox-DAG exploration now passes as a provider-free, non-executing synaptic protocol: the orchestrator controls immutable start-up policies while bilaterally authorised leaves may exchange typed data directly, policy amendments require a new container generation, and every command-shaped candidate stops at human authority. It adds no live container, model or product actuator. Yuri then authorised the bounded Synaptic Event Router protocol descendant. It passes as repository-local authored-synthetic evidence: immutable router and node policies bilaterally permit exact control-frame steering, deterministic scope intersection fans one event to two mailboxes, replay and unrelated changes are suppressed, fresh-read grants remain inert, supersession rejects stale completion, and source-hashed dry-run manifests start nothing. On 2026-07-23 Yuri authorised the Bounded Cognitive Work Cell and Proofreader Gate descendant. It passes as a non-executing protocol: node/leaf/container/agent roles are independent, one unoccupied agent-eligible work cell emits five typed drafts, and deterministic egress proves grounding, safe repair, bounded retry, supersession, atomic release and inert human routing. On 2026-07-24 the bounded Reception One visual/interaction synthesis passed as a deterministic, unoccupied product node: it adds an integrated intent rail, truthful candidate-time projection, explicit selected-but-not-reserved boundary and responsive desktop/tablet/phone/keyboard behavior while preserving existing read, proposal, privacy, interruption and reconciliation contracts. One disposable Sydney Vertex design cell returned HTTP 200 but its draft failed the deterministic proofreader, released nothing and was not used; the request-contract-only retry was ineligible. Yuri then authorised the provider-free Stage 3B representative-staff sequence. Its readiness node now passes: the consent-gated sidecar, closed anonymous export schema, desktop/tablet/phone evidence and disposable live-local authored-synthetic task population all verify with unchanged database truth and complete owned cleanup. No participant session or threshold result exists; Yuri must nominate or schedule five to eight voluntary current or recent Australian general-practice reception staff before execution. On 2026-07-30 the provider-free Proofreader Dialogue v4 passed one closed typed correction exchange, but its two-call occupied sequence closed without a candidate reaching proofreading: the primary failed at provider schema admission and the fully regated HTTP 200 repair failed local `$.version_code` admission. Both ledgers are consumed, no value was released and any redesign or further call requires a new descendant. Voice, other event families, external event transport/workers, new appointment write authority, further providers, PII, production, deployment and release remain separately closed. |
| Antigravity independent-verifier allocation | `docs/ariadne-antigravity-gemini-36-high-verifier-allocation.md`, `docs/ariadne-antigravity-gemini-36-high-verifier-allocation-closeout.md`, `docs/ariadne-antigravity-gemini-36-high-verifier-first-review-analysis.md`, `docs/ariadne-economical-deepseek-execution.md`, `scripts/ariadne_antigravity.py`, `orchestration/harness_settings/worker_pool.yaml`, `orchestration/harness_settings/sprint_worker_policy.yaml`, `orchestration/harness_settings/transport_adapters.yaml`, `orchestration/harness_settings/security_review_protocol.yaml`, `orchestration/harness_settings/operating_model.yaml`, `orchestration/agent_inbox/antigravity/ariadne-gemini-36-high-verifier-allocation-repair-review-receipt.json`, `orchestration/agent_inbox/codex/ariadne-antigravity-gemini-36-verifier-model-change-receipt.json`, `tests/test_ariadne_antigravity.py`, `tests/test_ariadne_allocation_schemas.py`, and `tests/test_ariadne_deepseek_claude.py` |
| Current Baton acceptance index | Historical and inactive acceptance lookup rows are preserved verbatim in `docs/handover-ledgers/current-baton-acceptance-index.md` and bound by `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`. The index has artifact lookup authority only and cannot override this live authority, protected boundaries, active acceptance or next work. |
| Ariadne agent error and correction register acceptance | `docs/ariadne-agent-error-correction-register-plan.md`, revisions 2-257 including current `docs/ariadne-agent-error-correction-register-revision-257.md`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`, `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`, `scripts/ariadne_agent_error_register.py`, `scripts/ariadne_serial_pytest.py`, `scripts/ariadne_verifier_worktree_preflight.py`, `orchestration/harness_settings/verifier_execution_policy.yaml`, `tests/test_ariadne_agent_error_register.py`, `tests/test_ariadne_serial_pytest.py`, `tests/test_ariadne_verifier_execution_policy.py`, `tests/test_ariadne_verifier_worktree_preflight.py`, `scripts/compact_agents_acceptance_index.py`, `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`, `tests/test_agents_acceptance_index.py`, `docs/ariadne-agent-error-correction-register-closeout.md`, and `orchestration/agent_inbox/codex/ariadne-agent-error-register-sol-acceptance.md` |
| Model-required Bureau architecture and paused development plan | `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`, `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`, `docs/security/emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md`, `implementation_plan.md`, `orchestration/bernie_interaction_model.md`, `orchestration/agent_inbox/codex/rayleen-self-healing-architecture-preplan-runtime-state.json`, `orchestration/agent_inbox/codex/rayleen-self-healing-architecture-preplan-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-preacceptance-runtime-state.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-preacceptance-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-pre-verifier-acceptance-runtime-state.json`, and `orchestration/agent_inbox/codex/model-required-bureau-architecture-pre-verifier-acceptance-receipt.json` |
| Model-required Bureau C4 allowlisted-actuator simulator acceptance | `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md`, `docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`, `docs/api-spine/openapi/technical-control-simulator-commands.yaml`, `scripts/model_required_bureau_c4_simulator.py`, `scripts/model_required_bureau_c4_acceptance.py`, `orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator/`, `tests/test_model_required_bureau_c4_simulator.py`, `orchestration/agent_inbox/codex/model-required-bureau-c4-worker-independent-review.md`, `orchestration/agent_inbox/codex/model-required-bureau-c4-repair-independent-audit.md`, `orchestration/agent_inbox/antigravity/model-required-bureau-c4-code-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-21.md`, `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-closeout.md`, `orchestration/agent_inbox/codex/model-required-bureau-c4-sol-acceptance.md`, `scripts/model_required_bureau_c4_continuity_update.py`, and `tests/test_model_required_bureau_c4_continuity.py` |
| Model-required Bureau C5 plan and recovery state | The exact disposable live-development-recovery plan and provider-free recovery provenance remain accepted. The first occupied Windows attempt exposed AER-0028, replacing an invalid literal TCP-refusal absence proxy with exact owned-process absence plus exclusive exact-port reacquisition retained through generation 2. AER-0029 separately records the orchestrator's ADC-versus-gcloud credential-store guidance error. Fresh exact-HEAD review of recovery commit `88b330870bd559b5276ae8191a41d152c48e9d7b` then found one clean-worktree interpreter-path defect; descendant `dff672049ab5ce47058d7340525e63589fefc5c1` binds the child to the exact active controller interpreter and passed a genuinely fresh Gemini 3.6 Flash/high veto with 132 provider-free tests. The frozen occupied run subsequently passed with one Sydney Vertex call, deterministic admission, generation-2 readback and complete cleanup. Controlling closeout and acceptance are `docs/emr4-model-required-bureau-c5-occupied-live-rehearsal-closeout.md` and `orchestration/agent_inbox/codex/model-required-bureau-c5-occupied-live-rehearsal-sol-acceptance.md`. |
| Provider-free unmounted durability inert DDL rehearsal acceptance | `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan.md`, `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-design.md`, `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-postgresql-representability-recovery.md`, `docs/security/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-threat-model-delta.md`, `scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py`, `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/`, `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py`, `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py`, `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py`, `orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-inert-ddl-postgresql-recovery-implementation-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-84.md`, `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-context-fabric-durability-inert-ddl-rehearsal-sol-acceptance.md`, `scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_continuity.py` |
| Context Fabric CF-D1 concurrency rehearsal acceptance | `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md`, `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md`, `docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/`, `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`, `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`, `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py`, `orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-replay-vocabulary-recovery-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-239.md`, `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-context-fabric-durability-concurrency-rehearsal-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-11--context-fabric-durability-concurrency-rehearsal.md`, `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_continuity_update.py`, and `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_continuity.py` |
| Ariadne CF-D2 workflow incident diagnosis and fluidity repair acceptance | `docs/ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair-plan.md`, `docs/ariadne-cf-d2-workflow-incident-diagnosis.md`, `orchestration/harness_settings/evidence_led_workflow.yaml`, `scripts/ariadne_evidence_gate.py`, `scripts/ariadne_antigravity.py`, `scripts/ariadne_orchestrator_preflight.py`, `orchestration/continuity/ariadne-cf-d2-workflow-fluidity-repair/`, `orchestration/agent_inbox/antigravity/ariadne-cf-d2-workflow-fluidity-final-review-v2-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-255.md`, `docs/ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair-closeout.md`, `orchestration/agent_inbox/codex/ariadne-cf-d2-workflow-fluidity-repair-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--cf-d2-workflow-incident-diagnosis-and-fluidity-repair.md`, `scripts/ariadne_cf_d2_workflow_fluidity_repair_continuity_update.py`, and `tests/test_ariadne_cf_d2_workflow_fluidity_repair_continuity.py` |
| Context Fabric source-owned-truth and conditional-command reorientation acceptance | `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-plan.md`, `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-architecture.md`, `docs/security/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-threat-model-delta.md`, `orchestration/continuity/raisa-context-fabric-source-owned-truth-conditional-command-reorientation/`, `scripts/raisa_context_fabric_source_owned_truth_reorientation_acceptance.py`, `tests/test_raisa_context_fabric_source_owned_truth_reorientation.py`, `orchestration/agent_inbox/codex/raisa-context-fabric-source-owned-truth-reorientation-vertex-review-zero-call-receipt.json`, `orchestration/agent_inbox/codex/raisa-context-fabric-source-owned-truth-reorientation-vertex-review-receipt.json`, `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-closeout.md`, `orchestration/agent_inbox/codex/raisa-context-fabric-source-owned-truth-reorientation-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--context-fabric-source-owned-truth-conditional-command-reorientation.md`, `scripts/raisa_context_fabric_source_owned_truth_reorientation_continuity_update.py`, and `tests/test_raisa_context_fabric_source_owned_truth_reorientation_continuity.py` |
| Provider-free unmounted conditional-command admission rehearsal acceptance | `docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-plan.md`, `docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md`, `docs/security/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-unmounted-conditional-command-admission-rehearsal/`, `scripts/raisa_provider_free_unmounted_conditional_command_admission_rehearsal.py`, `tests/test_raisa_provider_free_unmounted_conditional_command_admission_rehearsal.py`, `orchestration/agent_inbox/codex/raisa-conditional-command-admission-rehearsal-source-head-draft-failure-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-256.md`, `docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-conditional-command-admission-rehearsal-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--provider-free-unmounted-conditional-command-admission-rehearsal.md`, `scripts/raisa_provider_free_unmounted_conditional_command_admission_rehearsal_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_conditional_command_admission_rehearsal_continuity.py` |
| Provider-free unmounted legacy-route convergence kernel-interface acceptance | `docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-plan.md`, `docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-design.md`, `docs/security/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/`, `scripts/raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py`, `tests/test_raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py`, `orchestration/agent_inbox/codex/raisa-legacy-route-convergence-kernel-interface-preplanning-receipt.json`, `orchestration/agent_inbox/codex/raisa-legacy-route-convergence-kernel-interface-preplanning-v2-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-257.md`, `docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-closeout.md`, `orchestration/agent_inbox/codex/raisa-legacy-route-convergence-kernel-interface-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--legacy-route-convergence-kernel-interface.md`, `scripts/raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface_continuity.py` |
| Provider-free unmounted pure route-adapter differential rehearsal acceptance | `docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-plan.md`, `docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-design.md`, `docs/security/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal/`, `scripts/raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py`, `tests/test_raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py`, `docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-pure-route-adapter-differential-rehearsal-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--pure-route-adapter-differential-rehearsal.md`, `scripts/raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal_continuity.py` |
| Provider-free unmounted default-off shadow-comparison architecture acceptance | `docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-plan.md`, `docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture.md`, `docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture/`, `scripts/raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py`, `tests/test_raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py`, `docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-closeout.md`, `orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--default-off-shadow-comparison-architecture.md`, `scripts/raisa_provider_free_unmounted_default_off_shadow_comparison_architecture_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_default_off_shadow_comparison_architecture_continuity.py` |
| Provider-free unmounted authored-synthetic shadow-comparison rehearsal acceptance | `docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-plan.md`, `docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-design.md`, `docs/security/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal/`, `scripts/raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py`, `tests/test_raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py`, `docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-authored-synthetic-shadow-comparison-rehearsal-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--authored-synthetic-shadow-comparison-rehearsal.md`, `scripts/raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal_continuity_update.py`, and `tests/test_raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal_continuity.py` |
| Provider-free default-off runtime-instrumentation architecture acceptance | `docs/raisa-provider-free-default-off-runtime-instrumentation-architecture-plan.md`, `docs/raisa-provider-free-default-off-runtime-instrumentation-architecture.md`, `docs/security/raisa-provider-free-default-off-runtime-instrumentation-architecture-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-default-off-runtime-instrumentation-architecture/`, `scripts/raisa_provider_free_default_off_runtime_instrumentation_architecture.py`, `tests/test_raisa_provider_free_default_off_runtime_instrumentation_architecture.py`, `docs/raisa-provider-free-default-off-runtime-instrumentation-architecture-closeout.md`, `orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--default-off-runtime-instrumentation-architecture.md`, `scripts/raisa_provider_free_default_off_runtime_instrumentation_architecture_continuity_update.py`, and `tests/test_raisa_provider_free_default_off_runtime_instrumentation_architecture_continuity.py` |
| Provider-free globally-disabled runtime-instrumentation scaffold acceptance | `docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-plan.md`, `docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-design.md`, `docs/security/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-threat-model-delta.md`, `app/services/diary/shadow_instrumentation.py`, `app/middleware/shadow_instrumentation.py`, `tests/test_raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold.py`, `docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-closeout.md`, `orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--globally-disabled-runtime-instrumentation-scaffold.md`, `scripts/raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold_continuity_update.py`, and `tests/test_raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold_continuity.py` |
| Provider-free ordinary/fallback Diary client proposal-confirm parity acceptance | `docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-plan.md`, `docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-design.md`, `docs/security/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity/`, `docs/diary/diary.js`, `tests/test_raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity.py`, `review/test_diary_smoke.py`, `docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-closeout.md`, `orchestration/agent_inbox/codex/raisa-ordinary-fallback-diary-client-proposal-confirm-parity-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-12--ordinary-fallback-diary-client-proposal-confirm-parity.md`, `scripts/raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_continuity_update.py`, and `tests/test_raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_continuity.py` |
| Agent Execution Surface AES-C4 acceptance | `docs/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-plan.md`, `docs/raisa-agent-execution-surface-containment-gate-aes-c4-preexecution-factual-rebind.md`, `docs/security/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-threat-model-delta.md`, `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/`, `scripts/raisa_agent_execution_surface_containment_gate_aes_c4_provider_proof.py`, `tests/test_raisa_agent_execution_surface_containment_gate_aes_c4.py`, `tests/test_raisa_agent_execution_surface_containment_gate_aes_c4_plan.py`, `orchestration/agent_inbox/antigravity/raisa-aes-c4-provider-proof-rebind-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-227.md`, `docs/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-closeout.md`, `orchestration/agent_inbox/codex/raisa-aes-c4-bounded-occupied-provider-proof-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-11--aes-c4-bounded-occupied-provider-proof.md`, `scripts/raisa_agent_execution_surface_containment_gate_aes_c4_continuity_update.py`, and `tests/test_raisa_agent_execution_surface_containment_gate_aes_c4_continuity.py` |
| Agent Execution Surface AES-C5 acceptance | `docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-plan.md`, `docs/security/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-threat-model-delta.md`, `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/`, `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py`, `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py`, `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5.py`, `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py`, `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_plan.py`, `orchestration/agent_inbox/antigravity/raisa-aes-c5-gemini-36-high-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-233.md`, `docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-closeout.md`, `orchestration/agent_inbox/codex/raisa-aes-c5-product-runtime-admission-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-11--aes-c5-product-runtime-admission.md`, `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_continuity_update.py`, and `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_continuity.py` |
| Current result | At Continuity 253 / Compass 235, `raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_pass` is accepted at exact source `78cbcca756476fddfd0fda4b4d1241f195b21ab6`. The source-bound inventory names exactly seven native Diary raw appointment mutation call sites and zero remain. Every native create/update/status/waiting-area/delete proposal gesture sends an idempotency header; fresh blocks override prior warning review, changed warning codes require renewed review and missing signed evidence fails closed. Create/update follow-up status and delete-404 fallback use signed status confirmation, with explicit partial-outcome reporting after an already committed base write. Eight tranche tests, all 142 Diary browser tests, 242 focused backend/API tests and the canonical 191-test profile pass. The four backend raw compatibility routes, handlers, evidence signals and default `audit` mode remain mounted and unchanged. No external-consumer conclusion, route retirement, kernel convergence, create fence, observer/sink, operational source, product/patient data, provider call or command expansion opened. |
| Next implementation | Provider-free compatibility-consumer and kernel-convergence admission review is the next dependency-satisfied tranche. Inventory every remaining repository/system, import, recovery and migration consumer of the four compatibility routes; freeze the exact response, audit, idempotency and transactional behavior any convergence must preserve; and select the narrowest status, delete or update first implementation slice before create. This is read-only/static admission work. Compatibility routes must remain mounted and unchanged. It grants no kernel implementation, create schedule fence, shadow enablement, observer/sink/persistence, operational database/source/watcher/event access, product/patient data, provider call, command expansion, deployment, production, release, Pages or protected-ref movement. Continue under standing authority after a fresh five-source rehydration and receipt; preserve and exclude `docs/branding/` and all unrelated untracked files and use explicit-path staging only. |
| Future Consultant clinical direction | Yuri selected licensed Cochrane Library evidence as Consultant's central general evidence-based pillar, continuing Dr Michael Shera's original practice of ensuring every GP at his medical centre could access Cochrane through an EMR-toolbar button. The intended trial candidate is Wiley Agent Knowledge Base: Cochrane Library through AWS Marketplace, behind a provider-neutral source-type-aware evidence contract with complementary Australian, diagnostic, medicines, local-pathway, specialty, rare-disease and primary-literature layers. This direction grants no subscription/EULA, cost, provider call, patient/product data, clinical implementation, runtime, deployment or production authority. Controlling artifacts are `docs/consultant-safety-first-differential-diagnosis-doctrine.md`, `implementation_plan.md`, `docs/bernie-consultant-triage-implementation-roadmap.md` and `orchestration/research/cochrane_cds_pipeline.md`. |
| Raisa Practice Context Fabric direction | On 2026-08-05 Yuri accepted the backend-owned temporal Practice Context Fabric as Raisa's permanent cross-Bureau integration direction and subsequently added the Bureau Memory Bank. Query-shaped `ContextNeed` candidates must pass deterministic purpose, principal, role, tenant, source, field, time-window and freshness policy before a typed expiring `ContextFrameSet` reaches a Bureau and same-packet proofreader. Current facts, committed events, historical operational states, recent collective work, private session state, durable domain threads and cited knowledge evidence remain distinct threads with provenance and authority ceilings. The Bureau Memory Bank is a read-only, purpose-filtered, lossy, expiring and rebuildable projection; it is never raw audit access, a transcript store, current truth, command evidence or provider-model memory. The Fabric is not a shared prompt, database dump, vector/RAG authority, source of truth, workflow executor or command plane. Yuri's 2026-08-12 reorientation makes authoritative source services and atomic conditional commands the first-runtime correctness kernel: Context Frames are expiring evidence, events are acceleration hints, one logical watcher may serve each database partition and many users, and every consequential command rechecks current authority and source truth. Freshness, confirmation, idempotency and audit remain distinct; appointment create additionally fences its schedule-conflict domain. The prior durability evidence is preserved as a later Durable Event and Cue Delivery extension: CF-D1 passes, CF-D2 remains unproved and may reopen only through a fresh observability-first plan. This direction grants no patient/clinical/product data, further provider/external retrieval, real observation or source read, operational retention, runtime/persistence/wiring, command/write, deployment, production, release, Pages or protected-ref authority. Controlling artifacts are `docs/raisa-practice-context-fabric-direction.md`, `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-architecture.md`, the accepted Context Fabric closeouts, `implementation_plan.md`, `orchestration/bernie_interaction_model.md` and the `raisa-practice-context-fabric` Compass horizon item. |
| Agent Execution Surface and Containment Gate direction | On 2026-08-08 Yuri accepted a hard prerequisite before any occupied Bureau receives real product-derived context or any executable tool, filesystem, database, network, credential, provider-executed tool, command-adjacent capability or reusable runtime authority. The prerequisite Context Fabric serial durability behavior slice, architectural-health review, bounded CI/lifecycle repair and the finite AES-C0 through AES-C5 sequence now pass. AES-C0 freezes six closed messages and the external deterministic capability-broker boundary. AES-C1 proves exact manifest/grant/lease/current-authority admission, default denial, revocation and budget stops. AES-C2 proves broker-owned identity, custody, dispatch-time control-state recheck and exact budget commit around one pure inert function. AES-C3 proves hostile structural rejection, opaque digest-only handling, invalid-output non-release, cumulative latching and stale binding. AES-C4 proves one exact authored-synthetic Sydney Vertex call, deterministic no-command release, consumed ledger and complete cleanup without product data or provider tools. AES-C5 proves one exact authenticated, practice-scoped, authored-synthetic application-route/PostgreSQL read followed by one minimized provider call in a separate immutable generation, with terminal ledgers and exact cleanup. Controlling artifacts are `docs/raisa-agent-execution-surface-containment-gate-plan.md`, the accepted AES-C0 through AES-C5 artifacts, the accepted architectural-health review and `implementation_plan.md`. No AES-C6 is planned or authorised. This direction grants no real-person, patient/clinical or operational product data, continuing source/provider access, credential/IAM change, filesystem capability, provider tool, command, reusable runtime, deployment, production, release, Pages or protected-ref authority. |
### Compact historical evaluation and transition state

The detailed language-evaluation chronology is indexed in `docs/handover-ledgers/bernie-language-evaluation.md`; the active acceptance documents in the Current Baton remain authoritative. The compact facts needed for present decisions are:

- LC4V6-V9 are consumed and sealed historical certification attempts. V9D1
  found 7 extraction and 14 policy gaps, repaired only reproduced ordinary
  development patient-grammar causes, passed its focused/broader gates, and
  received a fresh Gemini pass. See `lc4v9d1-sol-acceptance.md`.
- LC4R10 completed the ordinary-development reconciliation at semantic counts
  `880/814/672/154/330/835`, safety 1,152/1,152, and zero variance over
  2,304 samples. No independently supported parser gap remains.
- LC4V10 fresh certification passed with `certification_pass`: complete and every dimension 576/576,
  safety 576/576, and zero variance. The authoritative
  records are `orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md` and
  `docs/bernie-lc4v10-fresh-certification-closeout.md`. No V11 is needed or authorized; the standing fresh-version cycle is complete.
- Synthetic Silver v2 completed with 96 coherent anchors, 192/192 accepted
  candidates complete over two observations, safety 384/384, and zero variance.
  It remains frozen ordinary-development evidence, not real-world, Gold,
  protected-holdout, provider/runtime, production, or write evidence.
- T3R1 proved only provider-free projection plumbing. T3R2-T3R4 produced bounded
  synthetic comparison/preflight evidence without selecting a production
  provider. T3R5-T3R6 remain no-call/readiness policy evidence. T3R7 consumed
  11/48 exact Sydney synthetic calls and stopped without retry on its first
  schema-invalid response; unused calls carry no authority.
- The provider lane remains paused. The T3R6 US synthetic-development policy
  begins no earlier than 2026-10-16 but grants no continuing call, prompt,
  cost, runtime, PII, production, or write authority. Australian production/PII
  review remains no earlier than 2027 unless Yuri changes that policy.
- The post-certification security transition, protected holdout history,
  appointment-call provenance stop, historical-diary limits, synthetic corpus
  lineage, exact hashes, worker failures/recoveries, and provider observations
  remain available through the Current Baton documents and topic ledgers. They
  are historical context and do not broaden current authority.
## 4. Authority Allocation

This section overrides conflicting historical text in archives, ledgers, packets, or older Ariadne documents.

- **GPT Sol** is Conductor, sprint planner, architecture and acceptance owner, recovery owner, and protected integrator.
- **DeepSeek V4 Flash/high via Claude Code `--bare`** is the preferred economical bounded implementation/test worker. Launcher: `scripts/ariadne_deepseek_claude.py`.
- **Gemini 3.6 Flash/high via Antigravity** is the preferred independent veto reviewer. Launcher: `scripts/ariadne_antigravity.py`.
- **DeepSeek Pro is not the Conductor** and must not be launched for planning, allocation, acceptance revision, or routine fallback without a new explicit instruction from Yuri.
- Deep Code is a real-TTY fallback only, not the default DeepSeek transport.
- Claude/Fable/Opus and native Codex workers are leverage- and availability-gated options. They never receive integration authority.
- No external worker or consultant may certify its own corpus, accept its own implementation, move the baton, or push protected refs.

The versioned execution contract is `orchestration/harness_settings/verifier_execution_policy.yaml`. It fixes Sol at High for routine bounded work and Extra High for material architecture, authority, security, provider, production or release decisions; DeepSeek V4 Flash/high owns bounded separable implementation/test artifacts; and Gemini 3.6 Flash/high owns fresh independent review only. External model review is eligible only after its deterministic gate passes.

Use workers only for bounded separable artifacts or genuine veto surfaces.
Tiny, serial, protected, or tightly coupled work may remain Sol-owned. Record
the actual worker mix and any substitution in closeout evidence.
### Worker-lane economy rule

Dispatch is an optimization, not a default. Sol keeps a task when its execution
is serial, stateful, tightly coupled to a disposable runtime/database, or small
enough that writing the worker packet plus monitoring, review, and recovery is
likely to cost as much as direct completion. This includes short live-browser
acceptance sequences whose scenarios share one mutable synthetic database.

Use DeepSeek Flash through Claude Code `--bare` when a stable, separable packet
can own a mechanical script, focused tests, fixture regeneration, or contained
repair and can return one durable artifact without acceptance judgment. Use
Gemini Flash primarily for a fresh independent veto or a genuinely separable
peer check, not as a second conductor for routine execution. A dispatch should
normally save at least one meaningful implementation/test cycle or supply
independence required by acceptance; otherwise Sol executes locally. Never
split a serial acceptance run merely to maximize worker utilization.

Native subagents follow the same rule. Sol may use them for parallel read-only
analysis, independent reproduction, or separable implementation/test artifacts
when their packet is bounded and their expected leverage exceeds briefing,
monitoring, review, and correction cost. They do not receive acceptance,
integration, baton, or protected-ref authority.
### Reasoning-level and closeout rule

Reasoning level follows decision risk; it is not a ceremonial Git gate. Sol at
High may plan and execute a frozen bounded tranche, review its own complete
evidence, integrate, commit, push through the normal protected-branch workflow,
advance the baton after acceptance, and send closeout notification. A second
Sol Extra High pass is not required merely because the implementation or
execution was performed at High.

Pause and use Extra High before:

- freezing or materially revising acceptance meaning, architecture, authority
  allocation, product policy, or user-visible behaviour;
- choosing among material privacy, protected-evidence, provider/cloud,
  production, release, migration, durable-session, security, licence, cost, or
  data-retention alternatives;
- overriding a failed gate, reconciling contradictory or incomplete evidence,
  accepting a conceptual recovery, or making a claim broader than the frozen
  evidence directly supports; or
- any point where the active plan or Yuri explicitly requires Extra High for a
  named material decision.

High remains sufficient for mechanical corrections already permitted by a
frozen plan, focused tests, deterministic harness/Playwright work, evidence
packaging, routine review, and check-gated Git closeout when no item above is
triggered. A fresh tranche chat is a context-hygiene rule, not a requirement to
change reasoning level or agent identity.

### Flash complexity and correction-loop rule

DeepSeek Flash is the default for stable, bounded implementation contracts,
mechanical test generation, fixture regeneration, and contained code repair. It
does not own cross-sprint taxonomy, frozen-selection meaning, acceptance
semantics, authority allocation, protected-evidence policy, or reconciliation
of several historical evidence layers. Those remain Sol work.

Classify a rejected Flash candidate before redispatch:

- a mechanical defect (for example a missing hash, file, assertion, or
  one-line verifier guard) may receive at most one bounded same-lane revision;
- a conceptual defect involving category meaning, frozen population versus
  corpus-wide population, acceptance criteria, provenance, or authority moves
  immediately to Sol's recovery lease without another Flash correction loop;
- any failed bounded revision ends external correction for that lane. Preserve
  the failure and scope breaches, then recover under Sol ownership or select a
  genuinely different implementation resource when new implementation work has
  clear leverage.

Large cached-token totals, elapsed time, or model reputation do not alone prove
inability. The stop signal is the kind and recurrence of acceptance error.
Gemini Flash remains a fresh-context independent veto after recovered material
changes; it does not inherit the failed worker's acceptance framing.
## 5. Protected Evidence and Closed Gates

### Protected holdouts v1-v10

Protected holdouts v1, v2, and v3 remain sealed. Protected holdouts v1-v10
share the same no-access boundary. Do not open, enumerate, list, search, import, run, regenerate,
evaluate, hash-check, infer labels from, or tune against any protected fixture,
support module, authoring surface, manifest, seal, receipt, or per-case report.
The committed v2 aggregate report and aggregate closeout are the only v2
evidence available for planning; only the committed aggregate report, closeout,
and Sol acceptance are available for v3-v10 planning. Historical metadata-
enumeration incidents do not authorize reuse.

V10 is consumed and sealed; only its committed aggregate report, closeout,
and Sol acceptance are available for future planning.

Yuri preauthorized successive genuinely fresh holdout versions beginning with
V10 until certification passed, progress stalled, or a material fork arose.
V10 passed, so that standing fresh-version cycle is complete and grants no V11.
Development work uses only ordinary development, Silver/pending, newly authored
synthetic, or otherwise explicitly authorized evidence.

### T3 and providers

The provider-experimentation lane is paused by Yuri without T3R7 retry. T3.1-T3.4 remain intact and blocked by default. The dedicated T3R4 and T3R7 synthetic evaluation exceptions are consumed and closed. T3R5 remains historical no-call evidence. T3R6 authorizes a US synthetic-development policy from 2026-10-16 but no continuing provider call, prompt transmission, cost acceptance, runtime, PII, or production authority. T3.5 adapters, further live calls/external prompts, raw-response persistence, provider-executed tools, promotion claims, and runtime wiring remain deferred.

### Historical diary material

Raw historical diary files may contain PHI. Keep them local and ignored under
`local_data/historical-diary-trove/`. Do not commit them, transmit them to an
external model/provider, retrieve from them at runtime, or fine-tune on them.
H15 approval is limited to the exact bounded payload in
`docs/historical-diary-trove-h15-approved-gate.json`; it does not authorize
broad-trove processing or product/runtime access.

### Product authority

Bernie may explain, clarify, read bounded context, and propose. The backend owns
identity, availability, conflicts, confirmation, writes, and audit. Do not open
API/database/GraphQL/UI/deployment/memory/RAG/write authority unless explicitly
authorized. Stage 1 permits only its local synthetic Diary/FastAPI/PostgreSQL
path: proposals do not mutate; staff confirms; the existing REST command may
create exactly one appointment, audit, idempotency result, and typed receipt.
Stage 3A additionally permits only its isolated typed/local/authored-synthetic
fixture study and a separately labelled rerun of that already accepted local
confirmation path. Its fixture browser has no mutation or event-runtime
authority. The accepted Stage 3B readiness descendant adds only its
provider-free sidecar, closed anonymous structured export, automated rendered
rehearsal and disposable authored-synthetic product-task harness. It does not
add participant recruitment, product mutation, provider, production,
deployment or release authority. The accepted Yuri-only internal descendant
adds only one concise acknowledgement, in-memory structured self-review,
optional bounded product notes, explicit local JSON export and the same
provider-disabled disposable harness. It creates no participant evidence and
does not open the paused external study, integrated Bureau implementation,
provider, voice, product write, real-data, production, deployment or release
boundary.

## 6. User Decision Boundaries

### Standing uninterrupted-development authority

Yuri's 2026-08-04 decision, recorded at Continuity 208 / Compass 189,
supersedes routine gate-by-gate permission pauses. Continue through each
dependency-satisfied gate when an active accepted plan freezes its scope,
inputs/outputs, material data/provider/cost posture, side effects, forbidden
surfaces, acceptance, recovery, evidence label and claim boundary.

Yuri clarified on 2026-08-05 that a planned gate's materiality never creates a
pause by itself and that the absence of a pre-existing descendant plan is not a
user decision fork. When the accepted sequence identifies the next gate, Sol
must derive and freeze its narrowest fail-closed architecture-strengthening
boundary, then plan, dispatch and execute it without seeking ceremonial fresh
authority. Older plan language requiring a `fresh decision`, `fresh authority`
or a `material decision` for a planned gate is satisfied by this standing
authority. The exact boundary remains an engineering and evidence control, not
a permission checkpoint.

This covers planning, dispatch, implementation, tests, review, recovery,
acceptance, task-branch publication and the next qualifying gate.
It never self-authorises a generic future candidate or erases an explicit closure.
When those recorded conditions hold, continue without another permission request.

Pause only for a genuinely non-inferable unplanned fork between materially
different user-owned outcomes, a human-only external choice/action, conflicting
evidence that changes acceptance, exhausted bounded recovery, protected-
evidence access, work outside the accepted programme sequence, or explicit
user pause. Gate materiality, missing descendant paperwork, older fresh-
authority language, routine failures, rehydration, receipts, commits, known
next steps and passing gate closeouts are not permission gates. Full policy:
`docs/ariadne-autonomous-continuation.md` and
`orchestration/harness_settings/autonomous_continuation.yaml`.

At every successful tranche closeout, report in concise lay terms what became
possible, what remains deliberately closed, and any issue the tranche exposed
or resolved. This report is a progress marker, not a handback or permission
gate: when no user-attention condition above is active, begin the next planned
tranche immediately after the report without waiting for acknowledgement.

Yuri's durable tranche mailbox is `orchestration/human_inbox/yuri/`. Before
each task-branch closeout commit and publication, write one dated Markdown
message there with paired lay and technical summaries, issues, deliberately
closed surfaces, the tranche's place in the overall Raisa direction, the
planned next tranche and whether Yuri's attention is genuinely required. Link
that message from the conversational closeout. The mailbox is a reporting
surface only and never overrides this baton, an accepted plan, protected
evidence, user authority or exact Git state.

When an already-authorised in-scope choice exists, choose the path that
strengthens the required architecture and occupied capability without a
routine Yuri pause. Model-required cognitive cells default to an explicit
positive bounded reasoning budget with sufficient typed-output headroom;
thinking-off is an evidence-backed task-specific exception, not the general
EMR4 intelligence posture. This preference cannot expand provider, model,
region, data, cost, authority, runtime/write, deployment/release or protected
scope.
Continue autonomously through authorised ordinary development, tests, review,
recovery, documentation, task-branch commit and push. Certification passed at
V10; no V11, synthetic v3 or frozen-v2 refinement is authorised. Stage 1 and
Stage 3A remain limited to their frozen synthetic/provider-disabled plans.
Historical Synaptic, cognitive-cell, DeepSeek, Terra/Gemini and T3R7
authorities are consumed and grant no continuing runtime or retry. Exact
chronology is in `docs/handover-ledgers/orchestration-and-agent-runtime.md` and
the named acceptance documents. The historical T3R7 rule remains: no further
provider call is authorized.
Historical Sydney Vertex and Reception One occupied authorities used only the exact Bernie keyless-ADC, `gemini-2.5-flash`, `australia-southeast1`, authored-synthetic, proofreader-gated, no-fallback/no-write envelopes recorded in the runtime ledger. Their calls and ledgers are consumed. Historical locational evidence proves configured/observed request paths, not Australian physical or sovereign processing. Codex has no credential or IAM mutation authority.
On 2026-08-11 Yuri selected that Sydney Vertex Bernie development lane as the standing default provider/model choice until he decides otherwise. This removes routine model-selection questions only: every occupied descendant still needs an exact current data, calls, cost, effect, isolation, proofreader, cleanup and claim envelope, current lifecycle/region verification and a distinct ledger.
For AES-C4 specifically, Yuri authorised the frozen one-call/no-retry USD 0.25 authored-synthetic envelope and reported the separate CLI and impersonated-ADC human authentication complete. That exact call now passes with a consumed ledger and no retry. No patient/product data, continuing provider call, provider tool, fallback, credential/IAM mutation, reusable runtime or product command is opened.
For AES-C5, Yuri selected the authenticated practice practitioner-directory GET and Reception One booking-context purpose. The exact authored-synthetic local route/PostgreSQL read and one separately brokered Sydney Vertex call now pass; both generation ledgers are consumed and cleanup is complete. No AES-C6 is planned or authorised. Any further real practice population, product-data class, reusable runtime, tool/command, deployment or production direction is a new Yuri-owned programme choice.
Stage 3B readiness is accepted, but representative participant execution is
paused and still requires reopening plus Yuri's cohort nomination. Accepted
Bureau/model-text/dual-planner/UI results remain proposal-only; a new live
isolated selection requires an exact call boundary and grants no real/product
data, confirmation, write, production, deployment or release authority.
The Hybrid Word/Reception One direction, Clinician One read-only adapter and
shared-host foundation are accepted only within their named authored-synthetic
plans. `Raisa` and `Clinician One` remain candidate names. The preserved Raisa
branding assets may inform future UI renders but grant no public rename,
trade-mark, deployment or release.
Shared application-authentication, Office-host compatibility, real-identity/
Microsoft-federation architecture and provider-free OIDC/directory lifecycle
descendants are accepted through Continuity 206 / Compass 187. EMR4 backend
identity and one server decision own authority; Microsoft/Office identity and
client claims confer none. The detailed accepted chain is indexed in the
Current Baton acceptance ledger. Live Microsoft connection, real identity
mapping, binding administration, product/clinical reads or writes,
organisational deployment and production credential lifecycle remain closed.
The Bernie/Davida seam and first five pairs pass. The Gate -1 containment and
Gate-zero shared contract also pass; every named intelligent loop remains
provider-model-required while deterministic labels, proofreading, authority,
human gates, commands and readback remain independently mandatory. For every
planned provider/data/cost, product, write, actuator, update, deployment or
release descendant, Sol freezes the narrowest architecture-strengthening
boundary and proceeds; materiality alone never returns the sequence to Yuri.
Only non-inferable competing outcomes, human-only actions, protected-evidence
access or work outside the accepted sequence require attention.
On 2026-08-03 Yuri replaced the preferred independent Antigravity verifier allocation with Gemini 3.6 Flash/high. It must use a fresh project, an exact bound non-protected worktree, the stable `gemini-3.6-flash-high` slug and explicit `high` effort. It may review repository code, diffs, tests and authored-synthetic evidence only; it receives no implementation ownership, self-acceptance, integration, baton, protected-ref, patient/clinical/product-derived data, deployment, production or release authority, and no silent model fallback is permitted. Its first live review envelope was rejected for duplicate decisions; the fail-closed single-decision repair then received one fresh exact `pass` with 25 independent tests and an unchanged clean candidate at `b439fb5c3bacc20c9b5f664b3af9322cfcdcbd3f`.
On 2026-08-03 Yuri authorised a durable agent-error register. Revision 42 records 48 bounded known incidents: 36 agent-behavior observations, three harness failures, two repository defects and seven transport timeouts. AER-0030 preserves the corrected verifier-dispatch observation method. AER-0031, AER-0034 and recurrent AER-0039 preserve separate Antigravity OAuth timeouts; AER-0039 reached no model and invoked the configured same-head independent-context fallback after one bounded retry. AER-0032 and AER-0033 preserve duplicate-decision egress failures. AER-0035 and AER-0037 preserve and mechanically reconcile verifier count/path misreports. AER-0036 and AER-0038 contain DeepSeek occupied transport timeouts without candidate admission; AER-0038 quarantines late partial source. AER-0040 records and corrects Sol's timestamp-regenerating read-only-worktree violation before review admission. AER-0041 rejects a fresh review that enumerated protected path names without opening content; the corrected review uses an exact path allowlist. AER-0042 corrects Sol's three-test direction versus 31-test Fabric/Memory review-packet substitution and reconciles `167 - 3 + 31 = 195` before final review admission. AER-0043 corrects Sol's native-worker spawn before the distinct pre-dispatch receipt, AER-0044 contains an exact-file schema query whose observed output broadened into repository search, and AER-0045 preserves the rejected under-frozen observation-to-signal plan plus its five exact pre-implementation corrections. AER-0046 preserves the rejected observation mapper's canonical-fixture overfit and proofreader bypass. AER-0047 preserves the first Sol recovery's one-sided mapping of admission's two-sided clock-skew domain. AER-0048 preserves the rejected generic safety-critical arrays in the first durability architecture; its exact ordered schema tuples, 28 adversarial mutations and fresh 160-check veto close only through the named Sol recovery lease at `14e8d3257b9531601260bef094c73e08a9c7b92d`. No rejected candidate was admitted and no incident remains open. AER-0027 preserves the rejected C5 worker self-pass and closes only through the named Sol recovery lease and fresh veto. AER-0028 preserves the Windows teardown defect and exact port-ownership correction. AER-0029 separately preserves and corrects the ADC-versus-gcloud credential-store guidance error; it is not operator error. Earlier provenance remains in revisions 2-41. Corrections never erase immutable failure evidence; the register remains a workflow-improvement control, not model fine-tuning or a comparative provider/agent score. Future qualifying rejected reviews, worktree postcondition failures, command-scope breaches, evidence conflicts or worker transports without a closeout must be registered before a corrected attempt is accepted.
The historical Gate-zero pause above is superseded; Gate zero now passes at Continuity 209 / Compass 190 under Yuri's standing authority. Older fresh-decision text does not bind a planned gate: Sol derives and records its exact
fail-closed boundary, then continues without repeat consent. Protected evidence,
human-only external actions and genuinely non-inferable alternatives remain the
exceptions.
Yuri then selected the exact historical Sydney Vertex development envelope for
paired A3/B3: `gemini-2.5-flash`, `bernie-emr4-dev`, the named Bernie service
account, existing keyless impersonated ADC, `australia-southeast1`, newly
authored synthetic data, no fallback, at most four calls and USD 1. The first
occupied launch stopped at `impersonated_adc_refresh_failed` before any prompt
or candidate-runtime provider call. Yuri restored the existing ADC, the fresh
read-only preflight passed, and one Rayleen primary call then ended at
`provider_content_invalid` before extraction or proofreading. It released
nothing and Davida did not start. The evidence-only terminal reconciliation,
fresh-worktree checkout correction and Review 9 veto now pass; no correction,
repeat, Davida or request-contract change is authorised. Codex still has no
credential, IAM or cloud-configuration mutation authority.

Yuri's later standing recovery authority opened one distinct A3/B3 request-
contract descendant without changing that outer envelope. At exact source HEAD
`a70d06fd047733bac9a72921d0fd2f81e1b946db`, the positive 1,024-thinking/
2,048-output request passed fresh source review and read-only preflight, then
admitted Rayleen before Davida with exactly two calls and USD 0.50 reserved.
Both releases are authored-synthetic and advisory-only; the ledgers are
consumed, no call followed success and all runtime resources are absent. This
new result supersedes the historical no-repeat pause for its completed
  descendant. A4 now passes its authored-synthetic development-only product-
  read/UI descendant, the paired A5.1/B4.1 command runtime passes, and C4's
  provider-free authored-synthetic actuator simulator passes after the named
  Sol recovery lease and fresh exact-head veto. Exact C5 planning, source
  recovery and the bounded occupied rehearsal now pass; the provider-free
  Practice Context Fabric contract, Current operational weave, patient-free
  temporal weave, intent-shaped retrieval, model-required intent shaping and
  the unmounted Rayleen A4 source adapter and provider-free
  invalidation/reassembly seam and fresh-generation rehearsal also pass. The
  architecture-only default-off live-source observation boundary, its provider-free unmounted authored-synthetic observation-to-signal rehearsal, source-specific durability architecture and pure durability state-machine rehearsal also pass.
  Migration-and-transaction architecture, function-and-trigger-body architecture, the recovered inert PostgreSQL-16 DDL rehearsal, the disposable parse-and-catalogue rehearsal and the twenty-scenario serial database behavior/transaction rehearsal now pass. The bounded architectural-health pulse and its CI/lifecycle conformance repair plus the finite AES-C0 through AES-C5 sequence now pass; AES-C5 consumed one authenticated authored-synthetic product-route read and one separately brokered Sydney Vertex call with terminal ledgers and exact cleanup. No AES-C6 is planned or authorised. A further real-data, reusable-runtime, tool/command, deployment or production descendant is a new Yuri-owned programme choice.
Dependabot alerts 5 and 8-15 and CodeQL alerts 295, 272 and 268 have exact evidence-backed dismissed readback matching the durable register under Yuri's consumed disposition authority. Dependabot alert 17 was created after that snapshot: it is registered as `SF-0020`, statically `not_actionable`, and remains native-open/`needs_review`; no dismissal is authorised. PR 70 CodeQL warning 543 and high alert 544 are fixed by source changes and fresh native readback without dismissal; alert 544 is registered as remediated `SF-0021`. The affected development-only dependency resolutions remain in the lockfile; do not force dependency overrides, erase instance history or broaden any disposition without a new register revision and current evidence.

At that historical point, revision 48 recorded 50 bounded incidents: 38 agent-
behavior observations, three harness failures, two repository defects and
seven transport timeouts. AER-0050 preserves three
rejected durability implementation candidates and closes only after exact
structural, retention-authority, effect, count and rotation-chronology recovery
passed a fresh 29-attack, 207-check veto at
`95a2ed5e960c58686262b5e82ce2e89354a3860a`. No incident remains open, and the
passing rehearsal grants only the provider-free unmounted migration-and-
transaction architecture tranche.

## 7. Ariadne Operating Rules
### Receipts and workspace isolation

Run `scripts/ariadne_orchestrator_preflight.py` for new-session, post-compaction, pre-plan, pre-dispatch, verifier-acceptance, integration, commit, and push continuation events as required by the active profile. A receipt is evidence only; it cannot spawn workers, realign worktrees, integrate, commit, or push.
The receipt builder emits `rehydrated_from_receipt`, the exact five named
`rehydration_sources` and their non-empty `source_evidence` directly. Do not
manually patch those fields. A missing source or missing evidence returns
`revision_required` and forbids dispatch.
Every worker packet must name its worktree, branch, source head, owned files, forbidden surfaces, tests, durable artifact, and decision format. Observe protected-master cleanliness before, during, and after external worker runs.

### Deterministic-first verification

Run the exact candidate, authority packet, settings fingerprint, focused tests,
static/filesystem checks and clean-worktree gates before deciding whether a
risk-triggered external verifier is needed. A deterministic failure means no
external model call. Gemini review uses a fresh project and exact read-only
non-protected worktree, excludes prior review artifacts, admits exactly one
terminal decision and must leave HEAD and the worktree unchanged.

Qualifying rejected reviews, worktree postcondition failures, command-scope
breaches, evidence conflicts and worker transports without a non-transferable
closeout must enter the closed agent-error register before a corrected attempt
is accepted. Preserve origin distinctions; do not attribute transport, harness,
repository or operator incidents to agent reasoning. Generate recurrence only
from the full origin/category/role/resource/signature composite.

### Recovery lease
Worker closeout provenance is non-transferable. Sol may adopt failed worker source only as an untrusted candidate under `docs/ariadne-orchestrator-recovery-lease.md`. Preserve the failure, record every Sol amendment, run risk-proportional independent verification, and apply the Flash complexity and correction-loop rule before same-lane redispatch.

### Tests
Repository pytest processes that load `tests/conftest.py` share a PostgreSQL test schema and must run serially. Do not parallelize them merely because file lists differ. Historical committed-report equality nodes may be deselected only when the active acceptance document records why their frozen artifacts must not be regenerated.
The earlier over-broad interpretation-runtime isolation assertion has been repaired and is no longer an accepted baseline failure. Runtime/provider readiness nevertheless remains deliberately blocked until a separately authorised product connection.

### Browser automation and evidence
Acceptance depends on the exercised path and interception boundary, not on whether the browser is driven interactively or by a script. A task-scoped Playwright script is equivalent to interactive browser control when it drives a real browser through the ordinary UI, makes real non-intercepted calls to the intended local or deployed backend, and records required screenshots, sanitized outcomes, and backend/database readback. Prefer a script for repeatable stable scenarios; interactive control remains useful for exploration and visual diagnosis.

The evidence label remains strict:

- no API interception or mocked transport, real local UI/backend/database: `live_local_browser_backend_postgres`;
- direct real local HTTP/backend/database without a browser: `live_local_backend_postgres`;
- `page.route(...)`, fixture responses, mocked APIs, or equivalent interception: `route_intercepted_browser`.

Do not call route-intercepted evidence live. A Playwright script must not bypass explicit staff confirmation, substitute internal page functions for visible UI action, or fabricate receipt/readback evidence. Protected-safe scripts use the active exact-path and exact-node allowlist and do not introduce repository-wide discovery. Browser processes and PostgreSQL-loading pytest processes remain serial when they share mutable runtime state.

### Git and handoff
- Sprint 156 status/delete confirm client header emission is the accepted historical closeout marker.
- Preserve unrelated user changes in a dirty tree.
- Workers commit only to disposable/task branches and do not push protected refs.
- Sol High may commit and push its own accepted bounded work without an additional Extra High pass. An accurately labelled partial result may be committed to a task branch/PR, but protected integration, baton movement, and a final product-stage claim wait for applicable acceptance gates.
- Sol reviews and integrates through a check-gated pull request, then advances `master` and `handoff/current`.
- Fetch and verify origin immediately before push. Never force protected refs.
- GitHub Pages deploys only from canonical `master`; a stale worker deployment can overwrite the live artifact.

Useful commands:
```powershell
python scripts\agent_worktrees.py handin
python scripts\agent_worktrees.py sync --fetch
python scripts\agent_worktrees.py submit --agent claude --commit-message "..." --message "..."
python scripts\agent_worktrees.py handoff --agent codex --commit-message "..." --message "..."
```

## 8. Product and Environment Guardrails

- Word Online is the target Office surface and is stricter than desktop Word about OOXML element order.
- The native browser Diary supersedes the retired Word-table diary for interactive scheduling.
- Use API Spine contracts under `docs/api-spine/` whenever work touches GraphQL/read models, REST/OpenAPI commands, proposals/confirmations, Access AI, context frames, manifests, async contracts, audit, security, or idempotency.
- Production settings fail closed for default secrets and CORS is allowlisted. PostgreSQL RLS, comprehensive audit logging, JWT storage hardening, and field-level encryption remain structural security work.

Local orientation:
```powershell
.\run_dev.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
.\.venv\Scripts\python.exe -m alembic upgrade head
```
Taskpane source is `EMR4 Sidebar/src/taskpane/`; synchronize its published `docs/taskpane/` copy with `sync_taskpane.py`. Command Centre lives in `docs/command-centre/`; native Diary assets live in `docs/diary/`.

## 9. Historical and Topic Index

The complete pre-compaction handover is preserved byte-for-byte at:

- `docs/handover-archive/AGENTS-2026-07-15-pre-compaction.md`
- manifest: `docs/handover-archive/AGENTS-2026-07-15-pre-compaction.manifest.json`
- SHA-256: `ad86887db6b640bdeac40111aa9f83c9e422f4ccab5f2eb61334a49449126b4c`; source Git blob: `ace44b93507737141a5e44004c24a087755561af`
- source commit: `6801fb214d41c41c14f94b90642f6a7d9ee0a6d6`
Every paragraph removed during the 2026-07-15 compaction remains in that immutable, manifest-tested snapshot. Archived history does not override this live file.
Topic ledgers:
- `docs/handover-ledgers/current-baton-acceptance-index.md`
- manifest: `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`
- `docs/handover-ledgers/bernie-language-evaluation.md`
- `docs/handover-ledgers/orchestration-and-agent-runtime.md`
- `docs/handover-ledgers/historical-diary-and-interpretation.md`
- `docs/handover-ledgers/product-platform-api-and-security.md`
- index: `docs/handover-ledgers/README.md`
- compaction closeout: `docs/handover-compaction-2026-07-15.md`
Use the ledgers for authoritative closeouts and policy documents. Use the immutable snapshot only for full historical reconstruction, retired workflow details, or provenance not yet represented in a dedicated closeout.
## 10. Updating This Handover
Update this live file whenever current authority, baton state, protected boundaries, active acceptance, or next work changes. Put chronology in the appropriate topic ledger or sprint closeout rather than expanding this file indefinitely.
Before ending a material session:
1. run relevant checks and `git diff --check`;
2. update active acceptance and the Current Baton;
3. commit intentional changes;
4. align and push `master` plus `handoff/current`; and
5. verify origin refs and a clean integration worktree; and
6. send the non-PHI Pushover closeout ping with `scripts/notify_sprint_closeout.py`, stating whether the sprint engine is continuing or paused and the concrete next work or pause reason. After a successful continuing closeout ping, immediately perform the next tranche's fresh five-source rehydration and begin that already-authorised work; do not yield or end solely because the preceding tranche closed. Yield only for a genuine user-attention gate or an unavoidable fresh-context handoff, and resume the authorised next tranche without asking Yuri to repeat permission. Also send one compact non-PHI Pushover alert whenever work pauses at a genuine user-attention gate; do not ping for routine progress. Report delivery failure explicitly in-thread.
7. commit a dated message to `orchestration/human_inbox/yuri/` and give Yuri the linked paired lay and technical closeout summary (capability gained, issues, deliberately closed surfaces, place in the Raisa direction and planned next tranche), then immediately continue to the next dependency-satisfied planned tranche unless his attention is genuinely required.
The user can say **"update the handover doc"** at any time to trigger a live baton refresh.
*Compacted 2026-07-15 after LC4R8. Full predecessor integrity is enforced by `tests/test_agents_handover_archive.py`.*
