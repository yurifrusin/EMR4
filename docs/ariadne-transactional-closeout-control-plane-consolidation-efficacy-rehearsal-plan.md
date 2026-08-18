# Ariadne transactional closeout control-plane consolidation efficacy rehearsal plan

Date: 2026-08-19

Timestamp: 2026-08-19T00:31:10.3800847+10:00 (Australia/Brisbane)

Status: `frozen_shadow_first`

Source HEAD: `f21072405a4d5877ec03e2cd1aefc7fa74d379e9`

Target result:
`ariadne_transactional_closeout_control_plane_consolidation_efficacy_rehearsal_pass`

Reasoning level: Extra High for the control-plane architecture, causal-time
contract and efficacy meaning frozen here. High is sufficient for the bounded
provider-free implementation, deterministic rehearsal, exact review and
closeout while this contract remains unchanged.

## Objective

Replace hand-copied closeout state with one typed reading. A closeout manifest
must select machine-observed `current_head`, describe the accepted outcome once
and produce one hash-chained causal journal. A deterministic reducer must derive
the prospective Continuity, Compass, report, latch-transition, incident
aggregate and DeepSeek WorkOrder projections from that journal before any
publication target is touched.

The DeepSeek native-Harness broker receives an opt-in WorkOrder containing the
same operation, authority digest, full source commit, lease and causal anchor.
Every broker event then advances the same monotonic, hash-chained bureaucratic
clock. Wall time remains observational metadata and never determines order.

This tranche is a provider-free shadow and efficacy rehearsal. It neither
launches the native Harness nor calls DeepSeek or Gemini during implementation.
It changes no product, practice, route, database or protected ref.

## Exact predecessor and baseline boundary

The accepted workflow foundation remains the risk-weighted reform at
`51866ce084c33fce600b792c66b180927658ed9e`. The current accepted product review
remains exact at `27101faa86b5aa3850e90bc4ded8600e5f8d7dc9`, Continuity
323 / Compass 305 and register revision 487. Local/origin `master` and
`handoff/current` remain exact at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Three non-protected historical closeouts form the representative shadow set:

1. `raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal`;
2. `ariadne-post-native-harness-successor-resolution-repair`; and
3. `raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review`.

Their bespoke Continuity updater and paired Continuity-test files are the
legacy maintained-surface baseline: six files and 1,002 physical lines
(295+56, 268+57 and 252+74). The first two write the graph before complete
graph/Compass validation; the third validates the prospective pair first but
still writes three canonical files sequentially.

The benchmark may read only those six files, the current non-protected graph,
Compass and latch, the three named accepted nodes/evidence paths, the accepted
risk-weighted workflow sources, the exact broker source/test, and the shared
Git/Continuity/Compass validators. It may not enumerate or inspect protected
holdouts or historical-diary material.

## Frozen clock and transaction contract

### One logical journal

The canonical candidate unit is a typed transaction bundle containing:

- one exact manifest digest and transaction ID;
- one automatically observed full 40-character source commit;
- one ordered event list beginning from an explicit causal anchor;
- one previous-event digest and one event digest per event;
- prospective Continuity, Compass, rendered-report, latch-transition and
  derived incident-aggregate projections;
- one optional provider-free DeepSeek WorkOrder; and
- exact content digests for every projection.

Event sequence is contiguous, unique and strictly increasing. Event digests are
computed over canonical sorted-key UTF-8 JSON without their own digest field.
The first event binds the declared prior digest; every later event binds the
immediately preceding event. A missing, duplicate, reordered, altered or
foreign event fails closed.

The manifest admits `source_anchor: current_head` only. It has no `source_head`
or abbreviated-ID field. The engine obtains HEAD through the existing fixed Git
snapshot helper, passes the resulting full object ID through the existing
strict commit resolver, and copies that resolved value into every projection.

### Transactional publication boundary

Preparation is pure with respect to publication targets. It must:

1. validate the manifest, live latch and current Git/ref snapshot;
2. reduce every prospective projection in memory;
3. validate the complete prospective Continuity/Compass pair with the existing
   validators;
