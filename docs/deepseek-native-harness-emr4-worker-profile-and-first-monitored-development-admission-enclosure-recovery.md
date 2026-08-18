# DeepSeek native Harness EMR4 worker admission enclosure recovery

Date: 2026-08-18

Timestamp: 2026-08-18T16:09:20.8230251+10:00 (Australia/Brisbane)

Status: frozen recovery boundary

Reasoning level: high

## Trigger

Exact pinned rc.7 package-source inspection after the original plan freeze
showed that `@deepseek-ai/dsh-fs-sandbox` fences mutations only. Its README
states that reads always pass through in every mode. The pinned
`dsh-credentials-local` README separately states that same-UID filesystem and
shell tools can read a stored credential and calls prompt discretion, not a
security boundary.

The original sparse-worktree plus `workspace-write` composition therefore did
not technically enforce its claim that unrelated host material and the
provider credential were outside worker read authority. No occupied request
was made under that composition. The credential-absent boot reached exact
`MISSING_CREDENTIAL`, with four durable Zstandard frames, 17 logical rows and
no provider call. Docker Desktop's Linux engine is available, and local image
`node@sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d`
is present.

This recovery supersedes the original plan's process-environment credential,
host-side filesystem and model-facing PowerShell controls for the first
occupied development trial. Every other authority and acceptance boundary
remains unchanged.

## Recovered execution enclosure

The first occupied `emr4-bounded-worker` run uses two disposable Linux
containers and two disposable Docker networks:

1. The Harness worker container is pinned to the exact Node image above. It
   receives only the sparse worker worktree as a bind mount, a disposable DSH
   home/package volume and a one-session broker capability token. It receives
   no DeepSeek provider credential. It joins only an internal broker network,
   with no direct egress route.
2. A separate broker sidecar receives the actual DeepSeek credential and the
   broker token. It shares no filesystem mount or process namespace with the
   worker. It joins the internal broker network and a separate egress network.
   It accepts only authenticated `POST /chat/completions`, forwards only the
   exact `deepseek-v4-flash` route to `api.deepseek.com`, replaces the broker
   token with the provider credential, streams the response, and records only
   sanitized request/response metadata.
3. The worker's DeepSeek adapter points to the broker and carries the broker
   token as its API key. The real provider credential is therefore absent from
   the worker filesystem, environment, process namespace and session log.
4. No model-facing shell is mounted for this first run. The exact tools are
   repository read, glob and string edit. Sol, outside the worker container,
   independently runs all focused tests after exact changed-path readback.
5. The existing one-fresh-session, zero-retry, zero-fallback, one-parallel-tool
   and 15-minute wall-clock controls remain. Yuri's prepaid balance remains the
   monetary ceiling; the broker counts and traces calls but does not introduce
   a request-count or token-spend budget.

The internal worker network, sidecar separation, exact image digest, exact
mount list, effective Harness configuration, process terminals, broker call
metadata and cleanup are all acceptance evidence. A missing enclosure fact,
unexpected mount/network/tool, direct worker egress, broker authentication
failure, non-allowlisted path/model, secret-shaped retained value or incomplete
cleanup rejects the trial before candidate admission.

## Recovered worker package

DeepSeek still owns exactly:

- `scripts/ariadne_deepseek_native_harness_profiles.py`;
- `tests/test_ariadne_deepseek_native_harness_profiles.py`.

It implements the provider-free validator/materializer frozen in the original
plan. It may author tests but does not execute a shell. Sol owns the broker and
enclosure implementation, launches the single occupied session, performs all
test execution and alone admits, repairs or rejects the candidate.

## Parallelism assessment

- DeepSeek native-Harness lane: `planned`, positive leverage after the
  enclosure is committed and provider-free boot evidence passes. It owns the
  same exact two-path sparse implementation package.
- Gemini lane: `declined`, neutral leverage. No independent verifier package is
  required before deterministic enclosure and worker admission; later review
  remains available only if the accepted workflow requires it.
- Native-subagent lane: `declined`, neutral leverage. Current developer policy
  prohibits proactive delegation and no independent package is authorised.

Enclosure implementation, provider-free rebind, occupied dispatch, readback,
Sol tests, admission, cleanup and closeout remain serial.

## Unchanged protected boundaries

No product, patient, clinical, historical Diary or protected data; no
application route, API, database, client, status, action grammar, waiting-area
or ordinary-practice change; no live product runtime, deployment, release,
Pages or protected-ref movement; no global Harness/npm install or durable user
profile. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only.
