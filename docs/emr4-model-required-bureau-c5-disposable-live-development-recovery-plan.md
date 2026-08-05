# EMR4 controlled recovery — C5 disposable live-development recovery plan

Date: 2026-08-05

Status: frozen recovery revision 2; live execution remains closed until the
repaired deterministic and fresh exact-HEAD independent gates pass

Source HEAD: `8bd1b315392378cfd7b0e67ec9cc66f5ad7e7a6f`

Parents:

- `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`
- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md`
- `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-closeout.md`
- `docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`
- `docs/ariadne-autonomous-continuation.md`

## 1. Exact result sought

C5 proves the smallest model-required live-development recovery loop without
touching EMR4 product runtime or any persistent data. A task-owned controller
starts one disposable authored-synthetic HTTP service on IPv4 loopback, proves
its healthy baseline, injects exactly one fault by terminating that exact child
process, and records closed technical observations. The approved provider model
must diagnose the stopped-process evidence, select the only eligible recovery
runbook and explain the proposed action. Deterministic code must then proofread
the candidate, revalidate current authority, mint one-use execution evidence,
start only the exact pinned service artifact, and release success only after a
distinct fresh loopback readback proves the expected new generation healthy.

The exact target is:

| Property | Frozen value |
|---|---|
| Environment | `c5_disposable_authored_synthetic` |
| Target kind | `task_owned_loopback_http_service` |
| Target id | `synthetic:c5-recovery-target` |
| Bind address | IPv4 `127.0.0.1` only |
| Port | OS-assigned ephemeral port, server-held and bound into every later object |
| Service artifact | one C5-authored Python module whose LF-byte SHA-256 is frozen before execution |
| Baseline | exact closed JSON health body, generation `1`, state `healthy` |
| Injected fault | controller terminates its exact child process, proves process exit, then atomically reacquires and retains the exact loopback address/port without address sharing |
| Recovery runbook | `start-c5-disposable-service.v1` |
| Rollback runbook | `stop-c5-disposable-service.v1` |
| Expected recovery | generation `2`, exact service-artifact hash, state `healthy` |

The target imports no `app` package, loads no repository or product settings,
uses no database, and accepts no request other than a fixed health read carrying
no input data. It is not an EMR4 service, deployment, container or production
approximation.

Target result:
`model_required_bureau_c5_disposable_live_development_recovery_pass`.

## 2. Exact occupied provider boundary

The provider/model choice follows Yuri's recorded ordinary development model
and locational preference while retaining the already accepted positive-
reasoning request contract:

| Property | Frozen value |
|---|---|
| Provider/model | Google Vertex AI `gemini-2.5-flash` |
| Project | `bernie-emr4-dev` |
| Provider identity | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` through the existing keyless impersonated ADC |
| Region | `australia-southeast1` |
| Endpoint | `australia-southeast1-aiplatform.googleapis.com` |
| Data | newly authored, patient-free C5 technical frames only |
| Thinking | explicit `thinkingBudget: 1024` |
| Output | `maxOutputTokens: 2048`, one candidate, temperature `0` |
| Calls | one primary; at most one evidence-selected correction; no call after admission |
| Cost ceiling | USD 0.50 total, reserved as USD 0.25 per possible call |
| Fallback | none |
| Provider tools/retrieval | none |

The provider identity is only the existing development Access AI transport. It
does not become the actuator identity and proves no future production technical-
control-plane identity separation. The local actuator receives a distinct,
task-local one-use capability and has no provider credential. No credential,
token, header, raw prompt, raw response, thought content or provider text is
retained.

The model receives one closed `SystemAnatomyFrameSet` containing only:

- the target kind and opaque target reference;
- frozen service-artifact and policy digests;
- the prior healthy observation and current post-fault observations;
- exact process-liveness and loopback-endpoint-ownership dispositions;
- timestamps, freshness and observation-source ids;
- the two signed-catalog runbook ids and their non-executable descriptions;
- the allowed risk tier and required approval class; and
- an explicit absence of patient, product, database, credential and ordinary-
  service context.

