# Provider-free unmounted default-off ordinary-practice canonical check-in admission-control kernel rehearsal plan

Date: 2026-08-19

Timestamp: 2026-08-19T03:47:11.9420134+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `249609a7f0c7131cff376aef315e1ff7742b44d7`

Accepted architecture source: `752b521c59f5b44bf46de0cf776a33ac74b8134d`

Target result:
`raisa_provider_free_unmounted_default_off_ordinary_practice_canonical_check_in_admission_control_kernel_rehearsal_pass`

Reasoning level: Extra High freezes the executable authority boundary. High is
sufficient for the bounded provider-free implementation, tests, deterministic
evidence, review packaging and closeout while this plan remains unchanged.

## Objective

Implement and rehearse one pure typed evaluator and transition kernel derived
from the accepted admission-control architecture. The canonical rehearsal has
zero active ordinary-practice records and cannot produce ordinary admission.
It must preserve the unchanged authored-synthetic decision, exact default
denial, global kill-switch dominance and disable-only rollback.

The kernel is unmounted. It has no route, OpenAPI, GraphQL, database,
environment, product import, provider, filesystem-write or clockwork-control
capability. It creates no admission record outside in-memory authored-
synthetic scenarios and changes no practice posture.

## Exact source boundary

The deterministic runner must verify these exact SHA-256 source bindings before
semantic execution:

| SHA-256 | Exact source |
|---|---|
| `744c175e18b335bd02cb954e501d6d3cba99744b052fc1e34f4b445050cc49f1` | `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-plan.md` |
| `ce520b9d8c90d46aba7cb5bad1c59585d508d9d1849051443c5a45e1a68371ab` | `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md` |
| `a52f8d108f5703b6bf19ca689fcf7911110b063f922cdac41f547b4fdbb43131` | `docs/security/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-threat-model-delta.md` |
| `505120968572362a7df8d67ab1d95947ed1cd467df0fbc520aca73a704755ba9` | `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json` |
| `1557801527dc8db675e1dc21bb0593b8ab94a253843703e53e1a67a77a2ea122` | `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.schema.json` |
| `5fdef13d61414002c7f5c2719062f9bbf81acabdab86cbb222d847f5d47cb712` | `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-closeout.md` |
| `da13d4c8c8ce12f37dbdab26a442edb2adb95c45b84fceebc0a3145a496e1bd7` | `orchestration/agent_inbox/codex/raisa-check-in-admission-control-architecture-sol-acceptance.md` |

Sources are decoded as strict UTF-8, CRLF is normalized to LF, remaining bare
CR bytes are rejected and the canonical-LF digest is compared before any
kernel claim is released. Reads after freeze are limited to these sources,
this plan, its threat delta, owned outputs and the already-read API Spine
documents. No repository-wide discovery is authorized.

## Frozen kernel profile

### Pure types

The implementation owns immutable typed values for:

- `AdmissionState`: `absent`, `prepared`, `active`, `suspended`, `withdrawn`;
- `KillSwitchState`: `clear`, `engaged`;
- `AdmissionLane`: `none`, `authored_synthetic`, `ordinary_practice`,
  `ambiguous`;
- one immutable snapshot, optional ordinary record, evaluation request and
  bounded decision;
- one control-command envelope and transition result; and
- one unknown-commit result requiring readback and forbidding blind retry.

All enums and record fields are closed. Unknown or extra contract fields,
unknown state/reason/operation values and malformed full-object IDs deny.

### Evaluator precedence

The pure evaluator executes exactly:

1. validate snapshot presence, schema, signature, full Git resolution,
   freshness, environment and one-current-record constraint;
2. deny unless the existing feature decision is exact `true`;
3. deny if the global kill switch is engaged;
4. compute synthetic and ordinary matches independently;
5. deny simultaneous or absent matches;
6. preserve the unchanged authored-synthetic admission when it is the only
   lane;
7. deny every ordinary lane in this rehearsal because
   `ordinary_activation_authority_granted` is frozen `false`; and
8. return only the six-field typed decision, with no command capability.

The canonical contract contains zero active ordinary records. An authored-
synthetic hostile input may describe an `active` record only to prove that the
current profile denies it; no scenario may release `admitted_ordinary`.

### Transition profile

The kernel represents the accepted future graph but executes only its
disable-biased current subset:

- `absent -> prepared` is accepted and remains non-admitting;
- `prepared -> active` is represented but denied as
  `activation_authority_closed`;
- `active -> suspended` is accepted and produces non-admitting state;
- withdrawal from `prepared`, `active` or `suspended` is accepted and terminal;
- `suspended -> active`, every resume edge and every transition out of
  `withdrawn` is denied;
