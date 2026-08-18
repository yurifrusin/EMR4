# Provider-free default-off ordinary-practice canonical check-in admission-control architecture plan

Date: 2026-08-19

Timestamp: 2026-08-19T02:45:50.1302422+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `062f5fb12eb82eab6ec570abea56ad1bd9a7b304`

Accepted readiness source: `27101faa86b5aa3850e90bc4ded8600e5f8d7dc9`

Accepted route source: `c82c3a741053a9c8da260aa62e1a968af22bb54e`

Target result:
`raisa_provider_free_default_off_ordinary_practice_canonical_check_in_admission_control_architecture_pass`

Reasoning level: Extra High for freezing a future practice-scoped admission
capability and its emergency precedence. High is sufficient for the bounded
provider-free contract, deterministic validator, hostile-mutation proof and
closeout while this plan remains unchanged.

## Objective

Close only the three design gaps in the accepted 6/3/3 readiness review:

1. specify an explicit ordinary-practice admission control that cannot be
   inferred from or represented by the authored-synthetic allowlist;
2. specify rollout, dominant kill-switch, suspension and disable-only rollback
   operations; and
3. specify low-cardinality, non-PHI A5.1 metrics, alerts and reason codes.

The result is a source-bound architecture and deterministic evidence package.
It does not edit application code, configuration, environment examples,
database schema, OpenAPI, GraphQL, routes or product tests. It creates no
admission record, enables no practice and calls no product or provider surface.

## Exact source boundary

All hashes are SHA-256 over the current strict UTF-8 source bytes, which are
canonical LF at the frozen source HEAD. The validator must decode strict UTF-8,
normalize CRLF to LF, reject remaining bare CR bytes and compare SHA-256 over
canonical LF bytes before accepting the architecture.

