# Threat-model delta: Gate -1 adversarial Bureau containment

Date: 2026-08-04

Status: accepted Gate -1 architecture requirement; no runtime control is
implemented

Parents:

- `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`
- `docs/security/emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md`
- `docs/security/hardening/model-required-bureau-gate-minus-one/hardening.md`

## Changed adversary assumption

The normal adversary model now assumes all of the following can occur without a
separate model failure:

- direct prompt injection in a user's natural-language request;
- indirect prompt injection in any product field, retrieved record, policy,
  runbook, document, provider response or prior model output;
- a provider-model or supply-chain compromise that produces deliberately
  hostile but schema-shaped output;
- compromise of the local cognitive wrapper before the candidate reaches the
  proofreader; and
- an operator who cannot reliably recognize hidden provenance, Unicode, covert
  encoding or indirect-injection influence in a confirmation preview.

The model, prompt, wrapper and model-generated explanation are therefore never
security principals or authority evidence.

## Newly protected assets

- integrity and confidentiality labels and their deterministic join rules;
- source-wrapper and sink-policy registries;
- capability and authority-ceiling metadata;
- endorsement, declassification and confirmation evidence;
- cognitive-cell input/output channels and hostile-byte parser;
- provider broker bindings and credentials;
- runtime profiles, bridge inventory and teardown/residue receipts; and
- cross-Bureau separation of identities, state, memory and quotas.

## New and refined trust boundaries

1. Source boundary: trusted deterministic wrappers assign initial labels to
   backend facts, user text, retrieved content and provider data.
2. Cognitive boundary: the mandatory provider model receives only the admitted
   labeled view and returns hostile candidate bytes.
3. Broker/parser boundary: a deterministic broker owns provider transport and
   admits one bounded canonical candidate; it evaluates no model-controlled
   code, path, URL, callback, template or object.
4. Proof boundary: deterministic label joins, schema, grounding, freshness and
   sink policies decide whether a candidate may proceed.
5. Authority boundary: human or dual review creates a separate signed,
   field-scoped, expiring authority fact; it does not upgrade source integrity.
6. Command boundary: only the existing REST/OpenAPI command path can mutate
   truth, after backend reauthorization, idempotency and conflict checks.
7. Execution boundary: recovery uses a separate single-purpose actuator and
   identity; neither the model, cell, broker nor proofreader owns its credential.

## Threats and candidate controls

### Low-integrity data changes a consequential action or argument

Controls:

- label every value and propagate deterministic dependencies;
- require high-enough integrity for action selection and each
  security-relevant argument;
- fail closed on a missing label, unknown transformation or low-integrity join;
- treat fixed plans and parameter allowlists as additional constraints, not a
  replacement for data-flow policy; and
- preserve a typed denial trace that names the source and failed sink rule.

### Confidential information is exfiltrated through an allowed response

Controls:

- attach reader sets to every value and preserve the least-permissive join;
- require each response, log, callback or command destination to be within the
  contributing reader sets;
- bound output shape, size and character policy according to the sink;
- make declassification explicit, scoped, signed, expiring and field-specific;
  and
- prohibit model-authored destinations, labels or declassification evidence.

### Prompt-controlled bytes become host instructions

Controls:

- one canonical UTF-8 JSON candidate with duplicate-key, depth, member, string
  and total-size limits;
- no generated-code execution, `eval`, polymorphic object deserialization,
  template evaluation, path dereference, URL fetch, callback or upload surface;
- parsers and validators run before logging or interpolation into another
  language; and
- differential and adversarial parser tests are required before runtime.

### A compromised cell reaches host or cloud authority

Controls:

- one fresh cell and identity for one Bureau attempt;
- non-root/rootless where supported, read-only, mount-free, no runtime socket,
  dropped capabilities, no-new-privileges and syscall restriction;
- no ambient network, metadata endpoint, provider credential, database,
  filesystem, command or actuator capability;
- broker-owned allowlisted provider transport with immutable destination,
  model, region, data class, budget and retry; and
- process, CPU, wall-time, memory and output quotas with deterministic kill,
  teardown and residue evidence.

### Cross-Bureau contamination or capability confusion

Controls:

- distinct Bernie, Rayleen, Davida and recovery cell generations, identities,
  source/sink allowlists and quotas;
- no shared conversation, cache, filesystem or writable memory;
- Bureau and practice scope included in every label and capability;
- label joins cannot widen either scope; and
- cross-Bureau transfer requires a separately declared typed backend contract,
  never a model-to-model memory path.

### Human review is socially engineered into endorsing hidden influence

Controls:

- present source, integrity, freshness, readers, semantic delta and exact
  command arguments in deterministic review UI;
- confirmation signs the displayed candidate hash and expiry;
- confirmation cannot upgrade low-integrity facts or broaden readers;
- sensitive operations retain dual review and separation of duties; and
- rate limits and grouped review avoid confirmation fatigue.

### Safety feature or detector is mistaken for authority

Controls:

- provider alignment, prompt hierarchy, delimiters, detectors, canaries and
  output scanning are defense in depth only;
- detector success never raises integrity, lowers confidentiality or grants a
  capability;
- detector failure may deny or quarantine but cannot create a permissive
  fallback; and
- provider-blocked and provider-occupied tests must produce the same
  deterministic authority outcome for equivalent candidate data.

## Required Gate-zero evidence

- closed schemas for labels, candidate dependencies, capabilities, source
  wrappers, sink rules, endorsement/declassification and denial receipts;
- algebraic and property tests for label propagation and no-scope-widening;
- exhaustive versioned bridge inventory with deny-unknown admission;
- one-attempt cell runtime contract with quota, kill and residue schemas;
- injection and hostile-output corpus covering every source and sink;
- parser differential and serialization-smuggling tests;
- provider-free deterministic tests before any occupied rehearsal; and
- fresh independent adversarial review after the candidate is frozen.

## Residual risks

The selected architecture cannot prove immunity to unknown host, kernel,
runtime or microarchitectural vulnerabilities; provider-side retention or
compromise; all covert channels; incorrect source labels; or a defective
security policy approved by authorized humans. A later microVM profile can
strengthen runtime isolation without changing the broker contract. Real
identity, patient or clinical data, product reads/writes, provider selection,
deployment, production and release remain closed.
