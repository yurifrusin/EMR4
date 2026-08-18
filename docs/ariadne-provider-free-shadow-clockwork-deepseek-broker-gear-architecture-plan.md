# Ariadne provider-free shadow clockwork / DeepSeek broker gear architecture plan

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: `frozen_shadow_architecture`

Source HEAD: `a29e99c2fbfca59a24c348ded49dd29352b72aa3`

Target result:
`ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_architecture_pass`

Reasoning level: Extra High freezes the causal-time, authority, migration and
efficacy meanings. High is sufficient for the bounded provider-free contract,
deterministic validator, hostile mutations, review packaging and closeout while
this plan remains unchanged.

## Objective

Freeze the narrowest architecture that lets Ariadne and the DeepSeek native-
Harness broker advance on one causal clock rather than exchanging hand-copied
bureaucratic state.

The clockwork takes a reading from validated current sources: the live
operation latch, configured stage catalogue, fixed Git/ref snapshot,
materialized evidence registry, incident register and previous journal tip. It
derives the full source object, operation/stage/disposition, side-effect class,
attempt identity, evidence identities, sequence and digests. None of those is a
caller-authored binding field.

When an admitted stage selects a DeepSeek work package, one digest-bound
WorkOrder becomes the gear tooth between the two harnesses. The broker may
continue only that exact parent tick. Ariadne may advance only after validating
and acknowledging exactly one terminal broker-result digest. Wall time is
metadata, never order.

This is an architecture and provider-free shadow-validation tranche. It does
not adopt a live clock, change the accepted transactional engine or broker,
start the native Harness, call DeepSeek/Gemini during implementation, retire a
current control or alter product authority.

## Accepted predecessor and factual baseline

The architecture must preserve and distinguish:

1. transactional closeout shadow acceptance at exact source
   `762cd8fd1a6493f4d4b82e24f97d851531b6f7f0`, which proves one hash-chained
   journal, derived closeout projections, atomic shadow publication and an
   opt-in provider-free broker WorkOrder;
2. the accepted unmounted check-in admission kernel at exact reviewed source
   `4204ec6348abb0f92b1a30314699d4a469fa860a`, whose closeout exposed the
   concrete stage/disposition, side-effect, materialized-evidence, attempt and
   full-Git requirements; and
3. the published task state at
   `a29e99c2fbfca59a24c348ded49dd29352b72aa3`, Continuity 326 / Compass 308 and
   register revision 521.

The retained kernel-closeout baseline is:

- manual-field count: not yet instrumented;
- occupied-provider retries: one;
- rejected register/pre-verifier drafts: four;
- failure-induced closeout/transition verification reruns: four;
- stale mutable-latch fixtures: two; and
- uncaught escapes: zero.

The earlier frozen transactional sample reduced 72 top-level legacy constants
to 54 manifest leaves, six files / 1,002 lines to five / 981, 12 publication
calls to one and seven controlled retries to zero. Those facts remain evidence;
they do not prove live adoption or remove the newer observed baseline.

## Frozen architecture

### 1. Clock sources and zero-derived-field invocation

One `take_reading` operation receives typed source objects, not a closeout
manifest:

- validated live operation latch;
- immutable configured stage catalogue and exact settings fingerprint;
- fixed Git/ref snapshot from the existing helper;
- materialized evidence registry entries containing path, content digest and
  creation tick;
- validated incident register and derived pattern report; and
- the last acknowledged journal tick or the configured genesis digest.

The invocation has no caller-supplied Git object, operation, stage,
disposition, effect class, attempt number, evidence digest, sequence, retry
count, peer link, population, cutoff, projection revision or WorkOrder binding.
Supplying any such field is an exact-key failure. The current latch and stage
catalogue select what reading can occur.

### 2. Typed causal tick

Every tick has a closed schema and contains:

- `clock_id`, `sequence`, `previous_tick_sha256` and `tick_sha256`;
- full lowercase 40-character resolved `source_commit` plus branch and
  protected-ref snapshot digest;
- exact `operation_id`, `stage_id`, `disposition` and `effect_class`;
- derived `attempt_id` and `attempt_ordinal` scoped to operation, stage, role
  and resource;
- settings, authority and forbidden-surface digests;
- zero or more already-materialized evidence object identities;
- actor/resource ownership and one bounded payload digest; and
- optional monotonic/wall-time observations excluded from tick identity and
  ordering.

Allowed dispositions are configured values only: `admitted`, `rejected`,
`started`, `succeeded`, `failed`, `unknown_commit`, `acknowledged` and
`superseded`. Every event digest is canonical sorted-key UTF-8 JSON without its
own digest field.

### 3. Effect classes and current posture

The closed architecture represents:

