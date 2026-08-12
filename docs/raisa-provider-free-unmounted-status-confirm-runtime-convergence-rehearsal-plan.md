# Provider-free unmounted status-confirm runtime convergence rehearsal plan

Date: 2026-08-12

Source HEAD: `0fe6b9bfaea2394d7fb7ebb9866bfb1fa56611cc`

Status: `frozen_for_provider_free_pure_in_memory_execution`

## Purpose

Exercise the accepted convergence architecture as a pure deterministic
in-memory state machine before any physical version storage, route or database
implementation is considered. The rehearsal may model locks, transactions,
authority changes, failures and retries as authored-synthetic state; it may not
import or execute application or database code.

## Exact accepted inputs

Only these exact non-protected artifacts may be read or content-searched:

| SHA-256 | File |
|---|---|
| `b2a645e11c28e625d13458d25cd6d6d959059897feef5f58c919ca5628e398f1` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture-plan.md` |
| `aa2eab6fddc0f8394ea3950965d525222917506a04b0ef10ab22999e2e442363` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md` |
| `b5be8112872ec870f5c889a92e2be85a09833ac72d240fd5fd7144641d5638ee` | `docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture-closeout.md` |
| `c726c94fd635727f9359ea5f707d6a4395317a7658ae795d24c99fc93c6340a5` | `orchestration/agent_inbox/codex/raisa-status-confirm-runtime-convergence-architecture-sol-acceptance.md` |
| `6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json` |
| `634f143c4dd6e29e9c796cd9c03a7ae4e91b8565ffa6e68f05ca5a8193a98fbf` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.schema.json` |
| `8e88d44b888eae461cfdbc4c0a8357e7cf60fffc9c93ee8d7436b0a4c023a750` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/provider-free-architecture-evidence.json` |
| `bddcd4120a24a5b733e1bbe6b7028d3a4f0424ba560ef47cd1a34d109034505d` | `scripts/raisa_provider_free_unmounted_status_confirm_runtime_convergence_architecture.py` |

No repository, application, `tests/`, `docs/` or orchestration-directory
content search is permitted. A need for another source requires a new plan.

## Frozen state machine

The simulator owns only authored-synthetic dictionaries for:

- one practice and one appointment at state version 7;
- one current actor/session authority record;
- an idempotency receipt map;
- an append-only audit list; and
- a mutation counter.

Each invocation follows the exact accepted order:

1. discriminate status-only intent;
2. accept only server-owned authority/session ingress;
3. model `practice -> appointment -> idempotency_record` lock acquisition;
4. recheck current authority before idempotency disclosure;
5. classify same/different digest;
6. compare locked state version;
7. compare exact warning sets;
8. verify signed evidence/session binding;
9. defer terminal re-transition;
10. stage mutation, audit and completed receipt in a private copy;
11. atomically publish the complete copy; and
12. render initial or replay delivery from stored canonical receipt bytes.

No real lock, transaction, route, database or command exists in the simulator.

## Frozen schedules

Exactly 24 schedules cover:

- clean commit;
- waiting-area discrimination, incomplete server authority, missing session,
  absent target and revoked authority;
- invalid signed evidence, session mismatch, stale version, missing/extra/
  duplicate/unknown warnings and terminal re-transition;
- failure after staged mutation, audit and completed receipt;
- response loss after commit followed by same-key retry;
- same- and different-digest two-participant races;
- authority loss and source-version loss while waiting; and
- replay attempts after current authority revocation or target removal.

Every schedule freezes participant outcomes, final appointment status/version,
durable mutation/audit/receipt counts and receipt-disclosure count.

## Acceptance

The rehearsal passes only if:

1. the fresh five-source receipt and all eight accepted-input hashes pass;
2. the closed packet and schema validate with `implementation_authorized:
   false`;
3. all 24 schedules reproduce their exact frozen results;
4. every effect-free schedule leaves appointment, audit and receipt state
   unchanged;
5. each committing schedule publishes exactly one correlated mutation, audit
   and receipt per accepted effect;
6. authority loss or target loss prevents replay/conflict disclosure;
7. response loss preserves one write set and same-key retry returns identical
   stored bytes without another effect;
8. at least 50 hostile mutations fail closed;
9. focused, dependency, API Spine, baton and whitespace gates pass; and
10. protected refs plus every unrelated untracked file remain unchanged.

## Forbidden surfaces

No application-source search/import/edit, route/database/SQL/real-lock
execution, physical version storage, migration/backfill, source/watcher/event,
provider, credential/IAM/browser authorization, network, executable tool,
product/patient data, command expansion, deployment, production, release,
Pages or protected-ref movement. Preserve and never stage `docs/branding/` or
any unrelated untracked file. Use explicit-path staging only.

## Recovery and handoff

One mechanical packet/schema/script/test correction is permitted if it changes
no schedule meaning or authority boundary. A semantic conflict stops at
`revision_required`.

On acceptance, the next candidate is a provider-free read-only physical
representability review for `appointment_state_version`, private receipt
correlation and the ordered lock boundary. It may inspect newly frozen exact
non-protected model/migration/service sources but cannot edit or execute them.
