# Provider-free read-only delete-confirm route convergence and Ariadne Git-object resolution plan

Date: 2026-08-16

Timestamp: 2026-08-16T15:21:37.9387937+10:00 (Australia/Brisbane)

Source HEAD: `c05fb57f17bf8b55fb02b34bd48b0ce18530ec86`

Status: `frozen_for_read_only_review_and_repository_only_control`

Reasoning level: material command-authority convergence and workflow hard-gate repair / Extra High

Risk classification: Tier 2 (`authority_or_security_contract`, `executable_tool`)

## Purpose

Close two already-authorised, tightly bounded questions without opening product
runtime authority:

1. decide whether the currently mounted delete-confirm handler is ready to
   converge onto the accepted database-owned authority and transaction seam;
   and
2. replace the recurrent manual Git object-ID completion failure with a
   read-only Ariadne continuation check that resolves the structured latch
   `source_head` as an exact commit before a receipt can pass.

The product lane is exact-file, provider-free and read-only. The Ariadne lane is
repository-only and cannot move a ref, modify a worktree or infer acceptance.
Combining them avoids two complete closeout cycles while keeping their evidence
and claim boundaries distinct.

## Admission

The fresh five-source runtime state and passing receipt are:

- `orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-preplanning-runtime-state.json`; and
- `orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-preplanning-receipt.json`.

