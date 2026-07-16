# LC4V9 Sol Framework Acceptance

Date: 2026-07-16

Decision: `framework_accepted_content_authoring_authorized`

The content-blind framework and one-shot rule were frozen before any actual V9
content. DeepSeek Flash's single candidate was preserved and rejected; Sol
recovered it under the lease. Gemini's first pass on `4c9283b0` was correctly
superseded for authorship after Sol found an ordinary-interface mismatch before
content. Sol amended the framework at
`b5aaa89cfc8ed4bf697e4b68e41cfaa301c59e38`.

A second fresh Gemini 3.5 Flash/medium Antigravity project independently
returned `DECISION: pass` on that exact amended head. It reproduced 63/63
framework-plus-taxonomy, 74/74 ordinary D1, and 2/2 selected runtime-isolation
tests. Its permitted single-file review commit was integrated at `17fa83e0`.
No external model session remains active.

At this acceptance point there is no actual V9 corpus, product evaluator,
authoring module, threshold file, manifest, seal, marker, report, or protected
case content. Holdouts v1-v8 remained sealed throughout framework work and
review.

## Frozen Sol-only protected surface

Sol may now create only these actual V9 certification surfaces:

- fixture: `tests/fixtures/bernie_lc4v9_fresh_certification.json`;
- thresholds: `tests/fixtures/bernie_lc4v9_thresholds.json`;
- evaluator: `app/services/bernie/lc4v9_certification_evaluator.py`;
- authoring tool: `scripts/author_bernie_lc4v9_certification.py`;
- one-shot runner: `scripts/run_bernie_lc4v9_certification.py`;
- source manifest: `orchestration/agent_inbox/codex/lc4v9-source-manifest.json`;
- seal: `orchestration/agent_inbox/codex/lc4v9-seal.json`;
- durable marker: `orchestration/agent_inbox/codex/lc4v9-attempt-marker.json`;
  and
- aggregate report: `orchestration/agent_inbox/codex/lc4v9-aggregate-report.json`.

Attempt ID is frozen as `lc4v9-fresh-certification-001`. The marker and report
must not exist until the sole run. Source authorship/validation commits first;
manifest and seal commit second; exclusive consumed-marker creation precedes
all protected reads in the only run.

From the first creation of any listed content surface, it is protected from all
external workers and providers. Sol alone may author, inspect, validate,
commit, manifest, seal, execute, and accept it. After the attempt is consumed,
only its aggregate report, closeout, and Sol acceptance remain available for
planning; no case-level repair, rerun, relabelling, rescoring, or reuse is
authorized.

T3.1-T3.4, T3.5/providers, historical data, runtime/product wiring, API/UI/DB,
deployment, release, and all live/write authority remain closed.

## Supersession

Before any protected content was created, Sol found one further ordinary-
interface mismatch: the accepted product policy may clarify an omitted or
unresolved practitioner with an empty `clarification_choices` array. The
framework amendment and required fresh third veto are recorded in
`lc4v9-second-post-veto-interface-amendment.md`. This acceptance is therefore
superseded for authorship until that exact amended head receives an independent
pass and a new Sol acceptance is committed. Its protected-surface allocation
and all closed boundaries remain frozen and unchanged.

## Final amended-head acceptance

The empty-choice amendment was committed and published before any protected
content existed. A third genuinely fresh Gemini 3.5 Flash/medium Antigravity
project independently returned `DECISION: pass` on exact review head
`c43b73ed3180b54c68aa1410197adbe7e49d692b`. It reproduced 64/64
framework-plus-taxonomy tests, 74/74 ordinary D1 tests, and 2/2 selected
runtime-isolation tests. Its one-file receipt commit was integrated at
`756264e4`; its session is closed.

The accepted framework therefore permits an empty clarification-choice array
only inside the otherwise exact clarification state. All mutation, authority,
projection, temporal/diary, source-binding, consumed-first, evidence-validity,
threshold, repeat, conjunction, and report-routing guards remain unchanged.

No actual V9 protected content surface existed at this acceptance point. The
frozen Sol-only file allocation and attempt ID above are now authorized for
Sol-only authorship, source commit, immutable manifest/seal creation, and the
single consumed run. No external model or provider may access those surfaces
from their first creation onward.
