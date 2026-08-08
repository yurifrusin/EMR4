# Disposable PostgreSQL parse/catalogue row-projection rebind closeout

Date: 2026-08-08

Status: runtime pass candidate; fresh exact-HEAD evidence veto required before
final acceptance

Result candidate:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

## Exact result

The disposable parse/catalogue harness was rebound to corrected source
`0931f3e658f06e02e7de4c5ea02238184da9e767` and canonical contract
`sha256:4dc142f8dd357474739fbc79b4964352b8ccd723459ae91f52633ddd1ab4093b`.
It admitted inert SQL
`sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`
at exactly 1,404,420 UTF-8/LF bytes and 412 statements.

The fixed rollback database rejected the appended invalid statement with the
exact closed admission shape and left no installed durability objects. The
success database then installed the corrected artifact atomically. All exact
relation, column, constraint, index, RLS, policy, function, trigger, role,
schema/type and privilege catalogue digests matched the accepted expectations.
This confirms that the positional row-projection source repair changed function
body behavior without drifting the catalogue-visible contract.

## Containment and cleanup

- Image: exact pre-existing `postgres:16-bookworm` at
  `sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8`
- Pull attempted: false
- Network: none
- Host ports: none
- Bind, named, workspace and Docker-socket mounts: none
- Database storage: container-local tmpfs
- Captured container ID:
  `e44443027e9ad46d4217c48ca042b13326f422b5bc7a88258eeaadb853769e0c`
- Cleanup: exact-ID removal passed and an independent exact-ID inspect returned
  the documented absent condition
- Total measured harness time: 9,016 ms

The new evidence file is
`orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence.json`
with raw checkout SHA-256
`sha256:ff127b4061bd9fe904c4929e8fff5ab0d06ef72b37710edc3dbd271bec5155d4`.

The predecessor pass remains byte-identical under
`provider-free-disposable-postgresql-evidence-pre-row-composite-projection-order-recovery.json`
with SHA-256
`sha256:3ef47b7a14b2581b6c7bf1732594b1e1c322a90e07ec7d43e2e5b5006b1a3281`.
It remains historical evidence only.

## Evidence gate

The exact evidence, closeout, rebound contract, historical separation and
deterministic tests must be committed and reviewed from a fresh clean
Gemini 3.6 Flash/high worktree. Final acceptance requires one terminal pass,
exact test reconciliation and an unchanged reviewer postcondition.

## Claim boundary and next work

This result proves PostgreSQL 16 can parse and atomically install the corrected
inert artifact and that its exact catalogue/privilege shape remains unchanged.
It does not prove any function, trigger, RLS or transaction behavior.

After final evidence acceptance, the next dependency is a separate behavior
contract rebind to this corrected artifact and this parse/catalogue pass,
followed by deterministic checks and a fresh exact-HEAD veto before behavior
attempt 016. No application migration/runtime, operational persistence or
credentials, watcher/listener/feed, patient/clinical/product/protected data,
provider/model call, tool, command or product write, deployment, production,
release, Pages or protected-ref movement is opened.
