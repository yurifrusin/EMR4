# DeepSeek native Harness pragmatic real-work adoption review and plan

Date: 2026-08-23

Timestamp: 2026-08-23T12:28:26.9746224+10:00 (Australia/Brisbane)

Status: `frozen_task_driven_adoption_plan`

Operation:
`deepseek-native-harness-pragmatic-real-work-adoption-review-and-plan`

Planning source HEAD:
`03950c102584b92677b791e615248de090f13b61`

Accepted evaluator product source:
`89640f1bb6ad992f68d5c20fd578b4062eeb193d`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. Yuri explicitly asked to lower the perfection target,
review the whole retained native-Harness investigation in light of its first
pragmatic real-work attempt, and bring the Harness into useful EMR4 work with
the minimum further stand-alone testing.

## Decision

Use the native DeepSeek Harness in the next suitable real EMR4 development
tranche as a **monitored implementation contributor**. Do not run another
generic qualification, boot-proof, synthetic coding or failure-coordinate
tranche first.

The earlier rule that a real task must fit an already accepted runner without
any runner change is retired. One small, reusable and task-coupled runner
adaptation is now allowed inside the real development tranche. It must narrow
the Harness to the accepted work order; it cannot broaden the broker, the tool
set, the repository scope or the worker's authority.

The stock rc.7 headless runner remains the native entry point. It must hand off
through the already proved HMR path to a parameterized descendant of the
accepted custom runner. Direct stock-runner provider requests are not selected
for brokered EMR4 work because the first pragmatic assignment proved that the
stock runner advertises seven tools while the broker admits exactly three.

This is a transport decision, not a reliability boast:

- the native Harness is already the better-evidenced DeepSeek transport for
  attribution and orchestrator control;
- useful EMR4 completion by DeepSeek inside it remains unproved; and
- Claude Code is not a validated reliability control and is not a silent
  fallback. Any later use of it requires a fresh explicit allocation.

## Review method and corpus

The accepted 2026-08-23 adoption review had already reconciled the first 68
accepted Continuity nodes whose IDs name `native-harness`. This review freshly
validated that accepted synthesis, then read the complete plan, evidence,
efficacy, closeout and Sol acceptance for it; the complete plan, terminal
review, efficacy, closeout and Sol acceptance for the first pragmatic real
development assignment; and the native-Harness dispositions in the two later
typed-input and evaluator product tranches.

The current retained inventory contains:

- 70 accepted Continuity nodes naming `native-harness`, from
  2026-08-18T04:37:03Z through 2026-08-23T10:30:23.9779889+10:00;
- 180 top-level native-Harness documents, including 73 plans and 73 closeouts;
- 66 native-Harness Continuity directories;
- 76 native-Harness scripts; and
- 96 native-Harness tests.

These counts measure scrutiny and retained evidence, not failure rates. The
canonical synthesis of the first 68 nodes is not duplicated here. This review
adds the two evidence-bearing developments that followed it: formal monitored
secondary-worker admission and the first pragmatic real-work outcome.

## What has been learned

### The Harness is versatile but presets are not a security boundary

The pinned Harness supports profiles, presets, HMR-loaded custom runners,
services, hooks, native tools, persistent sessions, reasoning-effort settings,
approval posture and transport substitution. Those features are useful for
giving different DeepSeek workers stable roles and work shapes.

The first real-work run proved the important limitation: a preset can set role,
sandbox and approval defaults, but does not by itself remove globally mounted
tool schemas. The stock runner declared `edit`, `exit_plan_mode`, `glob`,
`grep`, `read`, `read_image` and `write`. The broker correctly rejected that
request before provider I/O because the admitted worker contract was exactly
`edit`, `glob` and `read`.

The response is not to admit seven tools or weaken the broker. It is to use the
accepted custom-runner/HMR machinery to project the effective three-tool view.

### Traceability is a real gain

Across the retained sequence, native runs localized failure to package,
profile, startup, HMR, preset composition, runner factory, provider request,
tool lifecycle, candidate and cleanup coordinates. The final controlled
synthetic sequence reached DeepSeek and recorded one request, one edit result,
zero changed paths and a typed error coordinate. The pragmatic real task then
recorded a deterministic pre-provider broker rejection in 7.4 seconds with no
candidate and complete cleanup.

That evidence is materially better than an unexplained timeout, incomplete
output or unverifiable claim. It lets the orchestrator distinguish Harness,
transport, model, repository and acceptance failures. The first real task was
not a DeepSeek failure because DeepSeek never received its packet.

### Useful completion is still the missing reading

