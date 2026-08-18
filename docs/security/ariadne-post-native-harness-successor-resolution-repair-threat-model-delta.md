# Threat-model delta — post-native-Harness successor resolution repair

Date: 2026-08-18

Timestamp: 2026-08-18T21:31:22.5921213+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `5fab227e7a0bf1d308d1373858f490419fee660e`

## New seam

The repair changes only durable orchestration pointers after an accepted
additive Harness trial. It must distinguish an accepted product tranche from a
future successor without changing either product implementation or authority.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Repeating an already accepted mutation tranche | Compare live accepted-tranche names with `Next implementation`; fail if they intersect. Bind route acceptance to exact reviewed source `c82c3a741053a9c8da260aa62e1a968af22bb54e`. |
| Treating Harness failure as loss of route acceptance | Preserve route implementation, review, closeout and Sol acceptance unchanged except successor wording outside those accepted product claims. |
| Smuggling ordinary-practice enablement into continuity repair | Permit only a future read-only readiness-review pointer; forbid configuration, product code, route calls and product data. |
| Weakening the REST command boundary | Keep OpenAPI, request/response schema, practice scope, confirmer, idempotency, audit and event semantics byte-for-byte unchanged. |
| Using a worker to reconcile authority | Sol-only serial repair; DeepSeek, Gemini and native subagents are declined with explicit rationales. |
| Hiding the faulty closeout evidence | Preserve the committed Harness closeout and initial failed receipt; register incidents and add corrected descendants instead of rewriting history away. |
| Moving protected refs during repair | Validate all four refs before commit/closeout; no push to protected refs. |
| Touching user-owned files | Explicit-path staging only; preserve `docs/branding/` and every unrelated untracked file. |

## Residual boundary

The next readiness review may establish prerequisites only. Ordinary-practice
admission, feature enablement, product data, live route execution, client
cutover and production remain distinct future gates.
