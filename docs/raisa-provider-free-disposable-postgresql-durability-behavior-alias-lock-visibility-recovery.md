# Provider-free durability behavior alias lock-visibility recovery

Date: 2026-08-09

Status: bounded structural recovery candidate; behavior runtime remains closed

## Observed failure and deterministic diagnosis

Behavior attempt 027 stopped at `BTR-E02` with `CF004` in
`project_update_confirm_reschedule_v1` line 107, admitted zero of the frozen
twenty scenarios and removed its exact owned container with absence verified.
The immutable failure evidence is
`provider-free-behavior-transaction-failure-evidence-027.json`.

No diagnostic PostgreSQL run was needed. The source-bound diagnosis proves that
line 107 is the cardinality guard immediately after the producer's exact alias
`SELECT ... FOR KEY SHARE`. The body contract requires that lock, the alias
table forces RLS, and its accepted policy set contains only `SELECT` and
`INSERT`. It contains no applicable `UPDATE USING` policy.

PostgreSQL applies both the `SELECT` policy and the applicable `UPDATE USING`
policy to rows selected with `FOR UPDATE` or `FOR SHARE`. The same rule was
already independently characterized and accepted during the stream-head
lifecycle lock recovery. The new row was therefore admitted by the insert
check but filtered from the mandatory locking reselect.

## Exact recovery

Add one alias-table policy, `pol_cf_02_update_lock`, with:

- producer-scoped session-binding `USING`, permitting only the existing
  producer entry point to see its practice/source/stream row while locking;
- the same producer binding conjoined with literal `FALSE` as `WITH CHECK`, so
  no updated row can ever pass RLS; and
- no new table grant, role membership, function grant or runtime entry point.

The alias immutability trigger, forced RLS, `NOINHERIT`, `NOBYPASSRLS`, zero
runtime-role direct table DML and producer-owned insert/reload/compare contract
remain unchanged. The lock is retained rather than replaced by an unlocked
read.

## Required descendant proof

Before another behavior attempt, the recovery must pass exact structural
contract/schema resealing and hostile tests; body-parent rebind with no body
program change; inert artifact regeneration and recognizer checks; a fresh
disposable PostgreSQL parse/catalogue characterization and exact reproduction;
behavior six-parent rebind with all twenty scenarios unchanged; the complete
deterministic packet; and one fresh Gemini 3.6 Flash/high exact-HEAD veto.

Only then may exactly one new networkless behavior attempt run in a fresh owned
container with exact-ID cleanup. Attempt 027 remains immutable and the mutable
current evidence remains unstaged.

## Claim and authority boundary

This recovery grants only lock visibility for the already accepted producer
alias transaction. It grants no alias mutation, direct table access, product
or patient data, provider, operational database, application/API/Diary wiring,
watcher/listener/feed, command/write, deployment, production, release, Pages or
protected-ref authority.