- the global switch accepts only `clear -> engaged`; and
- no transition result in this rehearsal may produce `active`.

The active input cases are negative or disable-only authored-synthetic
scenarios. They are not records, persistence or enablement.

### Command envelope and unknown commit

The pure command-envelope validator requires all fourteen architecture command
requirements, including a current authenticated human, dedicated operator
role, server-owned practice/environment scope, correlation, request-digest-
bound idempotency, expected versions, closed reason, append-only audit,
freshness and a resolved lowercase `^[0-9a-f]{40}$` authority object.

It cannot dispatch a command. A simulated uncertain commit releases no
success, requires bounded readback by command/idempotency identity and forbids
automatic or blind retry. The seven-character abbreviation case is mandatory.

## Clockwork and DeepSeek gear boundary

The kernel contract and evidence use complete digests and full Git objects so
they can later be carried as a typed clock reading. The accepted shadow
Ariadne journal may emit a digest-bound WorkOrder, and the DeepSeek broker may
accept and answer only the exact parent tick before either advances.

This tranche does not implement that live gear mesh, call the broker, retire a
current procedure or confer product/activation authority. A later shadow
control-plane migration must separately prove causal-order, replay, stale-
parent and partial-publication behavior and must measure whether manual fields,
reruns and maintained fixtures actually fall.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- `orchestration_harness/check_in_admission_control.py`;
- one closed contract/schema plus derived evidence/report under
  `orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/`;
- one provider-free deterministic rehearsal runner;
- focused kernel, plan and hostile-mutation tests;
- required latch, receipt, error-register and independent-review artifacts;
  and
- closeout, Sol acceptance, Yuri summary, Continuity updater/test, baton and
  Compass/Continuity position if the tranche passes.

No `app/**`, `.env*`, migration, OpenAPI/GraphQL, product test, Diary/client,
deployment, Pages or clockwork/broker source is editable.

## Deterministic acceptance

Pass requires:

1. all seven source bindings match before semantic execution;
2. one closed JSON Schema validates one normative contract;
3. imports are limited to the standard library and no `app` module is imported;
4. canonical ordinary active-record count is exactly zero;
5. all malformed/missing/stale/multiply-current/wrong-environment snapshots
   deny before lane evaluation;
6. feature false denies, kill-switch engagement dominates both lanes, lane
   overlap denies and synthetic-only admission remains exact;
7. no ordinary input can release admission while activation authority is false;
8. the executable transition subset never produces `active`, has no resume,
   permits disable-only suspension/withdrawal and has no kill-switch clear;
9. every command requirement is fail-closed, a seven-character Git object is
   rejected and unknown commit releases no success/no retry;
10. at least 24 named evaluator/transition/command scenarios pass;
11. at least 192 independent hostile contract mutations fail closed with zero
    escapes;
12. focused tests, API Spine, latch, baton, register, compilation, Ruff and
    `git diff --check` pass; and
13. protected refs remain exact while `docs/branding/` and unrelated untracked
    files remain preserved.

One fresh Gemini 3.7 Flash/high exact-candidate read-only veto is mandatory
after deterministic admission.

## Parallelism assessment

- **DeepSeek:** declined. The kernel is mechanically bounded, but occupied
  native-Harness EMR4 execution remains behind its separate provider-free HMR
  boot proof; Claude Code is not a fallback.
- **Gemini:** reserved for one independent exact-candidate veto after all
  deterministic gates pass. It owns no implementation or acceptance.
- **Native subagents:** declined under current developer policy; the one
  normative contract, kernel and evidence reducer are tightly coupled.

Reassess after plan freeze, after deterministic admission, before verifier
acceptance, at closeout and before any product mount or occupied DeepSeek work.

## Recovery and claim boundary

One bounded mechanical correction may repair a type, schema, scenario,
deterministic reducer or test without changing semantics. Any proposal to
admit the ordinary lane, execute `prepared -> active`, clear the kill switch,
resume, restore active through rollback, omit a command requirement, mount a
route, edit product/API/database source, or treat the workflow clock as product
authority is conceptual and stops this tranche.

Passing proves only an unmounted provider-free pure kernel with zero active
ordinary records. It grants no ordinary-practice enablement, feature flag or
allowlist change, mounted product command, product/configuration/OpenAPI/
GraphQL/database/runtime-role change, generic-status `Arrived`, grammar/client
change, waiting-area movement, product/patient/clinical data, provider/network
call, production runtime, deployment, release, Pages, live clockwork adoption
or protected-ref movement. Preserve `docs/branding/`; stage explicit paths
only.
