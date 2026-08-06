# Model-required Practice Context Fabric intent-shaping rehearsal design

Date: 2026-08-06

Status: frozen authored-synthetic design

## Architectural seam

This descendant occupies only the probabilistic intent-proposal position in the
accepted Context Fabric. It does not insert a model between source truth and
policy, and it does not turn the model into a retriever.

`synthetic utterance -> isolated Gemini intent body -> deterministic candidate proofreader -> trusted IntentRetrievalCandidate wrapper -> accepted backend binding/catalog/retrieval -> accepted same-packet proofreader -> read-context-only release`

If the provider is absent or either proofreader blocks, no intelligent result is
released. The ordinary deterministic parent contract remains independently
testable but is not presented as the occupied intelligent completion.

## Typed objects

### `IntentShapingRequest`

A backend-authored and sealed request containing a synthetic case id, the exact
utterance, synthetic/date/timezone labels, the five code-owned intent
descriptions, allowlisted temporal-coordinate descriptions, exact parent
contract/policy digests, issued/expiry times and constant all-false authority.
It contains no source frames, identities, raw audit, product facts or command.

### `ProviderIntentBody`

The entire provider-visible candidate: `intent_code`,
`temporal_coordinate_code`, closed `cue_codes`, constant response code and the
all-false authority object. Every string value is enum-bounded. The schema is
closed and contains no narrative field.

### `ModelIntentCandidateEnvelope`

Trusted code binds the provider body to the request hash, provider-request hash,
sanitized provider-response hash/shape, exact provider/model/region policy,
attempt/ledger ids and immutable `candidate_provenance: untrusted_model`.
Provider text is not retained after parsing and hashing.

### `IntentShapingProofreaderTrace`

Deterministic code independently derives the expected intent, coordinate and
required cue codes from the authored-synthetic case. It rejects extra, missing,
contradictory or authority-bearing output. This proofreader admits a candidate;
it does not assemble context or grant a read.

### `ModelShapedIntentRetrievalRelease`

The final immutable envelope contains only hashes and admitted typed objects:
the model candidate envelope, intent proofreader, trusted parent candidate,
backend authority binding/catalog digests, accepted parent retrieval packet and
parent proofreader. Release requires both proofreaders and preserves
`read_only: true`, `provider_authority: false`, `command_authority: false`.

## Authority partition

- The model selects one candidate intent and temporal coordinate code.
- Code-owned case grounding decides whether that proposal is supported.
- Trusted wrapping supplies every field the provider is forbidden to control.
- The existing backend binding decides Bureau, purpose, session, component,
  field, time, sharing and disclosure authority.
- The existing parent engine assembles the minimum component set.
- The existing same-packet proofreader decides whether any frame set releases.
- No layer in this descendant can execute or authorise a command.

`RECEPTION ONE(TM)` and candidate `Clinician One` remain workspace brands only.
The request binds one atomic Rayleen capability independently of either brand.

## Provider isolation and evidence

The occupied controller uses one fresh one-shot cognitive cell and a host broker
with exact hostname/path, request-hash, response-size, single-use-ledger and cost
checks. The cell has no ambient provider fallback, filesystem source access,
database, product client, shell/tool bridge, callback or actuator. The broker
retains only allowlisted provider metadata and candidate/evidence hashes.

The frozen request uses `thinkingBudget: 1024`, `maxOutputTokens: 2048`,
temperature 0, one candidate, JSON MIME type and the exact provider-body schema.
Thought content is neither requested nor retained. Positive reported thinking
usage is acceptance evidence of the configured intelligence posture, not
clinical reasoning evidence.

## API Spine classification

The pure contract is unmounted read-context orchestration. The occupied Vertex
invocation is an isolated development Access AI command-like audit event, not a
product API. No GraphQL root/resolver/subscription or REST/OpenAPI product
command is added. A released Context Fabric packet remains read context and can
never serve as confirmation or mutation evidence.

## Failure semantics

- Preflight/setup with proven zero provider calls: close the attempt truthfully;
  a mechanical recovery may open a new attempt under the unchanged plan.
- Provider call without an admitted body: consume the attempt and release
  nothing.
- Eligible schema/grounding failure: discard the body and allow at most one
  complete-replacement correction with no previous candidate content.
- Parent proofreader, positive-thinking, authority or cleanup failure: no
  correction call and no pass.
- Admission: atomically close the cost ledger, release once, and forbid any
  further call.

Historical A3/B3, A4, C5 and Sydney Vertex ledgers and evidence are immutable
dependencies only. This descendant owns a new policy id, artifact root,
attempt ids, runtime names and ledgers.