It emits one closed `RecoveryDiagnosisCandidate` with evidence-linked
hypothesis, missing evidence, impact, exact runbook selection, expected effect,
rollback id, uncertainty and operator explanation. It has no shell, SQL,
PowerShell, path, URL, port, PID, module, callable, environment-variable, cloud,
IAM or free-form execution field.

## 3. Model-required but deterministic-authority sequence

The live rehearsal is one monotone state machine:

1. verify the exact committed source, plan/policy/catalog/schema hashes, clean
   task worktree and accepted independent source veto;
2. run the read-only provider preflight for the exact project, identity, model,
   region, endpoint, cache posture, ledger and cost reservation;
3. create a private task-owned temporary directory outside product paths and
   materialise only the hash-bound service launch metadata and sanitized audit;
4. allocate one loopback ephemeral port, start generation `1` with the fixed
   launcher, and prove exact healthy baseline by process and HTTP observations;
5. inject the sole fault by terminating the controller-owned child handle;
6. prove the process exited and atomically reacquire the exact loopback address/
   port without `SO_REUSEADDR`; on Windows the controller must set
   `SO_EXCLUSIVEADDRUSE` before every bind. Only successful exact reacquisition
   and retained ownership admit the provider-visible
   `loopback_endpoint_disposition: exact_port_reacquired` observation or any
   provider call;
7. invoke the model once with the exact admitted frame set;
8. strictly parse and deterministically proofread the candidate against current
   evidence, catalog, risk, scope, freshness and authority. One correction is
   eligible only for a separately hashed, proofreader-issued closed ticket;
9. bind Yuri's recorded standing programme approval to this exact accepted
   plan hash, target, runbook, cost ceiling and one rehearsal. The deterministic
   authority service, not Sol or the model, materialises the approval record;
10. mint one opaque, expiring, one-use execution-evidence reference after a
    final current-state and approval revalidation;
11. the separate actuator consumes that evidence and invokes only the fixed
    launch callable for `start-c5-disposable-service.v1` with the exact Python
    executable, isolated-mode flag, frozen module, loopback host, bound port,
    target nonce and generation `2` supplied as distinct argument-list items;
12. perform a separately invoked fresh process observation and HTTP read. Only
    an exact generation `2`, artifact hash and `healthy` tuple may release
    `live_development_recovery_verified`;
13. if execution, audit or postcondition verification fails after launch,
    invoke only `stop-c5-disposable-service.v1`, freshly prove process absence
    and exact no-sharing port reacquisition, and distinguish verified rollback
    from inconclusive rollback; and
14. in every terminal outcome, consume ledgers, terminate any owned process,
    close handles, prove the port is no longer listening, remove only the exact
    task-created temporary directory, and prove no C5 runtime resource remains.

No model output, approval prose, process return code, actuator return or audit
row can declare recovery success. Only the distinct fresh readback can do so.

## 4. Human authority

The risk tier is exactly `reversible_scoped_service_recovery` and requires one
human `ordinary_confirmation`. Yuri's standing uninterrupted-development
decision is the human approval basis for this already planned programme gate;
it explicitly directs progress through planned gates without ceremonial
handback. C5 does not reinterpret that decision as generic actuator authority.

After the plan and source gates pass, deterministic code may issue one
`ExecutionApproval` that binds:

- approval basis `yuri_standing_programme_authority_2026-08-04`;
- this plan's exact committed hash and revision;
- the exact target, fault, runbook, rollback and evidence label;
- the exact provider/call/cost envelope;
- one rehearsal and one expiry; and
- `scope_expansion: false`.

Any change in target class, process artifact, command, provider, model, region,
identity, data, cost, call count, fault, risk, rollback or claim needs a new plan
and cannot inherit this approval. A human-only credential restoration or console
action remains a genuine attention gate.

## 5. Controller and actuator capability boundary

The controller may create and remove only its validated task temporary
directory, allocate one loopback port, hold one exact child-process handle,
perform fixed health reads, and append closed audit records. The actuator is a
separate object that receives no model text, provider credential, filesystem
discovery, product setting or ambient command line.

The only process invocation is an argument array constructed from constants and
server-held values:

- current repository virtual-environment Python executable resolved and hashed
  during preflight;
- `-I` isolated mode;
- the exact frozen C5 service module path;
- `--host 127.0.0.1`;
- the server-held ephemeral port;
- the opaque target nonce; and
- exact generation `1` or `2` according to the controller state machine.

