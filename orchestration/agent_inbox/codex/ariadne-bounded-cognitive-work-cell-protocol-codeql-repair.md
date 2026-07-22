# Ariadne Bounded Cognitive Work Cell - CodeQL Repair Record

Date: 2026-07-23

Owner: GPT Sol Extra High

Decision: `contained_repair_approved_by_yuri`

Result: `repaired_and_reverified`

## Finding

The first draft-PR security run passed both CodeQL language-analysis jobs but
the GitHub Advanced Security aggregate gate reported two new alerts:

- alert 497, high severity: document-derived Markdown trace content reached a
  terminal output sink; and
- alert 498, note severity: a local `repair_rules` reset was assigned but never
  read.

No live, product, patient or provider data was involved. The canonical input is
authored-synthetic, but the CLI accepts a caller-selected repository document,
so minimising public diagnostic output is the safer contract.

## Approved repair

- Remove the unused assignment.
- Preserve validation and the internal deterministic result, but make the
  public Markdown trace emit only fixed verdict labels and aggregate
  edge/repair counts.
- Never echo source-document identifiers, payload values or rejection details.
- Add a focused negative assertion showing valid caller-selected protocol,
  workflow and title labels do not appear in trace output.

## Verification

- focused protocol population: 20 passed;
- combined acceptance population: 126 passed;
- Ruff and Python compilation: passed;
- exact manifest/evidence comparisons: unchanged and passed;
- GitHub CodeQL Python and JavaScript/TypeScript analyses: passed; and
- GitHub Advanced Security aggregate CodeQL gate: passed.

The repair changes no schema, verdict, edge, manifest, authority or runtime
meaning. Every database, event-feed, product, model, provider, container,
mailbox and command boundary remains closed.
