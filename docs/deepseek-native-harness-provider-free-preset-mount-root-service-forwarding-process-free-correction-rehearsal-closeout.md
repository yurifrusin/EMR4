# DeepSeek native Harness preset-mount root-service-forwarding process-free correction closeout

Date: 2026-08-22

Timestamp: 2026-08-22T09:01:43.2459891+10:00 (Australia/Brisbane)

Status: **accepted prospective process-free source correction**

Reasoning level: **Extra High**

## Result

At exact implementation source
`2c25ce7d65199e82c4d4fe93bbd1d0efc80474fe`, the controller derived a
prospective runner, guard and bridge with all 23 ordered source predicates
passing and closed result
`root_service_forwarding_correction_admitted`.

The corrected source shape is:

- the runner retains its admitted root `presets` service and passes it as the
  second argument to the guard;
- the guard receives an explicit `presetService`, passes it to the bridge and
  contains zero `agentCtx.agentPresets` dereferences;
- the bridge alone validates the service, reads and validates its mount handle
  and calls that handle with the service as receiver; and
- service or mount rejection occurs inside the bridge's sanitizing `try`, so
  the accepted sanitizer reduces it to the content-free
  `PRESET_MOUNT_UNCLASSIFIED` terminal rather than an outer unclassified
  composition escape.

The derived source existed only as in-memory bytes. JavaScript was not
materialized or executed.

## Clockwork and object-binding gain

The caller-authored contract contains no Git object identity. At evidence time
the repository resolver derived the planning commit as
`db80cd2790bb0453b7b1ab2bfa40e619681fc75c` and the implementation commit as
`2c25ce7d65199e82c4d4fe93bbd1d0efc80474fe`, proved the ancestor relation,
task-branch alignment, fixed protected refs, clean tracked state and preserved
`docs/branding/`.

This is the direct structural answer to the earlier abbreviated or manually
expanded object-ID lapses: the model no longer fills that field. It chooses the
plan path and takes the object reading from the resolver.

## Evidence and verification

- Accepted input hashes remained exact.
- The preliminary current-HEAD-bound evidence is preserved but superseded;
  immutable v2 evidence binds the controller-owning implementation commit and
  recomputes byte-equally after evidence commit
  `cb62d58cc6d4fea1eafac226f2c986fb1bed1472` advanced `HEAD`.
- Derived hashes are runner
  `5ef3b25babad23f4851faf7981cbdd6e77bf04701e91bf9ed80387df53f93ab9`,
  guard `76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9`
  and bridge
  `3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b`.
- The focused 11-test file passed.
- The exact broader collection was 169 tests; all passed with one platform-
  specific skip.
- Direct CLI, Ruff, `py_compile`, JSON Schema, deterministic recomputation,
  latch and Current-Baton checks passed.
- The complete five-source pre-verifier receipt passed at the pushed evidence
  source.
- Node, native Harness, worker, model and provider processes, requests, retries
  and resumes remained zero.

## Workflow-cost reading

Clockwork records AER-0912 through AER-0918. The historical-suite selection,
two PowerShell command forms, post-rewrite count, over-broad release predicate
rejected-result exit status and first time-sensitive candidate-source reading
all failed before acceptance and were corrected. They are real costs, but none
required an external worker rerun or consumed a native/provider attempt. The
accepted v2 resolver binding is idempotent across its descendant evidence
commit.

## Parallelism disposition

- DeepSeek: declined because the Harness/worker is the governed path and the
  tranche authorised no process or self-review.
- Gemini: declined because the latch forbade a provider process, all 23 exact
  predicates passed and the accepted claim is prospective only.
- Native subagents: declined under current developer policy.
- GPT Sol owned the serial derivation, tests and acceptance.

## Next tranche

Proceed with
`deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-isolated-node-fixture-rehearsal`.
It may materialize the exact derived bridge and sanitizer only inside one
disposable authored-synthetic fixture root and run exactly one isolated Node
process to prove success plus missing-service and missing-mount terminal
behavior. It may not start the native Harness, a worker, a model or a provider,
load the installed package seed, or retry the consumed native attempt.

## Boundaries

No JavaScript or native runtime path, runner/guard module graph, installed
package composition, DeepSeek turn, worker quality, model/provider request,
retry, product/configuration/API/database/route/adapter/flag/allowlist/grammar/
client/waiting-area change, ordinary-practice enablement, generic-status
`Arrived` change, patient/product/clinical/historical/protected data,
production, deployment, release, Pages, protected evidence or protected-ref
movement is accepted.
