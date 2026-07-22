# Ariadne Real-Isolation Rehearsal - Tranche Plan

Date: 2026-07-23

Owner: Yuri / GPT Sol High

Decision: `approved_scope_frozen_for_one_disposable_real_isolation_rehearsal`

## 1. Purpose

Yuri authorised the smallest materially new descendant of the accepted
Scripted Cognitive Work Cell Rehearsal: execute the unchanged finite,
authored-synthetic tape once inside one disposable local container and compare
the declared isolation policy with Docker's effective configuration and the
workload's bounded observations.

The target result is
`ariadne_real_isolation_rehearsal_pass`.

This tranche tests one isolation envelope. It does not add cognition, generate
a draft, connect a product surface or claim that containers make an agent safe.

## 2. Authority and inherited boundaries

This tranche may:

- inspect the local Docker engine and the exact official-image registry
  manifest;
- pull one digest-pinned official Python base image if it is not already
  present;
- build one local derived image from an allowlisted temporary context;
- create, inspect, start, inspect and remove one fixed-name container;
- run the unchanged accepted eight-scenario, 53-transition tape twice inside
  that container;
- inspect effective network, root-filesystem, identity, capability, mount,
  environment and resource-limit policy;
- record a blocked root-filesystem write probe and a loopback-only interface
  observation;
- remove the container, derived image, any base-image reference acquired by
  this run and the temporary context; and
- add deterministic repository-local tests, evidence and Continuity metadata.

It may not:

- attach an adaptive agent, fake agent, model, provider, plugin or worker;
- generate, alter or infer a draft, input frame, proofreader verdict or next
  step;
- connect to PostgreSQL, a database, event feed, broker, product API, GraphQL,
  REST/OpenAPI, FastAPI, live mailbox, human-gate UI or command adapter;
- mount the repository, host directory, Docker socket, secret, credential,
  named volume or writable input into the container;
- enable container networking, publish a port, perform a network call from the
  workload, or start another process outside the single foreground payload;
- use PII, clinical content, prompts, transcripts, protected evidence or
  historical Diary material;
- persist a retry, mailbox, checkpoint, evidence store or container; or
- prune daemon-wide images, containers, volumes or build cache.

## 3. API Spine classification

Boundary classification:
`local_disposable_container_authored_synthetic_isolation_rehearsal`.

The accepted API Spine remains unchanged. Context is typed, minimal,
source-labelled and non-authoritative. Identity, availability, policy and
freshness are accepted synthetic facts. GraphQL is read-only and unused;
REST/OpenAPI remains the future command plane and is unused. No API Spine,
product source, API contract, database or UI artifact changes.

## 4. Frozen image provenance

The only permitted base is the Docker Official Image:

- human-readable tag observed before planning:
  `python:3.12.13-alpine3.22`;
- immutable pull/FROM reference:
  `docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322`;
- required platform: `linux/amd64`;
- required platform manifest digest:
  `sha256:9381e50cc82f4279b949fcd2d2f5e57cf97b1da2399eb956502364ceea2f4e83`;
- source: `https://github.com/docker-library/python.git`;
- source revision: `3362634339580d3232e65a66dd5a36c47ae7ff14`; and
- registry creation annotation: `2026-04-17T00:30:54Z`.

Tags, alternate digests, caller-selected images and unpinned pulls fail closed.
The derived image is local-only and uses the fixed tag
`ariadne-real-isolation-rehearsal:v1`.

## 5. Allowlisted build context

The host harness creates a new temporary directory and copies only the exact
regular, non-symlink repository files named by the frozen manifest. The list is
limited to:

- the derived-image Dockerfile and container payload;
- the accepted scripted runner and bounded proofreader;
- the accepted scripted tape and bounded work-cell protocol JSON;
- the committed predecessor evidence used for exact comparison; and
- the predecessor plan/design/threat/closeout files required by existing
  semantic reference validation.

Each source is SHA-256 recorded before copying and verified again inside the
temporary context. No repository root is a Docker build context. No build arg,
host environment value, secret or caller-selected path enters the image. The
Dockerfile contains no `RUN`, package installation or network operation.

## 6. Frozen effective container policy

The harness creates exactly
`ariadne-real-isolation-rehearsal-v1` with:

