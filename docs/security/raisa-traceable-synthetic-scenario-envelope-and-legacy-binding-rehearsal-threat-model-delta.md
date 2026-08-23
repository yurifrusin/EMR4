# Raisa traceable synthetic scenario envelope and legacy binding rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T00:51:49.7346365+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-traceable-synthetic-scenario-envelope-and-legacy-binding-rehearsal`

## Assets

- canonical authored-synthetic scenario identity and provenance;
- authoritative deterministic and safety oracles;
- accepted reception semantic JSON and stateful YAML fixtures;
- future private-calibration evidence references;
- the unopened historical Diary trove;
- protected evidence and holdouts, which remain inaccessible; and
- the task branch and fixed protected Git refs.

## Threats and controls

### Source-authority self-promotion

Threat: a vendor claim, fiction prompt, method source, private observation or
local assumption declares itself eligible to define deterministic truth.

Control: oracle eligibility is a closed value derived from source type and
validated for exact agreement. Authoritative oracle entries accept only a
normative source after explicit scope review or an accepted EMR4 contract.

### Model self-certification

Threat: a model-generated case or extraction authors, adjudicates, reviews or
promotes its own oracle.

Control: role assignments are typed and distinct. Model identity is permitted
only in the extractor slot. Author, adjudicator and authoritative reviewer are
human/orchestrator roles; execution results cannot change evidence labels,
source classes or oracle eligibility.

### Duplicate or drifting scenario truth

Threat: the new envelope copies dialogue, actions, state or expected outcomes
and becomes a third scenario engine that can diverge from the accepted JSON and
YAML owners.

Control: bindings contain only identities, paths, digests and a complementary-
representation relation. The existing Pydantic semantic model and YAML loader
remain the payload validators. Hostile tests scan the manifest for forbidden
payload keys and known fixture names.

### Path expansion into protected or private data

Threat: a binding, locator or calibration reference becomes a generic path,
glob, URL or content hash that allows the validator to enumerate or resolve
protected evidence or the historical Diary.

Control: legacy validation accepts only four exact non-protected fixture paths,
performs no discovery, rejects traversal and root escape, and opens only an
explicit binding after allowlist comparison. Calibration references use a
restricted opaque-token grammar with no path, URI, extension or hash form and
typed false values for resolvability and de-identification claims.

### Hash-only false assurance

Threat: matching a digest is treated as proof that two semantically different
representations are equivalent or safe.

Control: each digest binds only one file's bytes. Both existing owning loaders
must pass and both identities must match. The declared relationship is
`complementary_shared_identity`, never field or outcome equivalence.

### Evidence-label laundering

Threat: an observed or privately calibrated sequence is relabelled as wholly
synthetic and admitted to execution without privacy review.

Control: the first envelope schema admits executable bindings only for
`wholly_authored_synthetic`. Other labels remain representable vocabulary but
cannot carry an executable binding in this version. Later admission requires a
reviewed schema change and the separate Diary privacy gate.

### PHI or recognisable-practice leakage

Threat: historical content, real notes, names, timestamps or trajectories are
copied into the new manifest or provider context.

Control: this tranche cannot access the Diary or provider. Its fixtures contain
only existing authored-synthetic references and abstract metadata. Tests reject
copied payload keys and the two known synthetic patient/practitioner names.

### Product/runtime authority expansion

Threat: a development evidence binding is mistaken for route, database,
ordinary-practice or deployment authority.

Control: the module remains inside `orchestration_harness`, imports no product
router/database/provider surface, grants no commands and does not execute the
replay engine. Product, provider, deployment, Pages and protected-ref surfaces
remain closed.

## Residual risk

Strict provenance prevents accidental authority promotion but cannot prove
that an authored scenario is realistic, complete or clinically correct.
Accepted fixture identity and digest checks do not prove real-world efficacy.
The future Diary review must measure contextual re-identification risk before
any private-derived material can become eligible for local development use.
