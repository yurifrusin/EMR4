# Ariadne DeepSeek In-Cell Generated-Draft Rehearsal - Closeout

Date: 2026-07-23

Result:
`ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required`

Owner: GPT Sol High

## Outcome

The first occupied-cognition attempt closed accurately as
`revision_required`. The purpose-built Claude Code process started inside the
inspected work-cell container, but its first broker request used a method or
path outside the frozen one-path gateway allowlist. The broker rejected that
request and Claude Code exited before any DeepSeek provider request.

The one occupied attempt is consumed. There is no retry authority.

## What happened

- The five-source rehydration and final pre-attempt receipts passed.
- The authored-synthetic contract compiled to six frames, 698 canonical
  payload bytes, a 12,033-byte prompt and five locked draft ports.
- Fifty-one pre-runtime focused/API checks passed before image construction.
- The first cell-image build exposed an invalid npm `package=version` spelling.
  It was corrected to `package@version` before any model process, key use,
  prompt transmission or attempt consumption.
- The allowlisted five-file rebuild passed using:
  - Node base
    `node@sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d`;
  - Claude Code `2.1.201`;
  - broker image
    `sha256:61a6385d7be5cd43813ca915a3194874311d983e416266274acecdc99dee0ef7`;
    and
  - work-cell image
    `sha256:129af6436f945a01a58c8a02da3f142bd08e2a4cf9c1a4f3da0e8878b3e08005`.
- The final pre-attempt receipt passed and the consumed ledger was written
  immediately before model-process start.
- The broker recorded `broker-ready` followed by one
  `method-or-path-not-allowlisted` rejection.
- It recorded no `provider-call-started` event.

Therefore:

- DeepSeek received zero requests;
- no provider prompt or context transmission occurred;
- provider usage and cost are zero for the model attempt;
- no model inference or generated draft occurred;
- schema validation remained `not-presented`;
- the deterministic proofreader received nothing; and
- no downstream or human-gate route was reached.

## Isolation result

The physical boundary itself behaved as designed:

- the work cell ran as `node`, read-only, with all capabilities dropped,
  no-new-privileges, no mount, no published port and only the Docker-internal
  network;
- `DEEPSEEK_API_KEY` was absent from the cell environment and present only in
  the broker;
- the broker had no mount or host port;
- no PostgreSQL, GraphQL, REST/OpenAPI, FastAPI, product API, event feed,
  mailbox, human action or command connection existed; and
- the cell, broker, internal network and both local image tags were removed.

The provider secret was never exposed to the cell.

## Failure diagnosis

The executed broker accepted only
`POST /anthropic/v1/messages`. Claude Code's documented LLM gateway contract
also includes `POST /v1/messages/count_tokens`, and Claude Code may query
`/v1/models` at startup. The installed `2.1.201` binary contains all three
endpoint strings.

The sanitised broker intentionally did not retain the rejected method or path,
so this evidence does not prove which preliminary endpoint Claude Code used.
It proves only that the first request did not match the single admitted
method/path. That omission is itself useful: the gateway needs a separately
bounded discovery/counting contract, and future diagnostics should retain the
rejected method and normalised path while still excluding headers and bodies.

## Evidence correction

The runner initially labelled the evidence
`live_provider_authored_synthetic_generated_draft_rehearsal`. That was too
broad because zero provider requests were forwarded.

The original generated evidence is preserved by hash:
`sha256:7058228c3a3cce7db7c9cd8d1417612e6f72735def25e6a326dacf5c41ee0973`.
The executed host runner is preserved by hash:
`sha256:0785438f802e81ca9e8c2f8b94280d8f3039b288ebb08b36a0837ad85c8986fe`.

Only metadata labels were corrected. Runtime observations did not change. The
canonical label is now
`provider_transport_attempt_authored_synthetic_no_provider_call`.

## Verification

After the attempt:

- focused generated-draft/API Spine population: 59 passed, 0 failed;
- combined work-cell, Continuity, Compass, orchestrator, API Spine and handover
  population: 242 passed, 0 failed;
- Draft 2020-12 attempt, output and runtime-evidence schemas: passed;
- exact container-input source hashes: passed;
- consumed-ledger and no-retry assertions: passed;
- no-provider-call and no-draft assertions: passed;
- effective isolation and cleanup assertions: passed;
- Ruff, Python compilation and Node syntax: passed.

The Continuity graph is revision 23 with a rejected exploration node. Compass
revision 11 blocks the generated-draft direction behind a fresh
provider-blocked gateway-diagnostic decision while preserving the seven-step
Reception One journey and current product node.

The first protected-PR Python Security run flagged Bandit B108 on the two
literal `/tmp` targets supplied to Docker `--tmpfs`. Both are
container-internal, memory-only scratch mounts rather than host temporary-file
paths. Yuri approved a focused CI-only correction; justified `nosec B108`
annotations now make that distinction explicit. The exact `ci-bandit` profile,
Ruff, compilation, whitespace and 59 focused tests pass after the correction.
No runtime input, executed image, evidence observation or consumed-attempt
state changed.

## API Spine result

Boundary classification:
`occupied_model_transport_attempt_rejected_before_provider`.

The API Spine boundary remained intact. The only context was opaque authored
synthetic data. Generated content never existed. GraphQL, REST/OpenAPI,
database, event and command planes remained unused. No API Spine or product
artifact changed.

## Next decision

The smallest next candidate is not another inference attempt. It is one
separately authorised, provider-blocked Claude Code gateway-shape diagnostic:

- start a fresh disposable cell with the same empty tools and synthetic prompt;
- forward nothing to DeepSeek;
- record only the rejected HTTP method and normalised path;
- locally answer a bounded `/v1/models` request if required;
- determine whether `/v1/messages/count_tokens` is required and how its token
  authority should be supplied; and
- remove everything without generated output.

Only after that diagnostic should Yuri consider a new one-attempt inference
authority with a gateway allowlist that distinguishes local discovery/token
counting from the single provider-generating `/v1/messages` request.

No diagnostic, retry, provider request, generated draft or broader authority is
granted by this closeout.
