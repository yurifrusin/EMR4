# Threat-model delta — CF-D2 event and cue disposable PostgreSQL parse/catalogue rehearsal

Date: 2026-08-13

Timestamp: 2026-08-13T19:21:56+10:00 (Australia/Brisbane)

Status: `provider_free_networkless_tmpfs_exact_artifact_only`

## Assets protected

- source-owned Diary truth and current command authority;
- the exact accepted inert SQL bytes and seven-relation meaning;
- existing databases, Docker resources and unrelated worktree content;
- protected, historical Diary, patient, product and credential data; and
- the distinction between catalogue evidence and runtime durability behavior.

## New boundary

The tranche opens one exact-artifact SQL execution against one newly created,
owned, networkless, tmpfs PostgreSQL 16 container. It opens no existing
database/source, port, external network, migration chain, application route,
watcher, provider or product data.

## Threats and controls

| Threat | Frozen control |
|---|---|
| An operational database is reached | No host URL or port; all SQL uses exact-ID `docker exec` and the owned container's Unix socket. |
| Docker contacts a registry | Exact cached image ID/digest inspected first; `--pull=never`; absence or drift fails without fallback. |
| A different SQL payload is executed | Exact fixed path, SHA-256 and byte count checked; the same bytes are streamed unchanged; no caller arguments. |
| Workspace or durable data is mounted | One container-local tmpfs only; no bind, named volume, workspace or Docker-socket mount. |
| Cleanup removes another object | Exact captured ID, name, image, labels and full containment profile are reverified immediately before exact-ID removal. |
| A partial schema survives an SQL failure | `ON_ERROR_STOP=1`, `--single-transaction` and unconditional verified container cleanup. |
| Catalogue queries become a generic database tool | Fixed query constants, fixed target schema and no caller-selected SQL or object name. |
| System catalogue noise is mistaken for artifact output | Every positive assertion is target-schema scoped; external bootstrap objects are excluded explicitly. |
| Constraint presence is overclaimed as behavior | Evidence says validated catalogue presence only; the five transaction protocols remain separately unproved. |
| Event coordinates gain semantic authority | Non-authoritative-coordinate annotation and fresh-read/current-command rules remain external and false as database claims. |
| Rows or payloads enter the rehearsal | No DML is sent; exact per-table zero-row readback is mandatory. |
| Raw errors leak sensitive content | Evidence retains only bounded stage/code and SHA-256 of capped diagnostics, never raw logs. |
| Worktree collateral is staged | Explicit-path staging only; `docs/branding/` and all unrelated untracked paths excluded. |

## Residual risk

The locally cached image remains a supply-chain dependency already present on
the host. This rehearsal does not prove constraint behavior, transaction
protocols, privileges under application roles, concurrency, restart,
unknown-commit recovery, watcher ownership, retention, delivery, performance,
migration integration or production operation.

If container ownership cannot be reverified, automated cleanup deliberately
stops rather than risking deletion of someone else's resource; that condition
requires human attention.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient identity/client, existing database/source, watcher runtime,
durable persistence, provider/ADC, credential/IAM/external network,
application route, command/write, deployment, production, release, Pages or
protected-ref authority is opened.
