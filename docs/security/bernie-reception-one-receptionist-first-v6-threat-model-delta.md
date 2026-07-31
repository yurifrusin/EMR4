# Reception One Receptionist-first v6 Threat-model Delta

## New surfaces

v6 adds a schema-admitted natural receptionist response, a bounded decision
note, evidence-utterance indices and non-zero internal model thinking.

## Threats and controls

- **Prose becomes command authority.** The natural response is audit-only in
  this study, is never parsed into the form and is never product-delivered.
- **Natural and typed outputs disagree.** A deterministic agreement gate checks
  the closed goal vocabulary and rejects contradictions before release.
- **The model claims an action occurred.** Command-shaped completion language
  is rejected; every admitted action remains a proposal for human review.
- **The decision note becomes chain-of-thought.** It is one bounded sentence
  with a closed goal prefix and no multi-step rationale. Hidden thoughts are
  neither requested nor retained.
- **Thinking increases unbounded cost or latency.** The budget is fixed at
  1024, output is capped, usage includes `thoughtsTokenCount`, and the 48-call /
  USD 1 ceilings remain decisive.
- **The development cohort is misrepresented as a holdout.** Evidence and
  closeout label the rerun as paired development only; a new untouched cohort
  is required for independent evaluation.
- **The notebook leaks provider or credential material.** It records only the
  authored-synthetic utterance and locally schema-admitted output fields plus
  bounded classifications and usage integers. Raw prompts, packets, errors,
  credentials and API-key information are excluded.
- **Prompt teaching overfits individual answers.** The desk guide states
  general language and form rules derived from error classes and contains no
  case identifiers or complete demonstration forms.

All inherited keyless ADC, Sydney endpoint, isolation, one-use ledger,
proofreader, no-fallback, no-tool, no-product and cleanup controls remain
unchanged.
