# Threat-model delta: preterminal observability corrected-veto recovery

Date: 2026-08-20

Timestamp: 2026-08-20T06:39:41.6215071+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-preterminal-observability-corrected-veto-recovery`

| Threat | Fail-closed control |
|---|---|
| A pasted authorization code enters repository or logs | Do not retain, print, stage or pass it; test the reauthorised existing CLI session first. |
| The rejected first pass is silently accepted | Its orchestrator disposition remains `revision_required`; only a new corrected receipt can satisfy the gate. |
| Repeated 403 calls consume resources | Permit one post-reauthorisation verifier attempt; another predecision 403 stops without fallback. |
| The candidate moves during review recovery | Bind exact HEAD `b5f0bc0d823a1c8009f3bb49efcc9a588b9703ab`, clean worktree and exact manifest digest before and after review. |
| The false 137-test count recurs | Packet states the exact 85 total and seven per-module counts. |
| Review recovery becomes implementation authority | No candidate, product, test, native Harness, DeepSeek, broker, Docker/database or protected-ref change is allowed. |

All predecessor evidence and closed product/data/deployment boundaries remain
unchanged.
