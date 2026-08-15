# Ariadne Prime-derived harness worker review

Date: 2026-08-15

Timestamp: 2026-08-15T18:34:00+10:00 (Australia/Brisbane)

Plan source: `961a833b65e57682e10088300f4b7909a5a5aee8`

DeepSeek candidate: `7ff8ea25b03b691bad0feef179e9cb05f01c72f4`

Decision: `revision_required`

## Admitted evidence

- The candidate is a clean exact child of the plan source.
- Exactly the nine worker-owned paths changed.
- Its focused suite passes 173 tests; Ruff, py_compile and whitespace checks pass.
- No product, database, provider-tool, command-runner, automatic-apply or
  protected-ref surface was added.

## Required bounded correction

1. `assess_command_submission` checks differing requests only after the
   `completed` state. A reused command id with a different request must return
   `conflict` in every recorded state; live or terminal state cannot hide the
   identity collision.
2. Journal validation accepts an input event array whose generation/sequence
   coordinates have been reordered. Append-only evidence must be in exact
   coordinate order, not merely sortable into validity.
3. `assess_gate` selects the latest exact-fingerprint attempt when earlier
   exact attempts disagree. Contradictory deterministic/uncertain outcomes are
   evidence conflict and must fail closed; they cannot use latest-wins.
4. Promotion does not carry or compare an exact source HEAD/source-evidence
   binding, and a rejected `validation_result=fail` is serialized as `pass`.
   The decision record must bind the exact proposal and preserve the actual
   validation result without permitting promotion on failure.
5. `assess_rollback` accepts a caller-supplied decision id, generation and base
   digest without validating the promoted decision, current state or decision
   history. Rollback must derive the next generation and recorded base from one
   exact latest unrolled-back promotion and reject intervening, repeated,
   unknown or non-promoted targets.

These are contract-admission defects inside the nine-file boundary. They do
not change the frozen product or harness authority and are eligible for the
plan's one bounded Sol correction. The DeepSeek commit remains untrusted
provenance until a corrected descendant passes deterministic admission and a
fresh Gemini 3.7 Flash/high veto.
