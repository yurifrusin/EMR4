# S11 Terra Plan - Appointment API Operational Hardening

Planning mode: Terra direct under `60e832a6`; optional Conductor consultation is not triggered.

## Boundary

Harden only the existing REST confirmation command family through deterministic
contract evidence. No route behavior, schema/database, provider, deployment,
external-client, GraphQL mutation, H15/trove, memory/RAG, new write authority,
or terminal-to-active policy change is allowed.

## Lanes

1. DeepSeek Flash/high implementation: add a focused route-contract matrix test
   for the five existing confirmation handlers, asserting their existing
   `Idempotency-Key`, operation/family, request-body binding, and audit completion
   invariants; prove proposal-only and raw compatibility routes remain excluded.
2. Gemini Flash 3.5 via Antigravity: independent adversarial review of the
   matrix's coverage and closed-gate boundary, with non-overlapping review
   artifact/tests only if a material gap is found.

## Acceptance

- Existing confirmation-family and API-spine suites pass.
- New matrix is deterministic and does not dispatch HTTP commands or write data.
- No production route, schema, model, migration, OpenAPI, or policy file changes.
- `git diff --check` passes.

## Protected-master Manifest Preconditions

Source branch `codex/s10-terra-staging` must be clean, contain only accepted S11
test/review/closeout commits, and merge conflict-free against the then-current
`origin/master`. Sol alone authorizes any protected-master integration.
