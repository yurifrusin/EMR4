# Context Fabric behavior outbox-select and result-marker parent rebind

Date: 2026-08-08

Status: candidate deterministic behavior-parent rebind; disposable behavior
runtime remains closed pending a fresh exact-HEAD independent veto.

## Exact repaired parents

The twenty-scenario behavior contract is rebound to the accepted outbox-select
repair chain:

- exact parse/catalogue reproduction source
  `6a6088e525762c456c6df7fcba5c8377a94fb2ca`;
- inert SQL and render-manifest source
  `497a4d1fe5b58fa4bcc03747abb3d389c3b51899`;
- structural contract source
  `e1ca28915b09636e5d9d693216beef450f71a356`;
- typed function/trigger body source
  `1a06961916bcf73d553eb401eb08094aa4c45e20`; and
- unchanged prerequisite contract source
  `1fd3445aea5839b7aa889fc962faa8ad2be0c95e`.

The canonical behavior contract digest is
`sha256:4ca9f7612bd79159bc2232cec5bc078219ac2145c9d1ad80927420d2f8706f16`.
The scenario population and order remain twenty with category counts
`6/4/3/4/3`.

## Exact transition-result proof

`BTR-E04`, `BTR-I03` and `BTR-B03` now emit one bounded JSON marker from the
same top-level transaction that invokes the transition function. The marker
proves exact result kinds `RECEIPT_APPLIED`, `RECEIPT_REPLAYED` and
`RECEIPT_APPLIED`, respectively. A materialized CTE invokes the function once,
and a transaction-local assertion aborts before commit if the returned kind is
wrong. Missing, duplicate, malformed, mismatched or unexpected markers fail
closed. `BTR-B03` proves the applied result before its fixed injected rollback.

This does not add `context_observer_generation` or any other relation to the
allowed change set.

## Outbox authority proof

The existing `BTR-R03` role matrix gains a ninth fresh connection:
`coordinator_outbox_direct_select`. Although forced RLS now permits the
coordinator security-definer path to see the exact outbox row it must process,
the coordinator has no direct table `SELECT` grant. The direct query must
therefore fail with standard SQLSTATE `42501` and leave every row unchanged.

## Gate and boundary

The rebound packet must pass its complete deterministic and hostile tests,
Ruff, `git diff --check` and one fresh exact-HEAD Gemini 3.6 Flash/high veto
before exactly one newly owned, pull-never, networkless, tmpfs PostgreSQL 16
behavior attempt.

This grants no applied migration, operational database or credentials,
persistence, watcher/listener/feed/source access, application/API/Diary
surface, patient/clinical/product data, provider call, command/write,
deployment, production, release, Pages or protected-ref authority.
