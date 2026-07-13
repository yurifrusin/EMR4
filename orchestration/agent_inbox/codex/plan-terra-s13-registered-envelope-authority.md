# S13 Terra Plan - Registered Envelope Authority

Status: approved by Sol for staging execution only.

## Boundary

Implement a pure internal Diary validation seam for registered Bernie
capability names. It may reject a registered action when its envelope type or
author conflicts with the existing capability registry. It must retain
unknown free-string action-name compatibility. No router, command handler,
provider, database, GraphQL, UI, confirmation route/action, audit-write, or
deployment behaviour may change.

The API Steward pass classifies this as a capability/authority contract change.
GraphQL remains read-only. Existing REST proposal/confirmation commands retain
their current idempotency, confirmation, freshness, revalidation, and audit
contracts; this sprint does not claim route-level enforcement or live evidence.

## Single Worker Lane

| Field | Value |
| --- | --- |
| Resource | `deepseek-flash-workers` |
| Model | `deepseek-v4-flash`, `high` |
| Transport | Detached real Deep Code PTY with shared Python/Node toolchain, atomic artifact ownership, bounded redacted transcript, and liveness observer |
| Worker worktree | `C:\\Users\\sarashera\\EMR4-worktrees\\deepcode-s13-envelope-authority` |
| Worker branch | `deepcode/s13-envelope-authority` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-flash-s13-envelope-authority.md` |
| Completion artifact | `orchestration/agent_inbox/deepcode/s13-envelope-authority-completion.md` |
| Ownership | `app/services/diary/envelope_capability_policy.py`, `app/services/diary/envelopes.py`, `app/services/diary/capability_manifest.py`, and focused tests/documentation required for that seam |

No second lane is allocated. Gemini's independent adversarial role belongs to
S14 only; a Conductor and independent verifier have no trigger in this
explicit, pure-domain S13 scope.

## Acceptance

1. Registered confirmations accept only the confirm tier and permitted author;
   registered proposals and suggestions accept only their compatible tier and
   permitted author.
2. Unknown free-string envelope action names remain accepted.
3. Existing envelope, grammar, capability-manifest, action-boundary,
   action-route-contract, action-route-coverage, workflow-chain, and API-Spine
   artifact tests pass.
4. New code remains deterministic and has no router, database, provider,
   GraphQL, H15/H-series, trove, memory/RAG/GraphRAG, or network imports.
5. Worker returns one canonical final `STATUS: complete` artifact and receipt;
   Terra validates artifact ownership, transcript, liveness, diff, tests, and
   candidate commit before staging integration.

## Escalation And Integration

Terra may request one same-lane correction for an artifact/implementation/test
defect. Repeated worker defects, scope or authority drift, conflicting
acceptance evidence, any blocked-gate touch, or manifest variance escalates to
Sol. Terra may integrate an accepted worker candidate only onto this staging
branch. Protected master remains untouched until Sol authorizes a later exact
S13 manifest.
