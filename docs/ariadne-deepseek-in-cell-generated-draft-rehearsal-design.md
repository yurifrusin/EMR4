# Ariadne DeepSeek In-Cell Generated-Draft Rehearsal - Design

Date: 2026-07-23

Status: frozen for one authored-synthetic DeepSeek V4 Flash attempt

## Design statement

This rehearsal seats an agent in the previously empty chair without giving it
keys to the room. Claude Code supplies the in-cell control process; DeepSeek V4
Flash supplies remote cognition; the launcher is a deterministic turnstile;
and the accepted proofreader remains the only door out.

The model has freedom to reason over its complete supplied evidence universe.
It has no freedom to acquire evidence, invoke a tool, choose a destination,
change policy or act.

## Physical topology

```text
authored-synthetic image layer
              |
              v
  read-only work-cell container
  Claude Code 2.1.201, no tools
              |
       internal Docker network
              |
              v
  read-only one-use broker container
  provider key present only here
              |
       broker egress network
              |
              v
 DeepSeek Anthropic-compatible endpoint

generated drafts -> host memory -> deterministic proofreader
```

The internal Docker network is created with `--internal`. The work cell joins
only that network. The broker joins it plus a separate egress network and
publishes no port to the host. Neither container has a mount or Docker socket.

## The purpose-built launcher

The launcher reads only two fixed image files: the exact attempt and its output
schema. It records their hashes, validates their frozen contents and budgets,
constructs the locked system and evidence prompts, and spawns exactly one
Claude Code child.

Claude Code runs in bare and safe mode with:

- the exact `deepseek-v4-flash` model;
- no built-in tools;
- no slash commands, skills, plugins, MCP servers, Chrome or IDE connection;
- no session persistence;
- an empty read-only working directory;
- memory-only runtime scratch;
- a minimal explicit environment; and
- one broker base URL plus a one-use token.

The launcher captures bounded stdout and stderr in memory. It never prints raw
stderr. It parses only Claude Code's successful JSON result and the model's
JSON draft envelope. It may reject malformed framing or excess bytes; it may
not repair, complete or reinterpret a draft.

## The one-use broker

The broker accepts only authenticated
`POST /anthropic/v1/messages`. It validates the model identifier, request byte
limit and one-call budget, clamps `max_tokens` to 2,048, replaces the one-use
cell token with the provider key and forwards to the exact DeepSeek endpoint.

It rejects redirects, every other method/path/model and every later request.
Its logs contain only event codes, sizes, hashes, status and call counts.
Request and response bodies, headers and secrets are never logged.

## Model task

The model receives six opaque authored-synthetic context frames and a locked
five-port form. It applies explicit selection rules:

- treat patient identifiers as candidates, never verified identity;
- choose the lexically first patient candidate for staff review;
- rank available slots chronologically;
- include the first two ranked slots;
- select the earliest included slot;
- preserve the supplied practitioner, duration, revision and confirmation
  requirement; and
- emit only the five draft frames.

These rules make the first occupied rehearsal a transport, isolation, typing
and proofreader test. They are not an open-ended model-quality benchmark.

## Egress

The launcher returns either:

- one bounded envelope containing exactly five untrusted drafts and sanitised
  usage metadata; or
- one sanitised failure reason.

The host hashes the envelope in memory, validates it against the frozen schema
and sends the five drafts to the existing pure proofreader. It persists only
hashes, counts, fixed verdicts, usage counts, container policy and cleanup
facts. No downstream recipient or human action is invoked.

## Single-use semantics

A repository-local ledger moves from `armed` to `consumed` immediately before
the work-cell model process starts. A consumed ledger blocks every later run,
including recovery from malformed output or provider failure. Build and static
preflight may be repaired before consumption because they transmit no prompt
and start no model attempt.

## Evidence meaning

A pass proves only that one specific installed transport and provider-labelled
model returned five schema-valid authored-synthetic drafts which the accepted
proofreader verified under one inspected disposable topology.

It does not prove immutable provider weights, general prompt-injection
resistance, clinical correctness, PII safety, product integration, human
approval quality, durable orchestration, command safety, production readiness
or autonomous action.