No controlled native-Harness EMR4 run has yet produced an accepted DeepSeek
candidate. This does not establish poor model quality: the occupied runs were
mostly stopped before provider I/O, and the one-request useful-worker tests
were too constrained to exercise ordinary multi-turn coding.

The only honest way to learn useful performance now is to assign bounded real
work and judge the resulting diff. More generic Harness tests would improve
our knowledge of the Harness while continuing not to answer whether it helps
build EMR4.

### The earlier pragmatic rule was too brittle

After the first pragmatic failure, the next two product tranches declined the
Harness because the surviving accepted custom runner hard-coded one synthetic
prompt, one pre-existing target and one edit, while the stock runner could not
satisfy the three-tool broker. That rule avoided another investigation spiral,
but made practical adoption depend on accidental task/runner identity.

The correction is a bounded adapter allowance, not a return to exhaustive
interoperability work.

## Minimum viable DeepSeek worker envelope

Every selected native-Harness work package retains only these gears:

1. pinned `@deepseek-ai/dsh@0.1.0-rc.7`, profile and accepted derivation-source
   identities;
2. one fresh sparse worktree and fresh session bound to the operation, a full
   40-character source object, explicit read packet, owned paths and forbidden
   surfaces;
3. a stock-headless HMR handoff to the parameterized custom runner;
4. exactly `read`, `glob` and `edit`, one tool call at a time, approval `never`,
   no model-facing shell, test, Git, web, subagent or workflow tool;
5. broker-held provider credential, no direct worker credential or egress,
   zero automatic provider retry, zero fallback and zero auxiliary model;
6. one natural multi-turn session bounded to 900 seconds;
7. structural request/tool/result/usage, changed-path and cleanup readings;
8. Sol-owned diff review, tests, integration and acceptance; and
9. explicit transport provenance if Sol or another allocated worker recovers
   an incomplete task.

Yuri's prepaid DeepSeek balance is the monetary ceiling. Usage is recorded
when available, but no Harness-native monetary-budget feature is required.

## The one-adapter allowance

The next real development tranche may add or revise at most one small runner or
coordinator module plus its deterministic focused test so the already accepted
custom-runner path becomes task-parameterized. The allowance may only:

- take the prompt/read packet, owned paths and terminal-summary instruction
  from the frozen work order;
- replace the old single synthetic target with an explicit finite owned-path
  set;
- allow ordinary multi-turn read/edit/error/reread/edit work inside the single
  session; and
- emit the minimal boundary terminal described below.

It may not add a tool, relax the broker, parse model prose for authority,
change the provider, add retry/fallback, expose credentials, mount product data
or build a second orchestration system. If the required correction exceeds
that allowance, the native lane ends for that task and Sol completes the EMR4
work. No diagnostic successor is opened merely to explain it more finely.

The adapter is part of the first real task's implementation cost. It is not a
predecessor certification tranche. Once accepted, later tasks reuse it by
changing only the typed work order.

## Clockwork coupling at tranche speed

The clockwork and native Harness need to agree at meaningful boundaries, not
share every internal tick. The broker does not write directly to canonical
Continuity and a model turn does not advance bureaucratic time.

The clockwork takes three readings:

1. `prepared` — exact source, worktree, work order, runner/profile identities,
   effective tools and zero provider calls before dispatch;
2. `terminal` — whether the provider was reached, whether a candidate exists,
   changed paths, coarse failure stage and cleanup; and
3. `accepted_or_recovered` — Sol's tested candidate decision and exact
   provenance.

The typed boundary vocabulary is deliberately small:

- provider: `not_reached`, `reached_completed`, `reached_failed`;
- candidate: `none`, `partial`, `complete`;
- failure stage: `pre_provider_envelope`, `provider_transport`,
  `agent_execution`, `candidate_validation`, `cleanup`, or `none`; and
- disposition: `accepted`, `recovered`, `rejected`, or `not_applicable`.

Detailed Harness diagnostics may remain in sanitized local evidence, but they
cannot invent new clockwork states. This preserves form-like determinism
without forcing the clockwork schema to model every internal Harness event.

## Testing deliberately not required

The following are retired as prerequisites to real work:

- another generic stock-headless boot proof;
- another provider-free preset, mount, HMR, runner-factory or tool-coordinate
  tranche;
- another synthetic coding benchmark;
- a one-provider-request ceiling;
- a distinct closeout for each runner subcoordinate;
- a clockwork tick per model request or tool call;
- an equal-depth Claude Code qualification; and
- perfect native-Harness/clockwork interoperability.

The next real tranche gets only one zero-provider pre-dispatch readback of the
exact HMR handoff and effective `edit`/`glob`/`read` view, then the occupied
work session. That readback is part of the task preflight, not a new rehearsal.

## Task selection and responsibility split

