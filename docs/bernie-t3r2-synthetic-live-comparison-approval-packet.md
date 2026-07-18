# Bernie T3R2 Synthetic Live-Comparison Approval Packet

Date: 2026-07-18

Decision: `blocked_pending_explicit_yuri_approval`

## Proposed experiment

Compare one GPT subscription lane, one Gemini subscription lane, and one
metered DeepSeek lane against a
frozen 24-case sample of the admitted synthetic Silver v2 dialogue projection.
Each model would see every case twice, producing at most 144 scheduled samples.
The sample balances all six actions, all eight dialogue forms, and medium/high
noise. It includes three clarification and three whole-action-reversal cases.

This packet prepares a decision; it does not make a provider call, implement a
live adapter, or change the blocked T3 gate.

## Subscription-aware usage controls

Precise marginal dollars are not a reliable control when execution is supplied
through subscription plans. The proposed run therefore uses hard observable
ceilings instead:

- 24 cases, three model lanes, and two observations per case: 144 samples
  maximum;
- one attempt per scheduled sample, with no automatic retries;
- 12,000 serialized prompt characters and 4,000 response characters per
  sample;
- 750,000 provider-reported tokens across the run when that measurement is
  exposed; and
- 180 minutes total wall-clock time.

A provider error consumes its scheduled sample. Missing token or cost telemetry
is recorded as unavailable and cannot silently relax the case, attempt,
character, or time ceilings. Provider-reported usage and cost are retained when
available, but neither affects correctness or safety scoring.

## Proposed model lanes

The requested lanes are OpenAI `gpt-5.6-sol` and Google
`Gemini 3.5 Flash (Medium)` using the user's existing subscription access, plus
DeepSeek `deepseek-v4-flash` at high reasoning through Claude Code `--bare`.
DeepSeek is a metered API lane rather than a subscription lane. The exact
resolved model identity must be captured before the first scheduled sample. No
silent model fallback is allowed. If a surface cannot report an exact revision,
the run may still be described by its requested and observed identity, but it
cannot support an exact reproducibility claim.

## Privacy, retention, and evidence

Only the committed synthetic Silver v2 projection may be sent. Patient or
practice data, historical diary material, external corpora, and protected
holdouts v1-v10 remain prohibited.

Raw prompts and raw responses will not be committed. The proposed durable
evidence is the normalized structured decision, response hash, exact model and
prompt/tool-schema ledger, timestamps, latency, and provider-reported usage.
Before approval, the subscription-account history and provider-retention
posture still need to be reviewed and explicitly accepted.

Correctness, safety, variance, latency, and usage remain separate measures. The
pilot cannot promote a model, certify Bernie, open product runtime, or grant
write or confirmation authority.

## Kill switch and fail-closed sequence

Before any call, the execution lane must prove that:

1. the committed approval is current and unexpired;
2. the exact provider/model ledger is complete;
3. the live T3 gate authorizes only this synthetic comparison;
4. no provider tool, runtime route, database, appointment, confirmation, audit,
   deployment, or release surface is reachable; and
5. sample, attempt, character, token-when-available, and time counters start at
   zero and stop the run at their ceilings.

Any gate drift, unscheduled call, tool/write request, retention mismatch, or
limit breach stops the run. There is no retry loop.

## Approval still required

The companion JSON remains `blocked`. A later approval must fill the exact
resolved model identities, retention review, kill-switch verification,
reviewer, approval and expiry dates, and explicit run decision. Only then may a
separate adapter-and-execution sprint be proposed. This packet itself sends no
external prompt and authorizes no provider access.
