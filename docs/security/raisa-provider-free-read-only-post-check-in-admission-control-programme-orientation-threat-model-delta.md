# Threat-model delta — post-check-in admission-control programme orientation

Date: 2026-08-22

Timestamp: 2026-08-22T22:38:25.4278425+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-read-only-post-check-in-admission-control-programme-orientation`

## Boundary

This tranche reads repository-static, non-protected acceptance evidence and
selects one successor. It changes no product, API, manifest, configuration,
route, client, database or runtime source and performs no provider call.

## Threats and controls

| Threat | Control |
|---|---|
| Repeating an accepted tranche under a new conversation | Require exact operation-ID non-membership in the accepted Continuity graph before successor selection. |
| Treating architecture as occupied operational proof | Keep `satisfied_contract_only` distinct from `operational_evidence_gap`; blocked database attempts cannot close recovery. |
| Treating a Harness-side target contract as the product artifact | Prove the exact API-Spine target is absent and describe the validator only as a frozen closed form. |
| Reviving the failed Harness sequence as an implementation lane | Record DeepSeek declined, native Harness unavailable and Claude historical-only in the receipt, plan and report. |
| Incidental ordinary-practice activation | Require zero active ordinary records, activation authority false, unchanged feature flag/allowlist and no product/configuration edits. |
| Conflating generic status `Arrived`, dedicated check-in and waiting-area movement | Preserve the accepted dedicated command identity and the separate later client/waiting-area gate. |
| Turning YAML/JSON policy into command authority | Classify the proposed runbook as declarative API-Spine input; runtime typed code remains the only future enforcement surface. |
| Bypassing rollback uncertainty with blind retry | Preserve `deny_success_no_blind_retry`; the failed unknown-response evidence remains an open operational gap. |
| Leaking PHI, secrets or protected evidence | Use only named repository-static sources; forbid historical Diary, product data, environment values, raw secrets, providers and protected fixtures. |
| Protected or unrelated workspace mutation | Verify protected refs, preserve `docs/branding/` and all unrelated untracked files, and stage explicit paths only. |

## Residual risk

The selected successor, if admitted, will still be a default-off declarative
contract rather than an exercised rollout. Unknown-commit recovery, live secret
custody, operational monitoring, activation and client cutover remain separately
closed. No production-readiness claim is supported.
