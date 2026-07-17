# Secure SDLC and Diary hardening — Final purple acceptance

Date: 2026-07-17

Final code candidate: `73eba9c144ac1a41be5b2e150b9d2c1c7c77675c`

DECISION: pass

## Final security decision

The material cross-layer tranche is accepted for protected integration. The
final Diary bootstrap invokes its dispatcher unconditionally; the dispatcher
can enter the local mock-only loader only through the local smoke capability,
while the authenticated loader independently returns before live rendering
when no token exists. The scheduled refresh follows the same dispatcher.
This removes the user-controlled authentication conditions rather than
suppressing the scanner results.

GitHub's representative pull request passes all observed gates on the final
candidate carrier: aggregate CodeQL, Analyze (Python), Analyze
(JavaScript/TypeScript), Python Security, Node manifest/security audits, and
Diary smoke. No CodeQL alert was dismissed. Dependabot alert 5 remains the one
documented moderate upstream dependency issue and was not overridden.

## Independent evidence and recovery chain

DeepSeek's original blue self-pass was rejected because it missed conceptual
materiality and evidence-binding fail-open behavior. Sol recovered it without
a correction loop. Gemini's original red review found valid gate weaknesses;
Sol repaired them. Each later changed code head invalidated the prior veto:
fresh Gemini projects reviewed `4efe9ff3`, `a248f659`, and finally
`73eba9c1`. The final project returned `DECISION: pass` without reading earlier
review outcomes.

For the final head, Gemini and Sol each reproduced 45 focused tests, all 139
Diary Playwright cases, Node syntax, and whitespace hygiene. Gemini also
traced unconditional startup, scheduled refresh, review/fixture inputs,
direct loader paths, remote/file/data/blob origins, confirmation paths,
randomness, practitioner-directory access, and selector handling without
finding an unauthenticated live-data path.

## Preserved boundaries and residual risk

The browser controls remain defence in depth. Backend authentication,
authorization, ownership, signed evidence, state/collision checks, audit, and
idempotency remain authoritative. Local file/localhost mock QA intentionally
remains available. The gate cannot infer materiality from an arbitrary diff;
Sol-owned classification, protected integration, candidate-bound evidence,
Git history, CI, and repository protection form the complete control.

Holdouts V1–V10, T3.1–T3.5, provider calls, historical data, runtime/product
wiring, database, deployment, release, and new write authority remain closed.
