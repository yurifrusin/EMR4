# Threat-model delta: preset-mount sanitizer Windows minimum environment

Date: 2026-08-22

Timestamp: 2026-08-22T05:27:53.1609563+10:00 (Australia/Brisbane)

Status: **frozen before implementation**

## Scope delta

The failed-closed lineage identifies a completely empty Windows child
environment as the shared untested launch difference. This successor projects
five operating-system runtime keys into one local Node process.

## Controls

| Threat | Fail-closed control |
|---|---|
| Environment repair leaks ambient secrets | Exact five-key allowlist; no values in logs, evidence, reports or exceptions. |
| `PATH` or `NODE_OPTIONS` alters execution | Both are absent; use the already resolved absolute Node executable and exact fixture path. |
| A missing Windows key yields another opaque abort | Validate all five keys before process launch; absence consumes zero Node processes. |
| Stream content leaks a path or environment | Persist only exit, byte counts and SHA-256 before admission; content remains discarded. |
| Environment success is mistaken for Harness readiness | The fixture imports only the pure sanitizer; DSH, runner, worker/model/provider and retry gates remain false. |
| Recovery becomes repeated probing | Exactly one successor process; any non-pass stops. |

## Security acceptance

Accept only the exact five-key child environment shape, unchanged code hashes,
one closed successful fixture vector and unchanged product/provider/protected
boundaries.
