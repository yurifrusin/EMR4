# Ariadne current-node closeout timestamp guard repair plan

Date: 2026-08-23

Timestamp: 2026-08-23T00:23:23.4768539+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation: `ariadne-current-node-closeout-timestamp-guard-repair`

Task baseline: `d12813744bbb815a80bb905e51a0244533a0c031`

Target result: `ariadne_current_node_closeout_timestamp_guard_repair_pass`

Reasoning level: High. This is a bounded mechanical enforcement of an already
accepted documentation invariant. It changes no acceptance meaning, product
semantics, authority allocation or protected boundary.

## Objective

Replace one recurring closeout memory obligation with a deterministic reading:

1. restore the exact accepted closeout time
   `2026-08-22T23:41:40.1369077+10:00 (Australia/Brisbane)` to exactly the
   three observability-manifest predecessor summaries that omitted it; and
2. add one reusable guard in `tests/test_current_baton_consistency.py` that
   derives the current node from the Continuity graph and validates all
   Markdown files referenced under `plans`, `closeouts` and `acceptances`.

The current node's `closeouts` category includes the Yuri lay/technical
summary, so no separate mailbox-specific rule or form is required.

## Exact owned outputs

The candidate may change only:

- this plan and its threat-model delta;
- the three predecessor summaries named below;
- `tests/test_current_baton_consistency.py`;
- the required five-source runtime states and receipts; and
- bounded efficacy, closeout, Sol acceptance, Yuri summary and clockwork
  evidence after acceptance.

The exact predecessor paths are:

1. `docs/raisa-provider-free-default-off-canonical-check-in-non-phi-observability-manifest-convergence-rehearsal-closeout.md`;
2. `orchestration/agent_inbox/codex/raisa-canonical-check-in-non-phi-observability-manifest-convergence-sol-acceptance.md`; and
3. `orchestration/human_inbox/yuri/2026-08-22--canonical-check-in-non-phi-observability-manifest-convergence.md`.

Their result, reviewed source, evidence, semantics and chronology remain
unchanged. Only the already-recorded graph timestamp is restored after the
existing `Date:` line.

## Frozen deterministic invariant

For every unique `.md` path named by the current graph node under `plans`,
`closeouts` or `acceptances`:

- the path must resolve inside the repository and exist as a file;
- exactly one `Date: YYYY-MM-DD` line must appear in the first twelve lines;
- exactly one `Timestamp:` line must appear in the first twelve lines;
- the timestamp must be parseable ISO 8601 with an explicit numeric offset;
- it must end with the literal zone label `(Australia/Brisbane)`;
- its offset must equal `+10:00`; and
- its calendar date must equal the `Date:` value.

The same validator must remain applied to the three repaired predecessor paths
after they cease to be the current graph node. Mutation checks must prove
absence, zone-label drift, offset drift, invalid ISO text and date mismatch all
fail closed.

## Acceptance

Pass requires:

1. the fresh five-source receipt and all three lane dispositions pass;
2. only the three exact timestamp lines change in predecessor evidence;
3. the graph-derived validator covers current plans, threat delta, closeout,
   Yuri summary and Sol acceptance without hard-coding the current operation;
4. the three repaired paths remain explicitly protected;
5. all five malformed-header mutations fail closed;
6. focused Baton, active-latch, Compass and clockwork tests pass;
7. the integrated deterministic closeout suite passes with Ruff, compilation
   and `git diff --check`;
8. the clockwork publishes one clean-closeout generation with zero bespoke
   updater; and
9. protected refs remain exact while `docs/branding/` and every unrelated
   untracked file remain preserved.

## Parallelism-efficacy assessment

- DeepSeek V4 Flash/high: `declined`, negative leverage. Native Harness worker
  allocation remains closed; Claude Code is historical only; briefing and
  monitoring would exceed this exact mechanical patch.
- Gemini 3.7 Flash/high: `declined`, neutral leverage. Strict parsing, graph
  traversal and mutation tests fully decide the invariant.
- Native subagents: `declined`, negative leverage. Developer policy prohibits
  proactive delegation and one writer must retain graph/test custody.
- GPT Sol owns implementation, deterministic review, acceptance, Git and
  closeout.

Reassess after focused mutation validation, if graph evidence categories prove
ambiguous, and at closeout.

## Recovery and stop rules

- A parsing or assertion defect may receive one bounded mechanical repair.
- Evidence-category ambiguity stops implementation before weakening coverage.
- No historical semantic rewrite, new form/ledger or manual receipt field is a
  valid repair.
- Any product, provider, data, runtime, deployment, Pages or protected-ref
  change stops acceptance.

## Claim and protected boundary

Passing proves only that one exact predecessor omission is repaired and future
current-node closeout metadata is mechanically checked. It does not prove that
all historical documents have complete metadata, nor does it alter their
substantive acceptance.

No application, configuration, route, OpenAPI, GraphQL, client, feature flag,
allowlist, ordinary-practice admission, generic-status `Arrived`, action
grammar, waiting-area, product/patient/appointment/clinical/historical/
protected data, provider, database/Docker, production runtime, deployment,
release, Pages or protected ref is authorised. Preserve `docs/branding/` and
every unrelated untracked file. Use explicit-path staging only.
