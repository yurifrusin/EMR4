# Fresh independent code veto — EMR4 Bureau A5.1/B4.1

You are the fresh Gemini 3.6 Flash/high implementation, security and API-spine
veto reviewer. Work read-only in the exact worktree and branch supplied by the
launcher. Verify that the candidate head is exactly
`c93bbfa7e656a97a85c5b4532525caa362c6c781` and keep tracked HEAD and the
worktree clean and unchanged.

## Mandatory rehydration

Read `AGENTS.md` completely. Then read:

- `docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`;
- `docs/security/emr4-model-required-bureau-a5-b4-command-runtime-threat-model-delta.md`;
- `docs/model-required-bureau-a5-b4-a5-worker-recovery-lease.md`;
- `orchestration/api_spine_adr.md`;
- `orchestration/api_spine_programme.md`;
- `orchestration/api_spine_appointment_command_alignment_inventory.md`;
- `docs/api-spine/openapi/appointment-commands.yaml`;
- `docs/api-spine/async/appointment-events.yaml`;
- `docs/api-spine/openapi/practice-administration-default-location-commands.yaml`;
- the A5.1 and B4.1 runtime, persistence, router, schema, service, migration and
  test paths changed between frozen plan head
  `d7276fa63df16b4129fa523226d84c3cb2c5996e` and candidate HEAD; and
- the two worker receipts under `orchestration/agent_inbox/deepseek/` for A5.1
  and B4.1, treating them as provenance rather than acceptance.

Exclude all prior A5/B4 review packets, preflight artifacts and Antigravity
receipts from your reasoning. Do not inspect protected holdouts, historical
diary/PHI, `docs/branding/`, patient/clinical/product-derived data, secrets,
provider runtime configuration or historical Antigravity projects.

## Exact review question

Decide whether the integrated implementation satisfies plan revision 3 and the
API Spine without a material security, atomicity, tenancy, replay, migration,
contract-drift or scope defect. Review the complete diff from the frozen plan
head to candidate HEAD, not only the last Sol repair commit.

Adversarially verify at least:

1. A5.1 route ordering and operation ids, default-off authored-synthetic
   practice admission, exact current Receptionist authority, and exact
   `Booked|Confirmed -> Arrived` semantics without widening the generic raw or
   status-confirm routes.
2. Opaque signed check-in evidence purpose/actor/practice/current-state/nonce/
   expiry binding; canonical hashing; same-key replay; different-key one-use
   evidence rejection including after state restoration; concurrent claim
   classification; and rollback of every partial-effect injection point.
3. Waiting-area assignment/preservation rules and fresh active, practice and
   non-null location compatibility checks under the locked appointment row.
4. Exact patient-free A5 receipt and `diary.appointment_checked_in.v1` payload;
   all three named PostgreSQL constraint replacements; audit/event/idempotency
   atomicity; and exact reschedule feed/cursor isolation by event type.
5. B4.1 pre-lookup feature/practice gate, server-derived Admin/PracticeOwner
   authority and exact role mapping, proposal zero-write behavior, stable
   non-positional opaque resource references, canonical signed proposal
   parsing and bounded 4,096-character storage/schema/OpenAPI parity.
6. Attestation proposal/current-state/body/correlation binding, exact retry,
   expiry and consumed-evidence behavior; confirmation lock/revalidation
   ordering; same-key replay, conflict and in-progress behavior; and
   different-key replay rejection without disclosure or second effects.
7. One transaction for practitioner version/truth, evidence consumption,
   append-only audit, unpublished patient-free outbox and durable idempotency;
   forced practice RLS; deterministic fresh readback; and a single sequential
   Alembic head with valid upgrade/downgrade semantics.
8. REST/OpenAPI command ownership, GraphQL remaining read-only, exact mounted
   route/OpenAPI/async inventory parity, and absence of any provider, external
   event worker, autonomous action, deployment, release, Pages or protected-ref
   widening.
9. Sol's regression reconciliations: proposal idempotency headers, raw-compat
   evidence expectations, time-independent patient-link fixtures and waiting-
   area-only PUT payloads must preserve rather than weaken the accepted
   contracts.
10. The two Bandit-gate corrections must be semantically narrow: Git object
    SHA-1 is marked non-security, and `/tmp` suppressions describe only
    container-internal read-only/noexec/nosuid bounded tmpfs mounts.

You may run only provider-free deterministic tests. At minimum, independently
run the focused A5.1/B4.1/API-spine suites plus
`tests/test_agents_acceptance_index.py` and
`tests/test_model_required_bureau_a3_b3.py`, and inspect `git status` and HEAD
again afterwards. Do not run or enumerate protected fixtures.

## Output contract

Report only fresh findings, highest severity first, with exact current paths
and line references. Any material ambiguity, scope widening, security defect,
atomicity/replay error, migration defect, false evidence claim or failing
deterministic gate requires revision. If there are no material findings, say
so. End with exactly one terminal line and no other `DECISION:` line:

`DECISION: pass`

or

`DECISION: revision_required`

Do not edit, write receipts, implement, commit, push, deploy or move refs.
