# Provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal closeout

Date: 2026-08-17

Timestamp: 2026-08-17T09:22:02.9442094+10:00 (Australia/Brisbane)

Status: accepted

Result: `raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_pass`

Exact reviewed candidate: `fe5dbcb31b06b027285aa84ee3cafb4fbbffb9db`

Evidence label: `live_local_backend_postgres`

Reasoning level: Extra High

## Outcome

The existing canonical delete-confirm route and its hidden compatibility alias
now have one accepted provider-free local integration proof through the exact
product adapter and physical transaction against an owned disposable
PostgreSQL 16 server. The route produced a non-mutating signed proposal, a
confirmed cancellation committed appointment, audit and private receipt state
atomically, retries replayed without a second effect, current-authority and
cross-practice denials disclosed no row, and an induced receipt-completeness
failure rolled the whole transaction back.

The two cross-seam repository defects exposed before execution were repaired
without changing command meaning: route-side delete material delegates to the
accepted adapter canonicalizers, and the command transaction establishes the
server-authenticated practice as transaction-local PostgreSQL context after
isolation and before any protected read.

## Accepted evidence

- all twelve `DHI-S01` through `DHI-S12` scenarios passed;
- all 135 hostile contract mutations were rejected before unsafe execution;
- the application role was non-superuser and non-`BYPASSRLS`;
- forced RLS covered eight tables, with six selected constraints and four
  selected triggers present at migration head `x3y4z5a6b7c8`;
- the transaction-local practice context was absent on two fresh pooled
  connections after the command;
- public and private receipt bytes were distinct, while each projection was
  independently byte-identical on replay;
- second-effect and rollback-effect counts were both zero; and
- the captured container and internal network were removed and independently
  absent after cleanup.

Verification passed with the 40-test integration/plan verifier profile, 58
route/physical tests, 286 register tests, the current 37-test API Spine/Diary
profile, the 130-test maintenance profile, Ruff, maintained-source compilation
and Git whitespace checks. One fresh eight-command Gemini 3.7 Flash/high veto
returned exactly one `pass` at unchanged clean candidate HEAD and worktree.

## Issues and corrections

The tranche preserved and corrected AER-0369 through AER-0378. The product
defects were the missing delete discriminator/nested signed evidence and
missing transaction-local tenant context. The harness/workflow issues included
an inherited Docker-profile field omission, two incomplete DHI-S07 probe
shapes, repeated manual expansion of abbreviated Git hashes, compound-shell
validation that could mask an earlier failure, and four excluded pytest runs
with the wrong conftest/serial-lock envelope. None of the rejected or excluded
runs supplied acceptance evidence.

The scheduled Ariadne effectiveness review will use these incidents as direct
inputs, including machine-populated Git references, explicit pytest profile
metadata and one authoritative inherited Docker-profile contract.

## Deliberately closed

This is authored-synthetic local integration evidence only. It does not admit
raw compatibility `DELETE`, a reusable capability, product/patient/clinical or
historical data, concurrency beyond the existing locks, crash/restart or
unknown-commit recovery, visible Reception One behavior, provider or credential
work, deployment, production, release, Pages or protected-ref movement.

## Worker and parallelism outcome

DeepSeek V4 Flash/high supplied the bounded harness/test package and one
mechanical correction; Sol recovered and completed the serial occupied
database work; Gemini 3.7 Flash/high supplied the required independent veto.
Native subagents remained declined by current developer policy. The shared
route/session/database lifecycle correctly remained serial.

## Next work

Before further product work, run the authorised evidence-based Ariadne
effectiveness review, inspect DeepSeek Harness primary sources, assess
adaptation versus conductor migration, and implement only the highest-leverage
workflow repairs. The inability to fund a DeepSeek Harness conductor through
the existing ChatGPT subscription is a presumptive migration blocker to be
verified from primary sources; portable mechanisms remain in scope.
