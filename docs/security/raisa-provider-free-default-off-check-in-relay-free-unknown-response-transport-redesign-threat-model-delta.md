# Threat-model delta — relay-free unknown-response transport redesign

Date: 2026-08-19

Timestamp: 2026-08-19T18:59:39.4552916+10:00 (Australia/Brisbane)

Status: `frozen`

Decision-transition source HEAD:
`44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4`

## Scope

This delta covers one provider-free relay-free caller/result design and one
network-disabled, no-database OCI-state proof. It removes the Windows host TCP
relay and multiprocessing queue from the future unknown-response evidence path.
It opens no database execution, product command, ordinary-practice, provider,
deployment or protected-ref authority.

## Assets

- exact full Git and immutable predecessor failure bindings;
- captured caller container identity, nonce, label and exact cached image;
- ephemeral authored-synthetic credential/token held in process memory;
- attached-stdin input channel separated from the result channel;
- terminal OCI state and closed exit-code vocabulary;
- no-complete-response, no-success and no-retry invariants; and
- exact host attachment and container cleanup.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A seven-character abbreviation binds the design | Clockwork derives the lowercase 40-character source from Git; schemas reject caller-authored Git/source fields. |
| A predecessor failure is rewritten as success | All three immutable artifacts are exact SHA-256 inputs and remain negative evidence; this tranche makes no database claim. |
| The old relay or queue silently remains | Source gate rejects host listeners, TCP forwarders, Docker-exec byte bridges, multiprocessing processes and queues in the new path. |
| Host attachment becomes outcome authority | Attachment is input-only; its return code, output and lifetime are forbidden classifier inputs. Only exact captured-container OCI state can close the outcome. |
| Credential leaks through Docker inspect | Container is inspected before delivery; token/password is sent only over stdin and forbidden from Config.Env, argv, labels, files, logs, evidence and hashes. |
| Credential leaks into logs or output | Logging driver is `none`; wrapper and child stdout/stderr are suppressed; recursive redaction rejects the credential and forbidden keys/values. |
| Any child error is mistaken for expected connection loss | Future exit `42` admission additionally requires the exact post-commit backend wait and exact backend termination. Every other state denies. The no-database fixture claim is explicitly only a simulated mapping proof. |
| Container exit state is read from the wrong object | Captured ID plus exact name, nonce, label and image reverification precede every state read and deletion. Discovery and names are never authority. |
| OOM, restart or runtime error masquerades as exit 42 | Require stopped state, exit 42, `OOMKilled=false`, restart count zero and empty Docker state error. |
| A missing or still-running container is treated as unknown success | Missing, unreadable, running or mismatched state is `unresolved_denied`, with no retry or success. |
| Wrapper reaches complete marker before failure | Fixed marker/exit consistency maps contradiction to exit 43 and denial. |
| Raw psql or Docker material enters evidence | Closed schema permits only booleans, enums, counts, digests and elapsed bounds; no raw output, logs, argv, environment, identifiers or exception. |
| Manifest becomes executable authority | Closed JSON describes expected state only; typed Python freezes commands and owns dispatch/classification. |
| No-database proof starts PostgreSQL accidentally | Override entrypoint, `--network none`, fixed inert child and process-state assertion; any `postgres` process or network invalidates the run. |
| Cleanup deletes unrelated resources | Delete only captured IDs after exact identity/profile reverification; attachment process is exact-owned and must be absent first. |
| Transport proof is overstated as database safety | Claim excludes connection, transaction, rollback, commit uncertainty, readback, idempotent effect and production handling. |
| Product/API authority leaks from command-shaped fixture | No `app/**`, schema, API Spine, OpenAPI, GraphQL, async, client or configuration source is editable; ordinary release stays zero. |
| DeepSeek or provider fallback occurs | DeepSeek native Harness and Claude Code fallback remain declined; no provider call occurs before the optional deterministic-admitted Gemini veto. |
| Protected or user-owned material is swept into Git | Explicit-path staging only; protected evidence remains unopened; `docs/branding/` and every unrelated untracked file remain preserved. |

## Residual risk and closed claims

The local Docker daemon and cached image are trusted development dependencies;
this tranche does not establish supply-chain provenance, daemon compromise
resistance or production container hardening. OCI exit state proves a closed
local result channel only when combined with the frozen wrapper and exact
future backend observation. It does not prove PostgreSQL wire semantics,
in-COMMIT failure, WAL/power-loss durability, network partition handling,
driver/pool retry behavior, concurrency, operational credentials or operator
recovery.

No database execution, GraphQL mutation, REST endpoint, async authority,
product write, ordinary enablement, feature/allowlist change, generic-status
`Arrived`, action grammar, client, waiting-area behavior, provider, production
runtime, deployment, release, Pages, protected evidence or protected ref is
opened.
