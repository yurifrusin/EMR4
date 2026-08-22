# Threat-model delta: check-in environment and secret-posture gap decomposition

Date: 2026-08-23

Timestamp: 2026-08-23T08:17:56.0913023+10:00 (Australia/Brisbane)

Status: `frozen_narrow_threat_delta`

## Scope

This is a provider-free, repository-static decomposition of the accepted sole
remaining check-in readiness gap. It creates no manifest, secret, role,
infrastructure binding, product integration or admission.

## Protected assets

- the accepted 11/0/1 matrix and
  `not_ready_for_ordinary_practice_admission` verdict;
- raw secrets, credential stores, process environment and secret references;
- exact environment, practice, role, generation and independent-evidence
  bindings;
- the distinction between architecture, repository code, operational fact and
  human authorization;
- API-Spine read/manifest/typed-enforcement/command separation;
- product, patient, appointment, clinical, historical and protected evidence;
- protected refs and every unrelated untracked file.

## Threats and fail-closed controls

| Threat | Control |
|---|---|
| Decomposition is reported as gap closure. | Output must retain dimension 11 as `operational_evidence_gap`, the exact 11/0/1 counts and the not-ready verdict. |
| A repository fixture substitutes for a real operational fact. | Every external-fact node explicitly rejects documentation, model, authored-synthetic and disposable-runtime substitution. |
| A secret reference is treated as proof of custody or possession. | Opaque reference bindings and current independent custody/rotation attestations remain separate mandatory facts; no resolver is opened. |
| Sol silently chooses a target practice, environment, provider, cadence or verifier. | Those values are closed `human_owned_external_decision` nodes and remain unselected. |
| A pure evaluator gains activation authority. | Repository prerequisites may return only the accepted typed evidence-gate reading; the admission evaluator, feature flag, records, kill switch, confirmation and later human activation remain separate. |
| YAML or free-form labels create authority. | One closed normalized schema and one four-value node-class vocabulary reject aliases, unknown fields and invented classes. |
| Live state leaks through local configuration. | The verifier reads only ten exact accepted inputs; `.env`, process environment, secret stores, database, application imports and network are forbidden. |
| The repeated shell mistake creates another bureaucratic layer. | Existing preflight `git_refs_snapshot` alone supplies acceptance Git/worktree readings; no new Git-summary control is added. |
| A human-only action is requested ceremonially too early. | Repository-only prerequisites proceed under standing authority; user attention begins only immediately before a required external selection or lasting action. |
| Protected or product state changes incidentally. | Provider-free no-write verification, explicit-path staging, protected-ref and preserved-untracked checks fail closed. |

## Residual risk and stopping rule

The decomposition can show what remains and in what order, but cannot prove the
selected environment exists, secret custody is current, rotation occurred, a
live role is correctly bound or a human authorized lasting external actions.
Those are deliberately irreducible operational facts and decisions, not more
repository paperwork.

The next tranche may implement only the provider-free unmounted closed
normalizer, typed evidence inputs and pure evidence-gate evaluator. It may not
create an operational instance, resolve a reference, access a secret or feed a
product admission path.
