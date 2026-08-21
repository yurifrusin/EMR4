# Threat-model delta: rebound future-runner agent-creation boundary rehearsal

Date: 2026-08-22

Timestamp: 2026-08-22T01:46:01.9815058+10:00 (Australia/Brisbane)

Status: **frozen before implementation or execution**

## Scope delta

This tranche advances from exact native runner activation to one real
`agents.create()` transaction, but deliberately vetoes the transaction at its
synchronous setup commit before registry publication. It grants no live agent,
live session, turn, model/provider request, target use or product authority.

## Assets

- exact rc.7 factory, session-registry and preset-mount source bytes;
- exact rebound runner/helper and stock-headless readiness bindings;
- exact `emr4-bounded-worker` preset and `edit`, `glob`, `read` projection;
- one fixed private identity and one exact publication-veto code;
- lifecycle counters, typed sidecar, all-zero broker reading and controller
  terminal;
- process, registry, target and disposable-root absence.

## Trust boundaries and controls

| Threat | Fail-closed control |
|---|---|
| A prepared private Session is misreported as no session object | The plan explicitly records one private session preparation. The zero claim applies only to live registry entries and lifecycle publication events. |
| A prepared Agent is misreported as a published worker | Accepted coordinate is `prepublication_veto`; one private preparation is reported separately from zero live agents and zero occupied workers. |
| `agents.create()` publishes before the stop | The stop is thrown by the synchronous setup commit, which exact package bytes place immediately before `publish`; independent listeners and registry readback must remain zero. |
| A fake runner bypasses the real factory | The descendant must call the injected `agents.create()` exactly once; exact agent-loop source bindings and the prepared `agentCtx.agent`/session identity are required. |
| Preset composition is skipped or widened | The accepted guard must mount the exact 158-byte `emr4-bounded-worker` preset and project exactly `edit`, `glob`, `read` inside unpublished setup. |
| An unexpected error is mistaken for the designed stop | Only the exact `EMR4_AGENT_PUBLICATION_STOP` rejection and exact finite sidecar coordinate pass; no raw error text is retained. |
| A returned handle is quietly disposed and called equivalent | Any resolved `agents.create()` call is a failure. Acceptance requires no handle and no publication/disposal lifecycle edges. |
| Provider configuration triggers traffic | No message enters the inbox and no turn starts; broker and network guards remain independently all zero; any request or network count rejects. |
| Session identity or cwd escapes evidence | The fixed id enters evidence only as an expected digest and equality booleans; the cwd is the disposable root and no absolute raw path is retained. |
| A standing preset mount survives the proof | It exists only inside the one disposable native process; acceptance requires process and root absence before evidence publication. |
| A second attempt obscures causality | One attempt id, one native process, zero retry/resume/fallback and exclusive canonical outputs. |
| Target or product state is touched | The inert target is absent before/after; no turn or tool call exists; repository/product/config/data surfaces remain closed. |

## Residual risk

This proves the native factory can construct and fully compose a bounded
DeepSeek-routed agent up to the atomic publication edge while deterministic
controls retain veto authority. It does not prove a published session, a model
request, DeepSeek transport, coding quality, broker dispatch, target editing or
product-development fitness.

## Security acceptance

Security acceptance requires exact source/package/preset bindings, one native
process, one real factory invocation, the exact prepublication veto, zero live
registries and lifecycle announcements, all downstream counts zero, no raw
retention, complete cleanup, preserved untracked files and unchanged protected
refs.
