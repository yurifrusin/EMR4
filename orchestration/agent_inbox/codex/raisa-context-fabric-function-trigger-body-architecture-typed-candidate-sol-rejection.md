# Sol rejection — typed function/trigger-body candidate

Date: 2026-08-07

Decision: `revision_required`

Candidate state: uncommitted, unsealed and not admitted for independent veto

Canonical candidate-content digest with `contract_sha256` excluded:
`sha256:f8afd0ce97169b0fae926dbe7999b9961d9be7506f711de579a3c035f75b2064`

## Rejection

The corrected-looking typed candidate is rejected during Sol's deterministic
admission audit. Draft 2020-12 schema validation succeeds only because the
schema freezes each large object by positional `const`; it does not establish
that the frozen instructions express the named body semantics.

Material contradictions include:

- the producer node named `INSERT_PAYLOAD_FREE_OUTBOX` targets
  `emr4_context_fabric.diary_context_aggregate_aliases_v1`, repeats alias
  bindings and derives no insert effect;
- the following stream-head update node derives no update effect;
- a `cf_fence_appointment_update_v1` predicate reads `NEW` as
  `public.diary_committed_events`, which is not the trigger relation and is an
  illegal row image;
- `DERIVE_COLUMN_VALUE` identifies a target column and only a whole source-row
  symbol, leaving the source column or transformation for a renderer to
  invent; and
- `PROFILE_EVAL` includes opaque operations such as
  `CLOSED_TYPED_DERIVATION`, which reintroduce the semantic-label defect the
  normative recovery forbids.

Stored local effects and graph facts are therefore not trustworthy derived
evidence. The candidate is neither renderer-complete nor safe to seal, stage,
commit or submit for veto.

## Recovery boundary

Sol retains recovery ownership under the existing normative implementation
recovery. A replacement must make every read, write value, predicate, branch,
row image, terminal and effect independently derivable, reject these exact
cross-body/cross-relation substitutions after resealing, and pass a fresh
candidate-independent exact-head veto. The untrusted candidate may be used
only as negative evidence; none of its semantic nodes may be presumed correct.

No SQL, DDL, migration, database/source/provider contact, product/patient
data, runtime wiring, deployment, Pages action or protected-ref movement
occurred.