No shell, PowerShell, `cmd`, command string, interpolation, `eval`, `exec`,
dynamic import, user-selectable path, URL, executable or environment overlay is
permitted. The child receives a minimal explicit environment and cannot inherit
cloud credentials. The process is non-admin, loopback-only and task-owned.

The controller must fail closed if it cannot prove PID/handle ownership,
artifact hash, bind address, port, generation, nonce, process transition or
cleanup. It never discovers, terminates, restarts or probes another process.

## 6. Closed schemas and evidence artifacts

Implementation must add closed Draft 2020-12 schemas and canonical examples
under
`orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/`
for:

- `system-anatomy-frame-set.v2`;
- `recovery-diagnosis-candidate.v1`;
- `proofreader-disposition.v1`;
- `execution-approval.v2`;
- `execution-evidence.v2`;
- `live-recovery-command-envelope.v1`;
- `live-recovery-attempt-receipt.v1`;
- `cleanup-receipt.v1`; and
- a source-bound `c5-policy.v2`, source-bound `live-preexecution-receipt.v2`
  and immutable two-entry runbook catalog.

Every object uses `additionalProperties: false`, canonical scalar bounds,
opaque identifiers, exact timestamps, explicit schema/policy versions and
digests. Duplicate JSON keys, non-canonical encodings, attacker-controlled
reason strings and executable-shaped keys or values reject before provider,
authority or actuator admission.

Durable evidence retains only allowlisted hashes, enum dispositions, bounded
counts/times, model/version, finish reason, safe token counts, HTTP status,
candidate shape, authority ids, target-generation ids, process/health
dispositions, readback hashes, rollback result and cleanup proof. It excludes
raw provider content, thoughts, credentials, child tokens and unrestricted
stdout/stderr.

## 7. Proofreader and correction policy

The deterministic proofreader must establish all of the following:

- exact input frame-set digest and current freshness;
- every hypothesis and selected runbook grounded in cited observation ids;
- exact stopped-process diagnosis and no unsupported alternative cause;
- exact target, environment, risk tier, runbook, rollback and empty parameters;
- no executable text or identifier, scope expansion, product reference,
  credential request, new observation, success claim or hidden authority;
- explanation accurately distinguishes inference, current evidence, proposed
  action, required authority, rollback and unverified outcome; and
- the candidate does not claim that an Australian endpoint proves physical or
  sovereign processing.

The first schema-valid but proofreader-invalid candidate may receive one closed
correction ticket containing only field paths, reason codes and the same
frame-set digest. It cannot reveal preferred prose or broaden the evidence. A
provider admission failure, transport failure, correction failure, cost/call
exhaustion, stale frame or changed target ends model admission and triggers
cleanup with no actuator action. No unchanged request is retried and no call
follows admission.

## 8. Replay, atomicity and failure semantics

One shared store coordinates plan revision, observations, provider ledger,
approval, execution evidence, idempotency, attempt sequence and cleanup state.
The execution critical section revalidates authority and target state before
consuming evidence. Same-key exact replay returns the stored terminal receipt;
same-key changed input conflicts; different-key evidence reuse rejects; two
runtime objects sharing the store can produce at most one launch attempt.

Provider ledger consumption and admitted attempt audit are monotone. A failed
effect can roll back process state but cannot reopen provider or execution
evidence. An unverified rollback is terminal, is labelled separately and cannot
be promoted to recovery success. Cleanup follows every terminal state and may
be retried idempotently only for the exact owned resources.

## 9. Deterministic-first and independent gates

Before any target process or candidate-runtime provider call:

1. closed schemas, examples, policy and runbook catalog validate and reproduce
   exact LF-byte hashes;
2. provider-free tests prove frame construction, parser/proofreader behavior,
   approval binding, evidence issuance, idempotency, shared-store concurrency,
   fault injection, exact no-sharing port reacquisition, launch allowlisting,
   readback, rollback and cleanup using
   fakes that start no process and open no socket;
3. source inspection proves no product import, database client, cloud-control
   client, generic shell/command runner, deployment route or ambient credential
   access;
