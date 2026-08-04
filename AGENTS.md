# EMR4 Centaur — Live Agent Handover

> **Purpose:** This compact file is the authoritative starting point for every human or AI agent working in EMR4. Read it completely. It controls current authority, protected boundaries, baton state, and next work. Historical detail lives in the indexed ledgers and immutable snapshot below.

## 1. Project

EMR4 Centaur is an AI-native, open-source General Practice management system for Australia. FastAPI/PostgreSQL owns clinical and diary truth. Microsoft Word with an Office.js add-in is the clinical workspace, and the native browser Diary is the scheduling surface. The full phase and architecture blueprint is [`implementation_plan.md`](implementation_plan.md).
## 2. Mandatory Rehydration

At a new session, after conversation compaction/restoration, after a model/provider change, and before a new sprint plan or dispatch:

1. Read this file completely.
2. Read the active acceptance/plan documents named in the Current Baton.
3. Restore the protected-evidence and user-decision boundaries in sections 5
   and 6.
4. Verify `git status`, `HEAD`, `master`, `handoff/current`, `origin/master`, and `origin/handoff/current`.
5. Generate a fresh Ariadne orchestrator receipt naming all five sources:
   `live_handover_current_baton`, `current_authority_allocation`,
   `active_plan_and_acceptance`, `protected_evidence_boundaries`, and
   `git_refs_and_worktree`.

A conversation summary is a continuity aid only. It is never authoritative for model allocation, provider transport, holdout rules, write authority, or user decision boundaries. `rehydrated_from_receipt: true` without the five named sources is insufficient and must return `revision_required`.

Use a fresh chat context for each named tranche by default. The new context must
repeat this full rehydration before acting; prior-chat memory never substitutes
for the five sources. Durable decisions that must survive the handoff belong in
this file and the active plan/evidence documents. The outgoing tranche must name
its exact result, artifacts, unresolved gates, next tranche, and reasoning level.

## 3. Current Baton

