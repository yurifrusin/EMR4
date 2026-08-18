# Gemini 3.7 Flash/high veto — default-off ordinary-practice check-in admission-control architecture

Date: 2026-08-19

Timestamp: 2026-08-19T03:06:52.3757568+10:00 (Australia/Brisbane)

Decision owner: GPT Sol. Reviewer role: one fresh Tier-2 independent read-only
veto after deterministic admission.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\check-in-admission-architecture-gemini-752b521c`
- Branch: `codex/review-check-in-admission-architecture-752b521c`
- HEAD: `752b521c59f5b44bf46de0cf776a33ac74b8134d`
- Tranche base: `062f5fb12eb82eab6ec570abea56ad1bd9a7b304`
- Required model: `gemini-3.7-flash-high`
- Required effort: `high`

First read `AGENTS.md` completely and perform the five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Review only. This packet, the clean-worktree preflight,
the exact command manifest and the fresh orchestrator receipt bind the
candidate.

## Review question

Return `pass` only if the architecture closes exactly the three accepted design
gaps while remaining default-off: ordinary admission is a separate typed
authority record, kill/rollback semantics cannot re-enable, telemetry remains
non-PHI and non-actuating, and no current product/API/configuration or live
clockwork authority changes.

## Exact allowlist

Read only the exact
`062f5fb12eb82eab6ec570abea56ad1bd9a7b304..752b521c59f5b44bf46de0cf776a33ac74b8134d`
diff and these paths. Do not inspect `docs/branding/`, unrelated untracked
files, product/patient/clinical data or protected/historical record content.

- `AGENTS.md`
- `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-plan.md`
- `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md`
- `docs/security/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-threat-model-delta.md`
- `docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md`
- `docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-closeout.md`
- `orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md`
- `orchestration/agent_inbox/codex/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-preplanning-runtime-state.json`
- `orchestration/agent_inbox/codex/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-preplanning-receipt.json`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json`
- `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.schema.json`
- `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/provider-free-architecture-evidence.json`
- `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/architecture-report.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/config.py`
- `app/routers/appointments.py`
- `app/services/appointment_check_in_product_adapter.py`
- `scripts/raisa_provider_free_default_off_ordinary_practice_check_in_admission_control_architecture.py`
- `tests/test_raisa_provider_free_default_off_ordinary_practice_check_in_admission_control_architecture.py`
- `tests/test_raisa_provider_free_read_only_ordinary_practice_check_in_admission_readiness_review_plan.py`

## Required challenges

1. Verify the exact branch, full 40-character HEAD, clean worktree, protected
   refs and exact allowlisted diff before and after review.
2. Confirm all eleven source bindings match and the contract is the one typed
   normative reading from which evidence is derived.
3. Challenge lane separation: synthetic allowlist membership, synthetic
   receipts, caller claims, GraphQL, events, models and WorkOrders must never
   imply ordinary admission; simultaneous or absent lanes must deny.
4. Challenge the four-state graph and six allowed transitions. There must be no
   resume edge, rollback-to-active edge, absent-to-active edge or in-place
   reactivation.
5. Confirm the global one-way kill switch denies both lanes and cannot clear
   automatically, via telemetry, or within the same generation.
6. Confirm future state changes are unmounted REST/OpenAPI commands requiring a
   current human, separate operations role, server scope, correlation,
   idempotency, expected versions, append-only audit, bounded receipt and a
   resolved lowercase 40-character Git object. A seven-character object must
   fail. GraphQL and async events remain non-authoritative.
7. Confirm the three operational-evidence gaps remain mandatory and cannot be
   replaced with authored-synthetic proof.
8. Challenge the exact five metric families, closed label domains, forbidden
   identifier/body fields and six critical alerts. No telemetry or alert may
   actuate, retry, activate, withdraw or clear.
9. Confirm 390 hostile mutations fail with zero escapes and no product,
   configuration, OpenAPI, database, route, provider, deployment, Pages,
   protected-ref or live-clockwork change is claimed.
10. Execute only the exact nine-command manifest. Every command must pass and
    the worktree must remain clean.

## Forbidden actions

Do not edit, format, commit, push, install, write source, invoke any provider
other than this exact Gemini review, access product/database/browser surfaces,
inspect `docs/branding/`, move refs, deploy, publish or accept your own output.

## Decision rule

Return one schema-constrained terminal `pass` only if every required challenge
passes without a P0-P2 finding, authority widening, false claim, command
failure or dirty postcondition. Otherwise return `revision_required` with exact
allowlisted-path evidence. Do not emit a second decision.