4. API Spine checks record the command boundary as local and `not_mounted`;
   GraphQL remains read-only and `app.main` route inventory is unchanged;
5. focused and inherited Gate-zero/C3/C4/Ariadne tests, Ruff, compilation,
   Bandit, JSON validation and `git diff --check` pass;
6. the complete plan candidate is committed to the existing non-protected task
   branch; and
7. a fresh Gemini 3.6 Flash/high Antigravity project reviews the exact clean
   HEAD from a fresh bound worktree, emits one terminal decision and changes no
   file.

Only one `pass` opens a distinct pre-execution receipt. A verifier finding is
handled under the agent-error and recovery-lease rules. Deterministic failure
means zero reviewer or candidate-runtime provider call as applicable.

## 10. Live rehearsal acceptance matrix

C5 passes only if all of these hold in one source-bound run:

- the initial process is exact, loopback-only, task-owned and freshly healthy;
- the sole injected termination is exact and the post-fault observations prove
  both process absence and retained exact-port reacquisition without address
  sharing;
- provider preflight, reservation and accounting bind the exact frozen envelope;
- one admitted model candidate cites only admitted technical evidence, selects
  only `start-c5-disposable-service.v1` and contains no executable material;
- deterministic proofreading, current authority, approval and one-use evidence
  all pass before the actuator receives anything;
- the actuator launches only the exact argument vector and pinned artifact;
- fresh readback proves generation `2` and exact healthy/artifact/target tuple;
- replay, changed-body, stale authority, target drift, unknown runbook, altered
  port/artifact/executable, concurrent attempt and injected launch/readback/
  audit/rollback failures cannot produce false success;
- cleanup proves no owned process, listener, handle, temporary directory,
  provider reservation or reusable execution evidence remains;
- candidate-runtime side effects are exactly the bounded provider call(s),
  task-owned loopback process lifecycle and task-directory lifecycle recorded by
  the plan; every other side-effect counter is zero; and
- the final evidence is reproducible, the widened suite passes, a fresh
  independent implementation veto passes and Sol accepts the exact exercised
  source.

Evidence label:
`occupied_authored_synthetic_disposable_live_development_recovery`.

This label proves neither Australian physical/sovereign model processing nor
product recovery, an ordinary development service, database recovery,
deployment, production, release or autonomous remediation.

## 11. Ownership and lane allocation

After the plan itself passes deterministic and fresh independent architecture/
security review:

- Sol owns the frozen plan, authority, provider envelope, live sequence,
  evidence interpretation, recovery, acceptance and Git integration;
- one DeepSeek V4 Flash/high worker through Claude Code bare may implement the
  stable schemas, provider-free controller/actuator modules, fakes and focused
  tests in an isolated descendant worktree;
- a second bounded worker lane may independently reproduce process-ownership,
  cleanup and adversarial argument-vector tests if it provides genuine leverage
  and owns disjoint artifacts;
- Gemini 3.6 Flash/high performs fresh read-only vetoes only after deterministic
  gates; and
- no worker or model starts the live target, calls the candidate provider,
  approves execution, accepts its own work, integrates or moves a protected ref.

The live sequence remains serial because its target, ledger, port and process
state are shared mutable resources.

## 12. Permanent exclusions and stop conditions

C5 grants no patient, clinical, participant, historical Diary, product-derived,
protected or production data; product API/database/runtime; real practice
database; ordinary service; container, VM or cloud target; provider tool or
retrieval; generic network; shell/SQL/PowerShell; cloud/IAM or credential
mutation; migration/update; deployment; production; release; Pages; protected
evidence; or protected-ref authority.

The accepted Practice Context Fabric remains a separate staged direction. C5
does not implement `ContextNeed`, `ContextFrameSet`, temporal retention,
cross-Bureau retrieval or any Context Fabric runtime.

Ordinary plan refinement, implementation defects, verifier findings and bounded
recovery do not require a user pause. Stop before live action if the exact plan
or deterministic/independent gates fail. Return to Yuri only if a human-only
credential restoration or console action is indispensable, bounded recovery is
exhausted, evidence conflicts change acceptance meaning, or completion would
require a target, provider, identity, region, data, cost, call, authority,
effect or claim outside this exact plan.
