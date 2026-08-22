# Provider-free read-only post-check-in admission-control programme orientation

Date: 2026-08-22

Timestamp: 2026-08-22T22:38:25.4278425+10:00 (Australia/Brisbane)

Status: `deterministic_candidate`

Evidence label: `provider_free_repository_static_read_only`

## Conclusion

The programme is moving forward, but the Harness recovery sequence did become
an expanding control loop. That loop is now closed. The accepted clockwork
prevented an actual circular successor during the preceding closeout, and this
orientation selects one artifact that is both genuinely absent and already
fully specified.

The narrowest next tranche is:

`raisa-provider-free-default-off-canonical-check-in-rollout-kill-switch-rollback-runbook-convergence-rehearsal`

It will materialize and validate exactly one default-off declarative API-Spine
runbook at
`docs/api-spine/manifests/canonical-check-in-rollout-kill-switch-rollback-runbook.json`.
The existing closed-form validator already defines the required bytes and
fail-closed meaning; the canonical manifest itself is absent. The operation ID
is absent from the accepted Continuity graph.

This is a real completion step, not another diagnosis. It closes the
product-facing artifact half of the rollout/runbook gap while enabling no
practice and changing no runtime.

## Reconciled matrix

| Dimension | Current classification | Exact reading |
|---|---|---|
| Route and API command identity | `satisfied_accepted` | Default-off A5.1 delegates to the canonical adapter at `c82c3a741053a9c8da260aa62e1a968af22bb54e`; OpenAPI retains `proposeAppointmentCheckIn` and `confirmAppointmentCheckInProposal`. |
| Ordinary admission control | `satisfied_contract_only` | Architecture at `752b521c59f5b44bf46de0cf776a33ac74b8134d` and unmounted kernel at `4204ec6348abb0f92b1a30314699d4a469fa860a` distinguish ordinary from authored-synthetic admission, but keep activation false and active ordinary records at zero. |
| Rollout/kill-switch/rollback runbook | `satisfied_contract_only` | The exact default-off closed form exists in `orchestration_harness/check_in_rollout_runbook.py`; its named API-Spine target is absent. |
| Non-PHI observability and alerting | `satisfied_contract_only` | Five low-cardinality metric families and six non-actuating critical alerts are frozen by the accepted architecture, but no operational telemetry is claimed. |
| Environment manifest and secret posture | `operational_evidence_gap` | Architecture at `a1f309a6d52d01f9866432f7e9abb8095788d023` has zero manifests, secret references or operational evidence artifacts. No live secret custody or rotation is proved. |
| Tenant isolation and runtime role | `satisfied_accepted` | Disposable PostgreSQL attestation at `6a2832575e9b4df5c40a13984db7281e79814a94` proved non-owner, `NOBYPASSRLS` and cross-tenant denial with exact cleanup. |
| Atomic rollback and unknown commit | `operational_evidence_gap` | Explicit rollback passed, but the unknown-response classifier never reached accepted readback. Relay-free redesign at `a00da58c630202085a33fe8e9afdb8ace4b2a028` did not prove a transaction, and attempt 005 at `03b94136c9c6cd82d5a8098705f263ba34a20de4` stopped before setup/readback. |
| Native Harness worker allocation | `closed_later_gate` | The final one-request terminal at `b9d9a32d111a23bff259a0ff9d5168cfdc305508` produced no candidate. The native Harness is unavailable; Claude Code is not a fallback. |
| Ordinary-practice activation | `closed_later_gate` | Feature default remains false, the synthetic allowlist default remains empty, activation authority is false and active ordinary records remain zero. |
| Atomic two-client cutover and waiting-area separation | `closed_later_gate` | Client cutover remains a later atomic gate; waiting-area movement remains semantically separate from dedicated check-in. |

Counts: two `satisfied_accepted`, three `satisfied_contract_only`, two
`operational_evidence_gap` and three `closed_later_gate`.

## Why this successor is narrowest

The alternative paths are wider or still blocked:

- another rollback/unknown-response execution would re-enter the exhausted
  database recovery chain without a new accepted cause;
- live environment/secret evidence requires external operational state and is
  outside this provider-free scope;
- mounting the admission kernel or control commands is closer to activation
  and depends on a stable runbook and later operational evidence;
- operational observability implementation is larger than committing its
  already-required declarative rollback triggers; and
- client cutover is explicitly a later atomic product gate.

The runbook manifest has a unique advantage: its target path, schema, complete
content, default-off posture and validator already exist, yet the artifact is
absent. Completion is binary and mechanically testable.

## API Steward reading

Boundary classification: declarative API-Spine manifest for a REST/OpenAPI
command family. The manifest is not a command, grant, executable policy engine,
GraphQL mutation or async authority surface.

Accepted pattern preserved:

- REST/OpenAPI owns the check-in proposal and confirmed mutation;
- server-side code retains actor, practice, confirmation, idempotency,
  freshness/revalidation, audit and typed-receipt enforcement;
- GraphQL remains read-only;
- events remain observational; and
- the proposed manifest declares a default-off rollout/disable procedure only.

No P0-P2 API Spine defect is introduced by this read-only orientation. The
material finding is the absent canonical runbook artifact. The unresolved
operational findings are unknown-commit readback, live secret posture and
unmounted monitoring; none is converted into a pass.

## Parallelism result

- DeepSeek: declined. The native Harness is closed and the orientation contains
  no external-worker implementation package.
- Gemini: declined after deterministic matrix freeze. Exact accepted-node
  membership, successor non-membership and target-file absence leave no
  material alternative requiring model judgment.
- Native subagents: declined under developer policy and serial graph custody.
- GPT Sol: performed the source reconciliation, deterministic evidence and
  successor selection.

## Claim and protected boundary

This orientation proves only the current repository-static map and the
non-circular successor choice. It does not make check-in ready for ordinary
practice and does not prove unknown-commit recovery, live secret custody,
operational monitoring, activation, client cutover or production suitability.

No application, configuration, API/OpenAPI/GraphQL, route, current manifest,
client, feature flag, allowlist, generic-status `Arrived`, waiting-area,
product/patient/appointment/clinical/historical/protected data, provider,
database/Docker, production runtime, deployment, release, Pages or protected ref
changed. `docs/branding/` and every unrelated untracked file remain preserved.