- `read_only`;
- `shadow_generation_write`;
- `candidate_workspace_write`;
- `provider_request`;
- `task_branch_git_write`;
- `protected_ref_write`; and
- `product_runtime_effect`.

The current shadow posture admits only `read_only` and
`shadow_generation_write`. Every other class is represented for unambiguous
future policy but denied here. A command manifest and external verifier tick
must be `read_only`; a generator in such a tick is rejected before execution.
Clock provenance never upgrades product or Git authority.

### 4. Attempt lifecycle and exhaustive receipts

An attempt is a derived state machine:

`admitted -> started -> succeeded | failed | unknown_commit`.

A policy/schema rejection produces `rejected` without `started`. Every
admitted or rejected attempt has exactly one terminal result receipt. A
terminal result becomes eligible for downstream projection only after one
`acknowledged` tick binds its exact digest. Duplicate terminal results,
acknowledgement before terminal, mismatched attempt identity and any event after
acknowledgement fail closed.

`unknown_commit` releases no success, requires bounded readback by the exact
attempt/idempotency identity and forbids automatic retry. A new attempt derives
a new ordinal and may be created only from an explicit configured recovery
stage; it cannot reuse or overwrite the old attempt.

### 5. The single-writer gear clutch

At any sequence the journal lease belongs to exactly one writer:

- Ariadne owns ordinary orchestration ticks;
- issuing a WorkOrder transfers the next-tick lease to the broker at an exact
  parent tick;
- the broker emits a contiguous provider-free event stream and one terminal
  `WorkerResultEnvelope`;
- Ariadne independently validates source, operation, stage, attempt, preset,
  authority, sequence and every digest; and
- only Ariadne's acknowledgement reclaims the next-tick lease.

Concurrent writers, stale parents, missing sequence values, replay, altered
events, a broker advance after terminal, or an Ariadne advance before terminal
acknowledgement are rejected. Rejection itself is recorded as a digest-only
tick by the current lease owner without incorporating untrusted payload text.

### 6. DeepSeek WorkOrder, preset and result binding

The WorkOrder is derived from one admitted Ariadne tick and includes:

- exact parent tick, clock, sequence, operation, stage and attempt identities;
- full source commit, exact branch/worktree, authority and forbidden-surface
  digests;
- exact owned/forbidden paths and command/test allowlist digests;
- pinned native-Harness package version/digest;
- selected versioned EMR4 profile family, permission preset and their digests;
- exact minimized tool view, with current bounded-worker default
  `edit`, `glob`, `read` only when that future effect class is separately
  admitted;
- zero automatic retry, no model/provider/transport fallback, auxiliary routes
  disabled unless a future accepted profile says otherwise;
- provider posture, cleanup/readback requirements and process-lifetime lease;
  and
- canonical whole-WorkOrder digest supplied independently to the broker.

The profile family retains `emr4-readonly-review`, `emr4-bounded-worker` and
`emr4-provider-free`; specialist presets require an independently assigned
package and prevailing policy. Presets are reusable configuration identities,
not authority: their selected digest must be allowed by the stage catalogue and
WorkOrder.

The result envelope binds the WorkOrder and terminal broker-event digest,
session identity hash, provider-call count, ordered tool/result digest,
candidate tree/diff digest when applicable, test-result digest, cleanup state
and a closed terminal class. It contains no raw prompt, reasoning, secret,
product payload or self-acceptance decision. Sol retains candidate acceptance.

Yuri's prepaid provider balance remains the monetary ceiling. This architecture
does not add a Harness-native financial budget mechanism. Process, authority,
tool, retry, output and provider-call measurements remain explicit and cannot
be interpreted as permission to spend or call.

### 7. Atomic projections

Journal append and prospective projections are reduced and validated in memory.
Continuity, Compass, report, latch, incident aggregate, receipts and broker
bindings are content-addressed views of the same acknowledged tick prefix.
Publication is to one private shadow generation followed by one atomic rename.

No projection may become current unless every declared projection validates
against the same journal tip. Partial publication, a stale current projection,
missing evidence identity, future evidence path or independent handwritten
revision/count fails before publication. Live canonical migration remains a
separate closed gate.

## Efficacy measurement contract

The architecture defines four primary readings, all derived from journal and
repository evidence rather than author claims:

1. `manual_binding_fields`: caller-supplied fields whose value could otherwise
   drift across Git, stage, attempt, evidence, count or digest projections;
2. `failure_induced_reruns`: distinct attempts or validation executions caused
   by a failed procedural invariant, separated from expected test cases;
3. `maintained_projection_fixtures`: assertions/files that name mutable current
   state rather than immutable event receipts or schema invariants; and
4. `uncaught_escapes`: seeded or observed invariant breaches that reach a
   published generation, external dispatch or downstream acknowledgement.

