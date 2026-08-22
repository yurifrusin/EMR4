# Canonical check-in environment-manifest and secret-posture gap-decomposition plan

Date: 2026-08-23

Timestamp: 2026-08-23T08:17:56.0913023+10:00 (Australia/Brisbane)

Status: `frozen_narrow_plan`

Operation:
`raisa-provider-free-read-only-canonical-check-in-environment-manifest-operational-secret-posture-evidence-gap-decomposition`

Planning source HEAD:
`a9fdee5e25b1096569e2322b5073a089e5705ce9`

Accepted 11/0/1 closeout source:
`ca18d64052241cd07bc1ac73887f849e2d245f98`

Accepted environment-architecture candidate:
`a1f309a6d52d01f9866432f7e9abb8095788d023`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. This tranche preserves the accepted architecture and
ordinary-practice denial. It classifies already-frozen requirements and does
not choose an environment, practice, custody provider, rotation policy,
verifier, deployment or activation outcome.

## Objective

Decompose the sole remaining readiness dimension,
`environment_manifest_and_operational_secret_posture`, into the smallest
ordered set of:

1. repository-only engineering prerequisites that can proceed without secrets
   or an operational environment;
2. external operational facts that only real infrastructure and independently
   verified evidence can establish; and
3. genuinely human-owned external decisions or lasting actions that the
   repository must not infer.

The output is a dependency map, not a gap closure. The exact result must remain
11 satisfied / 0 blocking / 1 operational-evidence gap with verdict
`not_ready_for_ordinary_practice_admission`.

## Exact accepted inputs

All inputs use strict UTF-8 canonical-LF SHA-256. Bare CR, digest drift,
abbreviated Git objects or non-ancestor bindings deny.

| SHA-256 | Path |
|---|---|
| `d2b6836a84465555e47ce97d66b3dddc0f866251bbf7cf53b73908103d7d7c46` | `orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-readiness-post-attempt-008-convergence-review/evidence.json` |
| `c93ab33095fc5be81a6e14a3eeb26ee402edd498ef8c8bdc2e435fda6c851a54` | `orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-readiness-post-attempt-008-convergence-review/report.md` |
| `f0dfeebd7f5ecafdc6ad2d63484e6ff83d515e4216107f990677947f28a82236` | `docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-admission-readiness-post-attempt-008-convergence-review-closeout.md` |
| `f0624b93eee19275365e7dd1b813ca318b8bb4c1c775803fe80cab68322806dd` | `orchestration/agent_inbox/codex/raisa-post-attempt-008-check-in-admission-readiness-convergence-review-sol-acceptance.md` |
| `e9aab3504520d955a0ce2c94c32a5f9a6ae25d7bbf129c7f2bd21951201c34d8` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/contract.json` |
| `786cab3b19231c391d281cf36568b4206fe5f11b2a2ac51469f0996c3e718e88` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/environment-manifest.schema.json` |
| `0f1b762f28247e5c9033cf377716b21a625080344c5996ea743d90b66b1eb32b` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/provider-free-architecture-evidence.json` |
| `35f09c1118734d6b40ae267732a168343e2b76ebd9dd00fd901a7d891a831018` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/architecture-report.md` |
| `0858486ff6cd173a6b3b397585e7b1ff74c578b341a8e34b8425e114e0520b5e` | `docs/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture-closeout.md` |
| `ecac18824503953828d876eda863f40c419af5d5b92b0ef1fd180730452570ea` | `orchestration/agent_inbox/codex/raisa-check-in-environment-manifest-secret-posture-architecture-sol-acceptance.md` |

## Closed decomposition vocabulary

Every node has exactly one class:

- `accepted_foundation` — already satisfied supporting evidence that this
  tranche may bind but not reopen;
- `repository_engineering_prerequisite` — provider-free code or conformance
  work that can use only synthetic/reference-only fixtures and cannot establish
  an operational fact;
- `external_operational_fact` — a fact that only an exact authorized
  environment plus current independent evidence can establish; or
- `human_owned_external_decision` — a target, custody, policy, verifier or
  lasting-action choice that Sol cannot infer or execute.

No free-form class or stage label is accepted.

## Frozen dependency map

### Accepted foundations

1. `readiness_matrix_11_0_1` binds the sole open dimension and unchanged
   not-ready verdict.
2. `reference_only_manifest_architecture` binds the closed normalized shape,
   one logical runtime role, three ordered secret-reference slots, current
   rotation evidence and deny-only break glass.
3. `disposable_role_tenant_attestation` remains supporting evidence for the
   role semantics only; it is not a live role binding.
4. `atomic_unknown_response_and_rollback` remains supporting transaction
   evidence only; it supplies no environment or custody fact.

### Repository engineering prerequisites

1. `closed_manifest_normalizer` — parse an explicitly supplied non-secret
   manifest through a safe bounded manifest layer into the accepted closed
   normalized reading; reject aliases, unknown keys, ambiguity, bare secret
   fields and non-canonical bytes. It must not read `.env`, process environment,
   a secret store or product configuration.
2. `typed_operational_evidence_inputs` — define closed typed readbacks for one
   role attestation, three rotation/custody attestations and deny-only
   break-glass evidence. These are inputs from external verifiers, never
   self-asserted Booleans or secret-resolution results.
3. `pure_environment_evidence_gate_evaluator` — implement the accepted ordered
   checks, uniqueness, full-object binding, freshness and closed reason codes,
   returning only a typed evidence-gate reading.
