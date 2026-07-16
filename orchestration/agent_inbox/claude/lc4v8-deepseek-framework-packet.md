# LC4V8 bounded content-blind framework candidate

You are DeepSeek V4 Flash/high through Claude Code `--bare`. GPT Sol is
conductor, threshold/corpus/acceptance/recovery owner, and protected integrator.
Implement only the empty framework and tests. DeepSeek Pro is forbidden.

## Receipt and owned files

- Worktree: `C:\Users\sarashera\EMR4-worktrees\claude`
- Branch: `claude/current`
- Exact source head: `deece41c09c1a23eaaa6e913da14697da5442870`
- Commit: `Implement LC4V8 content-blind framework`
- Decision: `CANDIDATE: ready` or `CANDIDATE: blocked`
- Owned files only:
  - `app/services/bernie/lc4v8_content_blind_framework.py`
  - `tests/test_bernie_lc4v8_content_blind_framework.py`
  - `orchestration/agent_inbox/claude/lc4v8-deepseek-framework-candidate.md`

Read `AGENTS.md`, the V8 Sol contract, V8 one-shot acceptance rule, and generic
`certification_decision_taxonomy.py` completely. Generate the five-source
Ariadne receipt and verify clean exact head before editing.

## Sealed boundary

Holdouts v1-v7 are sealed. Do not open, enumerate, list, search, import, run,
regenerate, hash-check, infer labels from, or inspect any prior protected
fixture, support/authoring module, manifest, seal, receipt, test, filename, or
per-case evidence. Do not use broad discovery. Do not create any V8 fixture,
real utterance, Gold expected label, authoring surface, manifest, seal,
threshold, or report. Tests use generated opaque placeholders only.

## Required framework

Create a standalone, product-runtime-isolated module that provides:

1. exact fail-closed validators for fixture, manifest, seal, threshold, and
   aggregate report objects with unknown-field rejection and strict primitive
   types (booleans are never integer counts);
2. fixed-shape validation for 24 groups, 288 scenarios, six actions at four
   groups each, six language forms at two scenarios per group/48 total, 12
   scenarios and 3 multi-turn per group, 72 multi-turn/216 one-turn, 288
   unique coverage cells, and two repeats/576 samples;
3. deterministic compact sorted UTF-8 SHA-256 helpers;
4. immutable source verification using injected Git/blob observations:
   source commit present and ancestor, exact fixture/framework blob hashes,
   current bytes matching, and manifest hash bound by the seal. Never trust a
   caller's single `valid=True`; validate every named observation field;
5. exclusive attempt consumption: validate unconsumed seal, atomically create
   the marker before evaluation, and ensure every subsequent success,
   exception, evidence-invalid, or product-fail path is consumed. A second
   attempt must fail before evaluator invocation;
6. an evaluator boundary accepting a callback and scenario object but passing
   no expected contract to that callback; two repeat observations are compared
   and scored only after callback return;
7. aggregation over the thirteen named dimensions, group/language slices,
   interpretation/policy/integration failures, and aggregate-only output with
   no scenario IDs, utterances, expected values, cases, or oracle content;
8. product-gate counter construction matching the frozen rule; and
9. final decision only by importing and calling `classify_certification`.

The framework may define exact schema constants and dataclasses but no semantic
content. Actual filesystem/Git orchestration can be represented by a strict
`SourceBindingObservation` input so tests remain temporary and content-blind.
Marker creation must use exclusive file creation (`x`/`O_EXCL` equivalent).

## Required tests

Generate opaque 24×12 in-memory fixtures (`utterance-placeholder-N` is enough)
and cover every valid count plus one-at-a-time failures for all counts,
duplicates, unknown fields, invalid types, source/manifest/seal/hash drift,
non-ancestor source, consumed seal, existing marker, evaluator exception,
repeat variance, missing dimensions, case artifact/oracle leakage, and report
unknown fields. Prove:

- evaluator never receives `expected` or scenario ID;
- marker remains consumed for pass, fail, invalid, and exception;
- nonzero policy/integration product failures yield `certification_fail`, not
  invalid;
- evidence defects yield invalid before product gates;
- all gates yield pass;
- report contains only frozen aggregate keys;
- complete report hash binds populated group/language failures;
- source contains no real receptionist names/prompts or prior-version imports;
  and
- the module is not imported by runtime app modules.

Run only the new focused test and taxonomy test serially with the integration
venv, plus `git diff --check`. Do not run or discover protected tests. Record
exact tests, hashes, APIs, changed files, commit, and any unresolved risk in
the closeout. Commit only the three owned files; do not push.
