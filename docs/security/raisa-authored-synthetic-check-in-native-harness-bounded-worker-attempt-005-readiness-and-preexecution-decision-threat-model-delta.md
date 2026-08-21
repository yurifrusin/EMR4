# Threat-model delta: native Harness attempt 005 readiness decision

Date: 2026-08-21
Timestamp: 2026-08-21T18:05:30.7944376+10:00 (Australia/Brisbane)
Status: `frozen`
Reasoning level: `high`

## Scope

This delta covers one provider-free, process-free deterministic decision about
whether a separately checkpointed authored-synthetic native Harness worker
attempt 005 can be represented. It grants no occupied execution authority.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Consumed-attempt replay or evidence rewriting | Bind attempts 001-004 and all boot attempts by exact path, digest, consumed state and `resume_permitted: false`; never write those paths. |
| Repair-chain omission | Require the accepted plugin-coordinate, relative-specifier, sentinel-escape, post-sentinel and inert-task readiness artifacts and current generated-source digests as one closed inventory. |
| Readiness mistaken for execution authority | Evidence fixes `occupied_attempt_authorized: false`; execution requires a new latch, rehydration, full source resolution and fresh clockwork checkpoint. |
| Attempt identity/output collision | Fix the operation, attempt, work-order, lease, root and output roster; require every prospective path absent. |
| Hidden process or provider activity | The readiness implementation may invoke only Git and local Python validation; source/test guards forbid Node, Harness, broker credentials, provider endpoints and process launchers other than the exact Git reader. |
| Stale or abbreviated Git binding | Machine-resolve full 40-character objects, prove ancestry/alignment and reject manual ref evidence. |
| Stale clockwork lease reuse | Take one read-only reading, mark it non-reusable and require a fresh successor checkpoint. |
| Runner/tool authority widening | Digest-bind one request, one direct literal edit, exact tool view, preset roots, conclusion and terminal checks; retries/fallbacks/second workers remain zero. |
| Raw or sensitive evidence retention | Retain only accepted sanitized structured terminals and digests; do not reconstruct or persist raw streams, prompts, responses, reasoning, paths, environments or credentials. |
| Product or operational scope creep | Keep `no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`; forbid product/config/API/database/route/adapter/flag/allowlist/grammar/client/waiting-area and generic-status `Arrived` changes. |
| Protected or user-owned state movement | Keep all protected refs fixed, exclude protected evidence, preserve `docs/branding/` and all unrelated untracked files, and stage explicit paths only. |

## Residual risk and claim limit

A passing decision proves only that the repaired exact composition is
deterministically coherent enough to freeze one separately checkpointed
authored-synthetic attempt. It does not prove runner HMR, broker reachability,
DeepSeek response quality, tool execution, longitudinal reliability, product
runtime, production suitability or Australian data-processing location.
