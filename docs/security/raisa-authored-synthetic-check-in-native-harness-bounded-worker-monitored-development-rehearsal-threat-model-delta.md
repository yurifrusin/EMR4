# Threat-model delta — authored-synthetic native Harness bounded-worker monitored development

Date: 2026-08-20

Timestamp: 2026-08-20T20:46:14.4461645+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal`

## Changed attack and failure surface

This tranche crosses the accepted native Harness frontier from provider-disabled
preset/tool composition into one occupied DeepSeek request and one writable
authored-synthetic file. It introduces a provider credential in the isolated
broker, model-generated tool arguments, one official filesystem edit and a
new tool-result turn-conclusion listener. It does not admit product source,
product data, database access or reusable production runtime.

| Risk | Fail-closed control |
|---|---|
| Product or protected material reaches the worker/provider | Construct a new one-file generic synthetic repository from controller-owned bytes; scan the prompt and workspace against forbidden identities and bind both digests before broker start. |
| Worker receives the provider credential | Put the credential only in the broker environment; worker receives a one-session broker capability and broker receives no worker mount. |
| Model sees more than the accepted tool view | Mount the accepted preset and run the unchanged exact projection guard immediately before agent execution; broker independently requires exactly `edit`, `glob`, `read`. |
| One-request shaping silently becomes a multi-request session | Broker admits ordinal one only; rc.7 `concludesTurn` must be present on the successful edit result. Any ordinal-two attempt is rejected before provider I/O and makes the terminal negative. |
| A timing-based process kill loses or misattributes the tool result | Success depends on the in-process rc.7 conclusion marker and durable call/result pair, never on an outer file watcher or kill race. |
| The conclusion listener suppresses a failed or wrong tool | It may mark only one successful direct `edit` on the exact owned path; failures, read/glob, multiple calls, nested calls and path drift remain non-terminal failures. |
| Listener changes the worker's edit or result | It observes only immutable execution/result fields and marks turn conclusion; deterministic tests prove it cannot rewrite arguments, value, content or errors. |
| Model creates, deletes, renames or edits another file | Sandbox and exact path policy admit one existing file; Git and literal-root inventories must show exactly that path changed and no untracked additions. |
| Model supplies an ambiguous, stale, no-op or broad edit | Official `edit` semantics reject it; exact before/after digests and one literal replacement are acceptance requirements. |
| Model emits multiple or parallel tool calls | Parallel width is one and the terminal contract requires exactly one model-requested call. Any surplus call fails the attempt even if the target bytes happen to match. |
| Controller applies or repairs model output | Only the native official tool may mutate the synthetic candidate after the occupied checkpoint. Controller writes baseline before dispatch and is read-only over the candidate afterward. |
| A retry/fallback hides an initial failure | Automatic retries, fallback and auxiliary routes are zero; first process creation consumes the attempt and all negative terminals are immutable. |
| WorkOrder or clock event loses exact provenance | Resolve every Git identity from Git, require 40 lowercase hex characters, bind canonical digests and validate the continuous event hash/sequence chain. |
| Raw reasoning, prompt, response or credential becomes durable evidence | Retain only prompt/request/response/session/log digests, safe event coordinates, counts, usage and sanitized terminal facts; delete raw disposable session/log/environment material during cleanup. |
| Cleanup erases the only failure evidence | Write the exclusive sanitized terminal outside the disposable root before literal-root removal; require terminal validation and process absence before acceptance. |
| Cleanup targets unrelated files | Resolve and verify the exact descendant of `C:/Users/sarashera/EMR4-worktrees/`; use literal paths and refuse root, workspace-parent, symlink or escape targets. |
| A synthetic success is overstated as EMR4 readiness | Claim boundary is one shaped non-product, one-request coding edit only; multi-turn reliability, product work, database/runtime safety and deployment remain unproved. |

## Protected boundaries

No second worker, retry, attempt 006, Docker, PostgreSQL, SQL, transaction,
database, product source/configuration, API, OpenAPI, GraphQL, schema,
migration, route, adapter, feature flag, allowlist, ordinary-practice,
generic-status `Arrived`, command grammar, first-party client, waiting-area,
product/patient/appointment/clinical/historical/protected data, production,
deployment, release, Pages or protected-ref action is authorised.

Passing evidence may prove only one provider-admitted DeepSeek request, one
successful exact native edit and one tool-result-concluded turn in a disposable
authored-synthetic non-product workspace under the pinned rc.7 Harness.
