# Threat Model Delta - Ariadne DeepSeek In-Cell Generated-Draft Rehearsal

Date: 2026-07-23

Scope: one remote-provider, authored-synthetic, tool-less generated-draft attempt

## New trust boundaries

This tranche adds a real Claude Code process, a remote DeepSeek inference call,
one disposable work-cell container, one disposable credential-holding broker
container and one Docker-internal network. It adds no product or command
connection.

The provider and generated output are untrusted. The provider key is an asset
held only by the broker. The one-use broker token is a short-lived cell
capability and carries no product authority.

## Assets and invariants

- the work cell never receives the provider key;
- only authored-synthetic, opaque, non-clinical context is transmitted;
- the model receives no callable tools or ambient repository context;
- work-cell network reachability terminates at the broker;
- broker egress permits one exact path, model and call;
- prompt and generated bodies are memory-only and uncommitted;
- generated output remains draft-only behind the deterministic proofreader;
- cancellation, deadline, supersession and attempt consumption are terminal;
- containers and network are removed after the attempt; and
- evidence labels distinguish a live provider call from product/runtime proof.

## Threats and mitigations

| Threat | Failure mode | Mitigation |
|---|---|---|
| Provider-key exposure | Key enters the work cell, image, argv, logs or evidence | Broker alone inherits the host key by environment-name forwarding; images and cell omit it; evidence records names/booleans only |
| General cell egress | Claude Code contacts telemetry, updates, web or another endpoint | Cell joins only a Docker `--internal` network; nonessential traffic is disabled; broker accepts one exact API path |
| Tool emergence | Default Claude tools inspect files or start commands | `--tools ""`, safe/bare mode, empty workdir, no mounts, no MCP/plugins/skills/Chrome, non-root and capability-free container |
| Hidden second model call | Retry, fallback, web search or agent loop spends another call | Broker increments before forwarding, permits one request and rejects all later requests; no fallback model |
| Oversized cost/output | Provider default requests excessive generation | 65,536-byte request limit, `max_tokens` clamped to 2,048, one call and 8,192-byte draft limit |
| Prompt or output persistence | Docker logs, sessions or files retain content | no session persistence; memory-only scratch; raw host output never printed or committed; cell removed immediately |
| Broker logging leak | Proxy records headers or bodies | fixed metadata-only events with hashes, sizes and status; no raw values |
| Prompt injection | Evidence requests tools, authority or bypass | immutable system contract, empty tools and exact schema; proofreader independently rejects authority or egress violations |
| Schema laundering | JSON validity is treated as verified meaning | schema is only a pre-proofreader gate; accepted proofreader remains sole semantic egress check |
| Late output race | Timed-out result reaches proofreader | launcher timeout kills child; late/cancelled state rejects before proofreader |
| Attempt replay | Operator reruns after malformed or failed result | consumed ledger written before model start and checked before every execution |
| Container escape or host access | Compromised runtime reads host or Docker | no mounts/socket/ports, read-only root, non-root, all capabilities dropped, no-new-privileges and finite resources |
| Base/package substitution | Mutable image/package changes the exercised binary | package version pinned; build context allowlisted; resolved base digest and built image IDs recorded; registry/package provenance remains a residual risk |
| Model provenance overclaim | Provider alias is described as immutable weights | evidence says provider-declared `deepseek-v4-flash`; no weight hash or reproducibility claim |
| Synthetic evidence overclaim | Passing fixture is described as clinical/product safety | closeout is limited to one authored-synthetic provider and proofreader rehearsal |

## Residual risks

The broker and Docker daemon remain host-trusted. Provider retention,
jurisdiction, account policy and provider-side model changes are not
independently verifiable. Claude Code and the Node base remain third-party
supply-chain inputs. A model can still return invalid or adversarial content;
the single attempt may therefore close `revision_required`.

No residual risk grants PII, product reads, persistence, commands, production
or another provider attempt.
