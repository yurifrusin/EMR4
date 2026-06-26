# EMR4 AI Provider Boundary

> Purpose: keep EMR4 flexible in a fast-moving AI market without adding a heavy
> abstraction layer before the product needs it.

## Decision

EMR4 should keep Gemini/Vertex AI as the first-class provider for current
clinical AI work, especially audio scribe, but the application should no longer
let provider SDK calls define EMR4's internal contracts. The boundary should be
thin, capability-based, and tested with golden fixtures before any future
provider switch.

The architectural centre is **EMR4's clinical and receptionist contracts**, not
Gemini, LiteLLM, DeepSeek, OpenAI, or any other provider. Providers are adapters
behind those contracts.

## Why This Matters

The AI sector is moving quickly. EMR4 should be able to respond to changes in:

- provider quality, cost, latency, and context windows
- data residency and healthcare compliance requirements
- multimodal support, especially direct audio
- structured-output reliability
- model/tool-call safety for Bernie and future agents

At the same time, over-abstracting too early would slow down delivery. Gemini is
already working, has Google Cloud credits available, and direct audio support is
a real advantage for the medical scribe path. The goal is therefore not
"provider neutrality everywhere today"; it is **portable EMR4 contracts with
Gemini as the initial adapter**.

## Current Coupling To Reduce Over Time

The current implementation calls the Google Gen AI SDK directly from runtime
routers, notably:

- `app/routers/consultation.py` for consultation analysis and audio scribe
- `app/routers/letters.py` for AI-drafted letters

That is acceptable for early integration but should not spread further. New AI
surfaces should call an EMR4-owned service interface instead of importing a
provider SDK directly.

## Boundary Shape

Prefer a small backend package such as:

```text
app/services/ai/
  contracts.py          # Pydantic request/response models and capability names
  service.py            # EMR4-facing service facade
  providers/
    gemini.py           # first production adapter
    litellm_text.py     # optional future text-only adapter
  evals/
    fixtures/           # de-identified golden inputs
    expected/           # accepted structured outputs
```

The service facade should expose EMR4 capabilities, not raw model names:

| Capability | EMR4 Contract | Provider Detail |
|---|---|---|
| Audio scribe | audio + patient/context -> transcript + SOAP/coding candidates | Gemini direct audio now; future ASR+LLM split if useful |
| Clinical extraction | consult text -> validated clinical JSON | any structured-output capable model |
| Letter drafting | intent + patient/encounter context -> draft + citations/source fields where relevant | Gemini now; other text models later |
| Reception intent parsing | staff utterance/text -> typed constraint object | Bernie translator stage |
| Tool-call selection | context + allowed tools -> proposed typed command | never direct DB mutation |

## Scribe Strategy

Do not split the scribe pipeline merely for architectural purity. Gemini's direct
audio support is currently a feature, not technical debt.

Use this progression:

1. Wrap the existing Gemini direct-audio path in an EMR4 `audio_scribe`
   capability.
2. Make its output schema explicit and validated.
3. Add a transcript-first adapter only if there is a measured reason: cost,
   quality, latency, data-residency, or provider availability.
4. Keep downstream clinical extraction independent of whether the upstream
   provider consumed audio directly or consumed a transcript.

## Bernie Strategy

Bernie should be provider-agnostic from the start because its safety boundary is
tool semantics, not model personality.

The LLM's job is to translate staff language into validated objects:

- patient identity constraints
- appointment/room/waiting-area constraints
- intent classification
- typed proposal candidates
- clarifying questions when required fields are missing

The LLM must not decide availability, create appointments, alter waiting-room
state, or mutate records. Deterministic EMR4 code owns search, conflict checks,
warnings, blocks, proposals, writes, and audit.

## LiteLLM / OpenAI-Compatible Gateways

LiteLLM or an OpenAI-compatible gateway may be useful later, especially for
text-only tasks, but should remain an adapter detail. EMR4 should not build its
domain model around a third-party gateway's lowest-common-denominator API.

Recommended posture:

- define EMR4 contracts first
- implement Gemini directly where its multimodal features matter
- consider LiteLLM for commodity text capabilities after the facade exists
- never let gateway-specific tool-call shapes leak into appointment, clinical,
  or Bernie contracts

## Evaluation Harness

Before any provider switch or major prompt rewrite, run a small repeatable
evaluation harness. The harness should use de-identified fixtures and emit
compact structured results.

Minimum evaluation dimensions:

- schema validity and parse failure rate
- clinically important omissions or hallucinations
- appointment/tool-call safety violations
- latency and cost
- provider/model version
- prompt version
- data-residency or compliance notes

The same cost-conscious sprint-review principle applies here: explore once,
crystallize into a fixture/check, then run the check cheaply forever.

## Implementation Rules For Future Sprints

- New AI runtime code should depend on EMR4 `app/services/ai` contracts, not
  provider SDKs in routers.
- Existing direct Gemini calls can be wrapped incrementally; do not refactor all
  AI paths in one large sprint.
- Structured outputs must be validated with Pydantic before reaching DB writes,
  UI command proposals, or clinical persistence.
- Bernie tool schemas must stay provider-neutral and match the existing
  command/proposal safety pattern.
- Provider-specific prompt tricks are allowed inside adapters, but output
  contracts must stay stable.
- Provider changes should require a fixture/eval update, not a product-code
  rewrite.

## Near-Term Sprint Candidates

1. Add a thin `app/services/ai` contract/facade around consultation and letter
   calls without changing user-visible behaviour.
2. Add de-identified golden fixtures for consultation extraction and letter
   drafting.
3. Define Bernie's first provider-neutral intent/constraint schemas before any
   runtime copilot implementation.
4. Add deterministic review checks for AI output schema validity and refusal/
   clarification behaviour.

