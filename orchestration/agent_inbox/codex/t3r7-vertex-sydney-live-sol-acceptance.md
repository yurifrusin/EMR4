# T3R7 Vertex Sydney Live Pilot - Sol Acceptance

Date: 2026-07-18

Decision: `accepted_fail_closed_terminal_stop`

Sol accepts the T3R7 evidence as a correctly bounded live pilot, not as a
completed comparison or provider-promotion result.

The accepted deterministic report hash is
`sha256:02e4df26cbae5aba3e214413a94e7c535610ef9eb19cf2ecc36ec15ae7299336`.

The source and controls were frozen before dispatch. Eleven calls were made to
Vertex `gemini-2.5-flash` through the exact
`australia-southeast1` endpoint. Ten normalized responses succeeded; the
eleventh contained no schema-valid Bernie JSON object. One-attempt semantics
consumed that observation and the runner correctly stopped without retry or
further dispatch. Thirty-seven calls were never sent and carry no continuing
authority.

All ten successful responses were safe. Nine were perfect, with 58/60 scored
dimensions overall. No case received its second observation, so the run
provides no variance evidence. The provider returned only the model alias, not
an exact backend revision.

The raw eleventh response was never persisted, as required. The accepted
diagnosis is therefore limited to normalized parse/schema failure; any more
specific attribution would be unsupported. Its missing usage also means the
USD 0.0274258 recorded estimate covers only the ten observations with reported
usage and is not an authoritative billing total.

The API Spine classification remains developer-only synthetic Access AI
evaluation. No product adapter, runtime input, route, API contract, database or
audit write, appointment/confirmation authority, PII, production, deployment,
release, or write surface is authorized. A fresh Yuri decision is required
before any new provider call.

No external worker was dispatched. This was a tightly coupled, fail-closed
live-control and evidence-consumption lane; Sol owns the boundary and direct
verification.
