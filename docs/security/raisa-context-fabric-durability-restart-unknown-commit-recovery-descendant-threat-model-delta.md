# Threat-model delta — CF-D2 recovery descendant

Date: 2026-08-12

Status: `frozen_provider_free_recovery_runtime_closed`

## New boundary

The recovery descendant adds a minimized terminal-coordinate evidence boundary
and a no-crash first-sequence diagnostic. It does not change the accepted SQL,
database authority, four-scenario recovery semantics or external closed
surfaces.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Adjacent calls collapse into one error | Every participant call has one mandatory closed coordinate; terminal failure stage is that coordinate. |
| Raw output is retained to aid diagnosis | Only return-code class, allowlisted SQLSTATE and allowlisted result tokens are schema-admissible. |
| Source order is mistaken for observed evidence | Diagnosis is admitted only from an immutable coordinate-specific artifact. |
| Diagnostic becomes an implicit crash test | Diagnostic profile fixes `SIGKILL=0` and restart count `0`; crash commands are unreachable. |
| Failure is bypassed to examine the next call | The first failed coordinate stops the sequence; anchor is ineligible unless apply and atomic delta pass. |
| Repeated execution finds a convenient answer | At most two immutable diagnostic attempts exist, with one evidence-backed correction and exact-HEAD review between them. |
| Harness repair changes database meaning | Correction allowlist excludes inert SQL, grants, atomic membership, classifier, anchor authority, isolation, durability and scenario meaning. |
| Diagnostic pass is promoted to durability pass | Separate result, schema and claim state that no restart or unknown-commit behavior is proved. |
| Full rerun becomes an open loop | Exactly one attempt 003 is eligible after the no-crash and review gates; no post-attempt correction or retry exists. |
| Cleanup harms unrelated resources | Exact nonce/name/image/container ownership is reverified; only captured ID removal and scoped absence are allowed. |
| Existing untracked evidence is staged | Explicit-path staging only; all 494 pre-existing untracked files and `docs/branding/` remain excluded. |

## Residual risk

The no-crash diagnostic can establish which closed expectation disagrees and
whether the exact first transition/anchor sequence is coherent. It cannot
establish restart persistence or either unknown-result classification. The
later full attempt still represents four deliberately constructed PostgreSQL
process cases, not hardware, filesystem, driver, pool or operational recovery.

No patient, clinical, product, provider, credential, deployment, production,
release, Pages or protected-ref authority is added.
