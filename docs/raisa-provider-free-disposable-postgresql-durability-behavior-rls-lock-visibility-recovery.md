# Provider-free durability behavior RLS lock-visibility recovery

Date: 2026-08-09

Status: bounded structural recovery candidate; behavior runtime remains closed

## Observed failure and diagnosis

Behavior attempt 023 stopped at `BTR-E01` with `CF004` in
`register_observer_generation_v1` line 81, admitted zero of the frozen twenty
scenarios and removed its exact owned container with absence verified.

The bounded diagnosis replaced only the two lock-path `CF004` messages in an
ephemeral in-memory function body, ran exact `BTR-E01` in one newly owned
networkless PostgreSQL 16 container and persisted no raw error. It proved:

- the lifecycle principal's plain stream-head `SELECT` saw exactly one row;
- the exact lifecycle binding was allowed; and
- the otherwise identical `SELECT ... FOR UPDATE` saw no row.

The diagnostic container was removed and exact-ID absence was verified. The
receipt is
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-failure-023-rls-lock-diagnosis-receipt.json`.

## PostgreSQL cause

PostgreSQL applies both the `SELECT` policy and the applicable `UPDATE USING`
policy to rows selected with `FOR UPDATE` or `FOR SHARE`. The accepted
stream-head policies allowed `LIFECYCLE` in `SELECT` and `INSERT`, but allowed
only `PRODUCER` in `UPDATE USING`. The lifecycle security-definer entry point
therefore saw the existing row in its ordinary precheck and lost it only when
requesting the serialization lock.

This is the documented PostgreSQL 16 policy combination, not a missing row or
invalid binding. See the official PostgreSQL
[`CREATE POLICY`](https://www.postgresql.org/docs/16/sql-createpolicy.html)
and [privilege](https://www.postgresql.org/docs/16/ddl-priv.html)
documentation.

## Exact recovery

Change only `pol_cf_01_update` for
`context_observation_stream_head`:

- `USING` admits `PRODUCER` or `LIFECYCLE`, so the lifecycle entry point can
  lock a row it is already authorised to select;
- `WITH CHECK` remains `PRODUCER` only; and
- `context_lifecycle` retains zero direct table DML, zero direct table SELECT,
  `NOINHERIT`, `NOBYPASSRLS` and only its closed security-definer entry points.

The row lock is preserved; it is not replaced by an unlocked read. Actual
stream-head mutation remains producer-owned. The contract and hostile tests
must reject both removal of lifecycle lock visibility and addition of
lifecycle to the write check.

## Required descendant proof

Before behavior retry, the correction must pass:

1. exact structural contract/schema reseal and focused hostile tests;
2. exact function/body parent rebind without body-program change;
3. deterministic inert artifact regeneration and recognizer checks;
4. a fresh disposable PostgreSQL parse/catalogue proof;
5. exact behavior-parent rebind with the twenty scenarios and `6/4/3/4/3`
   category population unchanged;
6. the complete deterministic/hostile packet and one fresh Gemini 3.6
   Flash/high exact-HEAD veto; and
7. exactly one new networkless behavior attempt with fresh exact-ID cleanup.

Attempt 023 remains immutable. The mutable failed behavior evidence remains
unstaged until a successful run replaces it.

## Claim and authority boundary

This recovery grants only the lifecycle lock visibility required by the
already accepted serial generation-registration transaction. It grants no
direct lifecycle mutation, product or patient data, provider, operational
database, application/API/Diary wiring, watcher/listener/feed, command/write,
deployment, production, release, Pages or protected-ref authority.