| Item | Current value |
|---|---|
| Current protected-integration result | On 2026-08-02 Yuri explicitly authorised PR 74 integration and exactly one consequent public GitHub Pages rebuild. PR 74 rebase-merged at protected master `09a661cfa83559b13c438f45734403f33d1e3bbb`; Pages run `30719055657`, Node/Office security run `30719055642`, Python security run `30719055679` and CodeQL run `30719055649` all passed. CodeQL alerts 546-548 are natively `fixed` without dismissal and their bot review conversations are resolved. The repository-local outcome receipt is `orchestration/agent_inbox/codex/raisa-real-identity-microsoft-federation-protected-integration-receipt.json`. No-`docs/**` baton PR 75 then merged at `2e34bdad732fdab32fbf778280b3d3c70d66d602`; its PR and default-branch Node/Office, Python-security and CodeQL runs all passed, it triggered no Pages run, and local/origin `master` plus `handoff/current` aligned. No further Pages rebuild is authorised. |
| Mode | Parallel-capable Ariadne workflow; protected single-track integration |
| Baton ref | `handoff/current` |
| Active development worktree | `C:\Users\sarashera\emr4` on `codex/ariadne-bernie-davida-parallel-seam`; protected integration remains closed and single-track through `master` |
| Worker worktree root | `C:\Users\sarashera\EMR4-worktrees\` |
| Required Git relation | Local/origin task refs aligned; local/origin `master` and `handoff/current` remain aligned at protected `2e34bdad732fdab32fbf778280b3d3c70d66d602`; bounded tracked task changes are permitted until closeout; user-owned untracked `docs/branding/` remains preserved and excluded |
| Conductor/integrator | GPT Sol |
| Implementation/test worker | DeepSeek V4 Flash/high through Claude Code `--bare` |
| Independent worker/reviewer | Gemini 3.6 Flash/high through a fresh Antigravity project |
| Active Ariadne descendant | Historical DeepSeek, Terra/Gemini, Gemini Developer API and Sydney Vertex failure nodes retain their immutable recorded results and consumed ledgers. Yuri subsequently authorised evidence-backed diagnose-repair-rerun cycles in the exact `gemini-2.5-flash` Sydney Vertex lane until success or bounded-option exhaustion, without changing the USD 1, provider, model, project, identity, keyless ADC, region, authored-synthetic, isolation, audit, no-fallback or no-product boundaries. The first repaired Sydney call still returned bounded HTTP 400. The next request removed the unsupported enum from the INTEGER field and used exact numeric bounds while the deterministic proofreader retained the exact integer release contract. A provider-free relay-readiness race was repaired with a connection-refused-only pre-connect retry and a distinct zero-call ledger. Occupied attempt `gemini-25-repair-002` then passed through `australia-southeast1-aiplatform.googleapis.com` using the exact Bernie impersonated ADC: HTTP 200, 1108 ms, 176 prompt tokens, 50 candidate tokens and 226 total tokens. The proofreader released exactly four grounded authored-synthetic fields with no repair. Every opened ledger is consumed, no call followed success, no fallback or external mutation occurred, and cleanup is complete. The terminal result is `ariadne_vertex_sydney_gemini_25_occupied_rehearsal_pass`, bound by Continuity graph revision 49 and Compass map revision 36. This proves the configured and observed Sydney locational request path and bounded typed release, not Australian physical or sovereign processing, production suitability, or authority for product-derived, patient, health or clinical data. |
| Active product track | Yuri accepted the strategic transition review and paused the provider lane without retry. Stages 1 and 2 passed the local synthetic provider-free appointment-create vertical and its durable authority/security foundation through protected PRs 36-39. Yuri then accepted the intent-projected, committed-event-aware conversational Diary north star and refined its fluid UX direction as a tablet-first portable projection console: conversation scopes the view, touch selects within it, and button or conversational confirmation converges on one backend-owned command path. Stage 3A passes its Yuri-only, typed, local, authored-synthetic, provider-disabled formative study. On 2026-07-20 Yuri removed the named-model dependency and authorised the bounded provider-neutral in-house meta-grid concept tranche, which passed with the typed projection grammar and implementation handoff. The bounded functional native Diary client, provider-free live-local integration, and exact combined patient/practitioner/time/duration proof all pass with desktop/tablet/phone, keyboard, privacy, interruption and ordinary-fallback evidence. On 2026-07-21 Yuri explicitly authorised the bounded committed-event runtime changes. That vertical now passes: the existing signed update-confirm path atomically appends one patient-free `diary.appointment_rescheduled` event with appointment truth, audit and idempotency completion; a default-off authenticated practice-scoped feed drives fresh authorized reads and one quiet controllable Reception One cue. Its authorised availability descendant also passes: the same signal triggers a fresh exact active-practitioner slot search, preserves a still-valid selection/proposal with fresh candidate data, clears invalid selection/proposal and stale Back history, and remains silent for other-practitioner or no-consequence changes. Reception One remains the leading provisional user-facing name while meta-grid remains the architectural/product term: many views and page-like focuses belong to one authoritative Diary. The candidate public hierarchy is explanatory `electronic medical records`, distinctive `RECEPTION ONE™`, concise umbrella `EMR`, and quiet technical/version `v4`; EMR4 remains internal nomenclature. This context grants no rename, artwork or trademark authority. Yuri then authorised Ariadne Compass Increment 2 to restore programme orientation. It passes as a revision-bound, repository-local, read-only map of the current Reception One journey, present capability, candidate directions and Yuri-owned decisions; it has no workflow-executive authority. On 2026-07-22 Yuri authorised Ariadne's first real continuity fork. The sandbox-DAG exploration now passes as a provider-free, non-executing synaptic protocol: the orchestrator controls immutable start-up policies while bilaterally authorised leaves may exchange typed data directly, policy amendments require a new container generation, and every command-shaped candidate stops at human authority. It adds no live container, model or product actuator. Yuri then authorised the bounded Synaptic Event Router protocol descendant. It passes as repository-local authored-synthetic evidence: immutable router and node policies bilaterally permit exact control-frame steering, deterministic scope intersection fans one event to two mailboxes, replay and unrelated changes are suppressed, fresh-read grants remain inert, supersession rejects stale completion, and source-hashed dry-run manifests start nothing. On 2026-07-23 Yuri authorised the Bounded Cognitive Work Cell and Proofreader Gate descendant. It passes as a non-executing protocol: node/leaf/container/agent roles are independent, one unoccupied agent-eligible work cell emits five typed drafts, and deterministic egress proves grounding, safe repair, bounded retry, supersession, atomic release and inert human routing. On 2026-07-24 the bounded Reception One visual/interaction synthesis passed as a deterministic, unoccupied product node: it adds an integrated intent rail, truthful candidate-time projection, explicit selected-but-not-reserved boundary and responsive desktop/tablet/phone/keyboard behavior while preserving existing read, proposal, privacy, interruption and reconciliation contracts. One disposable Sydney Vertex design cell returned HTTP 200 but its draft failed the deterministic proofreader, released nothing and was not used; the request-contract-only retry was ineligible. Yuri then authorised the provider-free Stage 3B representative-staff sequence. Its readiness node now passes: the consent-gated sidecar, closed anonymous export schema, desktop/tablet/phone evidence and disposable live-local authored-synthetic task population all verify with unchanged database truth and complete owned cleanup. No participant session or threshold result exists; Yuri must nominate or schedule five to eight voluntary current or recent Australian general-practice reception staff before execution. On 2026-07-30 the provider-free Proofreader Dialogue v4 passed one closed typed correction exchange, but its two-call occupied sequence closed without a candidate reaching proofreading: the primary failed at provider schema admission and the fully regated HTTP 200 repair failed local `$.version_code` admission. Both ledgers are consumed, no value was released and any redesign or further call requires a new descendant. Voice, other event families, external event transport/workers, new appointment write authority, further providers, PII, production, deployment and release remain separately closed. |
| Antigravity independent-verifier allocation | `docs/ariadne-antigravity-gemini-36-high-verifier-allocation.md`, `docs/ariadne-antigravity-gemini-36-high-verifier-allocation-closeout.md`, `docs/ariadne-antigravity-gemini-36-high-verifier-first-review-analysis.md`, `docs/ariadne-economical-deepseek-execution.md`, `scripts/ariadne_antigravity.py`, `orchestration/harness_settings/worker_pool.yaml`, `orchestration/harness_settings/sprint_worker_policy.yaml`, `orchestration/harness_settings/transport_adapters.yaml`, `orchestration/harness_settings/security_review_protocol.yaml`, `orchestration/harness_settings/operating_model.yaml`, `orchestration/agent_inbox/antigravity/ariadne-gemini-36-high-verifier-allocation-repair-review-receipt.json`, `orchestration/agent_inbox/codex/ariadne-antigravity-gemini-36-verifier-model-change-receipt.json`, `tests/test_ariadne_antigravity.py`, `tests/test_ariadne_allocation_schemas.py`, and `tests/test_ariadne_deepseek_claude.py` |
| Ariadne agent error and correction register acceptance | `docs/ariadne-agent-error-correction-register-plan.md`, `docs/ariadne-agent-error-correction-register-revision-2.md`, `docs/ariadne-agent-error-correction-register-revision-3.md`, `docs/ariadne-agent-error-correction-register-revision-4.md`, `docs/ariadne-agent-error-correction-register-revision-5.md`, `docs/ariadne-agent-error-correction-register-revision-6.md`, `docs/ariadne-agent-error-correction-register-revision-7.md`, `docs/ariadne-agent-error-correction-register-revision-8.md`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`, `scripts/ariadne_agent_error_register.py`, `scripts/ariadne_serial_pytest.py`, `scripts/ariadne_verifier_worktree_preflight.py`, `tests/conftest.py`, `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`, `orchestration/harness_settings/verifier_execution_policy.yaml`, `tests/test_ariadne_agent_error_register.py`, `tests/test_ariadne_serial_pytest.py`, `tests/test_ariadne_verifier_execution_policy.py`, `tests/test_ariadne_verifier_worktree_preflight.py`, `scripts/compact_agents_acceptance_index.py`, `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`, `tests/test_agents_acceptance_index.py`, `orchestration/agent_inbox/codex/fifth-pair-independent-review.md`, `orchestration/agent_inbox/codex/bernie-davida-fifth-pair-antigravity-detached-branch-failure-receipt.json`, `orchestration/agent_inbox/antigravity/bernie-davida-fifth-pair-review-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-preacceptance-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-pre-verifier-acceptance-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-gate-minus-one-detached-branch-failure-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-gate-minus-one-review-claim-failure-receipt.json`, `orchestration/agent_inbox/antigravity/model-required-bureau-gate-minus-one-review-2-receipt.json`, `docs/ariadne-agent-error-correction-register-closeout.md`, and `orchestration/agent_inbox/codex/ariadne-agent-error-register-sol-acceptance.md` |
| Current Baton acceptance index | Historical and inactive acceptance lookup rows are preserved verbatim in `docs/handover-ledgers/current-baton-acceptance-index.md` and bound by `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`. The index has artifact lookup authority only and cannot override this live authority, protected boundaries, active acceptance or next work. |
| Provider-free Office directory lifecycle descendants acceptance | `docs/raisa-provider-free-office-reload-terminal-reconciliation-plan.md`, `docs/raisa-provider-free-office-reload-terminal-reconciliation-closeout.md`, `docs/raisa-provider-free-office-session-loss-reconciliation-plan.md`, `docs/raisa-provider-free-office-session-loss-reconciliation-closeout.md`, `docs/raisa-provider-free-office-cross-surface-replay-isolation-plan.md`, `docs/raisa-provider-free-office-cross-surface-replay-isolation-closeout.md`, `docs/raisa-provider-free-office-lifecycle-observability-plan.md`, `docs/raisa-provider-free-office-lifecycle-observability-closeout.md`, `docs/raisa-provider-free-default-off-office-consumer-adapter-plan.md`, `docs/raisa-provider-free-default-off-office-consumer-adapter-closeout.md`, `docs/security/raisa-provider-free-office-directory-lifecycle-descendants-threat-model-delta.md`, `app/services/application_auth_office_consumer.py`, `scripts/raisa_provider_free_office_practitioner_directory_consumer.py`, `orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/taskpane.js`, `scripts/raisa_provider_free_office_directory_lifecycle_descendants_acceptance.py`, `orchestration/continuity/raisa-provider-free-office-directory-lifecycle-descendants/provider-free-acceptance-evidence.json`, `orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-postcompaction-receipt.json`, `orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-preacceptance-receipt.json`, `orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-precommit-receipt.json`, `orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-sol-acceptance.md`, `scripts/raisa_provider_free_office_directory_lifecycle_descendants_continuity_update.py`, `tests/test_raisa_provider_free_office_directory_lifecycle_descendants.py`, and `tests/test_raisa_provider_free_office_directory_lifecycle_descendants_continuity.py` |
| Bernie/Davida parallel seam acceptance | `docs/bernie-davida-parallel-seam-plan.md`, `docs/bernie-davida-shared-agent-boundary.md`, `docs/security/bernie-davida-parallel-seam-threat-model-delta.md`, `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json`, `orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json`, `tests/test_bernie_davida_parallel_seam.py`, `orchestration/agent_inbox/codex/bernie-davida-parallel-seam-gemini-review-packet.md`, `orchestration/agent_inbox/antigravity/bernie-davida-parallel-seam-review-receipt.json`, `orchestration/agent_inbox/codex/bernie-davida-parallel-seam-preacceptance-receipt.json`, `docs/bernie-davida-parallel-seam-closeout.md`, and `orchestration/agent_inbox/codex/bernie-davida-parallel-seam-sol-acceptance.md` |
| Native-Diary application-session practitioner composition architecture acceptance | `docs/raisa-provider-free-native-diary-application-session-practitioner-composition-plan.md`, `docs/raisa-provider-free-native-diary-application-session-practitioner-composition-design.md`, `docs/security/raisa-provider-free-native-diary-application-session-practitioner-composition-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition/composition-contract.json`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition/composition-contract.schema.json`, `tests/test_raisa_provider_free_native_diary_application_session_practitioner_composition.py`, `orchestration/agent_inbox/deepseek/diary-application-session-architecture-worker-receipt.json`, `orchestration/agent_inbox/deepseek/diary-application-session-schema-hardening-worker-receipt.json`, `orchestration/agent_inbox/antigravity/diary-application-session-architecture-review-2-receipt.json`, `orchestration/agent_inbox/codex/bernie-davida-parallel-architecture-preacceptance-receipt.json`, `docs/raisa-provider-free-native-diary-application-session-practitioner-composition-closeout.md`, and `orchestration/agent_inbox/codex/raisa-native-diary-application-session-architecture-sol-acceptance.md` |
| Davida practice-administration boundary acceptance | `docs/davida-practice-administration-boundary-plan.md`, `docs/davida-practice-administration-boundary-design.md`, `docs/security/davida-practice-administration-boundary-threat-model-delta.md`, `orchestration/continuity/davida-practice-administration-boundary/capability-contract.json`, `orchestration/continuity/davida-practice-administration-boundary/capability-contract.schema.json`, `tests/test_davida_practice_administration_boundary.py`, `orchestration/agent_inbox/deepseek/davida-practice-administration-architecture-worker-receipt.json`, `orchestration/agent_inbox/deepseek/davida-practice-administration-schema-hardening-worker-receipt.json`, `orchestration/agent_inbox/antigravity/davida-practice-administration-architecture-review-receipt.json`, `orchestration/agent_inbox/antigravity/davida-practice-administration-architecture-review-2-receipt.json`, `orchestration/agent_inbox/codex/bernie-davida-parallel-architecture-preacceptance-receipt.json`, `docs/davida-practice-administration-boundary-closeout.md`, and `orchestration/agent_inbox/codex/davida-practice-administration-boundary-sol-acceptance.md` |
| Native-Diary application-session practitioner runtime acceptance | `app/graphql/native_diary_application_session_practitioner.py`, `docs/raisa-provider-free-native-diary-application-session-practitioner-runtime-plan.md`, `docs/security/raisa-provider-free-native-diary-application-session-practitioner-runtime-threat-model-delta.md`, `scripts/raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py`, `tests/test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-runtime/live-local-backend-postgres-evidence.json`, `orchestration/agent_inbox/deepseek/native-diary-unmounted-application-session-adapter-worker-receipt.json`, `orchestration/agent_inbox/deepseek/native-diary-unmounted-application-session-adapter-seed-repair-worker-receipt.json`, `orchestration/agent_inbox/antigravity/native-diary-unmounted-application-session-adapter-review-receipt.json`, `orchestration/agent_inbox/antigravity/native-diary-unmounted-application-session-adapter-review-2-receipt.json`, `orchestration/agent_inbox/antigravity/native-diary-unmounted-application-session-adapter-review-3-receipt.json`, `docs/raisa-provider-free-native-diary-application-session-practitioner-runtime-closeout.md`, and `orchestration/agent_inbox/codex/native-diary-unmounted-application-session-adapter-sol-acceptance.md` |
| Davida provider-free practice-administration pure-read acceptance | `app/schemas/practice_administration.py`, `app/services/practice/active_location_directory_read.py`, `app/services/practice/practice_administration_context_desk.py`, `docs/davida-provider-free-practice-administration-pure-read-plan.md`, `docs/davida-provider-free-practice-administration-pure-read-design.md`, `docs/security/davida-provider-free-practice-administration-pure-read-threat-model-delta.md`, `orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.json`, `orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.schema.json`, `scripts/davida_provider_free_practice_administration_pure_read_acceptance.py`, `tests/test_davida_provider_free_practice_administration_pure_read.py`, `orchestration/continuity/davida-provider-free-practice-administration-pure-read/provider-free-in-process-backend-postgres-evidence.json`, `orchestration/agent_inbox/deepseek/davida-provider-free-practice-administration-pure-read-worker-receipt.json`, `orchestration/agent_inbox/deepseek/davida-provider-free-practice-administration-pure-read-sql-capture-repair-worker-receipt.json`, `orchestration/agent_inbox/antigravity/davida-pure-read-context-desk-review-receipt.json`, `docs/davida-provider-free-practice-administration-pure-read-closeout.md`, and `orchestration/agent_inbox/codex/davida-provider-free-practice-administration-pure-read-sol-acceptance.md` |
| Native-Diary practitioner reconciliation acceptance | `docs/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-plan.md`, `docs/security/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/client-reconciler.mjs`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/provider-free-client-state-machine-evidence.json`, `scripts/raisa_provider_free_native_diary_application_session_practitioner_reconciliation_acceptance.mjs`, `tests/test_raisa_provider_free_native_diary_application_session_practitioner_reconciliation.py`, `orchestration/agent_inbox/codex/native-diary-stale-response-reconciliation-recovery-receipt.json`, `orchestration/agent_inbox/codex/native-diary-stale-response-reconciliation-independent-sol-review.md`, `docs/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-closeout.md`, and `orchestration/agent_inbox/codex/native-diary-stale-response-reconciliation-sol-acceptance.md` |
| Davida practice-administration advisory acceptance | `app/schemas/practice_administration_advisory.py`, `app/services/practice/practice_administration_advisory_proofreader.py`, `docs/davida-provider-free-practice-administration-advisory-plan.md`, `docs/davida-provider-free-practice-administration-advisory-design.md`, `docs/security/davida-provider-free-practice-administration-advisory-threat-model-delta.md`, `orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.json`, `orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.schema.json`, `orchestration/continuity/davida-provider-free-practice-administration-advisory/provider-free-unoccupied-evidence.json`, `scripts/davida_provider_free_practice_administration_advisory_acceptance.py`, `tests/test_davida_provider_free_practice_administration_advisory.py`, `orchestration/agent_inbox/codex/davida-advisory-proofreader-envelope-recovery-receipt.json`, `orchestration/agent_inbox/antigravity/davida-advisory-proofreader-envelope-review-2-receipt.json`, `docs/davida-provider-free-practice-administration-advisory-closeout.md`, and `orchestration/agent_inbox/codex/davida-advisory-proofreader-envelope-sol-acceptance.md` |
| Native-Diary default-off application-session UI composition acceptance | `docs/diary/application-session-practitioner-directory.mjs`, `docs/diary/application-session-practitioner-reconciler.mjs`, `docs/diary/diary.html`, `docs/diary/diary.js`, `docs/raisa-provider-free-native-diary-application-session-ui-composition-plan.md`, `docs/security/raisa-provider-free-native-diary-application-session-ui-composition-threat-model-delta.md`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition/ui-composition-contract.json`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition/ui-composition-contract.schema.json`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition/provider-free-ui-composition-evidence.json`, `scripts/raisa_provider_free_native_diary_application_session_ui_composition_acceptance.mjs`, `tests/test_raisa_provider_free_native_diary_application_session_ui_composition.py`, `orchestration/agent_inbox/codex/native-diary-default-off-ui-composition-gemini-review-receipt.json`, `docs/raisa-provider-free-native-diary-application-session-ui-composition-closeout.md`, and `orchestration/agent_inbox/codex/native-diary-default-off-ui-composition-sol-acceptance.md` |
| Davida default-location dry-run proposal acceptance | `app/schemas/practice_administration_default_location_proposal.py`, `app/services/practice/practice_administration_default_location_dry_run.py`, `docs/davida-provider-free-practice-administration-default-location-dry-run-plan.md`, `docs/davida-provider-free-practice-administration-default-location-dry-run-design.md`, `docs/security/davida-provider-free-practice-administration-default-location-dry-run-threat-model-delta.md`, `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.json`, `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.schema.json`, `orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/provider-free-acceptance-evidence.json`, `scripts/davida_provider_free_practice_administration_default_location_dry_run_acceptance.py`, `tests/test_davida_provider_free_practice_administration_default_location_dry_run.py`, `orchestration/agent_inbox/codex/davida-default-location-dry-run-gemini-review-receipt.json`, `orchestration/agent_inbox/codex/davida-default-location-dry-run-gemini-review-receipt-2.json`, `docs/davida-provider-free-practice-administration-default-location-dry-run-closeout.md`, and `orchestration/agent_inbox/codex/davida-default-location-dry-run-sol-acceptance.md` |
| Native-Diary route-intercepted browser acceptance | `docs/raisa-provider-free-native-diary-application-session-route-intercepted-browser-plan.md`, `docs/security/raisa-provider-free-native-diary-application-session-route-intercepted-browser-threat-model-delta.md`, `scripts/raisa_provider_free_native_diary_application_session_route_intercepted_browser_acceptance.py`, `orchestration/continuity/raisa-provider-free-native-diary-application-session-route-intercepted-browser/route-intercepted-browser-evidence.json`, `tests/test_raisa_provider_free_native_diary_application_session_route_intercepted_browser.py`, `docs/raisa-provider-free-native-diary-application-session-route-intercepted-browser-closeout.md`, and `orchestration/agent_inbox/codex/native-diary-route-intercepted-browser-sol-acceptance.md` |
| Davida default-location command-boundary acceptance | `docs/davida-practice-administration-default-location-command-boundary-plan.md`, `docs/davida-practice-administration-default-location-command-boundary-design.md`, `docs/security/davida-practice-administration-default-location-command-boundary-threat-model-delta.md`, `docs/api-spine/openapi/practice-administration-default-location-commands.yaml`, `orchestration/continuity/davida-practice-administration-default-location-command-boundary/command-boundary-contract.json`, `orchestration/continuity/davida-practice-administration-default-location-command-boundary/command-boundary-contract.schema.json`, `orchestration/continuity/davida-practice-administration-default-location-command-boundary/architecture-acceptance-evidence.json`, `tests/test_davida_practice_administration_default_location_command_boundary.py`, `docs/davida-practice-administration-default-location-command-boundary-closeout.md`, and `orchestration/agent_inbox/codex/davida-default-location-command-boundary-sol-acceptance.md` |
| Bernie/Davida fifth-pair acceptance | `docs/bernie-davida-fifth-pair-closeout.md`, `orchestration/agent_inbox/codex/fifth-pair-independent-review.md`, `orchestration/agent_inbox/codex/bernie-davida-fifth-pair-antigravity-detached-branch-failure-receipt.json`, `orchestration/agent_inbox/codex/bernie-davida-fifth-pair-gemini-review-packet.md`, `orchestration/agent_inbox/antigravity/bernie-davida-fifth-pair-review-receipt.json`, and `orchestration/agent_inbox/codex/bernie-davida-fifth-pair-sol-acceptance.md` |
| Model-required Bureau architecture and paused development plan | `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`, `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`, `docs/security/emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md`, `implementation_plan.md`, `orchestration/bernie_interaction_model.md`, `orchestration/agent_inbox/codex/rayleen-self-healing-architecture-preplan-runtime-state.json`, `orchestration/agent_inbox/codex/rayleen-self-healing-architecture-preplan-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-preacceptance-runtime-state.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-preacceptance-receipt.json`, `orchestration/agent_inbox/codex/model-required-bureau-architecture-pre-verifier-acceptance-runtime-state.json`, and `orchestration/agent_inbox/codex/model-required-bureau-architecture-pre-verifier-acceptance-receipt.json` |
| Model-required Bureau Gate -1 acceptance | `docs/security/hardening/model-required-bureau-gate-minus-one/hardening.json`, `docs/security/hardening/model-required-bureau-gate-minus-one/hardening.md`, `docs/security/hardening/model-required-bureau-gate-minus-one/proposals/`, `docs/security/hardening/model-required-bureau-gate-minus-one/diagrams/`, `docs/security/emr4-model-required-bureaus-gate-minus-one-threat-model-delta.md`, `orchestration/continuity/model-required-bureau-gate-minus-one/provider-free-acceptance-evidence.json`, `scripts/model_required_bureau_gate_minus_one_acceptance.py`, `tests/test_model_required_bureau_gate_minus_one.py`, `orchestration/agent_inbox/codex/model-required-bureau-gate-minus-one-gemini-review-packet-2.md`, `orchestration/agent_inbox/antigravity/model-required-bureau-gate-minus-one-review-2-receipt.json`, `docs/emr4-model-required-bureau-gate-minus-one-closeout.md`, `orchestration/agent_inbox/codex/model-required-bureau-gate-minus-one-sol-acceptance.md`, `scripts/model_required_bureau_gate_minus_one_continuity_update.py`, and `tests/test_model_required_bureau_gate_minus_one_continuity.py` |
| Model-required Bureau Gate zero acceptance | `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`, `docs/security/emr4-model-required-bureau-gate-zero-threat-model-delta.md`, `orchestration/continuity/model-required-bureau-gate-zero/`, `scripts/model_required_bureau_gate_zero_acceptance.py`, `tests/test_model_required_bureau_gate_zero.py`, `orchestration/agent_inbox/antigravity/model-required-bureau-gate-zero-review-receipt.json`, `docs/emr4-model-required-bureau-gate-zero-closeout.md`, `orchestration/agent_inbox/codex/model-required-bureau-gate-zero-sol-acceptance.md`, `scripts/model_required_bureau_gate_zero_continuity_update.py`, and `tests/test_model_required_bureau_gate_zero_continuity.py` |
| Current result | Yuri restored the existing Bernie impersonated ADC and every fresh read-only control passed. The reviewed exact A3/B3 source then sent one authored-synthetic Rayleen primary request through Vertex AI `gemini-2.5-flash`, project `bernie-emr4-dev` and `australia-southeast1`. Its child ledger consumed one call, but the provider response failed broker content-shape admission at `provider_content_invalid` before extraction or proofreading. Nothing was released and Davida did not start. AER-0017 preserves the outer-harness interruption and exact split. The provider-free terminal finalizer has now reconciled the parent to one reserved and one consumed call at USD 0.25, emitted terminal no-release attempt/tranche evidence, proved current exact runtime absence and stopped before any further lane. It made zero provider calls. Deterministic acceptance passes with one historical candidate-runtime call and zero acceptance-runtime calls; fresh exact-HEAD independent veto remains pending. Checkpoint: `docs/emr4-model-required-bureau-a3-b3-terminal-rejection-checkpoint.md`. |
| Next implementation | Commit the reconciled terminal evidence and deterministic acceptance, then run a fresh exact-HEAD Gemini 3.6 Flash/high veto. On pass, close AER-0017, record Sol acceptance and publish only the explicit task paths. Never repeat Rayleen primary, open its correction turn or start Davida under the current authority. Any request-contract change, including a `thinkingConfig` change, or any further provider call is a new material Yuri decision. A4/A5/B4, C4, product/runtime/data/write surfaces, deployment, release, Pages and protected refs remain closed. Preserve and exclude `docs/branding/` and the four existing Consultant/Gate-minus-one pre-push files. |
### Compact historical evaluation and transition state

The detailed language-evaluation chronology is indexed in `docs/handover-ledgers/bernie-language-evaluation.md`; the active acceptance
documents in the Current Baton remain authoritative. The compact facts needed
for present decisions are:

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

This section overrides conflicting historical text in archives, ledgers,
packets, or older Ariadne documents.

- **GPT Sol** is Conductor, sprint planner, architecture and acceptance owner,
  recovery owner, and protected integrator.
- **DeepSeek V4 Flash/high via Claude Code `--bare`** is the preferred economical bounded implementation/test worker. Launcher: `scripts/ariadne_deepseek_claude.py`.
- **Gemini 3.6 Flash/high via Antigravity** is the preferred independent veto reviewer. Launcher: `scripts/ariadne_antigravity.py`.
- **DeepSeek Pro is not the Conductor** and must not be launched for planning,
  allocation, acceptance revision, or routine fallback without a new explicit
  instruction from Yuri.
- Deep Code is a real-TTY fallback only, not the default DeepSeek transport.
- Claude/Fable/Opus and native Codex workers are leverage- and
  availability-gated options. They never receive integration authority.
- No external worker or consultant may certify its own corpus, accept its own
  implementation, move the baton, or push protected refs.

The versioned execution contract is
`orchestration/harness_settings/verifier_execution_policy.yaml`. It fixes Sol
at High for routine bounded work and Extra High for material architecture,
authority, security, provider, production or release decisions; DeepSeek V4
Flash/high owns bounded separable implementation/test artifacts; and Gemini
3.6 Flash/high owns fresh independent review only. External model review is
eligible only after its deterministic gate passes.

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

This covers planning, dispatch, implementation, tests, review, recovery,
acceptance, task-branch publication and the next qualifying gate.
It never self-authorises a generic future candidate or erases an explicit closure.
When those recorded conditions hold, continue without another permission request.

Pause only for an unplanned material fork, missing user-only choice/action,
conflicting evidence that changes acceptance, exhausted bounded recovery,
scope/protected-evidence expansion, or explicit user pause. Routine failures,
rehydration, receipts, commits, known next steps and passing gate closeouts are
not permission gates. Full policy: `docs/ariadne-autonomous-continuation.md` and
`orchestration/harness_settings/autonomous_continuation.yaml`.

Continue autonomously through ordinary development-only analysis,
implementation, tests, review, recovery, documentation, commit, and push. The
completed fresh-certification and v2 authorizations grant no V11, synthetic v3,
or frozen-v2 refinement. Yuri's 2026-07-18 Stage 1 authorization permits only
the tranches and confirmed synthetic appointment-create path in its frozen
plan. Yuri's 2026-07-19 Stage 3A authorization permits only the Yuri-only,
typed, local, authored-synthetic, provider-disabled formative protocol in
`docs/bernie-stage3a-yuri-formative-validation-plan.md`, including its narrow
logged correction authority.

The 2026-07-22/23 Synaptic Router, Bounded Cognitive Work Cell, scripted cell,
real-isolation and bounded agent-admission authorities are fully defined by
their Current Baton plans. Their work is consumed and grants no continuing
model, provider, container, network, secret, database, product, event-feed,
mailbox, human-gate or command runtime.

The DeepSeek result remains `ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required`;
its occupied-process authority is consumed before any provider request; do not retry.
Terra/Gemini authorities and ledgers are also consumed. Diagnostic hardening
changed only repository-local contracts and evidence. No provider retry,
credential, container or product authority remains. Exact chronology is in
`docs/handover-ledgers/orchestration-and-agent-runtime.md` and the named acceptance documents. The historical T3R7 rule remains: no further provider call is authorized.

The Sydney Vertex `gemini-2.5-flash` authority was fixed to project `bernie-emr4-dev`, the exact Bernie service account, existing keyless impersonated ADC,
`australia-southeast1`, authored-synthetic data, isolated
proofreader-gated egress, no fallback and USD 1. Its successful typed-rehearsal authority is consumed. The later Reception One synthesis permitted one
disposable authored-synthetic design cell while the product UI remained
deterministic and unoccupied. That call returned HTTP 200 but its draft failed
the proofreader, released nothing and was not used; the conditional retry was
ineligible. Yuri later authorised a bounded continuing Reception One Model Text
Lane retry sequence under the same exact provider, model, project, identity,
keyless ADC, Sydney endpoint, authored-synthetic, isolation, proofreader, audit,
USD 1, no-fallback and no-write boundaries. Two compact-wire failures released
nothing; the third retry was admitted as a typed proposal-only result. That
authority stopped at its first admitted result and all of its ledgers are
consumed. Yuri later authorised the v5 pre-printed-form baseline, its accepted
six-case evaluation and the current twenty-four-case broad authored-synthetic
descendant under the same exact Gemini 2.5 Flash, Bernie keyless-ADC, Sydney,
proofreader, audit, USD 1, no-fallback and no-write boundary. The broad cohort
passes provider-free but its fresh occupied preflight stopped at
`impersonated_adc_refresh_failed` before any cell, ledger, prompt or provider
call. Yuri must restore the existing approved impersonated ADC before a fresh
read-only preflight; Codex may not recreate, replace or reconfigure it. No
model-connected product node, product/database/clinical/patient/command
authority, production, deployment or release is authorised. The historical
Sydney evidence proves bounded model interpretation and configured/observed
locational paths, not Australian physical or sovereign processing.
Stage 3B readiness is accepted, but on 2026-07-29 Yuri paused real participant execution while the product direction is simplified and the Bureau becomes experiential. The separate Yuri-only internal walkthrough is complete; its single-owner `promising_needs_revision`/`not_ready` findings create no representative result or threshold.
The provider-free integrated Bureau, its provider-free Typed
Plan Protocol descendant and the bounded authored-synthetic occupied Model
Text Lane are accepted. Yuri later authorised the minimal read-only synthetic
Diary-context bridge and the exact default-off dual-planner product-context
runtime. That runtime is now accepted with deterministic planning as the
default and one exact, closed, authored-synthetic occupied Sydney result; its
provider-call authority is consumed. The accepted route remains proposal-only
and grants no real or product-derived data, confirmation, write, production,
deployment or release authority. Its provider-free development UI descendant
is now accepted: the visible selector defaults to Standard, the browser
receives only proofreader-admitted typed proposal fields plus bounded
non-secret provenance, and disabled isolated selection fails closed without
fallback. A live isolated request initiated through that control is a new
occupied-provider result and requires fresh exact call authority. External
participant execution requires the accepted product revisions, an explicit
reopening and Yuri's later nomination or scheduling of a voluntary cohort.
On 2026-07-31 Yuri selected the Hybrid Word/Reception One direction; its provider-free contextual launch, compact companion, supervised installed-Word companion exercise and shared host foundation are accepted. The foundation inventories the earlier clinician/scribe and Reception One paths and classifies desktop/web/mobile capabilities without granting product authority. The first Clinician One adapter and one real installed-Word selection check are also accepted: a single-use, explicit, authored-synthetic, exact-current-selection read creates only a bounded typed in-memory context frame and exposes no document write, patient, provider, backend, command or clinical authority.
`Raisa` and `Clinician One` remain candidate names. On 2026-08-01 Yuri authorised the concurrently supplied Raisa branding assets for use in future UI renders; that permission does not grant a public rename, domain, ASIC, trade-mark, deployment or release action. Reception One must remain one backend-owned auditable system exposed through role-scoped receptionist, doctor and future patient surfaces. Future online booking and Rayleen arrival registration converge on the same truth; no third-party product may become the primary patient surface or a parallel source. Raisa is cloud-first practice management as a service; any future local model is a subordinate edge, not another clinical/reception system.
This grants no current patient client or identity, online-booking, Rayleen, arrival-write, local-model, provider, voice, clinical action, appointment command, production or release authority. The exact non-loopback Sydney development host and one task-specific signed-in personal Word Online authored-synthetic companion check are accepted under their frozen zero-authority plans. The repository-local shared EMR4 application-authentication and clinician-role architecture is accepted: EMR4 backend identity and one server decision own session, revocation, role, practice scope and required audit across desktop Word, Word Online and native Diary, while Microsoft/Office identity and client claims confer no authority. Its route-free authored-synthetic in-memory runtime, five-table PostgreSQL descendant, exact NOLOGIN capability role, seven default-off secure synthetic routes and operational-hardening descendant are accepted. The latest shared-auth proof adds only a separate finite-connection LOGIN, exact pool `SET ROLE`, strict one-hop proxy trust, bounded per-process rate admission and HMAC-only retained denial audit with complete disposable cleanup. The security-finding-governance descendant is accepted and protected-integrated: it adds only repository owner/SLA/register rules, exact native alert dispositions and daily workflow definitions now present on the default branch; no scheduled-run result is yet claimed. The provider-free authored-synthetic Office cookie-compatibility descendant is accepted under `docs/raisa-shared-application-auth-office-cookie-compatibility-plan.md`: independent in-memory sessions passed their exact lifecycle once in installed Word and Word Online through the reserved ephemeral development relay, then the relay, harness, listeners and developer registration were removed. Its separately authorised PostgreSQL-backed descendant is also accepted under `docs/raisa-shared-application-auth-postgresql-office-host-compatibility-plan.md`: the same independent real-host lifecycles passed through the disposable local PostgreSQL coordinator, separate finite LOGIN, exact NOLOGIN capability role, forced RLS and retained denial audit, followed by complete database, role, process, listener and desktop-registration cleanup. Yuri then authorised the architecture-only real-identity/Microsoft-federation boundary and its next two logical descendants. They pass as a tenant-specific organisational Entra/prebinding architecture, a default-off route-free provider-free authored-synthetic admission runtime, and a reversible two-table HMAC-only PostgreSQL binding/audit foundation with database uniqueness, terminal revocation, same-transaction audit, forced RLS and complete disposable cleanup. PR 74 protected-integrated that result at `09a661cfa83559b13c438f45734403f33d1e3bbb`; exactly one authorised Pages rebuild and all default-branch security gates passed. Yuri has now authorised the architecture-only maintained OIDC verifier, least-privilege provider-to-practice bootstrap and application-session bridge design. These results and authority do not establish a live Microsoft call, real identity mapping, login/callback or binding command route, product-derived read, organisational Office deployment, distributed abuse resistance, production key/credential/monitoring lifecycle, broader cloud resource, document read/write, command or real-data authority. Protected integration of the new architecture and any further Pages rebuild remain separately closed. Every material identity, product, deployment, production and release step remains a fresh decision.
The architecture-only maintained OIDC verifier, least-privilege bootstrap and session-bridge authority is consumed by the accepted parent design. Yuri then authorised the recommended two-component correction and verifier dependency review. That authority is consumed by the accepted MSAL 1.37.0 protocol/Authlib 1.7.2 plus JOSE RFC 1.7.4 verification split, exact pins, `form_post` contract and seventeen-case provider-free evidence. Yuri then authorised its next candidate; that authority is consumed by the accepted default-off route-free adapter, encrypted process-local one-use attempt store, exact state-schema reconciliation and twenty-five-case provider-free fault matrix. Yuri then authorised the described PostgreSQL successor; that authority is consumed by the accepted authored-synthetic forced-RLS attempt table, bounded versioned keyrings, exact committed `DELETE ... RETURNING`, NOLOGIN select/insert/delete capability role and disposable live-local PostgreSQL acceptance with complete database/role cleanup. Yuri then authorised its operational connection candidate; that authority is consumed by the accepted finite membership-only LOGIN contract, verified pool checkout/reset lifecycle, credential-free bounded key-reference provider and disposable live-local PostgreSQL acceptance with complete database/two-role cleanup. Yuri then authorised the three logical provider-free descendants: mounted start/callback transport; HMAC-only binding resolution plus the 60-second admission-grant boundary; and atomic one-use grant redemption into the accepted application-session runtime. Their authorities are consumed by the accepted sequence at Continuity 199 / Compass 180. Yuri selected the provider-free product direction; that authority is consumed by the accepted unmounted, active-only, exact-column practitioner-directory read at Continuity 200 / Compass 181. Yuri then authorised and supervised the provider-free Office consumer; that authority is consumed by the accepted installed Word and Word Online result at Continuity 201 / Compass 182. Yuri also authorised five clear provider-free descendants along Sol's recommended path; all five are now consumed by the accepted reload/history/retry, session-loss, cross-surface replay, sanitized-observability and unmounted-adapter sequence at Continuity 206 / Compass 187. The architecture-only Bernie/Davida parallel seam and its first five pairs now pass. The fifth Diary result is exactly route-intercepted authored-synthetic Chromium evidence with no live backend/database claim. The fifth Davida result is a non-executing proposal-to-confirm REST boundary with actual confirmation/apply/write still closed. On 2026-08-04 Yuri approved the model-required, deterministic-authority Bureau doctrine and its paused development plan: Bernie, Rayleen, Davida and controlled recovery/update must each use an accepted provider model for intelligent dialogue and candidate formation, while typed context, deterministic proofreading, backend authority, human gates, commands and readback remain independently mandatory. Foundational deterministic safety automation and ordinary/manual PMS controls may continue during provider outage, but no equivalent agentic result may be silently substituted. Yuri then explicitly authorised Gate -1. That architecture-only authority is consumed by the accepted 21-source adversarial review at Continuity 207 / Compass 188, which requires deterministic label/capability flow and one-shot brokered cognitive cells while proving no runtime implementation. The earlier pause remains in force: Gate zero requires fresh Yuri authority before any further worker or lane dispatch. Material forks, provider/model/data/cost/licence, real identity/data, Rayleen product access, administrative or recovery writes, actuators, external update ingestion, cloud/IAM/deployment/production/release/protected actions, protected evidence and economically preferable manual intervention return to Yuri. Live Microsoft connection, real identity and internal principal truth, binding administration, patient/clinical or broader product access, product commands/writes, protected integration and any further Pages rebuild remain closed.
On 2026-08-03 Yuri replaced the preferred independent Antigravity verifier allocation with Gemini 3.6 Flash/high. It must use a fresh project, an exact bound non-protected worktree, the stable `gemini-3.6-flash-high` slug and explicit `high` effort. It may review repository code, diffs, tests and authored-synthetic evidence only; it receives no implementation ownership, self-acceptance, integration, baton, protected-ref, patient/clinical/product-derived data, deployment, production or release authority, and no silent model fallback is permitted. Its first live review envelope was rejected for duplicate decisions; the fail-closed single-decision repair then received one fresh exact `pass` with 25 independent tests and an unchanged clean candidate at `b439fb5c3bacc20c9b5f664b3af9322cfcdcbd3f`.
On 2026-08-03 Yuri authorised a durable agent-error register. Revision 9 candidate records 17 bounded known incidents: 13 agent-behavior observations, three harness failures and one transport timeout, with AER-0017 open pending fresh independent acceptance after successful evidence-only reconciliation and deterministic acceptance. Corrections never erase immutable failure evidence and recurrence is keyed by the full classification composite. Two exact two-occurrence patterns now exist: duplicate verifier terminal decisions and detached verifier worktrees. AER-0014 activates an executable exact-HEAD/clean/non-protected-branch preflight before verifier receipts or launches. AER-0015 preserves the first Gate -1 review's transport-accounting error. AER-0016 preserves the preflight-blocked A3/B3 reservation, and AER-0017 preserves the provider-contacted terminal child/parent accounting split and adds evidence-only reconciliation. The register drives a controlled correction loop: preserve, classify, apply a narrow control, regress it mechanically, then admit a corrected attempt only after the applicable deterministic and independent gates pass. It is evidence-backed harness learning, not autonomous model fine-tuning or comparative provider/agent quality scoring. Future qualifying rejected reviews, worktree postcondition failures, command-scope breaches, evidence conflicts or worker transports without a closeout must be registered before a corrected attempt is accepted.
The historical Gate-zero pause above is superseded; Gate zero now passes at
Continuity 209 / Compass 190 under Yuri's standing authority. Older fresh-decision text binds only unresolved material boundaries
(including sealed/protected evidence, unspecified provider/data/cost/write/
release scope or external authority), not routine permission checkpoints. Once
an active accepted plan resolves one exactly, continue without repeat consent.

Yuri then selected the exact historical Sydney Vertex development envelope for
paired A3/B3: `gemini-2.5-flash`, `bernie-emr4-dev`, the named Bernie service
account, existing keyless impersonated ADC, `australia-southeast1`, newly
authored synthetic data, no fallback, at most four calls and USD 1. The first
occupied launch stopped at `impersonated_adc_refresh_failed` before any prompt
or candidate-runtime provider call. Yuri restored the existing ADC, the fresh
read-only preflight passed, and one Rayleen primary call then ended at
`provider_content_invalid` before extraction or proofreading. It released
nothing and Davida did not start. Current authority is evidence-only terminal
reconciliation; no correction, repeat, Davida or request-contract change is
authorised. Codex still has no credential, IAM or cloud-configuration mutation
authority.

Dependabot alerts 5 and 8-15 and CodeQL alerts 295, 272 and 268 have exact evidence-backed dismissed readback matching the durable register under Yuri's consumed disposition authority. Dependabot alert 17 was created after that snapshot: it is registered as `SF-0020`, statically `not_actionable`, and remains native-open/`needs_review`; no dismissal is authorised. PR 70 CodeQL warning 543 and high alert 544 are fixed by source changes and fresh native readback without dismissal; alert 544 is registered as remediated `SF-0021`. The affected development-only dependency resolutions remain in the lockfile; do not force dependency overrides, erase instance history or broaden any disposition without a new register revision and current evidence.

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
The user can say **"update the handover doc"** at any time to trigger a live baton refresh.
---
*Compacted 2026-07-15 after LC4R8. Full predecessor integrity is enforced by `tests/test_agents_handover_archive.py`.*
