# T3R2 Synthetic Live-Comparison Approval — Sol Acceptance

Date: 2026-07-18

Decision: `accepted_blocked_approval_packet`

## Accepted scope

Sol accepts the frozen 24-case synthetic selection, subscription-aware hard
usage ceilings, privacy/retention questions, fail-closed evidence protocol, and
Pushover sprint-closeout restoration as preparation only.

This acceptance does not approve a provider call, live adapter, subscription
retention term, model fallback, product runtime, provider tool, raw-response
persistence, promotion claim, API/database/UI change, confirmation, write,
deployment, or release.

## Evidence

- source projection:
  `sha256:c39cc71a988a425886d96ccb75ccf07a3937f5e1363899b08366319f4dd7b4bd`;
- selection:
  `sha256:7871dff782747c9aadf42aaed840b21981a37410c52862329a9e99380d31ea0e`;
- cases: 24, balanced 4 per action, 3 per dialogue form, and 12 per noise
  level;
- maximum scheduled samples: 96;
- automatic retries: false;
- provider calls performed: false;
- T3 live gate: `blocked`;
- focused verification: 24/24; combined preservation gate: 36/36; and
- Pushover credential-redacted closeout dry run: passed.

## Decision boundary

Before the first external prompt, Yuri must explicitly approve the final dated
payload after the exact resolved model identities, account retention posture,
and kill-switch verification are recorded. Subscription-plan execution may use
sample/attempt/character/token-when-available/time ceilings instead of a
precise marginal-dollar estimate. Missing cost telemetry cannot relax those
ceilings.

Protected holdouts v1-v10 and all historical/external/sensitive data remain
outside the experiment. No model may execute a tool or obtain product or write
authority.
