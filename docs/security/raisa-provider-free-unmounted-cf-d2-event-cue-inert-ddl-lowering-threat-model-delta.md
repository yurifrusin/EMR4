# Threat-model delta — CF-D2 event and cue inert-DDL lowering

Date: 2026-08-13

Timestamp: 2026-08-13T18:14:01+10:00 (Australia/Brisbane)

Status: `provider_free_unmounted_sql_text_only`

## Assets protected

- source-owned Diary truth and command-time authority;
- the exact accepted seven-relation, fifty-field representation;
- payload-free partition, receipt, obligation and reconciliation boundaries;
- the distinction between static DDL coverage and database behavior; and
- protected, patient, product, credential and unrelated worktree data.

## New boundary

The tranche adds a deterministic repository-local renderer and recognizer. It
reads two fixed JSON contracts and writes three fixed continuity artifacts. It
opens no parser, driver, socket, subprocess, database, source, migration,
provider, browser or application route.

## Threats and controls

| Threat | Control |
|---|---|
| Parent meaning drifts during lowering | Exact path, source commit and SHA-256 binding before render |
| Generic SQL input creates injection or path escape | No caller-selected input/output; all identifiers and literals are closed constants |
| Payload or appointment truth is introduced | Exact fifty-field census; prohibited fragments/types; no JSON, bytea or free-text payload column |
| DDL is mistaken for an executable migration | `.sql.inert` suffix outside Alembic, inert header, no transaction/installer statements, explicit claim boundary |
| Static checks overclaim PostgreSQL behavior | Evidence label says text only; parser/catalogue/behavior claims are false and separately gated |
| Semantic authority is disguised as a row constraint | `coordinate_is_non_authoritative` remains annotation-only; external authority remains unlowered |
| Mutable-field declarations are mistaken for enforcement | Exact declarations retained in manifest/comments with `enforced_by_ddl=false`; triggers/functions/roles are forbidden |
| Transaction atomicity is smuggled into schema acceptance | All five protocols remain `unlowered_transaction_protocol`; any proved claim fails admission |
| Reference cycle/order causes hidden renderer variance | Tables keep accepted order; all seven references are added in one deterministic later phase |
| Hostile text adds DML, functions or privileges | Exact-byte admission plus explicit forbidden-statement and metacommand census |
| Renderer reaches runtime or external state | Standard-library file-only implementation and monkeypatched import/process/socket/database sentinels in tests |
| Worktree collateral is staged | Explicit-path staging only; `docs/branding/` and all unrelated untracked files excluded |

## Residual risk

A static renderer cannot establish that PostgreSQL 16 parses the artifact or
creates the intended catalogue. It cannot prove runtime constraint behavior,
foreign-key timing, atomicity, fencing, locks, concurrency, restart, delivery,
retention or migration safety. Those claims remain closed for separately
frozen descendants.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client, real identity, database/source access, SQL/migration
execution, persistence, operational retention, watcher/listener/worker
runtime, provider/ADC, credential/IAM/network, executable tool, command/write,
route, deployment, production, release, Pages or protected-ref authority is
opened.
