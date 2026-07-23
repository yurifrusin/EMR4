# Ariadne DeepSeek In-Cell Generated-Draft Rehearsal - Tranche Plan

Date: 2026-07-23

Owner: Yuri / GPT Sol High

Decision: `approved_scope_frozen_for_one_deepseek_v4_flash_generated_draft_attempt`

## 1. Purpose

Yuri selected the first occupied-cognition rehearsal described after the
accepted Bounded Agent-Admission Design. One purpose-built, tool-less Claude
Code control process will inhabit one disposable work-cell container and use
DeepSeek V4 Flash for inference through a separate one-use egress broker.

The model receives only the accepted six authored-synthetic frames and may
return only the accepted five draft ports. The deterministic proofreader
remains the sole egress route.

Exact passing result:
`ariadne_deepseek_in_cell_generated_draft_rehearsal_pass`.

A failed build or preflight does not consume the model attempt. Starting the
work-cell model process consumes the only authorised attempt regardless of
whether a provider request or valid draft follows. No automatic or manual
second attempt is authorised.

## 2. Selected topology and provenance

The selected topology is
`in_cell_claude_code_remote_provider_broker_v1`:

- the Claude Code control process runs inside the work-cell container;
- inference remains remote at DeepSeek's Anthropic-compatible API;
- a separate broker container holds `DEEPSEEK_API_KEY`;
- the work cell receives only a generated one-use broker token;
- the work cell joins one Docker-internal network and has no direct Internet
  route;
- the broker joins that internal network plus one egress network, exposes no
  host port and accepts one allowlisted provider request; and
- both containers and the internal network are removed after the attempt.

Model identifier is exactly `deepseek-v4-flash`. Claude Code is pinned to npm
package `@anthropic-ai/claude-code@2.1.201`. The build uses a resolved,
recorded Node 24 Bookworm Slim image digest. Provider-side weights are not
available for hashing; provenance is therefore limited to the provider-
declared model identifier, API endpoint, observed usage and request/response
hashes. No claim of immutable model weights is permitted.

Claude Code is proprietary software already installed for the authorised EMR4
worker lane. This tranche builds an ephemeral local test image and does not
vendor, redistribute or commit its binary.

## 3. Authority

This tranche may:

- build two local images from an allowlisted temporary context containing only
  the Dockerfile, dedicated launcher, dedicated broker, exact synthetic
  attempt and output schema;
- download the pinned Claude Code npm package and a resolved Node base image
  during image construction;
- start one broker container and one work-cell container under the frozen
  resource and network policy;
- transmit the exact authored-synthetic prompt to DeepSeek V4 Flash once;
- receive up to five draft frames and 8,192 canonical output bytes;
- run the accepted deterministic proofreader over those untrusted drafts;
- record sanitised hashes, counts, usage, verdicts, image/container policy and
  cleanup evidence;
- add deterministic tests and closeout documentation; and
- perform normal check-gated Git integration after acceptance.

It may not:

- transmit PII, PHI, clinical text, patient names, real identifiers, protected
  holdouts, historical Diary material, repository content or secrets;
- expose `DEEPSEEK_API_KEY` to the work cell;
- give Claude Code `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`, web,
  browser, MCP, plugin, skill, subagent or any other model-callable tool;
- mount the repository, host filesystem, Docker socket, credential store or
  any persistent volume into either container;
- give the work cell general Internet access or allow any provider path other
  than one `POST /anthropic/v1/messages`;
- permit provider fallback, a second provider request, autonomous retry,
  context retrieval, fresh read, session persistence or late-result release;
- connect PostgreSQL, GraphQL, REST/OpenAPI, FastAPI, product APIs, event feeds,
  mailboxes, human-gate actions or commands; or
- treat generated output as identity, availability, policy, approval, audit,
  command or control-plane authority.

## 4. Context and output contract

The input is the accepted six-frame authored-synthetic context:

1. synthetic request scope;
2. principal scope fixture;
3. opaque patient candidates;
4. selected practitioner fixture;
5. exact availability fixture; and
6. evaluated appointment policy fixture.

