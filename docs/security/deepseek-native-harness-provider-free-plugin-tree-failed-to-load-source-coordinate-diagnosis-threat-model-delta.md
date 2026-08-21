# DeepSeek Native Harness Plugin-Tree Source-Coordinate Diagnosis Threat-Model Delta

Date: 2026-08-21
Timestamp: 2026-08-21T13:08:01.6272499+10:00 (Australia/Brisbane)
Status: `frozen`

## Scope

This delta covers provider-free static diagnosis of the pinned rc.7
plugin-tree failure observed in immutable attempt 004. It opens no executable,
provider, worker, product or data surface.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A different package version is diagnosed | Require exact scoped package name and `0.1.0-rc.7` from local `package.json`; bind selected source files by SHA-256. |
| Diagnosis downloads or executes code | Forbid network/package installation, Node, dynamic import and subprocess execution; tests guard those entry points. |
| Raw stderr is reconstructed to recover hidden detail | Admit only the immutable sanitized structured terminal. Forbid raw messages, codes, stacks, paths, streams, sessions and credentials in inputs and outputs. |
| A four-node shape is overinterpreted | Require a unique static wrapper branch matching the admitted top coordinate and full cause-chain structure. Zero or multiple candidates remain insufficient. |
| Historical failures are conflated | Attempt 004 is bound by its own terminal digest. Historical raw output and equal byte counts are non-evidence. |
| A diagnosis silently changes the preset | Profile and preset files are read-only inputs. This tranche cannot modify package, profile, runner, broker or product source. |
| A repair recommendation widens authority | `repair_justified` requires one exact non-product boundary and provider-free proof strategy; implementation remains a separately latched tranche. |
| Product or ordinary-practice scope leaks in | No API, database, route, adapter, flag, allowlist, grammar, client, waiting-area, ordinary-practice or generic `Arrived` change. |
| Another occupied attempt is smuggled into validation | All process/request counters must be zero and the active latch forbids Harness, broker, worker, model and provider activity. |
| Untracked user work is disturbed | Preserve all unrelated untracked files, especially `docs/branding/`; stage explicit paths only. |

## Residual risk

A source-supported coordinate does not prove that a repair will boot the
Harness or reach DeepSeek. It only narrows the next provider-free engineering
question. Any repair and any later occupied attempt require their own frozen
authority and evidence.
