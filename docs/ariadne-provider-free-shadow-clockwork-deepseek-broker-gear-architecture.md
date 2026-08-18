# Ariadne / DeepSeek shared bureaucratic-clock gear architecture

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: normative shadow architecture candidate

Source HEAD: `a29e99c2fbfca59a24c348ded49dd29352b72aa3`

## Architectural decision

EMR4 should have one causal clock, not two cooperating diaries. Ariadne owns
the clock source. The DeepSeek broker becomes a temporarily engaged gear: an
admitted Ariadne tick transfers the next-sequence lease through one digest-
bound WorkOrder; broker events continue that exact chain; one terminal result
returns to Ariadne; and Ariadne's digest acknowledgement disengages the gear
and permits the next orchestration tick.

The “clockwork” is deliberately not a model memory aid. It is a deterministic
state reducer. It observes the current latch, stage catalogue, Git/ref
snapshot, materialized evidence registry, incident register and previous
journal tip. The engine, not the orchestrator, supplies all values that have
repeatedly drifted: source object, stage, disposition, side-effect class,
attempt identity, evidence digest, sequence, revision, count and WorkOrder
binding.

## The reading

The only meaningful input is that the configured next stage is being
evaluated. There is no caller-authored closeout manifest and no field through
which a seven-character Git abbreviation, remembered count, invented attempt
name or future evidence path can enter.

The resulting tick is a content-addressed statement:

```text
previous acknowledged tick
        + current latch and configured stage
        + machine-resolved Git/ref state
        + already-materialized evidence identities
        + derived incident/attempt state
        = next causal tick and its projections
```

Wall-clock and monotonic durations can accompany the tick as observations, but
they are excluded from its digest and cannot order events.

## Gear engagement

For a DeepSeek stage, Ariadne first records `admitted`. The derived WorkOrder
binds that tick, the exact native-Harness package, EMR4 profile, permission
preset, tool view, owned/forbidden paths, authority ceiling and process lease.
The broker accepts both the WorkOrder and its independently supplied digest.

The sequence lease then belongs to the broker. Ready, rejection, provider-
start, response, tool and terminal observations extend the same digest chain.
The result envelope carries only identifiers, counts and content digests. Raw
prompts, reasoning, secrets and product payloads do not become clock metadata.

The lease returns only after Ariadne independently validates the complete
stream and appends `acknowledged` over the exact terminal-result digest. The
broker cannot emit after terminal; Ariadne cannot advance before acknowledgement.
That clutch rule makes unexplained missing worker results a visible stopped
clock rather than an ambiguous orchestration memory.

## Presets and versatile Harness features

The native Harness's presets are used as pinned, reusable configuration
profiles:

- `emr4-readonly-review` selects read/search/test-only capability;
- `emr4-bounded-worker` selects exact owned-path edit/glob/read behavior,
  serial tools, no automatic retry and no fallback; and
- `emr4-provider-free` retains the trace and validation shape without provider
  credentials or external I/O.

The stage catalogue selects one exact profile/preset digest. A preset never
confers authority merely because the Harness can perform the action. Specialist
workflows or auxiliary/subagent presets remain closed unless an accepted stage
assigns them a bounded package and current policy permits them.

Yuri's prepaid provider balance remains the monetary ceiling. The gear does
not add a redundant Harness-native financial budget. It still records calls,
tokens, retries and process limits as measurements and retains EMR4's separate
authority/data/tool ceilings.

## Failure and recovery

Every rejected or admitted attempt produces one terminal receipt. Rejections
are digest-only. Started attempts end in `succeeded`, `failed` or
`unknown_commit`; unknown commit releases no success and cannot retry until
bounded readback. Recovery creates a new derived attempt ordinal and preserves
the old chain.

Stale parent, replay, sequence gap, concurrent writer, wrong lease owner,
profile/preset/tool drift, duplicate terminal, result-before-start, broker-
after-terminal, acknowledgement-before-terminal and projection from an
unacknowledged tip all fail closed.

## Projection model

Continuity, Compass, report, latch, register aggregate, receipts and broker
bindings are views of the same acknowledged journal prefix. They are reduced
and validated together, written to a private shadow generation and published
with one atomic directory rename. Exact historical facts remain immutable
receipts; mutable current state is tested structurally rather than by a growing
list of predecessor literals.

This architecture does not solve live migration of independently addressed
canonical files. No existing updater, latch, register or preflight is retired.

## Efficacy as an instrument reading

The gear must report, from the journal and repository rather than prose:

- manual binding fields;
- failure-induced procedural reruns;
- maintained mutable-current projection fixtures; and
- uncaught escapes to publication, external dispatch or acknowledgement.

It also reports provider attempts, rejected drafts, commands, files, lines,
validation-before-write, partial publications and timing. Expected hostile
tests do not count as reruns. Shared-engine growth cannot be omitted. Timing is
not an acceptance criterion.

The next shadow rehearsal must have zero caller-supplied derived fields, at
least 50 percent fewer failure-induced reruns than its frozen comparator, no
new mutable-current fixture, no coverage loss, zero partial publication and
zero escape before any live-adoption discussion.

## Authority boundary

This architecture is provider-free and non-actuating. Current shadow execution
admits only read-only and private shadow-generation effects. Candidate writes,
provider requests, task-branch Git, protected Git and product runtime are
represented so they can be denied unambiguously; none is opened here.

No live clock adoption, current-control retirement, occupied DeepSeek call,
HMR retry, ordinary-practice enablement, product/API/database/client change,
product/patient/clinical data, production runtime, deployment, release, Pages
or protected-ref movement is authorized.
