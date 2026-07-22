# Ariadne Scripted Cognitive Work Cell Rehearsal - Design

Date: 2026-07-23

Status: repository-local in-memory authored-synthetic rehearsal

## Relationship to the accepted protocol

The rehearsal is a direct descendant of the accepted Bounded Cognitive Work
Cell and Proofreader Gate protocol. It changes no predecessor frame, attempt,
port, verdict, repair, retry budget, grant, supersession or authority rule.

The predecessor proved the static grammar. This descendant exercises that
grammar as a finite state sequence. It answers a deliberately smaller question
than a real agent runtime: can a deterministic control plane consume already
authored attempts and proofreader outcomes in the correct order without
silently widening authority?

The answer is limited to process memory and authored-synthetic evidence. No
adaptive reasoner is attached, and the runner never generates a draft.

## Execution boundary

The word "rehearsal" is intentional. The local Python process executes the
state machine, but every external-effect boundary remains false:

- `rehearsal_execution_enabled: true` means only that the finite tape advances;
- `in_memory_only: true` means transition state is returned to the caller and
  never written by the runner;
- `external_effects_enabled: false` excludes reads, writes and calls;
- `adaptive_agent_attached: false` excludes model or fake-model cognition;
- `container_started: false` excludes runtime isolation claims;
- `persistence_enabled: false` excludes mailbox, queue, checkpoint and retry
  storage;
- `human_action_performed: false` makes the gate a destination envelope only;
  and
- `command_authority: false` keeps every appointment and product action closed.

The runner reads only two fixed repository artifacts: the canonical rehearsal
tape and the accepted canonical work-cell protocol. It exposes no caller-
selected path and has no write method.

## Finite authored tape

The tape contains eight independent scenarios and 53 total steps. Each
scenario starts at `ready`, advances through a numbered ordered list and ends
at one declared terminal state. The hard ceiling is eight scenarios, 32 steps
per scenario and 256 total steps.

No step can name a branch condition, loop, jump, timer, callback, executable
string, endpoint or dynamic capability. The runner accepts only eleven actions:

1. submit one declared immutable attempt;
2. invoke the accepted proofreader for its exact verification case;
3. apply the computed disposition;
4. record the complete verified release set;
5. record the verified human-gate subset;
6. record a bounded correction request;
7. bind the accepted inert fresh-read grant;
8. supersede along accepted lineage;
9. reject completion from the stale generation;
10. abort the declared failed edge; and
11. finish at the declared terminal state.

The tape cannot discover a next step. Its next action is simply the next
authored array element. Sequence, state and source-hash drift fail closed.

## Proofreader remains sovereign over egress

At `verify-drafts`, the runner calls the already accepted pure proofreader. It
does not carry its own schema, grounding, freshness, authority, repair or
atomic-consistency logic.

For each step, the runner compares the authored expected disposition with the
computed result. A mismatch is `revision_required`; the tape cannot say
"release" after the proofreader says "abort" or "retry". A release step must
name the entire proofreader-produced edge set. A human-gate step must name the
entire verified human-gate subset. Missing or additional members fail closed.

This preserves the metaphor: the scripted work cell supplies pre-authored
typing, the deterministic proofreader decides whether it leaves the desk, and
the control plane can only carry out the proofreader's typed disposition.

## Scenario coverage

### Primary multi-output work

The first attempt emits the accepted five ports. All five verified envelopes
enter the in-memory release set; only the human-review and advisory envelopes
enter the inert human-gate set. The scenario stops at
`awaiting-human-authority`. No human action occurs.

### Canonical repair

Two scenarios exercise the accepted repair variants. One repaired UX envelope
releases downstream; one repaired booking-review envelope routes to the inert
human gate. The runner observes two immutable proofreader repair receipts and
adds no repair rule.

### Bounded retry

The schema scenario records one minimal correction request and advances only
from attempt 4 to accepted `retry_of` attempt 5. The later draft verifies and
routes to the human gate.

The grounding scenario records one minimal correction request, advances from
attempt 6 to accepted attempt 7 and then observes the retry-budget
`abort-edge`. No third attempt can be represented.

### Fresh-read supersession

The stale scenario observes `fresh-read-and-supersede`, binds only the accepted
grant with `execution_enabled: false` and `returns_data: false`, advances from
attempt 8 to accepted generation-2 attempt 9, records stale-completion rejection
and stops at `awaiting-fresh-context`. It performs no read and fabricates no
replacement frame.

### Authority and atomic stops

The authority scenario aborts immediately and releases nothing. The atomic
inconsistency scenario records one bounded correction request, releases neither
group member and stops without inventing a later attempt.

## Immutable transition evidence

Every step becomes a transition record containing:

- global and scenario-local sequence;
- fixed scenario and action labels;
- from-state and to-state;
- a canonical hash of action-specific accepted coordinates;
- the previous transition hash; and
- its own canonical transition hash.

The seed binds the complete rehearsal-tape hash and accepted-protocol hash.
Two executions return byte-identical evidence. The committed projection omits
the full 53-transition tape for compactness but retains per-scenario terminal
hashes and the final chain hash.

## Public diagnostics

The CLI exposes only `validate`, `rehearse` and `trace`. It accepts no document
path, writes no file and returns fixed labels plus aggregate counts. The full
internal evidence remains available to deterministic tests, but caller-selected
titles, scenario identifiers, references or rejection details are never echoed
by the public command surface.

## API Spine result

Boundary classification:
`repository_local_in_memory_authored_synthetic_control_plane_rehearsal`.

The rehearsal receives only the predecessor's typed, minimal and source-
labelled synthetic context. It treats identity, availability, policy and
freshness as supplied facts. Candidate and advisory envelopes remain non-
authoritative. GraphQL is read-only and unused; REST/OpenAPI is the explicit
future command boundary and unused; the tape is declarative input rather than
policy or product authority. No API Spine or product artifact changes.

## What remains unproved

This result does not prove adaptive cognition, request interpretation, prompt
safety, model behaviour, token budgets, real container isolation, live
authorization, product context sourcing, database or event connectivity,
mailbox delivery, concurrency, cancellation, durable retry, persistence,
retention, human-gate usability, signed approval, backend revalidation,
appointment commands, PII handling, production enforcement or product
behaviour.

Every such surface remains a separate Yuri decision.