4. validate the latch transition, incident aggregate, WorkOrder and journal;
5. render every output and compute its digest;
6. write and reread a private sibling staging generation; and
7. publish the complete generation with one directory rename only after every
   check passes.

This tranche publishes only to a disposable or tranche-owned shadow root.
Live `AGENTS.md`, the active latch, Continuity graph, Compass and current report
are forbidden publication targets. Fault injection before validation and after
each staging write must leave no published generation and no changed canonical
file. Existing closeout controls are not replaced or retired here.

### Derived rather than remembered fields

The reducer, not the manifest author, owns:

- full Git source commit and task/protected-ref snapshot;
- graph, Compass and event sequence numbers;
- journal, authority, payload and projection digests;
- incident population, latest identifier, peer symmetry and source cutoff;
- retry/rerun totals and efficacy arithmetic; and
- WorkOrder causal anchors and broker-event sequence.

Manifest attempts to supply any derived field fail exact-key validation. This
is the clockwork memory mechanism: the orchestrator selects the reading and the
engine supplies the measurements.

## DeepSeek broker gear contract

The broker integration is default-off. Without an
`EMR4_BROKER_WORK_ORDER_PATH`, all accepted current behavior and log shapes
remain compatible. With the variable set, the orchestrator must also provide
the independently derived canonical WorkOrder digest through
`EMR4_BROKER_WORK_ORDER_SHA256`; broker startup fails closed on a missing or
different digest or unless the WorkOrder is strict UTF-8 JSON with:

- schema/version, WorkOrder, transaction, operation and lease IDs;
- the automatically resolved full source commit;
- journal ID, next sequence and prior-event digest;
- authority and forbidden-surface digests;
- exact branch/worktree identity;
- exact allowed tools `edit`, `glob`, `read`; and
- provider-free/occupied posture and expiry-free process-lifetime scope.

The broker decorates every ready, rejection, provider-start, response, terminal
and failure event with the WorkOrder/transaction IDs, source commit, authority
digest, contiguous sequence, prior-event digest and event digest. The Python
control plane must validate a captured provider-free broker event stream as a
continuation of the journal. Wrong WorkOrder, source, authority, sequence,
digest or tool set fails before upstream provider I/O. No provider call,
credential mutation, HMR retry or occupied Harness run is authorised.

## Exact implementation allowlist

GPT Sol may create or edit only:

- this plan and its threat-model delta;
- `orchestration_harness/transactional_closeout.py`;
- `scripts/ariadne_deepseek_native_harness_broker.mjs`;
- `tests/test_ariadne_transactional_closeout.py`;
- `tests/test_ariadne_transactional_closeout_plan.py`;
- `tests/test_ariadne_deepseek_native_harness_broker.py`;
- `orchestration/continuity/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal/control-plane.schema.json`;
- one combined historical-shadow fixture JSON in that directory;
- one generated provider-free efficacy-evidence JSON and paired report there;
- exact Ariadne runtime states/receipts and the current latch;
- qualifying closed incident-register evidence;
- closeout, Sol acceptance, Yuri summary, Continuity/Compass update evidence,
  current baton and related focused tests required for closeout.

No application, product configuration, API Spine, migration, database, UI,
provider launcher or protected-ref source is editable. `docs/branding/` and all
unrelated untracked files remain untouched. Staging is explicit-path only.

## Controlled efficacy protocol

The evidence generator must be deterministic except for separately labelled
monotonic timing observations. It must:

1. prove byte/field parity for the three accepted historical node and journey
   projections and preserve their exact accepted source IDs;
2. prepare one prospective current-tranche shadow bundle from `current_head`;
3. inject at least these seven observed defect classes: abbreviated Git ID,
   stale live latch, asymmetric incident peer, stale source cutoff, stale
   standalone population literal, protected-boundary paraphrase and a failure
   immediately before each prospective publication step;
4. record prevented defects, escaped defects, commands/API phases, attempts,
   reruns, writes-before-validation, partial publications, physical files and
   lines, declarative fields, fixture count and monotonic elapsed time;