Select native Harness work when all are true:

- the contribution is useful source or tests, not a Harness demonstration;
- the contract is already frozen and can be expressed through an explicit
  packet;
- two to four owned files are sufficient;
- ordinary work can be done with read/glob/edit while Sol runs commands;
- no secret, product/patient/clinical data, live provider other than the
  isolated DeepSeek broker, database mutation, deployment or protected ref is
  needed; and
- Sol can safely review, repair or discard the diff.

Prefer pure functions, serializers/normalizers, typed adapters, conformance
tests, bounded bug fixes and mechanical source/test implementations. Decline
the native lane for live database or infrastructure work, broad refactors,
visual browser work, ambiguous product design, protected integration, or tasks
whose orchestration overhead is larger than the likely contribution.

DeepSeek owns only the bounded candidate. Sol owns architecture, authority,
work-order freeze, runner adaptation, verification, integration and acceptance.
Gemini remains risk-triggered, not ceremonial. Native subagents remain
declined under developer policy.

## First use under this plan

The first opportunity is the next dependency-satisfied canonical check-in node:

`default_off_admission_input_seam`

Its separately frozen tranche will make the existing admission evaluator
consume the accepted typed `EnvironmentEvidenceGateReading` as one additional
mandatory input while remaining default-off. It cannot create or activate an
admission record. The feature flag, authored-synthetic practice allowlist,
ordinary admission record, kill switch, authorization and confirmation remain
independently mandatory.

Within that tranche:

- Sol freezes the exact API meaning and chooses a separable two-to-four-path
  source/test package;
- Sol applies the one-adapter allowance and performs the zero-provider
  effective-tool preflight;
- one fresh native DeepSeek session implements the bounded package;
- Sol runs the normal focused and surrounding EMR4 verification and owns any
  integration repair; and
- the closeout records useful candidate, task completion, trace boundary,
  correction cost and scope integrity.

This is a selected real-work use, not a promise that DeepSeek owns the
authority-sensitive integration decision. If the seam plan reveals no safely
separable worker package, Sol must record that factual constraint and select
the next bounded real source/test package without reopening generic Harness
testing.

## API Spine classification

This review changes workflow allocation only. It adds no GraphQL read model,
REST/OpenAPI command, async event, Access AI boundary, product route or
first-party client behavior.

The next `default_off_admission_input_seam` tranche is an internal typed
admission-prerequisite change. Its plan must preserve the existing command
envelope, authentication, authorization, confirmation, idempotency and audit
meaning. Any public request/response or API Spine manifest change is a separate
risk trigger owned by Sol and cannot be inferred from this Harness plan.

## Failure and retry rule

Natural multi-turn self-correction inside one session is ordinary worker
behavior and is allowed.

After a terminal:

1. one fresh run is allowed only when DeepSeek did not receive the packet and
   one directly attributable mechanical envelope defect can be corrected
   inside the one-adapter allowance;
2. after DeepSeek receives the packet, there is no automatic rerun of the same
   assignment; Sol reviews any candidate and recovers or rejects it; and
3. no silent Claude Code fallback, generic diagnostic successor or expanding
   runner/broker project follows from a failed task.

## Rolling efficacy decision

Every real assignment records five comparable readings for whichever transport
is explicitly used:

- `useful_candidate` — accepted, partial or none;
- `task_completion` — complete or incomplete against the frozen packet;
- `trace_boundary_complete` — prepared, terminal and cleanup readings exist;
- `correction_cost` — Sol changes, occupied attempts and elapsed time; and
- `scope_integrity` — source, paths, data and authority stayed bounded.

There is no fixed three-run certification gate. After each useful assignment,
Sol may keep, broaden, narrow or retire native-Harness use based on accepted
work per unit of correction. Default-worker promotion is a separate future
allocation decision; it is not required for continued secondary use.

## Parallelism assessment

- DeepSeek native Harness: `declined` for this self-review, then `selected` as
  a bounded contributor in the next suitable real development tranche.
- Gemini: `declined`, neutral leverage for this retained-evidence process plan;
  it remains available only on an ordinary risk trigger in the real task.
- Native subagents: `declined`, negative leverage under developer policy.
- GPT Sol owns this review, the runner-adaptation boundary, work-order freeze,
  verification, acceptance, clockwork and Git.

## Protected boundary

This review and plan run no Harness, provider, database, Docker, application,
route, API, client or configuration surface. They use no secret, environment,
product, patient, appointment, clinical, historical or protected data. They
authorize no ordinary-practice enablement, feature-flag or allowlist change,
command mounting, generic-status `Arrived`, action grammar, waiting-area
movement, production runtime, deployment, release, Pages or protected-ref
movement.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
