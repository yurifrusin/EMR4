# LC2 Corpus Factory: Provenance and Promotion Rules

## Purpose

`app/services/bernie/corpus_tier.py` is a pure domain-layer gate around the LC1
`ReceptionScenarioSpec`. It records where a candidate came from, preserves its
source evidence, and prevents a generator from certifying its own material. It
does not call a provider, dispatch a route, mutate the diary, or itself decide
that a scenario is semantically correct. Protected Sol retains corpus authority.

Typed text and future speech transcripts are both surface inputs to the same
canonical semantic contract. Channel-specific spelling, punctuation, ASR, or
prosody handling must not change the provenance and promotion rules below.

## Tiers and origins

| Tier | Meaning |
|---|---|
| Gold | A human/Sol-authored reference, or a Silver candidate independently accepted with all generator, source, derivation, and adjudication history preserved. |
| Silver | A bounded candidate linked to a canonical Gold source and awaiting or carrying independent review evidence. |
| Bronze | Discovery or external material that may not yet be linked to a Gold source. It cannot enter Silver scoring until that link exists. |

`CandidateOrigin` distinguishes `human_authored`, `model_generated`, and
`external_source`. Human-authored Gold has no generator or source derivation.
Promoted model-generated Gold retains its generator, source scenario ID, full
source-content hash, transformation parameters, and every promotion event.
External-source material cannot become Gold in this LC2 no-import factory.

Wrapper and embedded scenario values for provenance, adjudication, and family
must agree. A Silver wrapper around a Gold scenario is invalid.

## Independent identities

Generator identity records contain provider, model, and optional lane instance.
Model judges contain the same fields. Human and protected-orchestrator judges
instead carry explicit actor kinds and actor IDs.

Independence is evaluated on the canonical lower-case model ID. A second lane,
instance, CLI transport, or provider wrapper around the same model is not an
independent judge. Provider and instance remain in stable trace keys and
derivation evidence, but cannot be used to bypass self-certification.

## Adjudication evidence

Every promotion requires an immutable `AdjudicationRecord` containing:

- an `accepted`, `rejected`, or `disputed` decision;
- the independent judge identity;
- an evidence-supplied timestamp;
- the checked semantic scope;
- the checked evidence scope; and
- a durable evidence reference.

A bare judge identity never promotes a case. Rejected and disputed decisions
enter quarantine. Promotion timestamps come from the record; the factory never
uses `datetime.now()` as authority evidence.

Each `PromotionEvent` embeds its complete adjudication record. A Bronze to
Silver to Gold path therefore retains both independent records even though the
candidate's top-level `adjudication_record` points to the latest review.

## Allowed transitions

| From | To | Requirements |
|---|---|---|
| Bronze | Silver | Accepted independent record, a linked canonical source ID, and its complete source-content hash. |
| Silver | Gold | Accepted independent record, valid schema/evidence/authority checks, and model-generated origin. |

Gold is terminal. Bronze to Gold, Silver to Bronze, external-source Silver to
Gold, and any transition without sufficient evidence are rejected or
quarantined.

## Lossless derivation

`compute_scenario_hash()` hashes the full canonical JSON representation of the
source `ReceptionScenarioSpec`. A derivation ID is then computed from:

1. that `sha256:<64 lowercase hex>` source-content hash;
2. the provider-qualified generator model identity; and
3. canonical explicit transformation parameters.

Timestamps and lane instances do not affect the result. A supplied derivation
ID is recomputed at construction and promotion. A mismatch fails closed.

```python
source_hash = compute_scenario_hash(source_scenario)
derivation_id = _compute_derivation_id(
    source_hash,
    generator.derivation_key(),
    transformation_parameters={"family": "paraphrase", "variant": 1},
)
```

## Authority boundary

Authority is represented only by the strict `AuthorityGrant` fields:

- `provider_write`
- `diary_write`
- `confirmation`
- `override_authority`

Generated Silver or Bronze candidates must have all fields false. Scenario
descriptions may discuss providers or confirmation without granting authority,
and `forbidden_tool_calls` are restrictions rather than grants. This avoids
unsafe substring heuristics while keeping the boundary explicit.

## Quarantine reasons

The machine-readable reasons cover self-certification, schema invalidity,
explicit authority grants, source-span mismatch, missing provenance, unsafe
instructions, invalid transitions, missing source Gold evidence, rejected or
disputed adjudication, and derivation mismatch. Quarantine never silently
promotes or rewrites a candidate.

## External-source registry

`CandidateRegistry` is metadata only. Entries may contain a primary source URL,
publisher-declared licence text, capability labels, an estimated count, access
notes, and structured review gates. Decisions are limited to `candidate_only`
or `requires_licence_review`. They never mean eligible, accepted, or licensed.

The registry currently records SGD/SGD-X, SMCalFlow, MultiWOZ, and the user-
suggested Healthcare Appointment Booking Calls dataset. For the latter, the
publisher-declared PDDL label and reported 739 files are not treated as verified
rights or a verified dialogue count. Required gates cover licence provenance,
recording consent, jurisdiction/privacy, redaction leakage, and local-only
inspection. No dataset content has been downloaded or accepted.

Repository/code licences can differ from dataset and underlying-source rights.
All licence metadata here is descriptive, not legal advice or acceptance.