5. report shared-engine cost separately from per-tranche manifest cost; and
6. calculate every total from source/fixture data rather than accepting a
   caller-supplied result.

Physical-line surface accounting includes every added or changed executable,
schema and test line in the candidate engine and broker integration. It excludes
plans, threat reports, immutable evidence output and historical fixture values,
and makes the same exclusion for the legacy comparator. The candidate must
remain below the legacy six-file / 1,002-line baseline and use fewer than six
maintained executable/schema/test surfaces. Both raw repository growth and the
amortised per-tranche declarative cost must still be reported; neither may be
hidden by calling the shared engine free.

Wall time is measured over at least 20 alternating legacy/candidate shadow
iterations and is informational because scheduler noise must not decide
correctness. The report must nevertheless show median and range for both.

## Deterministic acceptance

Pass requires all of the following:

1. the fresh post-compaction five-source receipt and active-operation latch
   validate with explicit DeepSeek, Gemini and native-subagent dispositions;
2. all three historical shadow fixtures have exact source, node, journey,
   authority, evidence and closed-boundary parity;
3. the prospective current-tranche bundle passes existing Continuity, Compass,
   active-latch and Git-object validators before shadow publication;
4. all seven defect classes are prevented before publication, zero defect
   escapes, zero canonical write occurs before validation and every injected
   failure leaves zero partial published generation;
5. no manifest contains or accepts a hand-copied Git object ID;
6. candidate procedural retries/reruns are at least 50 percent fewer than the
   controlled legacy reference, with no coverage loss across the seven named
   defect classes and the existing graph/Compass/latch/broker invariants;
7. maintained candidate executable/schema/test surface is fewer than six files
   and fewer than 1,002 physical lines under the exact accounting rule;
8. the default-off WorkOrder mode and provider-free broker chain pass, while
   malformed WorkOrders/events fail before upstream I/O and legacy no-WorkOrder
   broker tests remain exact;
9. focused tests, applicable existing latch/Continuity/Compass/Git/broker tests,
   compile, Ruff and `git diff --check` pass; and
10. a fresh Gemini 3.7 Flash/high read-only veto passes only after deterministic
    admission, with exact candidate/worktree preflight and no silent fallback.

Failure of any threshold produces `efficacy_not_proven`. It preserves the
candidate as negative evidence, retains every existing control and returns to
the deferred product successor without claiming workflow replacement.

## Parallelism assessment

- **DeepSeek Flash:** declined for implementation. Occupied native-Harness work
  remains paused behind the separate stock-headless-to-custom-runner HMR boot
  proof. This tranche exercises only its local provider-free broker boundary;
  Claude Code is not a fallback.
- **Gemini 3.7 Flash/high:** reserved for one independent read-only final veto
  after the exact deterministic candidate and efficacy evidence pass. It owns
  no implementation, acceptance, integration or protected authority.
- **Native subagents:** declined. Architecture, baseline selection and the
  transaction aggregate are serial Sol work, and current developer policy
  prohibits proactive delegation.

Reassess the three lanes after the deterministic candidate, before verifier
acceptance and at closeout.

## Claim, recovery and next work

Passing proves only a provider-free repository-local shadow control plane: one
typed reading can produce causally ordered, fully prevalidated projections and
an opt-in DeepSeek broker event chain with less measured maintained ceremony.
It does not prove crash-atomic live canonical replacement, occupied Harness
startup, model quality, product throughput or production suitability.

One mechanical correction of a deterministic implementation defect is
permitted. A conceptual conflict in transaction meaning, efficacy accounting
or authority moves to Sol recovery without weakening a threshold. No live
control is retired in this tranche.

After closeout, continue to the deferred
`raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture`.
That tranche may consume the accepted manifest preparer, but Sol still reviews
and applies authority projections under the existing controls until a separate
measured live-adoption boundary is warranted.

No ordinary-practice enablement, feature-flag or allowlist change, generic-
status `Arrived`, grammar/client/waiting-area change, product/patient/clinical
or historical data, provider call, HMR retry, credential/IAM/network change,
production runtime, deployment, release, Pages or protected-ref movement is
authorised.
