# Ariadne post-compaction active-operation latch threat-model delta

Date: 2026-08-13

Timestamp: 2026-08-13T09:14:16+10:00 (Australia/Brisbane)

Status: frozen

| Threat | Control |
|---|---|
| Chronological last prompt replaces unfinished work after compaction | Latch states that recency is not authority and side questions/status requests answer then resume. |
| Terminal response silently ends an authorised tranche | `in_progress` requires `terminal_response.permitted=false`; terminal-intent validation fails closed. |
| Stale checkpoint causes duplicated or restarted work | Exact source HEAD, completed stage and next executable stage are mandatory. |
| Latch claims progress without five-source authority | Every continuation receipt still requires the existing five sources and additionally validates the latch. |
| User pause or redirect is ignored | Explicit pause/replacement classifications remain admitted and require a reason. |
| A completed/blocked label is used as a ceremonial stop | Non-progress states require a terminal reason; policy still limits blocking and user attention to existing accepted conditions. |
| Latch becomes a new authority source | Schema and policy label it evidence-only; authority remains in AGENTS.md, accepted plans and Yuri decisions. |
| Mutable metadata opens product surfaces | Validator is pure and repository-local; no route, database, provider, credential, network or product operation is imported or executed. |

Residual risk: a language model can still ignore repository policy. The latch
reduces ambiguity and makes that error mechanically visible in the required
continuation receipt; it cannot intercept the host application's final-channel
operation directly.