Secondary readings are provider attempts, rejected drafts, commands, files,
physical lines, validation-before-write, partial publications and monotonic
elapsed time. Timing is informational only.

This architecture passes by making each numerator, denominator, source and
exclusion deterministic. It makes no reduction claim. A later provider-free
shadow rehearsal may consider adoption only if caller-supplied derived fields
are zero, failure-induced reruns fall by at least 50 percent against a frozen
representative baseline, no new mutable-current fixture is required, all
existing coverage remains represented, partial publications are zero and
uncaught escapes are zero. Shared-engine growth and clean-run overhead must be
reported, never hidden by amortisation.

## Exact owned outputs

Sol may create or update only:

- this plan, one architecture document and its threat-model delta;
- one closed normative contract/schema plus deterministic evidence/report
  under
  `orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture/`;
- one provider-free architecture validator/runner and focused architecture,
  plan and hostile-mutation tests;
- required latch, five-source receipt, register and exact independent-review
  artifacts; and
- closeout, Sol acceptance, Yuri summary, Continuity updater/test, baton and
  Compass/Continuity projections if the architecture passes.

The accepted `orchestration_harness/transactional_closeout.py`,
`scripts/ariadne_deepseek_native_harness_broker.mjs`, native-Harness package,
profiles and presets are read-only predecessor evidence in this tranche. No
`app/**`, configuration, API Spine, route, migration, database, Diary/client,
provider launcher, deployment, Pages or protected-ref source is editable.

## Deterministic acceptance

Pass requires:

1. the fresh five-source preplanning receipt passes and the successor latch is
   valid with explicit DeepSeek/Gemini/native-subagent dispositions;
2. exact canonical-LF digests bind the accepted transactional plan, code,
   schema, efficacy evidence/closeout and kernel plan/closeout/Sol acceptance;
3. one closed contract/schema defines every clock source, tick field,
   disposition, effect class, attempt transition, lease transfer, WorkOrder,
   result, acknowledgement and projection rule;
4. all Git, stage, disposition, effect, attempt, evidence, count, sequence and
   digest values are engine-owned; caller-supplied derived values are rejected;
5. read-only/generative mismatch, stale parent, replay, sequence gap, concurrent
   writer, duplicate terminal, result-before-start, acknowledgement-before-
   terminal, broker-after-terminal and Ariadne-before-acknowledgement deny;
6. WorkOrder and result bind exact package/profile/preset/tool/source/authority/
   attempt/journal identities, and malformed or stale bindings fail before a
   simulated upstream boundary;
7. the efficacy definitions reproduce the kernel-closeout baseline exactly and
   reject supplied totals, hidden shared-engine cost, weakened coverage or
   timing-based acceptance;
8. at least 36 named architecture scenarios and 256 independent hostile
   contract mutations pass with zero escapes;
9. focused tests, applicable transactional-clock/broker/latch/Git/register/
   Compass/API Spine guards, compilation, Ruff and `git diff --check` pass; and
10. one fresh Gemini 3.7 Flash/high exact-candidate read-only veto passes after
    deterministic admission, with no silent fallback and unchanged clean HEAD.

## Parallelism assessment

- **DeepSeek:** declined. Authority/causal architecture is serial Sol work and
  occupied native-Harness use remains behind its separate provider-free HMR
  boot proof. The broker is inspected and modeled provider-free; Claude Code is
  not a fallback.
- **Gemini:** reserved for one independent exact-candidate architecture veto
  after deterministic admission. It receives no implementation, acceptance or
  integration authority.
- **Native subagents:** declined under current developer policy; no separable
  package outweighs briefing and reconciliation cost.

Reassess after plan freeze, deterministic admission, before verifier acceptance,
at closeout and before any live clock adoption or occupied DeepSeek worker.

## Recovery, claim and successor boundary

One bounded mechanical correction may repair schema, validator, scenario,
evidence reduction or test without changing semantics. Any proposal to make
wall time authoritative, allow two writers, accept an unacknowledged result,
permit caller-supplied derived fields, weaken a preset/tool/source binding,
adopt the clock live, retire a current control, start the Harness, call a
provider or confer product/Git authority is conceptual and stops this tranche.

Passing proves only a provider-free architecture for shared causal bureaucratic
time and measurable future shadow rehearsal. It authorizes no live adoption,
current-control retirement, occupied DeepSeek/provider call, HMR retry, ordinary
practice, product/configuration/API/database/client change, product/patient/
clinical data, production runtime, deployment, release, Pages or protected-ref
movement. Preserve `docs/branding/` and all unrelated untracked files; stage
explicit paths only.

If accepted, the narrow successor is a provider-free shadow gear rehearsal
against frozen representative workflow fixtures. It may implement only the new
clock request/lease/result validator and compare the four efficacy readings; it
may not replace live controls or start the native Harness.
