# Provider-free read-only status-confirm runtime-gap admission review plan

Date: 2026-08-12

Source HEAD: `1a26b49c0c3af84e8e8d2b6456268b7fff0d25f6`

Status: `frozen_for_exact_file_read_only_execution`

## Purpose

Decide whether the existing status-confirm route can receive the accepted pure
adapter and transaction protocol without first changing its runtime contract.
The tranche is an admission review, not an implementation. It may report
`admitted`, `admitted_after_bounded_prerequisites`, or `not_admitted`; it may
not edit or execute an application route or database.

## Exact review dimensions

1. global and status-subset lock order;
2. server-owned practice, actor, role, active-user and session ingress plus an
   in-transaction current-authority recheck before receipt disclosure;
3. status-only discrimination from the current status/waiting-area union;
4. terminal re-transition parity with the accepted effect-free
   `transition_policy_deferred` boundary;
5. exact warning acknowledgement without duplicate or unknown codes;
6. signed-evidence and freshness binding under a locked current source state;
7. atomic appointment mutation, attributable audit and completed receipt,
   including durable target/audit correlation;
8. authority-first idempotency conflict/replay disclosure; and
9. canonical stored-receipt delivery and recovery after post-commit response
   failure without another effect.

## Frozen non-protected source allowlist

Only these exact files may be read or content-searched:

| SHA-256 | File |
|---|---|
| `59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb` | `app/routers/appointments.py` |
| `d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d` | `app/schemas/appointments.py` |
| `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` | `app/services/appointment_idempotency.py` |
| `d44f777f742074f0ee4717d599d7ee71dd6343c7096c87793149c727c1c4b0a9` | `app/dependencies.py` |
| `af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952` | `app/models/appointments.py` |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `0ecc5b2bff0853d3f9797163b979f575f9604c6ba0895cf5bd36c165664eb8af` | `tests/test_api_spine_status_confirm_idempotency_route_contract.py` |
| `4881bde300c6c62a061518aec8a1ddfc5e7b185e0c1cd4f86c490c5fef2c6ef6` | `tests/test_api_spine_confirmation_contract_matrix.py` |
| `fbfa53e8fc8cf22b522437c1d74aa77638ef930bfc1fec5ff678b45c221555b6` | `review/test_raw_status_terminal_rollback_guard.py` |
| `a45b601a375c7dec7ee08e46be53e23991542cf9699a9ac75798c2e70d2865d8` | `scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py` |
| `14883b8dcdf26a1f0ef88214d7b3f6b105a0fcc3e298298d4b14d1c703a93083` | `scripts/raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal.py` |

No repository, `tests/`, `docs/`, `review/` or application-directory search is
permitted. An apparent need for another source is an explicit review stop and
new-plan question, not an implicit expansion.

## Evidence method

A provider-free script validates the exact hashes, checks closed source
markers without importing application code, compares each dimension against a
closed JSON contract, and emits a minimized gap matrix. Every finding must
name the exact allowlisted file and line range, the current observed behavior,
the accepted required behavior, its admission effect and the narrowest
prerequisite. Authored-synthetic mutation cases must prove that missing or
softened blockers cannot become an admitted verdict.

The two named tests-root files may be executed serially as existing behavioral
evidence. The out-of-tree terminal guard may be read but not changed or counted
as passing runtime evidence because its accepted closeout records an elapsed
date fixture.

## Acceptance

The review passes only if:

1. the five-source receipt passes and all allowlisted hashes match;
2. a closed schema validates all nine dimensions and exact citations;
3. the verdict follows deterministic blocker rules with no implementation
   authority encoded;
4. at least 30 hostile mutations fail closed;
5. the generated review, source script and tests agree byte-for-byte;
6. focused/API/canonical checks and whitespace pass;
7. the application tree remains byte-identical to source HEAD; and
8. protected refs plus every unrelated untracked file remain unchanged.

## Forbidden surfaces

No app edit/import, route or database execution, SQL, lock, migration, source
read beyond the allowlist, watcher, event, real session, signature, credential,
provider, network, executable tool, command, product/patient data, deployment,
production, release, Pages or protected-ref movement. Never stage
`docs/branding/`, use broad staging, or derive evidence from AER-0291 content.

## Recovery and next decision

A mechanical contract/schema/script/test defect may receive one bounded
correction without changing the nine dimensions or blocker rule. A need to
choose terminal product policy, runtime authority semantics or a migration
strategy stops this review at `not_admitted` and hands the exact prerequisite
set to a separate provider-free unmounted convergence-architecture tranche.