4. `default_off_admission_input_seam` — permit the existing admission evaluator
   to consume that typed reading as one independently mandatory prerequisite,
   while retaining feature flag, ordinary admission records, kill switch,
   authorization and command confirmation. It cannot create or activate an
   admission record.
5. `unmounted_reference_only_conformance_packet` — prove prerequisites 1-4
   with authored-synthetic references, stale/wrong-environment/duplicate/
   self-verified/break-glass hostility and zero secret, database or product use.

The next dependency-satisfied tranche is only prerequisites 1-3 plus their
unmounted conformance packet. The product-adjacent admission input seam remains
a later separately frozen tranche.

### External operational facts

1. `one_current_environment_manifest_instance` — exactly one non-secret,
   current, unambiguous instance for an authorized environment and practice
   scope.
2. `live_runtime_role_binding_and_attestation` — the physical role exists in
   that exact environment and current independent evidence proves non-owner,
   `NOBYPASSRLS`, no product ownership and cross-tenant denial.
3. `three_current_opaque_secret_bindings` — distinct provider namespaces,
   opaque references, key IDs and versions exist for the database credential,
   application signing key and admission-snapshot verification key; no values
   enter repository evidence.
4. `three_current_rotation_custody_attestations` — each slot has immutable,
   fresh, independently verified policy/custody/rotation evidence bound to the
   same environment, generation, key and version.
5. `current_deny_only_break_glass_posture` — current independent evidence binds
   break glass exactly `inactive`; absence, `engaged_deny`, `retired` or stale
   evidence denies.
6. `operational_uniqueness_and_freshness_readback` — the authorized runtime
   observes one current manifest generation and no ambiguous or stale fallback.

Repository fixtures, documentation, model statements and authored-synthetic
rehearsals can never satisfy these nodes.

### Human-owned external decisions and actions

1. `select_target_environment_and_practice_scope` — identify the real target
   and environment class; the repository cannot choose a practice or promote a
   synthetic identifier.
2. `approve_secret_custody_and_operational_owners` — select the custody system,
   namespaces and accountable owners for all three slots.
3. `approve_rotation_policy_and_independent_verifiers` — select cadence,
   evidence-retention policy and who may independently attest role, custody,
   rotation and break-glass posture.
4. `authorize_live_role_secret_and_manifest_provisioning` — approve the lasting
   external creation/binding actions and their exact rollback/cleanup plan.
5. `confirm_ordinary_activation_separately` — after dimension 11 is honestly
   proved, an additional explicit human confirmation remains required before
   any ordinary admission record, flag/allowlist change, client cutover,
   deployment or production effect. Dimension 11 never supplies that consent.

These decisions need not be requested during repository-only prerequisites.
They become a genuine user-attention gate only immediately before a tranche
would require one of them or perform the corresponding lasting action.

## Deterministic deliverables

1. This plan and its narrow threat-model delta.
2. One closed decomposition contract and schema.
3. One standard-library read-only verifier that binds the ten exact inputs and
   emits one JSON dependency graph plus one concise Markdown report.
4. Focused tests for exact node sets/classes/dependencies, not-ready retention,
   external-fact non-substitutability and at least 128 hostile mutations.
5. Closeout, Sol acceptance, paired Yuri summary, non-PHI Pushover and one
   clockwork publication.

No reusable workflow layer, form framework, product adapter or operational
manifest is created.

## Workflow control and efficacy

The same invalid PowerShell grouping pattern recurred once while assembling a
Git summary after the preceding publication. It failed before reading or
changing state. This tranche will not add another Git-summary tool: the fresh
preflight receipt's existing `git_refs_snapshot` is the sole acceptance input
for branch, protected-ref, ancestry, tracked-clean and preserved-untracked
readings. Ad hoc composite PowerShell summaries are diagnostic only and cannot
establish acceptance.

Closeout must report substantive dependencies clarified, remaining human forks,
test/form reruns, runtime/provider actions, and whether the new evidence reduced
or merely renamed the gap.

## Parallelism assessment

- DeepSeek: `declined`, negative leverage. Its native Harness remains paused
  pending a separate boot proof; worker/provider use is forbidden and this
  authority-bound decomposition has no separable mechanical package.
- Gemini: `declined`, neutral leverage. Provider use is forbidden and exact
  accepted repository evidence plus a closed taxonomy decide the result.
- Native subagents: `declined`, negative leverage. Developer policy prohibits
  proactive delegation and the engineering/external/human boundary needs one
  serial acceptance owner.
- GPT Sol owns source binding, plan, contract, verifier, tests, acceptance,
  clockwork and Git.

Reassess after exact binding, on any source conflict, after deterministic
validation and at closeout.

## Acceptance and stop conditions

Pass requires all ten source hashes and all full Git bindings to pass; the
accepted result to remain 11/0/1 and not ready; every node to use the closed
taxonomy; every repository prerequisite to have no secret/database/product
capability; every external fact to reject synthetic or documentary
substitution; every human decision to remain unselected; and every hostile
mutation to reject.

Stop failed closed on source drift, an invented prerequisite, a hidden
activation step, any claim that architecture or synthetic evidence closes the
gap, secret/reference resolution, environment-variable or credential-store
access, database/product/provider activity, protected-ref drift or untracked
loss.

## Protected continuation boundary

No operational manifest instance, secret value or reference resolution,
credential-store/environment-variable read, live role/rotation/infrastructure
action, application import, route/API/client/configuration change, ordinary
enablement, admission record, generic-status `Arrived` change, grammar change,
waiting-area movement, product/patient/appointment/clinical/historical/
protected data, provider, production, deployment, release, Pages or protected-
ref movement is authorized.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
