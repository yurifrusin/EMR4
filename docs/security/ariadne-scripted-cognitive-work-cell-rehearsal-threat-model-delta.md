# Threat Model Delta - Ariadne Scripted Cognitive Work Cell Rehearsal

Date: 2026-07-23

Scope: repository-local, in-memory, authored-synthetic rehearsal only

## Boundary statement

This delta covers one finite deterministic runner, one authored-synthetic tape,
one committed evidence projection and deterministic tests. The runner reuses
the accepted Bounded Cognitive Work Cell proofreader and reads only fixed local
artifacts. It has no model, provider, real container, database, event feed,
product API, network, live mailbox, persistence, thread, timer, human-gate UI or
command connection.

The trust boundary has two layers:

1. the existing proofreader remains the sole egress verifier; and
2. the rehearsal control plane may apply only the exact computed disposition
   through a finite source-hashed tape.

## Assets and invariants

- exact accepted-protocol source hash;
- pre-authored attempts and drafts only;
- proofreader sovereignty over verdict and disposition;
- immutable retry and supersession lineage;
- no partial atomic-group release;
- no human routing for rejected frames;
- finite forward-only execution;
- process-memory-only state and evidence;
- transition hash-chain integrity; and
- zero external effect or command authority.

## Threats and deterministic mitigations

| Threat | Failure mode | Required mitigation |
|---|---|---|
| Script becomes adaptive executor | Tape chooses a branch, loops, waits or discovers work | Fixed ordered array, frozen action vocabulary, hard step limits and no branch/loop/timer fields |
| Draft generation laundering | Runner synthesises a corrected or fresh draft | Every attempt, draft and case must resolve to the accepted protocol; runner has no generation action |
| Proofreader override | Tape declares release after reject or changes a verdict | Expected disposition must equal the freshly computed accepted proofreader result |
| Partial release | Tape records only a convenient subset of a verified or atomic group | Release step must equal the complete proofreader edge set; rejected atomic case has no release step |
| Human-gate bypass | Rejected or non-human edge is routed to the gate | Human step must equal the complete verified-human-gate subset and occurs only after verified release |
| Human action laundering | Inert gate record is described as approval | `human_action_performed: false`, `command_authority: false` and authority terminal state |
| Unbounded retry | Tape resubmits indefinitely or repeats an attempt | Each attempt may submit once; later submission requires exact `retry_of` lineage and hard step ceilings |
| Retry feedback injection | Correction record carries draft content or new instructions | Rehearsal records only accepted coordinates and hashes; no draft body is copied into transition evidence |
| Fabricated successor | Tape invents a retry after atomic failure | A scenario may stop at correction-requested; any later submission requires an existing accepted lineage |
| Fresh-read simulation | Grant binding creates replacement data | Only accepted grant may bind; it must remain non-executing and return no data |
| Stale completion resurrection | Old attempt completes after generation change | Exact supersession trace plus mandatory stale-completion rejection before terminal state |
| Source drift | Protocol or tape changes while expected evidence remains stale | Canonical source hashes bind the run; schema, semantic validation and exact evidence comparison fail |
| Evidence rewrite | Transition history is reordered or modified | Forward sequence, previous-hash link, per-record hash and final chain hash |
| Persistence creep | Runner writes a checkpoint, mailbox or evidence file | No write API; static AST checks reject file-write methods and persistence imports |
| Concurrency creep | Thread, timer or async scheduler changes ordering | Imports and actuator fields for thread, time, async, callback and delay are rejected |
| Adapter smuggling | Tape embeds endpoint, DSN, topic, query, command or credential | Active actuator-key inspection and exact per-action fields fail closed |
| Diagnostic echo | Caller-controlled labels reach terminal output | No caller-selected path; CLI emits fixed labels and aggregates only |
| API authority drift | In-memory envelope is treated as a GraphQL/REST/product call | API Spine surfaces are absent and closed; candidate and human envelopes remain non-authoritative |
| Evidence overclaim | Rehearsal is described as agent/container/product runtime proof | Exact evidence label and explicit unproved-surface inventory |

## Residual risks deferred to later authority

- adaptive-model prompt injection, hallucination and tool use;
- real container escape, workload identity and network enforcement;
- live authorization, PHI minimisation and purpose limitation;
- operational concurrency, cancellation and race handling;
- durable queues, retries, dead letters, recovery and retention;
- mailbox authentication and message delivery semantics;
- human-gate role authentication, coercion, usability and signed decisions;
- backend command revalidation, audit and idempotency; and
- production observability, RLS, encryption and incident response.

No residual risk here authorises a larger runtime.
