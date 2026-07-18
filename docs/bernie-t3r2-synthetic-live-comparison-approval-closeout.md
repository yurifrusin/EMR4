# Bernie T3R2 Synthetic Live-Comparison Approval Closeout

Date: 2026-07-18

Decision: `approval_packet_ready_calls_blocked`

## Outcome

T3R2 prepared a fail-closed approval packet for a later synthetic-only
comparison between one GPT subscription lane and one Gemini subscription lane.
No provider adapter was activated, no external prompt was sent, and the T3 live
gate remains blocked.

The packet replaces unreliable marginal-dollar budgeting with observable hard
ceilings: 24 balanced cases, two model lanes, two observations per case, 96
scheduled samples maximum, one attempt per sample, no automatic retry, bounded
prompt/response characters, provider-reported token accounting when available,
and a 120-minute wall-clock stop. Provider errors consume their scheduled
sample.

## Frozen population

The deterministic selection binds to T3R1 projection
`sha256:c39cc71a988a425886d96ccb75ccf07a3937f5e1363899b08366319f4dd7b4bd`.
Its 24 case IDs have selection hash
`sha256:7871dff782747c9aadf42aaed840b21981a37410c52862329a9e99380d31ea0e`.
The sample contains four cases for each of six actions, three for each of eight
dialogue forms, and 12 each at medium and high noise.

## Remaining approval fields

The candidate aliases are `gpt-sol` and `gemini-3.5-flash`. The exact resolved
model identities remain deliberately blank. Silent fallback is prohibited.
Before any call, the final payload still requires exact observed model
identity, subscription-account privacy/retention review, verified kill-switch
implementation, dated reviewer and expiry fields, and explicit Yuri run
approval.

Raw prompts and responses are not committed or retained locally. The proposed
durable evidence is normalized structured output, response hash, model/prompt/
tool-schema ledger, timestamps, latency, and provider-reported usage. Protected
holdouts v1-v10, historical diary material, external corpora, patient/practice
data, product runtime, provider tools, API/database/UI, confirmation, writes,
deployment, and release remain excluded.

## Pushover restoration

`scripts/notify_sprint_closeout.py` now supplies the standard Pushover-only
closeout command. It requires a compact verification summary and an explicit
engine state: continuing with named next work or paused for a concrete reason.
The live handover now requires this ping after refs are aligned. A credential-
redacted dry run succeeded; the real non-PHI ping is sent only after this
closeout is merged and origin refs are verified.

## Verification

- T3R2 packet checker: `blocked`, 24 cases, two lanes, 96 maximum samples,
  `provider_calls_performed=false`;
- Pushover closeout dry run: passed with credentials redacted;
- focused T3R2, Pushover, live-gate, T3R1, and Silver v2 tests: 24/24;
- combined focused plus handover/archive/closeout preservation gate: 36/36;
- worker mix: Sol only; no external worker or reviewer prompt was needed for
  this no-call, tightly coupled approval-boundary tranche; and
- model calls, protected access, and write authority: none.

## Disposition

The packet is ready for Yuri's decision but does not itself authorize
execution. The next implementation may build and statically test the exact
subscription-lane adapters and kill switch only after the selected transport
can supply the required identity and retention evidence. The first external
prompt remains a separate explicit approval boundary.
