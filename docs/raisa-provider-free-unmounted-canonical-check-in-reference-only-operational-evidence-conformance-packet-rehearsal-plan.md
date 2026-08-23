# Provider-free unmounted canonical check-in reference-only operational-evidence conformance packet rehearsal plan

Date: 2026-08-23

Timestamp: 2026-08-23T14:40:30.0790284+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation:
`raisa-provider-free-unmounted-canonical-check-in-reference-only-operational-evidence-conformance-packet-rehearsal`

Planning source HEAD:
`0e8138c39ece888aa8e63db3f5612ff02328ed67`

Target result:
`raisa_provider_free_unmounted_canonical_check_in_reference_only_operational_evidence_conformance_packet_rehearsal_pass`

Reasoning level: High. All component semantics and denial vocabularies are
already accepted. This tranche proves their exact composition without changing
admission meaning, product behavior or an external environment.

## Objective

Pass one fixed authored-synthetic, opaque-reference-only packet through the
accepted manifest normalizer, typed operational-evidence input normalizer,
pure evidence-gate evaluator and default-off admission seam. The canonical
packet must produce a satisfied evidence-gate reading while the ordinary lane
still ends at `ordinary_activation_closed` with zero admission release.

Exercise a closed hostile matrix for absent, ambiguous, secret-bearing, stale,
wrong-environment, wrong-role, self-verified, duplicated, rotation-mismatched,
break-glass, generation-mismatched and digest-mismatched variants. Every
variant must fail closed at its existing component boundary and release no
ordinary admission.

The result proves cross-component repository conformance only. It cannot
establish a live role, secret binding, custody/rotation attestation,
break-glass fact, current environment manifest, uniqueness/freshness readback,
target selection or lasting authorization.

## Narrow implementation

The tranche owns only:

1. one immutable JSON packet and its closed schema;
2. one small provider-free rehearsal script that loads that exact packet and
   calls the five accepted pure functions without bypass or substitute logic;
3. focused tests for the canonical path, all twelve hostile cases, stable
   reason precedence, source immutability and zero forbidden capability;
4. deterministic evidence/report artifacts; and
5. normal closeout, acceptance, Yuri summary and clockwork publication.

No reusable form framework, general Harness adapter, environment reader,
secret resolver, product adapter, API, route, client or configuration layer is
created.

## Exact accepted Git bindings

| Accepted result | Full Git object |
|---|---|
| Manifest normalizer product | `ae62faf95b289b369a6eea1793ee4325f33447bc` |
| Typed operational-evidence inputs product | `9011d83d769f45bb717c039a126a890d43922dce` |
| Pure environment evidence-gate product | `89640f1bb6ad992f68d5c20fd578b4062eeb193d` |
| Ordinary-admission kernel product | `4204ec6348abb0f92b1a30314699d4a469fa860a` |
| Environment-evidence admission seam product | `1fd1d5f77a02c671528dd0a5f18de4da2f070eaa` |
| Post-seam readiness evidence | `f1e88ccfa62a90bd72cbc5dc6c0ac3e249245d4d` |
| Post-seam readiness closeout | `0e8138c39ece888aa8e63db3f5612ff02328ed67` |

Every object must resolve as a full commit and ancestor of the candidate.

## Exact text inputs

Use strict UTF-8, CRLF-to-LF canonicalization, bare-CR rejection and SHA-256:

| SHA-256 | Path |
|---|---|
| `6bc34af8b8d7347a0a5096e937e2054c98cb0cc81e437d2c345247049231f0d0` | `orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-readiness-post-evidence-seam-convergence-review/evidence.json` |
| `adad1642e1de628246eb7e39263a381f837139eb662baeefe8b2873a71b56bc2` | `orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-environment-manifest-operational-secret-posture-evidence-gap-decomposition/contract.json` |
| `95dbc5f6dfb79e8a5f43f84ec3b4af51fbdca16902bc07859e9aacc6d970b2ef` | `app/services/appointment_check_in_environment_manifest.py` |
| `cabcb9dce213469b9a53bd2201e47a33fd3ac73c9f568874debbf85468420bf0` | `app/services/appointment_check_in_operational_evidence.py` |
| `d1b39368814a4b9c59f0aaa7dd3b211f106bf9c21cef42fd0a59057c733f1a4e` | `app/services/appointment_check_in_environment_evidence_gate.py` |
| `9f9d3e1dd9dd1527e21cca1b6b0f920455d79bc26900698d7743ec919d45c526` | `orchestration_harness/check_in_admission_control.py` |
| `df28c6cbf67e45ffed555ffadfe806591ffbc56c600f16a210c982380b2d878a` | `orchestration_harness/check_in_environment_evidence_admission.py` |

