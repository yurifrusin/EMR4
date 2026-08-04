# EMR4 model-required Bureau A3/B3 request-contract recovery threat-model delta

Date: 2026-08-04

Status: authorised authored-synthetic recovery delta; no product, write,
deployment, release or protected-ref authority

Parent:
`docs/security/emr4-model-required-bureau-a3-b3-threat-model-delta.md`

Plan:
`docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-plan.md`

## Security claim

This delta covers a new, isolated recovery namespace for the rejected A3/B3
occupied rehearsal. It replaces unbounded automatic thinking plus a 512-token
output cap with one explicit bounded allocation: 1,024 thinking tokens and
2,048 total output tokens. It also adds sanitized pre-parser shape evidence.
All parent trust boundaries,
one-use-cell controls, deterministic proofreading and zero-product-authority
invariants remain mandatory.

Success proves only that the exact Sydney Vertex development request produced
one grounded, proofreader-admitted authored-synthetic advisory release for
each lane. It does not prove the prior cause, production suitability,
Australian sovereign processing, patient-data safety or any product effect.

## New threats and controls

### R1: Historical evidence or accounting is silently reused

**Threat.** Recovery overwrites the old attempt, reopens its consumed ledger or
uses the same logical identities, making call/cost history ambiguous.

**Controls.** Use a distinct artefact root, policy id, parent tranche id,
attempt/ledger ids and Docker resource prefix. Tests bind the old evidence and
ledger hashes before and after recovery. Existing files are read-only inputs.

### R2: A multi-variable retry prevents causal diagnosis

**Threat.** Thinking policy, output budget, schema, prompt and parser are all
changed together, so a success teaches nothing and a failure cannot select a
bounded next remedy.

**Controls.** The first provider request changes exactly the coupled generation
allocation: `thinkingConfig.thinkingBudget = 1024` and
`maxOutputTokens = 2048`. The two fields are intentionally bound because the
total output cap must leave room for both reasoning and the typed visible
answer. Its canonical diff must show no other request change. Observation-only
telemetry may become more precise but cannot alter candidate admission or
release. Each later attempt requires a distinct, evidence-selected request
hash.

### R3: Diagnostic telemetry leaks provider content

**Threat.** Improving diagnosis persists raw prompt/response text, thoughts,
finish messages, headers or credentials.

**Controls.** Persist only closed enums, booleans, non-negative counts,
response byte size/hash, model version and bounded token usage. Part kinds are
classification labels only. Never retain part values, prompt feedback text,
raw exceptions or response bodies. Secret/raw-content tests scan all durable
recovery artefacts.

### R4: Provider multipart flexibility weakens the parser

**Threat.** Recovery concatenates arbitrary parts, selects a convenient part
or admits thought/function/tool material as the selector body.

**Controls.** The first recovery keeps the exact one non-thought text-part
admission boundary. Missing, invalid, empty, multiple, thought and non-text
parts receive precise terminal reason codes and release nothing. Any future
parser change is separately hashed, reviewed and justified by observed safe
metadata.

### R5: Davida starts after a transport success but before Rayleen admission

**Threat.** HTTP 200, parse success or a rejected proofreader result is treated
as sufficient to consume the Davida call.

**Controls.** Davida remains ineligible until Rayleen's deterministic
proofreader verdict is `admitted` and one atomic advisory release exists. Any
Rayleen pre-parser or proofreader rejection closes the current sequence with
zero Davida provider calls.

### R6: Bounded recovery becomes an unbounded loop

**Threat.** Routine continuation is interpreted as permission for unchanged
retry, additional providers, higher cost or indefinite calls.

**Controls.** Enforce at most two calls per lane, four calls and USD 1
cumulative, one call per single-use ledger, no unchanged request hash and no
call after admission. Stop at exhausted materially distinct remedies. Standing
continuation removes permission pauses, not ceilings or user-owned material
forks.

## Required proof

- exact old/new request comparison with only the 1,024/2,048 bounded-reasoning
  allocation changed;
- distinct recovery namespace, ids and parent accounting;
- provider-free response fixtures for valid `STOP`, `MAX_TOKENS`, safety or
  prompt block, missing/invalid/empty/multiple parts, thought/non-text parts,
  malformed JSON and schema-invalid JSON;
- sanitized metadata before extraction and literal false raw-retention fields;
- no correction/release/Davida call following Rayleen pre-parser rejection;
- fresh source-only independent veto and exact read-only preflight before the
  first occupied call; and
- zero patient/clinical/product data, product/database access, commands,
  writes, actuators, cloud/IAM mutation, deployment, release, Pages and
  protected-ref movement.

The protected refs remain
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. This delta grants no protected
integration or evidence authority.