- `--network none` and no published or exposed port;
- `--read-only` and no bind, volume, tmpfs, device or Docker-socket mount;
- non-root `--user 65532:65532`;
- `--cap-drop ALL`;
- `--security-opt no-new-privileges=true` with the engine's default seccomp
  policy retained;
- `--memory 128m` and `--memory-swap 128m`;
- `--cpus 0.5`;
- `--pids-limit 32`;
- `--ulimit nofile=64:64`;
- a fixed hostname and labels; and
- no command override, host environment forwarding or secret attachment.

Before start, `docker inspect` must match the frozen policy. A mismatch triggers
cleanup without starting the container.

## 7. Workload proof

The single foreground payload:

1. verifies its UID/GID are 65532;
2. observes exactly the loopback network interface without attempting an
   outbound connection;
3. attempts one fixed write under `/workspace` and requires an OS-level
   read-only failure with no residual file;
4. verifies the allowlisted source hashes;
5. runs the accepted tape twice through the unchanged proofreader;
6. requires byte-identical full evidence and an exact match with the accepted
   committed evidence projection; and
7. emits one canonical JSON result containing only fixed labels, hashes,
   aggregate counts and isolation booleans.

After the payload exits, the host verifies exit code zero, no OOM condition and
the expected stopped state before explicit removal.

## 8. Cleanup and collision policy

Pre-existing use of the fixed container name or derived-image tag fails closed;
the harness never deletes an object it did not create. Objects created by this
run are tracked and removed in `finally` order. The acquired base reference is
removed only if it was absent before this run. The temporary build context is
deleted by the host runtime and its absence is verified.

No daemon-wide prune is permitted. Docker may retain unreferenced content or
BuildKit cache containing only the official base and allowlisted
authored-synthetic bundle. That bounded residual is recorded rather than
laundered into a stronger cleanup claim.

## 9. Exact implementation surface

- this plan, design, threat-model delta and closeout;
- `scripts/ariadne_real_isolation_rehearsal.py`;
- `scripts/ariadne_real_isolation_payload.py`;
- `orchestration/continuity/ariadne-real-isolation/Dockerfile`;
- `orchestration/continuity/ariadne-real-isolation-rehearsal-manifest.json`;
- `orchestration/continuity/ariadne-real-isolation-rehearsal-evidence.schema.json`;
- `orchestration/continuity/ariadne-real-isolation-rehearsal-evidence.json`;
- `.gitattributes` for the exact Dockerfile LF rule;
- `tests/test_ariadne_real_isolation_rehearsal.py`;
- exact receipts, Sol acceptance and metadata-only Continuity node; and
- mechanical Compass, handover and orchestration-ledger updates after pass.

## 10. Acceptance gates

The tranche passes only when:

1. the manifest and every allowlisted source hash validate;
2. image name, index digest, platform digest, architecture and provenance match
   the frozen record;
3. the temporary context contains exactly the allowlist and never the repo;
4. derived image configuration is fixed, non-root and has no build-time
   execution or caller input;
5. pre-start inspection proves the complete frozen effective policy;
6. the container has no mounts, secrets, host environment forwarding, port
   publication, extra capabilities or writable root filesystem;
7. the workload observes non-root identity, loopback only and a blocked fixed
   write with no residue;
8. two in-container tape runs are byte-identical and match the accepted
   predecessor projection (8 scenarios, 53 transitions);
9. stopped-state inspection proves exit code zero, no OOM and no engine error;
10. explicit cleanup proves the container, derived image, temporary context and
    run-acquired base reference are absent;
11. failure-path tests prove inspect-before-start, collision refusal, evidence
    rejection and cleanup ordering;
12. the accepted predecessor artifacts remain unchanged and their tests pass;
13. focused and combined Ariadne/API Spine/handover tests, Ruff, compilation,
    JSON/schema parsing and whitespace gates pass serially; and
14. closeout claims remain limited to one local disposable isolation rehearsal.

## 11. Allocation and deferred decisions

GPT Sol High owns the tightly coupled plan, harness, one real run, evidence,
acceptance and protected integration. No subagent or external model is used.

Fresh Yuri authority remains required for adaptive/generated cognition, any
model or provider, additional images or repeated/long-lived containers,
networking, writable or mounted runtime input, secrets/workload identity,
concurrency, durable state, database/event/product connections, live mailboxes,
human-gate UI, signed approval, appointment commands, PII,
protected/historical evidence, production, deployment, release or autonomous
action.
