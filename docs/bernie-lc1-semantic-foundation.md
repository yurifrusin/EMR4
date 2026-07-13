# Bernie LC1 Semantic Foundation

Status: implemented and deterministically verified on 2026-07-14.

LC1 fixes the known deterministic interpretation regression without opening a
provider, confirmation, or write-authority gate. Before the change, the fake
interpreter service path returned `earliest_time=null` and `latest_time=null`
for `tomorrow at 3pm`. The same non-intercepted path now returns equal `15:00`
bounds with `temporal_relation=exact`.

## Implemented boundary

- The temporal parser distinguishes `exact`, `not_before`, `not_after`,
  `interval`, `approximate`, and `unspecified` relations. It covers `3pm`,
  `3 pm`, `3.00pm`, and `15:00` forms.
- Explicit non-exact relations cannot grant exact-duplicate authority. Legacy
  commands without a relation retain their pre-LC1 classifier behaviour.
- An exact point is compared as a point for duplicate classification and is
  widened to the existing five-minute half-open unit only for slot search.
- The public deterministic route regression interprets the real wording,
  reaches `existing_booking_found`, offers no confirmation, and produces no
  second appointment or audit write.
- `ReceptionScenarioSpec` records the deterministic clinic clock, original
  dialogue, action/entity/temporal semantics, normalized values, source spans,
  initial synthetic state, expected tool/outcome/appointment/audit evidence,
  forbidden outcomes, provenance, and independent adjudication state.
- Language normalization preserves the original utterance and derives only a
  Unicode-NFKC, whitespace-collapsed, case-folded, punctuation-normalized
  matching view. Time, number, and authority-bearing operator spans point back
  to the original text; no stop-word removal, stemming, or lemmatization is
  used for authority.

## First coverage gap report

The machine-readable report is
`docs/bernie-lc1-coverage-gap-report.json`. Three independently adjudicated
Gold adaptations cover 3 of 152,064 cross-product cells. The report records
152,061 empty cells, includes a bounded explicit cell sample, and carries a
complete per-dimension missing-value summary. Major visible gaps include all
non-create actions, non-exact entity states, open and approximate temporal
relations, most dialogue forms, and every non-plain language form.

Empty cells are evidence for later corpus work, not a failing release gate.
The reporter can emit the complete cross-product list with
`--all-empty-cells` when an offline consumer needs it.

## Preserved gates

- T3.1-T3.4 shadow-evaluation scaffolding remains unchanged and tested.
- T3.5 DeepSeek/Gemini provider adapters remain deferred.
- Live provider calls, provider prompts, raw historical-trove access,
  memory/RAG/GraphRAG, confirmation changes, and diary write-authority changes
  remain blocked or out of scope.

## API-spine classification

LC1 adds the optional `temporal_relation` field to the existing REST
`SlotSearchCommandIn` and normalized `SlotSearchProposalIn` shapes. This is an
additive interpretation/read-model constraint: it changes no route, auth,
practice scope, idempotency key, audit payload, confirmation evidence, or
mutation contract. Invalid relation values fail normalization closed. There is
no GraphQL surface, new OpenAPI command route, async integration, or agent
context-frame surface added by this tranche.