The evidence payload remains under the inherited 4,096-byte cap. The compiled
model prompt, which also contains the locked output form and instructions,
must remain under 32,768 UTF-8 bytes. The broker rejects a provider request
body above 65,536 bytes.

The model may return exactly one draft for each of:

- `port-ux`;
- `port-human-review`;
- `port-audit`;
- `port-orchestrator`; and
- `port-advisory`.

Output must validate against the frozen Draft 2020-12 schema before entering
the proofreader. Schema validation is not proofreader acceptance and cannot
repair generated content.

## 5. Budgets and cancellation

- authorised occupied attempts: 1;
- provider calls: 1;
- provider fallback calls: 0;
- maximum provider output tokens: 2,048;
- maximum prompt bytes: 32,768;
- maximum provider request bytes: 65,536;
- maximum generated draft bytes: 8,192;
- maximum generated drafts: 5;
- model-process deadline: 180 seconds;
- cell memory/swap: 768 MiB / 768 MiB;
- cell CPUs: 1;
- cell PIDs: 64;
- broker memory: 256 MiB;
- broker CPUs: 0.5;
- broker PIDs: 32; and
- scratch: size-limited, memory-only `/tmp`.

The broker deterministically lowers any larger provider `max_tokens` value to
2,048 and rejects every request after the first. Current published DeepSeek V4
Flash rates are recorded as cost context only. The hard safety controls are
one call, request bytes and output tokens; provider billing remains the
authoritative cost source.

Cancellation, timeout and supersession are terminal. The launcher kills the
child process, emits only a reason code and rejects late output before the
proofreader. The consumed-attempt ledger prevents rerun.

## 6. Proofreader and API Spine

Boundary classification:
`one_attempt_authored_synthetic_remote_provider_generated_draft_rehearsal`.

Generated content is `model_interpretation`-class draft evidence. The accepted
proofreader applies exact schema, scope, source, freshness, authority,
grounding, selection and atomic-consistency checks. Passing a proofreader
check creates only the already-defined verified-edge envelope; the rehearsal
performs no downstream, human or command action.

GraphQL is read-only and unused. REST/OpenAPI is the command plane and unused.
Audit-port output is generated evidence, not a persisted audit event. No API
Spine or product artifact changes.

## 7. Acceptance gates

The tranche passes only when:

1. the five-source rehydration receipt passes and protected refs begin aligned;
2. the plan, threat delta, attempt and output schema are internally consistent;
3. the Docker build context contains only the exact allowlist;
4. both built images and their resolved base/package provenance are recorded;
5. the work cell has no mounts, host ports, provider key or non-internal
   network and runs read-only, non-root, capability-free and no-new-privileges;
6. the broker has no host port or mount, holds the provider key outside the
   cell and permits exactly one path, model and call;
7. Claude Code runs `--bare`, `--safe-mode`, `--tools ""`, no session
   persistence, no slash commands, no Chrome and no configured MCP server;
8. the consumed-attempt ledger is written before the model process begins;
9. broker metadata proves no more than one provider call;
10. raw prompt, raw provider response and generated draft bodies are not
    committed or printed by the host runner;
11. any generated output is byte/draft bounded and schema checked without
    repair;
12. the accepted deterministic proofreader receives the exact generated
    drafts and records all five verdicts;
13. both containers and the internal network are explicitly removed;
14. focused and combined Ariadne/API Spine/handover checks pass serially; and
15. closeout claims no model quality, immutable-weight, PII, product, command,
    human-action, production or autonomous-safety result beyond the evidence.

If the single generated attempt fails any output or proofreader gate, the
accurate result is
`ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required`.
The failure is preserved and no retry occurs.

## 8. Allocation

GPT Sol High owns plan, implementation, deterministic verification, the single
provider attempt, acceptance and integration. DeepSeek V4 Flash is the
untrusted cognition under test, not an implementation worker or reviewer. No
subagent or independent veto reviewer is assigned before the single attempt.
