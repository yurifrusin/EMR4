# Secure SDLC and Diary Hardening — Purple Acceptance

Date: 2026-07-17

Candidate: `4efe9ff3363c3f563a03a1f5bd0978998ca55d07`

DECISION: pass

## Synthesis

The security-sensitive code candidate is accepted. It hardwires a fail-closed,
risk-triggered red/blue/purple review protocol into Ariadne and removes the
four bounded Diary defence-in-depth weaknesses reproduced before repair:
non-local URL capabilities, unconstrained confirmation destinations, insecure
random fallback, and selector construction from appointment identifiers.

The original DeepSeek blue self-pass is preserved but not relied upon for
acceptance. It missed materiality and evidence-binding fail-open behavior, so
Sol rejected the conclusion and recovered under the Ariadne recovery lease
without a Flash correction loop. The original Gemini red review returned
`revision_required`; each finding is dispositioned instance-preservingly in
`security-hardening-sol-recovery.md`.

A fresh Gemini project then reviewed only the exact recovered candidate and
returned `DECISION: pass`. It reproduced the plan gate, passed the focused
44-test command, passed Node syntax, and verified the malicious-input and
preservation cases. Its observation that the gate cannot infer materiality
from an arbitrary Git diff is correct: materiality remains a Sol-owned signed
classification plus protected integration review, while the executable gate
fail-closes the declared evidence contract. The cadence ledger is likewise
hash-bound and Git-auditable, not a substitute for protected review authority.

## Sol verification

Sol independently reproduced on the exact candidate:

- 44/44 focused Python tests;
- the executable plan gate with `status: passed`, tier `dual_review`, and
  purple review required;
- `node --check docs\diary\diary.js`;
- whitespace validation over the current candidate, excluding only the two
  preserved trailing spaces in the superseded original Gemini red artifact.

The two historical whitespace findings are intentionally retained so the
failed worker artifact remains byte-preserved and its recorded SHA-256 remains
valid. They are evidence formatting only and do not occur in executable or
current acceptance material.

## Security result and residual risk

The client remains defence in depth; backend authentication, authorization,
evidence, ownership, current-state, collision, audit, and idempotency checks
remain authoritative. Local `file:` smoke is intentionally available for
static QA, approved ngrok backend suffixes remain supported, and all five
canonical signed-confirm route families remain available.

The protocol does not claim that a manifest alone can discover a dishonest
scope declaration. Protected Sol integration, immutable Git history,
candidate-bound independent evidence, required CI, and repository protection
form the complete control. No unresolved critical or high finding remains.
Holdouts V1–V10, T3.1–T3.5, providers, historical data, runtime/product wiring,
database, deployment, release, and new write authority remain closed.
