# Provider-free check-in server post-readiness exit-state and stdin-lifecycle conformance repair plan

Date: 2026-08-20

Timestamp: 2026-08-20T14:50:08.3884319+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`2ebb05ebaf28cc4978e1f21bf8a7340fb6ee44bd`

Accepted attempt-005 occupied execution source:
`905184b76f576006232fcfdc78da71d98fcf0ca0`

Accepted attempt-005 closeout source:
`03b94136c9c6cd82d5a8098705f263ba34a20de4`

Accepted complete-composition clockwork source:
`f9a4ede953cc496e9b778a6162d77dc7e73121df`

Accepted complete-composition reviewed candidate:
`6ef058b87a2c927efd9d9d2027b59d6ad279fec5`

Operation:
`raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair`

Target result:
`raisa_provider_free_check_in_server_post_readiness_exit_state_and_stdin_lifecycle_conformance_repair_pass`

Reasoning level: Extra High freezes the credential-channel lifetime, closed
diagnostic vocabulary, native-Harness pre-provider coordinate and immutable
attempt boundaries. High is sufficient for the exact deterministic repair,
one separately admitted provider-disabled native mount probe, focused tests,
fresh independent veto and clockwork closeout while this plan remains exact.

## Authority and objective

Yuri's standing uninterrupted-development authority admits the narrowest
conformance repair supported by the accepted attempt-005 negative terminal.
Attempt 005 ran once, passed the readiness sidecar and then found the server not
running. It retained no closed exit-state reading at that point. Independently,
the sole native-Harness worker stopped before a DeepSeek request at the
collapsed coordinate `EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`.

This tranche must make both failures mechanically readable without replaying
either one. It may:

1. keep the server attachment's stdin write end open after the exact credential
   line is written and flushed, and close it only under the existing final
   attachment cleanup owner;
2. project a stopped post-readiness server into one closed sanitized OCI and
   host-attachment diagnostic with no raw Docker value, output, log or secret;
3. prove the stdin and attachment lifecycle using deterministic fakes;
4. distinguish the `server/post_readiness` family from the
   `native_harness/preset_mount` family in typed evidence;
5. add a provider-disabled native-Harness mount probe whose safe stage markers
   identify discovery, validity, standing activation, scope binding and final
   effective-tool projection without retaining exception text; and
6. make the smallest source and test corrections supported by those readings.

The tranche starts with no Docker object, container, PostgreSQL process, SQL or
database execution. Attempt 006 is not authorised. One local native-Harness
process may run only after its separate deterministic and checkpoint gates
pass; it receives no provider credential and must exit before any model request
or turn.

## Immutable evidence and exact inputs

Attempts 001 through 005, including every failure, envelope and consumed worker
terminal, are immutable. The exact retained inputs are:

| SHA-256 | Exact path |
|---|---|
| `62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c` | `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py` |
| `aaa9d1d5851742f757869919d610d610afd91678f5882fb066a82b1eb23a0d3f` | `tests/test_raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py` |
| `a9e6331471dadc06ddc1fc7f5f6e9510a231fa7cd3a0fc748495f8c9794bb887` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/rehearsal-failure-evidence.json` |
| `dedfcbf008ea11c9dac9241a59c900582f5ca82a1de003bcd9f740409c0bbb54` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/attempt-005-execution-envelope.json` |
| `daf1bccfd8fbd1ca005be68cb1ac0eecaa30fd2a34236e9ce543a1f9c0e0ae14` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/deepseek-native-worker-attempt-001/attempt-terminal-evidence.json` |
| `9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0` | `orchestration/continuity/deepseek-native-harness-provider-free-complete-composition-native-boot-recovery/provider-free-complete-composition-native-boot-evidence.json` |

Every Git binding used by implementation or evidence must be supplied by the
repository's resolver as a full 40-character commit and proved an ancestor of
the candidate. No builder accepts an abbreviation or caller-completed object
identifier.

## Factual stdin-lifecycle basis

The Docker CLI's current official contract says `docker start --interactive`
attaches the container's stdin, while `--attach` attaches stdout/stderr. Its
implementation attaches before start, copies the caller's input to the hijacked
connection, sends a write-side EOF when caller input closes, and continues
waiting for output or container exit. The current EMR4 controller writes and
flushes one credential line and immediately closes its parent pipe. The
container therefore receives EOF by design even though the Python attachment
process may remain alive.

This plan does not claim that EOF was the hidden attempt-005 cause. It repairs
the lifetime mismatch directly: the server's credential channel must remain
open for the server lifetime, and its safe exit state must be observable if the
server nevertheless stops.

Primary sources:

- `https://docs.docker.com/reference/cli/docker/container/start/`
- `https://github.com/docker/cli/blob/master/cli/command/container/start.go`
- `https://github.com/docker/cli/blob/master/cli/command/container/hijack.go`

