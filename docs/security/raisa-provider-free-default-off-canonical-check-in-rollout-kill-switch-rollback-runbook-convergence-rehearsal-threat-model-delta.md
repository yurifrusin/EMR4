# Threat-model delta — default-off canonical check-in rollout runbook convergence

Date: 2026-08-22

Timestamp: 2026-08-22T23:14:54.9671906+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation:
`raisa-provider-free-default-off-canonical-check-in-rollout-kill-switch-rollback-runbook-convergence-rehearsal`

## Security boundary

This tranche adds one repository-static JSON manifest. It adds no parser to the
product, route, actor, credential, secret, network, database, command, runtime
or deployment surface. The existing closed-form validator is the sole byte and
semantic authority.

## Protected invariants

1. Ordinary practice remains disabled and activation authority remains false.
2. The kill switch defaults to engaged and only a clear-to-engaged transition
   is represented.
3. Unknown commit state never releases success or permits blind retry; future
   recovery still requires source-truth readback.
4. Audit fields are non-PHI, prohibit secret values and require full Git object
   IDs.
5. The manifest is declarative policy evidence, not command, grant, activation
   or operational rollback evidence.
6. Existing REST/OpenAPI confirmation, server-side authority, audit and typed
   receipt boundaries remain unchanged; GraphQL remains read-only.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Semantic drift in a human-edited manifest | Exact object equality and frozen SHA-256/byte-count validation reject any field change. |
| Duplicate JSON keys hide an authority expansion | The existing duplicate-pair hook rejects duplicates before admission. |
| Non-canonical encoding or newline ambiguity | UTF-8, LF-only, bounded-size parsing plus exact canonical bytes are required. |
| Manifest mistaken for executable or activation authority | Plan, schema version, `prepared_not_authorized` status and all admission/effect booleans preserve a declarative-only claim. |
| Unknown commit treated as success or retried blindly | `deny_success_no_blind_retry`, source-truth readback and zero post-rollback ordinary release remain exact. |
| PHI, credentials or secret material enter the runbook | Non-PHI-only audit, explicit secret-value denial and static public identifiers only are admitted. |
| Short Git abbreviation weakens traceability | `full_git_object_id_required` remains true; deterministic tests bind the exact field. |
| Completion is overstated as operational rollback proof | Acceptance and closeout may claim only byte-exact manifest presence, never executed rollback/readback. |
| Scope expands into product or protected surfaces | Exact-path ownership, explicit-path staging, protected-ref checks and preserved-untracked-file checks fail closed. |

## Residual risk

The manifest does not itself enforce runtime behavior. Future product mounting,
ordinary activation, secret custody, alert transport, rollback execution and
unknown-commit readback still require separately authorised typed runtime and
occupied evidence. This tranche deliberately leaves those gates closed.

No protected evidence, PHI, provider, database, Docker, live route, deployment,
release, Pages or protected ref is accessed or changed.
