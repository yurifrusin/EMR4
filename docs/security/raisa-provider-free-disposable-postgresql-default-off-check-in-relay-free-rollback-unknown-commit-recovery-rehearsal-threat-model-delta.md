# Threat-model delta: relay-free check-in rollback and unknown-commit recovery

Date: 2026-08-19

Timestamp: 2026-08-19T20:13:10.6208443+10:00 (Australia/Brisbane)

Status: `frozen`

Parent controls are the accepted canonical check-in admission, runtime-role
tenant-isolation and relay-free OCI-result transport boundaries. This delta
adds one disposable PostgreSQL transaction proof and grants no product or
ordinary-practice authority.

## Assets and trust boundaries

- Exact full-Git and SHA-256 source bindings.
- One newly frozen authored-synthetic transaction manifest.
- Ephemeral admin/runtime credentials held only in controller and child
  process memory.
- One captured internal Docker network, one server and captured short-lived
  sidecars.
- Admin-owned forced-RLS probe relations and a non-owner `NOBYPASSRLS` role.
- Exact stopped-container OCI state as the only action/outcome channel.
- Immutable predecessor failures and accepted relay-free proof artifacts.
- Sanitized transaction attestation, evidence and cleanup disposition.

Trust crosses only the host-to-Docker control API, post-inspection attached
stdin, the captured internal network, PostgreSQL authentication/RLS and closed
artifact validators. Attachment output, Docker logs and model prose are not
trusted evidence.

## Threats and required controls

| Threat | Fail-closed control |
|---|---|
| Host relay or worker control failure recreates the predecessor ambiguity | No listener, published port, forwarding, socket-copy relay, `docker exec` byte bridge, multiprocessing process or queue exists. |
| Attachment lifetime or output is mistaken for caller outcome | Attachment bytes, status and return code are discarded; only exact captured OCI terminal state is admissible. |
| Credential leaks through environment, argv, file, logs or evidence | Create first, inspect exact no-secret configuration, then deliver one bounded line over captured-ID attached stdin; log driver `none`; recursive forbidden-field/value scan; exact cleanup. |
| A wrong or replaced Docker object receives credentials or cleanup | Captured ID plus name, nonce, label, image and network are reverified before attach, classification and deletion. |
| Ambiguous connection loss is treated as success or retried | Success requires a complete marker; expected loss requires prior exact `Timeout/PgSleep` observation/termination and caller exit 42; retry count is structurally zero. |
| Wrong backend is terminated | The fixed observer predicate requires exactly one backend matching application identity, restricted role, database and wait tuple and terminates only that row. |
| Partial commit or contradictory packet is accepted | Exact receipt/effect/audit cardinality, identities, digest, action/outcome and cross-references are checked; every other shape is `unresolved_denied`. |
| Rollback leaks a durable effect | Fresh restricted readback by command and idempotency identity must find zero members after explicit rollback. |
| Cross-practice inference or write | Enabled and forced RLS, transaction-local practice setting, non-owner `NOBYPASSRLS` role, exact grants and other-practice zero-visibility checks. |
| Runtime role escalates through ownership, membership or public/product grants | Catalogue predicates require no ownership, membership, bypass, role/database/schema creation, default or product privileges. |
| Runtime-chosen SQL or model authority enters the harness | SQL, wrappers, scenario identities and allowed action classes are typed constants and contract-digested; the manifest is declarative only. |
| Raw SQL/output/PID/object identity or PHI reaches durable evidence | Closed schemas retain only enums, booleans, counts and non-secret digests; forbidden-key/value scan rejects raw or sensitive fields. |
| Cleanup targets unrelated resources or leaves residue | Cleanup is captured-ID-only after ownership reinspection; role and attachments are absent before sidecars/server/network; matching owned resource count must be zero. |
| Historical failure evidence is overwritten | New topic and filenames are mandatory; all three predecessor failure artifacts remain immutable. |
| Rehearsal is mistaken for production or ordinary admission evidence | Evidence label is authored-synthetic/provider-free/disposable; ordinary release, product records and configuration changes are asserted zero. |

## Residual limits

The rehearsal proves explicit rollback and caller-level unknown-response
recovery for one serial authored-synthetic PostgreSQL transaction. It does not
prove an in-WAL commit crash, distributed partition, pool/driver semantics,
concurrency, product schema compatibility, production availability, live
secret posture or ordinary-practice safety.

## Closed boundaries

No live/existing/cloud/product database, provider call, external network,
product/patient/appointment/clinical data, ordinary-practice enablement,
feature flag/allowlist change, canonical route mounting, generic-status
`Arrived` change, action grammar, first-party client, waiting-area movement,
product/API/schema/configuration source, deployment, release, Pages, protected
evidence access or protected-ref movement is authorised.