## Frozen server correction

Only the accepted base harness and its exact focused test may change for the
server correction. `_start_attached` must write the exact ASCII credential
payload, flush it and return while `attachment.stdin.closed` is exactly false.
It must not retain a second credential copy, spawn a thread, read output or add
another cleanup owner.

`_stop_attachment` remains the sole attachment cleanup primitive. It must:

1. close the parent stdin handle exactly once when it exists and is open;
2. inspect the child process after that close;
3. terminate and bounded-wait only while it is still running;
4. kill and bounded-wait only after the existing timeout; and
5. return success only when the child is absent.

An already closed, missing or malformed stdin handle must not crash cleanup.
It is a closed lifecycle reading, not permission to leave the child running.

## Closed post-readiness diagnostic

When `State.Running` is not exactly `True`, the base failure carries one
`server_post_readiness` object with exactly these keys:

- `projection_valid`: boolean;
- `status`: one of `created`, `running`, `restarting`, `removing`, `paused`,
  `exited`, `dead`, `unknown`;
- `running`: boolean or null;
- `exit_code`: integer `0..255` or null;
- `oom_killed`: boolean or null;
- `state_error_empty`: boolean or null;
- `restart_count`: integer `0..1000000` or null;
- `attachment_process`: `running`, `exited_zero`, `exited_nonzero` or
  `unreadable`; and
- `attachment_stdin`: `open_after_delivery`, `closed_before_verification`,
  `missing` or `unreadable`.

`projection_valid` is true only when every OCI field and both host attachment
readings have an admitted type and value. An unknown or malformed value is
collapsed to its null/`unknown`/`unreadable` form and sets the validity flag
false. No raw `State.Error`, status string outside the enum, exception, return
code other than the closed zero/nonzero class, ID, name, timestamp, path,
credential, nonce, stdout, stderr or log may be retained.

All other failure families carry `server_post_readiness: null`. Existing
sorted profile-predicate handling remains exact. Historical terminals are not
rewritten to the new shape.

## Native-Harness coordinate repair and provider-disabled probe

The accepted generic preset-mount terminal remains immutable. A new probe must
use the pinned official `@deepseek-ai/dsh@0.1.0-rc.7` package, the same exact
158-byte `emr4-bounded-worker` preset and the same full-profile
`agents.create({setup})` path as the consumed worker. The worker environment
contains no DeepSeek key or provider credential. The outer broker, if needed
for construction, is hard-disabled and must record zero requests.

The probe may retain only these ordered safe coordinates:

1. `PRESET_DISCOVERY_ENTERED` / `PRESET_DISCOVERY_PASSED`;
2. `PRESET_VALIDATION_PASSED`;
3. `AGENTS_CREATE_ENTERED`;
4. `AGENT_SETUP_ENTERED`;
5. `PRESET_RESOLUTION_ENTERED` / `PRESET_RESOLUTION_PASSED`;
6. `PRESET_STANDING_ENTERED` / `PRESET_STANDING_PASSED`;
7. `PRESET_SCOPE_BINDING_ENTERED` / `PRESET_SCOPE_BINDING_PASSED`;
8. `EFFECTIVE_TOOL_VIEW_PASSED`;
9. `AGENT_CREATED_PROVIDER_DISABLED`; and
10. `AGENT_DISPOSED`.

The controller must verify the pinned package methods before wrapping them.
Missing or changed method shape fails before launch. At runtime the first
missing success marker maps to one exact safe coordinate; exception text,
stack, raw runner output, session content and environment values are discarded.
The process must create no turn and make zero model, provider, network, Docker
or database request. A single process terminal is retained and never retried.

If safe package structure cannot distinguish resolution, standing and binding
without changing rc.7 or relying on raw exceptions, the probe must stop at
`PRESET_SUBSTAGE_INSTRUMENTATION_UNAVAILABLE`. It must not invent a more
specific diagnosis.

## Schema-generated workflow readings

This tranche may not add another memorised checklist. Its controller must
derive and validate:

- every Git binding through the existing full-object resolver;
- every provider-free test dependency from the admitted command manifest and
  an explicit compatibility/dependency manifest, never filename proximity;
- every bounded checkpoint string through a schema-owned length-limited
  renderer before receipt construction;
- every changed path by comparing baseline and terminal SHA-256 maps, excluding
  byte-identical placeholders; and
- every evidence path from a schema-owned artifact role.

