# Threat-model delta — check-in native Harness preset-validation subcoordinate recovery

Date: 2026-08-20

Timestamp: 2026-08-20T16:36:42.2544702+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery`

## Changed attack and failure surface

This tranche reads one pinned local npm installation and one authored-synthetic
preset, then may run a package-only discovery scan and, after a distinct
checkpoint, one provider-disabled native validation process. It introduces no
product or data access and no provider call.

| Risk | Fail-closed control |
|---|---|
| A manually transcribed Git ID binds evidence to the wrong commit | Full IDs are forbidden in the narrative Git evidence field; exact refs come only from the machine snapshot, while structured latch source IDs retain commit/ancestry resolution. |
| A different or updated package is characterized | Exact rc.7 version, lockfile integrity, package/source digests and retained installation root are bound before execution; no install or network package command is allowed. |
| Roster discovery success is mistaken for a healthy selected row | Row found, exact path/trust and `broken` absence are separate mandatory readings. |
| File readability is mistaken for valid package syntax | Byte read and the package's `js-yaml`/`entryListSchema` parse-shape admission are separate readings. |
| Parsed content is not the accepted preset | Exact length and SHA-256 are separately bound after read/parse. |
| Raw package errors leak into durable evidence | Only closed reason codes persist; raw exceptions and stdout/stderr are discarded. |
| A diagnostic imports or starts the wider Harness too early | Static proof precedes a package-only import; the package probe cannot assemble the Harness service graph. Native Harness process count remains zero until a distinct latch checkpoint. |
| Native validation drifts into an agent or provider request | The runner contains no `agents.create`, mount, session, turn or model call; process/profile/network counters must remain zero outside the one local native process. |
| A failed native process is retried | First process creation consumes the one-shot allowance; terminal and cleanup are immutable and retry count must be zero. |
| Disposable files or processes persist | Exact terminal checks require process and disposable root absence. |
| Diagnostic work broadens product authority | Product, route, flag, API, client, data, Docker/database, deployment, Pages and protected refs remain explicitly closed. |

## Claim boundary

Passing evidence may prove only that the pinned rc.7 discovery path can find,
read, parse and byte-bind the exact authored-synthetic preset under the frozen
provider-disabled envelope. It does not prove preset mount, effective tools,
agent creation, occupied DeepSeek work, model quality, attempt 006, database or
product behavior, production suitability or deployment authority.