They name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`, and carry all three lane dispositions.

The pre-edit canonical fast profile passed at exact source
`c05fb57f17bf8b55fb02b34bd48b0ce18530ec86`: Ruff, maintained-source
compilation, 196 focused tests, Diary JavaScript syntax and whitespace. Its
typed record is
`orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/baseline-fast-profile.json`.

At admission the tracked tree was clean before the volatile latch/receipt
transition. Local and origin task were exact `c05fb57f17bf8b55fb02b34bd48b0ce18530ec86`.
Local/origin `master` and `handoff/current` were exact protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Six hundred thirty-five untracked
paths, including `docs/branding/`, were preserved.

## API Spine classification

`confirmAppointmentDeleteProposal` is the sole eligible dedicated delete-confirm
REST command identity. GraphQL remains read-only. The existing
`POST /appointments/proposals/delete-confirm` is a mounted alias candidate for
canonical `POST /appointments/proposals/delete/confirm`; literal mounting is
not physical-seam admission. Raw compatibility `DELETE /appointments/{id}`
remains a distinct legacy ingress and receives no dedicated-kernel authority by
analogy. Events remain non-authoritative acceleration hints.

## Exact read-only product bindings

Only these exact non-protected sources may be content-read or searched after
this plan is frozen:

| SHA-256 | Path | Purpose |
|---|---|---|
| `0e0f42290688943bc9dd7d5711826acf10430133be0b309eae94bad15da46ca2` | `app/main.py` | router mounting |
| `f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624` | `app/routers/appointments.py` | current delete/status route and legacy effect |
| `70574af69c73664a9f8ebda15b749bc5b5b25fe291a55be1f080096146bf47bc` | `app/dependencies.py` | authenticated request and command-session ingress |
| `c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf` | `app/schemas/appointments.py` | public confirmation shapes |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` | appointment/audit/private-receipt fields |
| `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` | `app/models/tenancy.py` | authority generation and exact grants |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | `app/services/appointment_delete_physical.py` | accepted physical seam and six-field receipt |
| `a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55` | `app/services/appointment_status_product_adapter.py` | accepted application-owned convergence analogue |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` | canonical operation, path and public envelope |
| `fbfe46f27d733e017d4f21734ad653a72e4fdeb27fd64820604b5bb199a41774` | `orchestration/api_spine_appointment_idempotency_delete_confirm_preflight.md` | legacy route contract history |
| `4768d438c3031b4a726bcdbc8236330a05db51b3c3c3c504a06da40453a1a2c6` | `orchestration/api_spine_appointment_idempotency_delete_confirm_route_tests.md` | existing semantic obligations |
| `90d42d80d06d1c173fde25b7da153173b195cbc118e672cac6746493ef0aa507` | `docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md` | accepted serial physical behavior |
| `41603381260b72a61f5976305f132846897541b4ca31b9884bb10eebfa4f178e` | `orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-sol-acceptance.md` | accepted claim boundary |
| `5f6c602f68594996635648db55f5e473e303593b2df8e8bb26c3bf7785c71fa9` | `docs/raisa-provider-free-read-only-status-confirm-route-mounting-admission-review.md` | review-dimension analogue |
| `c75c7c707ab0023cf8d4bf4a90dfe638c36179fbd1a87b81397cda51fea5e10f` | `docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-closeout.md` | coupled-adapter precedent |
| `27f7f033b20db36e06bad285bd0318f5f41e7c5d849ba786e6f3aae1363b3db5` | `docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md` | bounded route-convergence precedent |
| `f6e75c7428dc5c1327166bc0e900c2804f3201ea1b32cd5577d1f8134b16c2a8` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-plan.md` | deferred response-transition boundary |
| `584405db5d49a56e18061f80fcd1faa72c278cf0d4975cf95febc86783609019` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-closeout.md` | minimized-receipt decision |

No product source in this table may change. Every text binding uses strict
UTF-8 with CRLF canonicalized to LF and rejects any bare carriage return, so
equal committed content is stable across clean worktrees. The deterministic
reviewer may read only these files and must not import `app`, open
configuration, call a route or connect to a database.

## Frozen route-convergence dimensions

Preserve this order and classify each as `satisfied`, `partial_gap` or
`blocking_gap`:

1. literal mounted handler and application inclusion;
2. canonical operation identity, canonical path and compatibility alias;
3. physical transaction-seam invocation versus route-local legacy ownership;
4. command-owned session, current authority generation and exact capability ingress;
5. locked target, proposal-version, signed-evidence, freshness and waiting-area re-admission;
6. atomic cancellation, attributable delete audit and private receipt completion;
7. minimized six-field stored receipt versus the full public confirmation envelope;
8. exact stored-byte delivery and closed physical outcome-to-HTTP mapping;
9. raw compatibility DELETE isolation; and
10. accepted serial PostgreSQL authority/transaction foundation.

Any blocking gap yields
`unmounted_adapter_and_response_transition_required`. No blockers with partials
yields `ready_for_bounded_unmounted_route_candidate`; only all satisfied yields
`ready_for_bounded_route_convergence_candidate`. The review cannot recommend
mounting around an absent adapter or replay contract.

## Ariadne Git-object resolution contract

The CLI receipt builder must use one exact repository root and the configured
continuation policy to validate the already schema-checked
`active_operation.source_head`:

1. require exactly forty lowercase hexadecimal characters;
2. run only fixed-argv, `shell=False`, bounded Git commands;
3. require `git rev-parse --verify <object>^{commit}` to return exactly the
   supplied full object ID;
4. require that commit to be an ancestor of the repository's machine-observed
   full `HEAD`;
5. emit the supplied source, resolved commit and observed HEAD as typed receipt
   evidence; and
6. change a would-be passing receipt to `revision_required`, forbid dispatch and
   append a closed reason when Git is absent, times out, returns malformed
   output, resolves a non-commit/different object or finds a non-ancestor.

The core evidence validator remains pure. The repository-aware CLI wrapper owns
this read-only check. It may not accept a ref, path, revision expression or
command from runtime state; only the already validated full object ID is passed
as one literal argv element. It never writes, fetches, checks out, stages,
commits or moves a ref.

## Exact owned implementation paths

Product review artifacts:

- `orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/route-convergence-contract.json` and schema;
- minimized evidence document and schema in the same directory;
- `scripts/raisa_provider_free_read_only_delete_confirm_route_convergence_review.py`;
- `tests/test_raisa_provider_free_read_only_delete_confirm_route_convergence_review.py`;
- this plan, its threat delta and the resulting read-only report.

Ariadne hard-gate artifacts:

- `orchestration_harness/git_object_resolution.py`;
- `orchestration/harness_settings/orchestrator_requirements.yaml`;
- `scripts/ariadne_orchestrator_preflight.py`;
- `tests/test_ariadne_git_object_resolution.py`; and
- the narrow assertions required in `tests/test_ariadne_orchestrator_preflight.py`
  and its existing authored fixture.

Sol alone owns acceptance, latch/receipts, register, Continuity/Compass, baton,
closeout and Yuri summary. No worker, reviewer or renderer receives those
authorities.

## Verification and acceptance

Pass only if:

1. all five rehydration sources and every frozen product/harness input hash pass;
2. all ten route dimensions are reproduced from exact literal evidence and the
   verdict follows the closed classification rule;
3. the accepted database behavior is consumed without rerunning Docker,
   PostgreSQL, SQL or a route;
4. every remaining blocker names one narrowest unmounted prerequisite and the
   response-envelope contradiction is neither hidden nor mislabelled as
   durability;
5. the reviewer imports no application or database runtime and all named route
   threats have hostile-test coverage;
6. every configured continuation event fails closed for an unresolvable,
   different, non-commit or non-ancestor structured source object;
7. exact valid ancestors produce machine-observed full IDs, the resolver runs
   no shell and performs no write-capable Git operation;
8. focused review/harness tests, Ruff, compilation, policy validation,
   API Spine/current-baton/latch gates, one post-freeze canonical profile and
   whitespace pass;
9. exactly one fresh Gemini 3.7 Flash/high final veto passes on the unchanged
   exact candidate after deterministic admission; and
10. protected refs, `docs/branding/` and every unrelated untracked path remain unchanged.

## Parallelism efficacy

- DeepSeek V4 Flash/high is declined. The route output is an architectural
  admission decision and the Git repair is small and tightly coupled to its
  hard-gate semantics; a worker packet and recovery cycle have negative leverage.
- Gemini 3.7 Flash/high is reserved for exactly one final Tier-2 veto after all
  deterministic gates pass. No intermediate or stacked external review is admitted.
- Native subagents are declined under the current developer constraint and
  because there is no state-independent package whose leverage exceeds shared
  authority-packet coordination.

Reassess only on a material recovery, a previously unseen blocker, pre-verifier
acceptance or closeout.

## Recovery and next direction

One mechanical resolver or deterministic-review defect may receive one bounded
Sol repair inside the owned paths. A contradiction in frozen product sources or
a need to change user-visible delete semantics stops without editing product
source. Git unavailability or ambiguity fails closed; there is no fallback to
manual object completion.

If the expected blocking verdict passes, the next safe product candidate is one
provider-free unmounted delete-confirm response-compatibility and product-adapter
architecture tranche. It must reconcile the minimized six-field private receipt
with byte-exact replay of the full public confirmation envelope, bind
server-owned session/generation/capability and locked proposal re-admission, and
preserve raw DELETE isolation before any route edit or execution is considered.

## Forbidden surfaces

No route edit, mount or call; product database/source access; Docker, migration
or SQL execution; capability provisioning; product command; UI; patient,
clinical, product-derived, historical-diary or protected data; provider, ADC,
credentials, IAM, browser or external network; deployment, production, release,
Pages or protected-ref movement. Preserve `docs/branding/` and every unrelated
untracked file. Stage explicit paths only.