The same readings are used by checks and reports; callers cannot separately
retype them. Hostile tests must reject abbreviations, dependency omissions,
overlong text, noncanonical artifact roles and unchanged-placeholder false
positives.

## Owned implementation surfaces

The exact owned implementation set is:

- the base relay-free harness and its focused test named above;
- `scripts/raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py`;
- `tests/test_raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py`;
- `tests/test_raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair_plan.py`;
- `orchestration/continuity/raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair/contract.json`;
- the contract, diagnostic and evidence schemas in that same topic;
- provider-free evidence, report and efficacy reading generated there; and
- exact continuation receipts, later verifier packet/receipt, closeout, Sol
  acceptance and Yuri summary for this operation.

No accepted predecessor controller, native-Harness evidence, attempt terminal,
product source, API Spine artifact or canonical governance surface is directly
edited. Clockwork alone owns canonical governance publication at closeout.

## Deterministic and execution admission

Before any native process, provider-free tests must prove:

1. exact stdin write, flush and open-after-delivery lifetime;
2. close-once final cleanup on live, exited, closed, missing and timeout fakes;
3. every canonical and malformed post-readiness projection;
4. raw error, ID, path, credential, nonce, stdout/stderr and unknown-status
   rejection;
5. historical attempt-005 bytes and hashes unchanged;
6. exact separation of server and native-Harness coordinate families;
7. schema-generated Git, dependency, bounded-text, changed-path and artifact
   role readings with hostile mutation rejection;
8. the native probe's source/package/profile/preset bindings and zero-provider
   environment contract; and
9. no Docker/database command, attempt-006 path or product/API path in the
   admitted manifest.

Run all Python tests serially through the provider-free admitted runner. Ruff,
Python compilation, JSON/schema validation and `git diff --check` must pass.

Only then may one fresh preexecution receipt plus one separate clockwork
checkpoint admit exactly one local provider-disabled native-Harness process.
Its first start consumes the probe. Pass requires all ten safe coordinate
stages, exact `edit`, `glob`, `read`, zero model/provider/network/Docker/
database counts, exact agent disposal, process absence and disposable-root
absence. A failure is accepted only as accurately bounded negative evidence
and receives no retry.

## Independent veto and acceptance

After the exact deterministic candidate and any admitted native probe terminal
are clean, one fresh Gemini 3.7 Flash/high isolated read-only veto may inspect
the exact candidate. Gemini receives no write, provider-execution, product,
database, cleanup, Git or acceptance authority. A P0-P2 finding requires one
bounded Sol correction and one fresh corrected veto; otherwise the tranche
closes honestly as blocked evidence.

Pass requires the new closed server diagnostic, corrected stdin lifetime,
provider-disabled safe Harness subcoordinates, all generator controls, zero
historical drift and exact cleanup. It does not prove attempt 006, PostgreSQL
transaction success, DeepSeek reasoning/coding quality, occupied worker
reliability, product readiness or production suitability.

## Explicit parallelism assessment

- **DeepSeek native Harness:** `declined`, negative leverage. The sole worker is
  consumed before provider dispatch and no repeat is authorised. The current
  work diagnoses its mount path provider-disabled under Sol; DeepSeek itself is
  not called.
- **Gemini:** `reserved`, required independent leverage. It owns one fresh
  exact-candidate read-only veto only after deterministic and provider-disabled
  native-probe acceptance.
- **Native subagents:** `declined`, negative leverage. Current developer policy
  prohibits proactive delegation, and the vocabulary, process lifetime and
  one-run probe are a coupled serial architecture boundary.

Reassess the three lanes at candidate precommit, native-probe preexecution,
pre-verifier and closeout. Sol alone owns plan meaning, process admission,
source correction, tests, acceptance, Git and successor selection.

## API Spine, product and protected boundaries

This is a harness and workflow-control repair, not an API change. GraphQL
remains read-only. No REST/OpenAPI, GraphQL, async contract, route, schema,
migration, feature flag, authored-synthetic allowlist, action grammar,
first-party client, waiting-area behavior or product configuration may change.
Dedicated check-in remains default-off; generic status does not gain `Arrived`;
ordinary practice remains denied; no product record or product/patient/
appointment/clinical/historical/protected data is used.

No attempt 006, Docker/database execution, live DeepSeek call, other provider
call before the separately admitted Gemini veto, production runtime,
deployment, release, Pages, protected evidence access or protected-ref movement
is authorised. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

At closeout write the paired lay/technical Yuri summary, send the usual non-PHI
Pushover notification, stage only explicit paths and preserve `docs/branding/`
plus every unrelated untracked file. `git add .` and `git add -A` are forbidden.
Continue to the narrowest dependency-satisfied successor unless a genuine
user-attention fork arises.
