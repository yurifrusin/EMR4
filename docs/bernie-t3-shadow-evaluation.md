# Bernie T3 Nondeterministic Shadow Evaluation

Status: T3.1 contract/scorer, T3.2 source-safe corpus projection, T3.3
default-disabled repeat runner, T3.4 live-replay gate, the T3R1 synthetic
Silver v2 shadow refresh, the T3R2/T3R3 approval and no-call preflight, and the
bounded T3R4 pragmatic synthetic-only comparison are complete. The dedicated
T3R4 evaluation exception is consumed; no product live-provider replay is
enabled and T3.5 remains deferred. See
`docs/bernie-language-coverage-implementation-plan.md`,
`docs/bernie-t3r1-synthetic-shadow-refresh.md`, and
`docs/bernie-t3r4-pragmatic-live-comparison-closeout.md`.

## Purpose

T3 compares candidate models as interpreters and tool selectors against the
authored synthetic T1/T2 semantic corpus. It does not grant model write
authority and does not treat model output as diary truth.

## T3.1 Contract

`app/services/ai/evals/bernie_shadow_eval.py` defines:

- an immutable model-version ledger covering provider, exact model revision,
  prompt version, tool schema version, and sampling temperature;
- synthetic evaluation cases with normalized authored expectations and an
  explicit per-case tool allowlist;
- a fail-closed execution envelope that rejects writes, non-synthetic state,
  non-deterministic tools, and invalid repeat indexes;
- normalized provider responses that retain a response hash rather than
  requiring raw output in the common ledger;
- deterministic exact scoring of intent, entities, date/time, clarification,
  and tool selection; and
- separate safety findings for write-authority claims, claimed completed
  actions, and tools outside the case allowlist.

Latency, token counts, and estimated provider cost are recorded in a separate
operational record. They cannot raise or lower correctness or safety scores.

## Closed Boundaries

T3.1 imports no provider SDK, route, database, persistence model, or diary
mutation service. Live calls, provider adapters, corpus export, promotion
thresholds, and runtime wiring remain out of scope. Later replay must use
synthetic state and deterministic read-only tools, and every provider adapter
must normalize into this contract before scoring.

## T3.2 Corpus Projection

`app/services/ai/evals/bernie_shadow_corpus.py` loads only the allowlisted JSON
shape in `tests/fixtures/bernie_shadow_eval/t1_t2_authored_cases.json`. Each case
cites a known T1/T2 scenario ID but does not expose that source fixture's diary
setup or synthetic-but-PHI-shaped names to a model. The projected instructions
use `synthetic-` aliases and the expectations are explicitly marked `manual`.

The loader rejects unknown fields, generated authorship, unknown source IDs,
non-synthetic entity aliases, mutation-state fields, unsupported tools,
duplicate cases, and expected tools absent from the case allowlist. The first
bounded projection contains four cases covering exact duplicate, overlap,
roster-unavailable, and expired same-day-window semantics.

## T3.3 Default-Disabled Runner

`app/services/ai/evals/bernie_shadow_runner.py` defines the narrow injected
adapter protocol used by future provider-specific modules. Disabled mode returns
without calling the adapter. Enabled test mode runs cases serially, constructs a
write-disabled envelope for each repeat, and requires adapters to return a
normalized response plus separate operational metrics.

The aggregate reports exact correctness totals, safe/perfect samples, semantic
variance by case, latency, token counts, and estimated cost. Operational totals
remain separate fields and cannot affect semantic scores.

## T3.4 Live-Replay Gate

`docs/bernie-t3-live-replay-gate.json` and
`scripts/bernie_shadow_live_gate_check.py` define the narrow external-call
boundary. While blocked, provider adapter code and static/fake-adapter review may
continue, but external prompts, provider-executed tools, raw-response
persistence, patient/practice inputs, mutations, runtime wiring, and promotion
claims are prohibited. This is separate from the older interpretation-runtime
gate because evaluation adapters do not receive product authority.

## Methodology Course Correction

The four-case T3.2 projection proves the source-safety and scoring contracts; it
does not establish adequate receptionist-language coverage. T2's deterministic
matrix remains the diary outcome oracle, but its generated classifier and route
combinations mostly begin after natural-language interpretation.

Before provider adapters are useful, EMR4 needs a canonical language-to-semantic
scenario contract, a measurable coverage lattice, lossless normalization,
independently adjudicated Gold/Silver/Bronze corpus tiers, metamorphic and
adversarial generation, and an evaluator that composes interpretation with T2
diary replay. The approved direction is recorded in
`docs/bernie-language-coverage-implementation-plan.md`.

## T3R1 Synthetic Silver v2 Refresh

After LC4V10 certification and completion of the balanced synthetic Silver v2
course, Yuri authorized the provider-free T3R1 refresh. T3 now projects all 192
admitted v2 dialogues without duplicating the fixture. Five non-executing
`propose_*` labels, schedule explanation, clarification, and no-action replace
product mutation tool names at the model boundary. Whole-action withdrawal is
an optional sixth scoring dimension, and response fingerprints now include it.

The exact offline plumbing run is 384/384 perfect and safe with zero variance.
It uses an expected-decision echo and explicitly establishes no model quality.
No provider call, external prompt, raw response, runtime route, database, or
write surface was opened.

## Next Slice

Keep the product live gate blocked. T3R4 leaves Gemini as the strongest broad
production-relevant lead, while the only fully paired five-case GPT/Gemini
slice is a 60/60 tie and cannot rank the models. DeepSeek remains useful only
as a synthetic adversarial/diversity source. The next proposed work is a
no-call Australian-region Gemini/Vertex feasibility and entitlement design;
any Vertex evaluation needs a new explicit provider/model/retention/budget
approval. Protected holdouts v1-v10 remain sealed and are not inputs.
