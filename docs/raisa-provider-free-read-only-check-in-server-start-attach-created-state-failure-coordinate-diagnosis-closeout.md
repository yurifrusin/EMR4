# Provider-free read-only check-in server start/attach created-state failure-coordinate diagnosis closeout

Date: 2026-08-23

Timestamp: 2026-08-23T02:22:13.0856700+10:00 (Australia/Brisbane)

Status: `accepted`

Operation:
`raisa-provider-free-read-only-check-in-server-start-attach-created-state-failure-coordinate-diagnosis`

Exact reviewed source:
`2ab8707e2ac03be3b1a4c9c538dfa45382d7d92d`

## Result

The diagnosis passes with exact coordinate `cli_option_surface_mismatch`.
Docker client/server 29.5.3 advertises `--attach` and `--interactive` for
`docker start`, but not `--sig-proxy`. The accepted database harness supplies
`--sig-proxy=false` in that exact argument vector.

This explains attempt 006 without another occupied run: the Docker CLI could
reject the unsupported option while the host process exited nonzero and the
captured OCI server stayed `created`, `running=false`. The evidence SHA-256 is
`924ca23b361770fa31037232aa342e39c377e91685ac7137d1bb4da264647bb0`.

The evidence is closed and typed. It retains only client/server version,
read-only command return codes, a help-output digest, three advertised-option
booleans, one exact source-argument profile, the immutable attempt-006 safe
projection and one enum coordinate. It retains no raw help, stderr, path,
credential, environment value or Docker object identity.

## Exact execution and proof

- Read-only Docker metadata commands: `2`.
- Docker object commands and objects created: `0`.
- PostgreSQL processes and SQL/database attempts: `0`.
- Provider/model requests: `0`.
- Product effects and ordinary admissions: `0`.
- Attempt-006 retries: `0`.
- Attempt 007 authorised: `false`.
- Initial focused tests: `10 passed`.
- Current postterminal and lineage tests: `58 passed`.
- Ruff, compilation, canonical JSON and JSON Schema: passed.

The database harness remains exact SHA-256
`839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2`.
Attempts 001 through 006 remain immutable.

## Narrow repair and remaining gate

The smallest repair surface is
`remove_unsupported_sig_proxy_option_from_docker_start_argv`. The successor
may remove only `--sig-proxy=false` from `_start_attached` and update exact
static/conformance bindings. It must prove through source checks,
deterministic process fakes and read-only CLI help/version that the resulting
`docker start --attach --interactive <container_id>` vector preserves the
required attachment, stdin, default signal-forwarding and cleanup behavior.

This closeout does not implement that repair. It does not authorise attempt
007. A future occupied attempt still requires accepted repair evidence, a
separately frozen plan, fresh five-source preexecution receipt and one-run
checkpoint.

## Workflow efficacy and parallelism

The important efficiency result is positive: no blind database retry was
needed to identify the cause. Two read-only metadata readings plus exact source
comparison resolved the coordinate.

One broad validation manifest mixed consumed preterminal tests and an obsolete
historical exact-hash assertion with current postterminal tests, producing
three expected lifecycle-inapplicable failures before a 58-test current
manifest passed. Two new postterminal assertions also overtreated a safe
placeholder and Markdown capitalization as semantic data; both were corrected
before publication. These were low-cost validation-shape loops, not Docker,
database, provider or canonical-governance reruns. The prospective control is
to generate validation manifests from terminal/lifecycle tags and prefer
schema-structural predicates.

DeepSeek remained declined because worker/provider authority was closed and a
model had negative leverage on the exact local CLI grammar comparison. Gemini
remained declined because no material repair candidate yet existed. Native
subagents remained declined under developer policy and the serial diagnostic
surface. GPT Sol retained sole custody.

## Protected boundaries

Dedicated check-in remains default-off. Generic status does not gain
`Arrived`. No route, feature flag, allowlist, action grammar, first-party
client, waiting-area behavior, REST/OpenAPI, GraphQL, product configuration,
product/patient/appointment/clinical/historical/protected data, provider call,
production runtime, deployment, release, Pages or protected ref changed.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and every
unrelated untracked path remain preserved.
