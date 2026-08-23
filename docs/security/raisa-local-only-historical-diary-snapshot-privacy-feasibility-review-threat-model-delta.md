# Raisa local-only historical Diary snapshot privacy feasibility review — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T01:33:35.0694120+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-local-only-historical-diary-snapshot-privacy-feasibility-review`

## Assets

- the unopened historical Diary archive and its temporal structure;
- direct identities, contact details, external identifiers and free text;
- linkage between repeated observations of the same scheduling record;
- relative timing, lifecycle and correction patterns needed for development;
- ephemeral pseudonymisation key material and any reversible mapping;
- private-derived local projections and their contextual-risk measurements;
- existing H5/H15 controls and approval scope; and
- the task branch and fixed protected Git refs.

## Threats and controls

### Premature archive access

Threat: designing the gate becomes an excuse to discover, enumerate or sample
the real archive before its access boundary exists.

Control: this tranche accepts only authored-synthetic in-memory inputs. Its
module has no path, file-opening, parser, glob, directory-discovery or
subprocess API. The future access artifact is declarative and requires a later
accepted operation to supply ignored local bindings.

### Pseudonymisation mistaken for anonymity

Threat: replacing names with stable tokens is treated as proof that a dense
longitudinal trajectory cannot identify someone.

Control: outputs are labelled synthetic rehearsal or locally restricted
private-derived candidates. Equivalence, uniqueness, rarity, linkage and
multi-release attacks remain explicit. No pass state is named anonymous,
de-identified-safe or provider-safe.

### Direct or free-text leakage

Threat: an identity, contact value, identifier, path, filename, timestamp,
note, staff label or reversible mapping survives projection or error handling.

Control: every input field has a closed privacy class and output treatment;
unknown fields fail closed. Only category counts and booleans enter reports.
Free text is reduced to a closed bucket. The HMAC key and mappings are
in-memory only and never serialized. Hostile tests scan serialized output and
exception text for detector targets.

### Temporal and trajectory linkage

Threat: rare attendance patterns, precise edit cadence, unique resource/time
combinations or a sequence of changes identify a person even after labels are
removed.

Control: source wall-clock observations become relative interval-censored
bounds. The gate computes record and trajectory equivalence, uniqueness,
rarity and defined auxiliary-clue attacks. The first real pass may only produce
a typed risk reading and a locally restricted candidate; it cannot promote a
fixture or external release.

### Multi-release composition

Threat: separately pseudonymised releases can be intersected to recover stable
rows, rare sequences or mappings.

Control: the synthetic rehearsal measures differencing attacks across
independently keyed releases. Future access uses one newly created ignored
output root and forbids retained mapping tables. Any second release is a new
operation and must be evaluated together with prior releases.

### False precision in re-identification probability

Threat: a small synthetic attack rate is presented as the mathematical chance
that no person can be reconstructed from the real archive.

Control: every metric is scoped to its exact population, quasi-identifiers,
adversary clues and integer trials. Empty trials fail. Reports state that the
numbers are conditional empirical readings, not universal probabilities or
legal determinations.

### Utility destroyed by over-redaction

Threat: privacy filtering reduces the archive to aggregates that cannot
reconstruct check-in, rescheduling, cancellation, correction or contention
mechanics.

Control: the projection intentionally preserves stable nonsemantic linkage,
relative observation windows, scheduling fields and lifecycle values. Exact
synthetic transition recovery is an acceptance requirement. A gate that is
safe but fails utility remains `revision_required`.

### Historical gate weakening

Threat: the new near-lossless research projection silently expands the H15
semantic fixture approval or replaces the aggregate-output validator.

Control: existing gate payloads, validators and tools remain byte-unchanged.
The new layer is additive. Its strongest outcome is
`locally_restricted_candidate`, which grants none of H15's fixture-promotion
authority and no broader use.

### Access-contract authority inflation

Threat: a committed future-access policy itself triggers a broad or recursive
run, network transfer or retention of raw output.

Control: the artifact is non-executable and contains no real path. It fixes one
leaf root, one dense day, non-recursive access, 80 files, 128 MiB total and
8 MiB per file as absolute maxima. Real execution requires a separate accepted
plan, ignored local bindings, readback and failure cleanup.

### Product or provider boundary escape

Threat: private-derived sequences enter product runtime, a model prompt,
memory, deployment or protected integration.

Control: the module imports no product route/database/provider surface. The
latch forbids network, model, product, memory, production, Pages and protected
refs. Any later use is a distinct gate and authority decision.

## Residual risk

No finite synthetic suite can prove that the real archive lacks unexpected
fields, recognisable trajectories or external linkage opportunities. A
successful tranche proves only that the measurement and transformation
mechanics fail closed on hostile invented inputs. The first bounded real read
must measure the actual schema and risk distribution locally, and its result
may still be `blocked`.
