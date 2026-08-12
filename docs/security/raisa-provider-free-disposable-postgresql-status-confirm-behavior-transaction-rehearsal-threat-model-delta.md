# Threat-model delta — disposable PostgreSQL status-confirm behavior/transaction rehearsal

Date: 2026-08-12

Source HEAD: `d4f637d6c2afadccc95d4b7ae8cfc1f522444133`

## Scope

This delta covers one host-side invocation of the exact unmounted SQLAlchemy
status-confirm seam against one authored-synthetic, internally networked,
tmpfs-backed PostgreSQL 16 container through a fixed in-process loopback relay,
followed by exact owned container and network cleanup.

## Threats and controls

| Threat | Frozen control |
|---|---|
| The host reaches an operational database | The URL is built internally from one operating-system-selected `127.0.0.1` relay port; every relay child targets only the captured exact container ID and a fixed literal container-loopback PostgreSQL endpoint. Caller URLs/hosts/ports/commands are rejected. |
| The container reaches an external network | A uniquely owned Docker `--internal` network is the container's sole network; registry access is forbidden and `--pull=never` is mandatory. |
| PostgreSQL becomes remotely exposed | Docker publishes no port. The only listener is the harness-owned IPv4 socket bound exactly to `127.0.0.1:<dynamic>`; wildcard, IPv6, second listener or caller-selected port fails before SQL. |
| The relay becomes a generic command surface | The host invocation is a frozen argv with `shell=False`, exact captured container ID and fixed `bash -c` text; database targets and caller values are never interpolated. The relay exists only for the bounded harness lifetime and stops before cleanup. |
| Workspace or data persists | Database storage is container-local tmpfs; bind, named-volume, workspace and Docker-socket mounts are forbidden. |
| Cleanup removes another object | Exact ID/name/image/labels/profile/network membership are reverified; only captured IDs are removed, container first and empty network second. |
| A minimum schema overstates full compatibility | Only selected mapped columns and correlation constraints exist; the claim excludes full schema, migration chain and route compatibility. |
| The harness silently reimplements the seam | It imports and calls the exact hash-bound `status_confirm_locked_transaction`; source modification or a substitute entry point fails preflight. |
| Lock order is inferred rather than exercised | The real SQLAlchemy connection records value-free statement classes and must show practice share, appointment update, conflict-safe insert and idempotency update locks in order. |
| Stored receipt leaks before authority | Revoked-authority scenarios require no idempotency statement token and no response-byte disclosure. |
| A partial write survives | The seam guard plus fixed appointment-only, appointment/audit and complete-set outer-abort scenarios require identical before/after digests. |
| Replay causes another effect | Response-loss retry must return the stored byte digest with unchanged appointment/audit/receipt counts. |
| Correlation is merely conventional | Composite foreign keys and unique command/audit correlations are installed and read back before scenarios. |
| Evidence leaks credentials or data | Only digests, fixed labels, counts, versions and value-free SQL tokens are retained; raw SQL, URLs, logs, bytes and runtime IDs are forbidden. |

## Residual risks

The rehearsal is serial and does not prove lock contention, deadlock handling,
concurrent idempotency races, serializable retries, restart, crash or unknown-
commit recovery. It does not prove the full historical migration chain, full
application schema, route/adaptor behavior, warning/evidence/transition policy,
performance, retention or production operations.

## Authority boundary

No existing/product database, durable product data, route or product command,
patient/product/protected data, provider/ADC/credential/browser authorization,
external network, watcher/event, deployment, production, release, Pages or
protected-ref action is opened. `docs/branding/` and all unrelated untracked
paths remain preserved and excluded.
