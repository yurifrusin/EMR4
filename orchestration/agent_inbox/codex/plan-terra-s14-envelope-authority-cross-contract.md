# S14 Terra Plan - Envelope Authority Cross-Contract Hardening

Status: approved by Sol for staging execution only after integrated S13.

## Boundary

S14 independently hardens the pure Diary envelope/capability/grammar contract.
It may correct registered-name alias, author, and envelope-tier gaps exposed by
adversarial tests, including author enforcement for registered intent envelopes
without imposing an intent-tier restriction. Unknown free strings remain
compatible. No route, command, GraphQL, provider, database, client, UI,
confirmation action, deployment, or write-authority surface may change.

The prior API Steward classification carries forward: this is not a REST/OpenAPI
command or GraphQL change. GraphQL remains read-only and the existing
appointment proposal/confirmation command contracts keep their idempotency,
freshness, evidence, revalidation, and audit boundaries.

## Single Worker Lane

| Field | Value |
| --- | --- |
| Resource | `antigravity-gemini-flash-3-5-worker` |
| Model | Gemini 3.5 Flash, high reasoning |
| Transport | `agy --print` in a disposable Antigravity worktree, with captured local output and a durable repository artifact |
| Worker worktree | `C:\\Users\\sarashera\\EMR4-worktrees\\antigravity-s14-envelope-authority` |
| Worker branch | `antigravity/s14-envelope-authority` |
| Packet | `orchestration/agent_inbox/antigravity/antigravity-gemini-s14-envelope-authority.md` |
| Completion artifact | `orchestration/agent_inbox/antigravity/s14-envelope-authority-completion.md` |

Gemini owns the S14 cross-contract implementation and adversarial tests. No
DeepSeek, Conductor, or verifier is allocated: the independent model viewpoint
is the only distinct S14 need, and deterministic acceptance remains Terra-owned.

## Acceptance

1. Registered direct names and grammar aliases enforce the same author/tier
   contract where an envelope validator applies.
2. Registered intent envelopes reject unauthorized authors but do not gain a
   write, confirmation, route, or tier authority.
3. Unknown names and planned grammar verbs without a registry capability remain
   compatible and non-authoritative.
4. Cross-contract tests prove registry/grammar/envelope consistency and import
   purity, then the S13 focused plus API-Spine artifact suites pass.
5. Gemini returns one durable final artifact and local candidate commit. Terra
   accepts only after diff, deterministic tests, and closed-gate review.

S14 may integrate accepted work on this staging branch only. Protected master
and S15 remain closed until a separate Sol authorization.