No source discovery is needed after these seven bindings are frozen.

## Frozen packet and happy path

The packet classification is exactly
`authored_synthetic_opaque_reference_only`. It uses the synthetic environment
`env:authored-reference`, practice reference
`practice-ref:authored/reference`, snapshot generation 7, explicit evaluation
time `2026-08-25T00:00:00Z`, three ordered opaque secret-reference slots and no
secret material.

The exact canonical component path is:

1. `manifest_normalized`;
2. `evidence_inputs_normalized`;
3. `evidence_gate_satisfied`;
4. ordinary-practice `denied` at `ordinary_activation_closed`; and
5. zero ordinary admission release and `operational_fact_status =
   not_established`.

The packet requests the ordinary lane only. It never marks itself as admitted
authored-synthetic product traffic; `authored_synthetic` describes evidence
provenance, not an admission bypass.

## Closed hostile matrix

| ID | Mutation | Required terminal component result |
|---|---|---|
| `manifest_absent` | no selected manifest | `manifest_absent` then `ordinary_evidence_missing` |
| `manifest_ambiguous` | two identical normalized manifests | `manifest_ambiguous` then `ordinary_evidence_missing` |
| `manifest_secret_material` | add forbidden secret material field | `manifest_invalid` then `ordinary_evidence_missing` |
| `evidence_boolean_claim` | replace a typed observation with a Boolean | `role_evidence_invalid` then `ordinary_evidence_missing` |
| `manifest_stale` | evaluate outside the manifest window | `manifest_stale` then `ordinary_evidence_missing` |
| `wrong_environment` | bind role evidence to another environment | `environment_mismatch` then `ordinary_evidence_missing` |
| `wrong_role` | bind a different database role | `role_binding_missing` then `ordinary_evidence_missing` |
| `self_verified_role` | reuse the role evidence reference as verifier | `role_evidence_invalid` then `ordinary_evidence_missing` |
| `duplicate_evidence_reference` | duplicate a rotation evidence reference | `rotation_evidence_invalid` then `ordinary_evidence_missing` |
| `rotation_key_mismatch` | mismatch observed and declared key IDs | `secret_reference_invalid` then `ordinary_evidence_missing` |
| `break_glass_engaged` | declare and attest `engaged_deny` | `break_glass_not_inactive` then `ordinary_evidence_missing` |
| `snapshot_binding_mismatch` | mismatch generation or manifest digest | satisfied gate then `ordinary_evidence_missing` |

Every case must keep `admission_released = false`,
`ordinary_admission_released = false`, and external-fact count zero.

## Deterministic acceptance

Pass requires:

1. all seven hashes and seven full Git bindings pass;
2. the packet and evidence validate against closed JSON Schemas;
3. the canonical path reaches the exact four accepted component reasons and
   remains non-admitting;
4. all twelve hostile cases reach their exact existing closed reason codes;
5. no result contains secret material, a resolved reference or a capability;
6. source inputs and packet bytes remain unchanged;
7. the six external facts remain absent, the five human choices remain
   unselected, and the readiness clock remains 11/0/1 not ready;
8. focused tests, surrounding component tests, Ruff, compilation and
   `git diff --check` pass; and
9. protected refs and all unrelated untracked files remain unchanged.

The accepted result completes the last repository engineering prerequisite.
It does not close the operational-evidence gap. Yuri's attention becomes
required immediately afterward, before any target, custody, policy,
provisioning or activation choice.

## Harness and parallelism assessment

- **DeepSeek:** declined. The active latch forbids a provider/Harness call, the
  failed exact native profile has no naturally in-scope fix evidence and
  Claude Code is not a fallback.
- **Gemini:** declined. This provider-free pure-composition result is decided
  by closed deterministic contracts; reassess only on conflict or material
  semantic change.
- **Native subagents:** declined under current developer policy and because the
  packet, denial matrix and acceptance are serially coupled.
- **GPT Sol:** owns implementation, verification, acceptance and closeout.

## Closed surfaces

No external fact or human choice, operational manifest, environment variable,
credential store, secret/reference resolution, network, provider, database,
Docker, PostgreSQL, SQL, live role, infrastructure, existing product source,
route, API, client, configuration, feature flag, allowlist, ordinary admission
record, command mount, action grammar, generic-status `Arrived`, waiting-area
movement, product/patient/appointment/clinical/historical/protected data,
production, deployment, release, Pages, protected evidence or protected-ref
movement is authorized. Preserve `docs/branding/` and every unrelated
untracked file. Use explicit-path staging only.
