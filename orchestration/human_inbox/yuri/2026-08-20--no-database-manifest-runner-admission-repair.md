# Provider-free no-database manifest and runner admission repair

Date: 2026-08-20

Timestamp: 2026-08-20T01:45:06.9565729+10:00 (Australia/Brisbane)

## Plain-language summary

The new interlock works. “Provider-free and no database” is no longer a rule I
must remember while composing a test command. The machinery now reads the
selected tests before launching anything and refuses ordinary pytest, shared
database fixtures, uncertain fixture wiring, unsafe paths or changed evidence.

This directly addresses the kind of procedural rerun you observed. The check
is taken once at manifest admission and checked again at launch and at the
DeepSeek broker boundary. A mismatch stops before the worker can become ready.

The independent reviewer found one evidence-portability defect on the first
candidate: two synthetic fields contained the main worktree's absolute path.
That was corrected to repository-relative operands, proved identical across
worktrees, and a fresh review then passed cleanly.

## Technical summary

- Corrected reviewed candidate:
  `60ce7b7603331d4e69d551db92eb592c7fef1ea3`
- Focused tests: 48/48 passed
- Wider admitted clockwork functions: 527 passed
- Hostile mutations: 128/128 rejected
- A5.1 database-backed selection: rejected before subprocess
- Manifest/runner admission identity: exact
- DeepSeek WorkOrder: v2, bound to manifest and admission SHA-256s
- Gemini: first portability rejection, then one fresh corrected pass
- Prohibited deterministic invocations: all zero
- DeepSeek model calls and attempt-004 executions: zero
- Protected refs: all four remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

No product/API/config/client behavior, feature flag, ordinary-practice
admission, data, database, provider, production, deployment, release, Pages or
protected ref has opened.

## Next tranche

The remaining prerequisite before occupied native-Harness work is a very
narrow provider-free boot proof: start the pinned Harness through its documented
stock headless path, prove it reaches the custom runner under HMR, capture its
readiness/terminal/cleanup trace, and make no model call. Yuri's attention is
not required; standing authority covers this dependency-satisfied successor.

## Closeout publication

Clockwork accepted source `958ae762e7c6a065b5926f47eb1a2b63115212c7`
at Continuity 338 / Compass 320 and lease sequence 28, with zero canonical
drift or bespoke updater execution. The post-publication admitted suite passed.
The usual non-PHI continuing notification succeeded with request
`dbce6052-ee2a-4656-9a04-daa541096a9f`.
