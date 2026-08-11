# Threat-model delta: Raisa AES-C2 provider-free inert broker simulator

Date: 2026-08-11

Status: frozen authored-synthetic, provider-free, in-process simulation boundary

## Security delta

AES-C2 exercises the first simulated adapter call after AES-C1 admission. The
security objective is that a work-cell candidate cannot turn an admission into
control over adapter identity, destination, method, implementation or custody,
and that control-state changes between admission and dispatch stop the call.

The adapter is one pure local function with effect class `none`. There is no
broker/work-cell process, plugin loader, real adapter, real credential or
external I/O. Process and OS isolation are therefore residual future risks, not
claims of this tranche.

## Assets and data

- exact inherited AES-C1 contract, scenario and implementation identities;
- one immutable broker registry entry and its implementation digest;
- broker-owned operation identity and cumulative budget commit;
- fresh generation, authority, revocation and kill state at dispatch time;
- one authored-synthetic noncredential custody fixture;
- closed invocation/result/evidence digests; and
- newly authored synthetic values only, with no patient, clinical or product
  data.

## Trust boundaries

1. exact AES-C1 admission artifacts to the C2 simulator;
2. untrusted closed work-cell candidate/proofreader view to broker-side
   admission;
3. broker-private registry, control state, budget commit and synthetic custody
   fixture to the fixed dispatch function;
4. one broker-created invocation to one statically selected pure inert adapter;
5. untrusted adapter result to closed result validation; and
6. minimized simulator evidence to repository-local acceptance only.

## Attacker-controlled inputs

- every work-cell candidate field and value;
- malformed or mismatched broker-side admission objects;
- stale or changed post-admission generation/authority/revocation/kill state;
- mutated registry fields or attempted additional entries;
- mismatched expected budget commit or candidate digest; and
- malformed adapter-result fixtures in the exact negative scenario.

The registry callable, broker-private synthetic custody fixture and fresh
control-state provenance are deterministic authored-synthetic controls. Their
real runtime isolation and provenance are not proven.

## Dangerous capabilities

No dangerous capability is opened. The only callable is a statically named
pure function with no external-effect imports. It cannot reach a provider,
network, filesystem, database/source, process, environment, metadata service,
tool or command. The custody fixture is explicitly not a real credential and
is unusable outside the simulator.

## Abuse cases and required controls

| Abuse case | Control | Required evidence |
|---|---|---|
| Candidate chooses adapter, operation, destination, method or executable | closed work-cell view plus identity resolved only from exact one-entry registry | selector scenario is not dispatched and work-cell identity mutations reject |
| Candidate receives a lease, registry or custody value | work-cell schema excludes all authority/custody fields and recursively checks forbidden keys | custody-exposure scenario stops with zero released result |
| Add or mutate a registry entry | exact registry count, closed schema and full identity equality | every registry mismatch scenario stops before call |
| Swap the pure implementation behind a valid adapter ID | separate exact inherited C1 adapter-artifact identity and recomputed C2 definition-digest bindings | implementation/artifact mismatch scenarios stop |
| Revoke or supersede after admission but before dispatch | mandatory fresh control-state recheck immediately before call | generation, authority, revocation and kill scenarios stop |
| Dispatch before cumulative state is committed | exact AES-C1 budget-after digest/count equality before call | budget-commit mismatch stops |
| Smuggle selector or executable content through allowed values | adapter treats values as opaque strings and has no parser/template/deserializer | generated selector mutations reject or remain inert |
| Leak the synthetic custody fixture through request/result/evidence/exception | fixture stays in broker-private scope; closed outputs plus recursive forbidden-value scan | zero fixture handle/value occurrences outside private comparison |
| Return command-shaped or sensitive adapter output | exact closed result schema and `command_authority: false` | malformed-result scenario stops and releases nothing |
| Invoke more than once or after terminal state | exact call counter and terminal-state latch | repeat-after-terminal scenario invokes zero additional calls |
| Turn the simulator into a plugin/runtime | static callable map of size one; no dynamic import/reflection/I/O/process modules | AST/static boundary checks pass |
| Turn a simulated result into product authority | no API route and all command fields remain false | focused API Spine tests pass |

## Verification evidence

- exact inherited C1 hashes and full AES-C1/AES-C0 regressions;
- exact closed simulator contract, schema, one-entry registry and 26 scenarios;
- exact status/reason/invocation counts and independent digest assertions;
- 18 generated hostile attempt/result mutations plus nested contract mutations;
- recursive custody fixture absence checks across all non-private outputs;
- static import, callable-selection and external-effect checks;
- focused API Spine compatibility tests;
- DeepSeek blue defensive implementation/test evidence; and
- fresh exact-head Gemini red/veto after deterministic gates.

## Residual risk owner

GPT Sol owns acceptance of this in-process simulator. AES-C3 owns broader
hostile content/egress challenges. Later gates separately own real process and
container isolation, time-of-check/time-of-use concurrency, real broker/adapter
defects, real credential custody, provider behavior, product data, operations
and deployment.

## Stop boundary

Any candidate-selected identity, registry ambiguity, fixture leakage, stale or
revoked dispatch, budget mismatch, second call, open result, external-effect
import, real adapter/provider/data/credential need or unresolved critical/high
review finding returns `revision_required`. This delta grants no real runtime,
adapter, credential, provider, data, network, database/source, filesystem,
executable tool, command, deployment, release, Pages or protected-ref authority.