| SHA-256 | Exact source |
|---|---|
| `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` | `app/config.py` |
| `8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08` | `app/routers/appointments.py` |
| `ef6abdfef1b99737c527790be007ab07296bbc0422197858a5ae561012230570` | `app/services/appointment_check_in_product_adapter.py` |
| `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |
| `3bffad89188d3f700e769d4d39301b8f440d763b21d0e4b7c64fe67354ed78ba` | `docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md` |
| `81a4a92e4f1f7e539282a646d59474420309f2f93785fe2c007e413ef26c297f` | `orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review/admission-readiness-review-report.md` |
| `335c82727662a408305e18954bc2927d724e8e312182af5b1ca0d4b32d32d3e8` | `docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-closeout.md` |
| `584756f6723e0e699c4dd9ffc7d504b3d7b5cea8dd1f735c63e3e13aef31af53` | `orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md` |
| `e577f20e1b164be1abce990f915bd792eb4e158051f48c5c1d629825cd93a78f` | `docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-closeout.md` |

After this freeze, implementation reads are limited to those sources, this
plan, its architecture document and its threat-model delta. No repository-wide
discovery, application import, route call, database, SQL, Docker, browser,
provider or network operation is permitted.

## Frozen admission model

### Separate lanes

The future evaluator receives two independent inputs:

- `authored_synthetic_admitted` is the unchanged current result of the exact
  A5.1 feature flag plus exact authored-synthetic practice allowlist; and
- `ordinary_admission_record` is a separate server-owned, practice-scoped,
  operation-family-scoped, environment-scoped, versioned control-plane record.

An ordinary admission record can never be synthesized from membership in the
synthetic allowlist, a synthetic test receipt, a feature flag, a caller claim,
an inbound header, a GraphQL mutation, a committed event or a model result.
Both lanes present simultaneously are an invalid configuration and deny.

### Ordinary state machine

Absence is equivalent to `disabled`. The only represented states are:

| State | Admits ordinary requests? | Meaning |
|---|---:|---|
| `prepared` | no | Versioned candidate with complete proposed controls but no runtime authority. |
| `active` | only after every shared and ordinary prerequisite passes | A future explicitly authorised activation has admitted exactly one practice and command family. No such record exists in this tranche. |
| `suspended` | no | Practice-scoped emergency stop; cannot resume in place. |
| `withdrawn` | no | Terminal disable-only rollback result. |

Allowed transitions are `absent -> prepared`, `prepared -> active`,
`prepared -> withdrawn`, `active -> suspended`, `active -> withdrawn`, and
`suspended -> withdrawn`. Reactivation requires a new record, new version, new
evidence set and a separately authorised activation; there is no `resume`
transition and rollback can never restore an active version.

The architecture describes `prepared -> active` so that it can be proved
closed. This tranche grants no authority to implement or execute that
transition.

### Dominant decision order

One future immutable admission snapshot is evaluated without fallback in this
order:

1. reject an absent, malformed, unsigned, unresolved, expired, stale,
   multiply-current or wrong-environment snapshot;
2. deny when the existing A5.1 global feature flag is not exactly enabled;
3. deny when the global monotonic kill switch is engaged;
4. compute the synthetic and ordinary lane matches independently and deny if
   both match;
5. preserve the unchanged synthetic decision when only the synthetic lane
   matches;
6. for the ordinary lane, require one exact `active` record binding the server
   practice, environment, operation family, generation and every operational-
   evidence digest;
7. deny on any missing, invalid, stale or unverified operational gate; and
8. return only a typed admission decision. It cannot execute check-in, mutate a
   patient record, weaken route authentication or manufacture confirmation
   evidence.

The kill switch dominates both lanes. Unknown states, fields, versions, reason
codes and transitions deny. The evaluator has no fail-open mode and no cached
last-known-good fallback after freshness expiry.

## Frozen control-plane operations

State changes belong to future REST/OpenAPI command endpoints, not GraphQL.
This tranche records candidate operation identities only and does not add them
to the live OpenAPI manifest:

| Candidate operation id | Effect |
|---|---|
| `prepareAppointmentCheckInAdmission` | Create one non-admitting `prepared` record. |
| `activateAppointmentCheckInAdmission` | Future separately authorised activation; closed by this tranche. |
| `suspendAppointmentCheckInAdmission` | Move one exact active record to non-admitting `suspended`. |
| `withdrawAppointmentCheckInAdmission` | Terminal disable-only rollback to `withdrawn`. |
| `engageAppointmentCheckInGlobalKillSwitch` | Monotonic global clear-to-engaged transition. |

Every command must require an authenticated current human with a separately
defined operations role, exact server-owned practice/environment scope,
correlation id, idempotency key bound to the complete request digest, expected
record/generation version, explicit reason code, full 40-character lowercase
Git authority object id resolved by the shared Git-object guard, freshness,
append-only audit and a bounded patient-free receipt. A model, committed event,
async worker or client cannot be the authority source.

Unknown commit releases no success. Readback is by server-owned command id and
idempotency identity. The real database role, concurrent transition,
unknown-commit and recovery proof remains a later operational-evidence gate.

Read-only posture may later be exposed through REST and GraphQL. GraphQL may
report the evaluated state, generation, freshness and non-sensitive reason
code; it cannot prepare, activate, suspend, withdraw, engage or clear a switch.

## Frozen operational-evidence gate

`active` is invalid unless all three accepted operational-evidence gaps have
current, independently verified, exact-generation evidence:

- a non-owner, `NOBYPASSRLS` ordinary runtime-role and tenant-isolation
  attestation;
- atomic rollback plus unknown-commit recovery drills with bounded readback and
  no false-success release; and
- environment manifest, secret/key-reference, rotation and break-glass posture
  evidence.

Evidence references are immutable digests plus full 40-character resolved Git
objects. Missing, abbreviated, unresolved, stale, reused-across-generation or
wrong-environment evidence denies. The architecture cannot generate those
operational proofs from authored-synthetic tests.

## Frozen non-PHI observability

The future metric set is exact and low-cardinality:

- `emr4_check_in_admission_decisions_total{environment,lane,outcome,reason_code}`;
- `emr4_check_in_admission_snapshot_age_seconds{environment}`;
- `emr4_check_in_admission_kill_switch{environment}`;
- `emr4_check_in_unknown_commit_total{environment}`; and
- `emr4_check_in_control_commands_total{environment,operation,outcome}`.

Allowed label values are closed enums. Metrics and alerts contain no practice,
appointment, patient, practitioner, user, correlation, idempotency, command,
evidence, token or free-text value. Raw request/response bodies and route audit
records are never telemetry inputs. Practice-attributable append-only control
audit remains a protected authority record, not an observability label.

Immediate alerts are required for an engaged kill switch, invalid or stale
snapshot, any unknown commit, rejected active record, control-audit failure and
rollback failure. Bounded rate alerts may use aggregate deny/error counts only.
No alert can clear a switch, activate a record, retry a command or feed back
into route behavior.

## One typed reading and clockwork boundary

The machine contract is the one normative architecture reading. The
deterministic validator derives the evidence report and rejects disagreement
between state transitions, decision precedence, API operations, operational
gates, telemetry and closed boundaries. Git object fields use exact 40-character
patterns rather than prose memory.

The accepted Ariadne/DeepSeek shared clock remains shadow-only. A later live
control-plane adoption may carry a digest-bound admission architecture reading
or review WorkOrder through that journal, but this tranche neither adopts the
clock nor gives the DeepSeek broker product or activation authority.

## Exact owned outputs

Sol may create or update only:

- this plan;
- `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md`;
- `docs/security/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-threat-model-delta.md`;
- one contract and closed JSON Schema under the named Continuity directory;
- one provider-free deterministic validator and its focused tests;
- one derived evidence JSON and technical report;
- required current-latch, error-register, receipt and review artifacts; and
- closeout, Sol acceptance, Yuri summary, Continuity updater/test, baton and
  Compass/Continuity position if the tranche passes.

No existing application, configuration, migration, API Spine, runtime, product
test, client or deployment source is editable.

## Deterministic acceptance

Pass requires:

1. all eleven source hashes match before semantic validation;
2. one closed JSON Schema validates one exact contract;
3. synthetic and ordinary inputs are distinct, ambiguity denies and absence
   defaults to disabled;
4. the transition graph is exact, has no resume edge and rollback cannot
   produce `active`;
5. the global kill switch dominates both admission lanes;
6. every ordinary activation prerequisite includes exact practice,
   environment, operation family, generation, version/freshness, three
   operational-evidence classes and full 40-character resolved Git objects;
7. all five future state-changing operations are REST/OpenAPI commands with
   human authority, idempotency, correlation, optimistic versioning, audit and
   unknown-commit readback; GraphQL remains read-only;
8. telemetry has exactly five metric families, closed low-cardinality labels,
   no PHI/tenant identifiers or feedback authority, and exact alert classes;
9. default-off, product/config/OpenAPI no-write and every protected boundary is
   machine represented;
10. at least 96 independent hostile contract mutations fail closed;
11. focused architecture, API Spine, latch, baton, register, compilation, Ruff
    and `git diff --check` gates pass; and
12. protected refs remain exact while `docs/branding/` and all unrelated
    untracked files remain preserved.

One fresh Gemini 3.7 Flash/high exact-candidate veto is mandatory after the
deterministic candidate passes.

## Parallelism assessment

- **DeepSeek:** declined. Occupied native-Harness execution remains behind the
  separate provider-free stock-headless-to-custom-runner HMR boot proof; the
  serial admission semantics are not a bounded worker package, and Claude Code
  is not a fallback.
- **Gemini:** reserved for one independent read-only veto of the exact clean
  candidate after deterministic admission. It receives no implementation,
  acceptance, integration or protected-ref authority.
- **Native subagents:** declined because current developer policy prohibits
  proactive delegation and the state machine/precedence decision is serial.

Reassess after plan freeze, after deterministic admission, before verifier
acceptance, at closeout and before any future product implementation or
occupied DeepSeek worker.

## Claim, recovery and closed surfaces

Passing proves only that the three design gaps have one fail-closed,
provider-free, source-bound architecture. It does not close the three
operational-evidence gaps and does not prove or authorize ordinary runtime.

One bounded mechanical correction may repair schema, validator, evidence or a
test without changing admission semantics. Any proposal to reuse the synthetic
allowlist for ordinary admission, clear the kill switch in place, resume a
suspended record, restore active state through rollback, omit an operational
gate, expose identifiers in telemetry, use GraphQL/async/model authority, or
change product source is conceptual and stops the tranche.

No ordinary-practice enablement, feature flag or allowlist change, product code
or configuration, live route, database, generic-status `Arrived`, action
grammar, first-party client, waiting-area movement, product/patient/clinical
data, occupied provider call, production runtime, deployment, release, Pages,
live clockwork adoption/control retirement or protected-ref movement is
authorised. Preserve `docs/branding/` and every unrelated untracked file; stage
explicit paths only.
