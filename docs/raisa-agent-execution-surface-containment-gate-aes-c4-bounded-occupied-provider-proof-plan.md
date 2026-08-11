# Raisa AES-C4 bounded occupied authored-synthetic provider proof plan

Date: 2026-08-11

Source HEAD: `07c70ebb03eae7ccbcb3b7f831766b7f6eef52d6`

Status: `frozen_for_provider_free_implementation_and_one_conditionally_authorised_occupied_call_after_human_adc`

## Authority and exact result sought

Yuri selected the usual Sydney Vertex Bernie development lane and directed
EMR4 to treat its Vertex model as the default until he changes that decision.
This supplies the provider choice that was missing at AES-C3 closeout. It
removes future routine model-selection pauses, but it does not turn the model
choice into generic call, data, cost, product, tool or runtime authority.

AES-C4 will prove the smallest occupied descendant of the accepted AES-C0/C1/
C2/C3 chain: exactly one newly authored-synthetic request is admitted by the
immutable-generation capability broker, sent to the exact regional Vertex
endpoint, checked by a deterministic output proofreader, and closed with every
lease, alias, token, ledger, process/listener and task-owned temporary resource
absent. A failed admission, preflight, provider result, proofreader decision or
cleanup check releases nothing and closes the one-call ledger.

Target result:
`raisa_agent_execution_surface_containment_gate_aes_c4_bounded_occupied_provider_proof_pass`.

Evidence label:
`occupied_authored_synthetic_brokered_provider_containment_proof`.

## Exact provider and cost envelope

The canonical machine-readable authority is
`orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/provider-envelope.json`.

| Property | Frozen value |
|---|---|
| Provider/model | Google Vertex AI `gemini-2.5-flash` |
| Project/quota project | `bernie-emr4-dev` |
| Identity | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` |
| Authentication | existing keyless impersonated service-account ADC; no key file or API key |
| OAuth scope | `https://www.googleapis.com/auth/cloud-platform` |
| Permission | existing prediction-only `aiplatform.endpoints.predict` binding |
| Region | `australia-southeast1` |
| Host | `australia-southeast1-aiplatform.googleapis.com` |
| Method/path | `POST /v1/projects/bernie-emr4-dev/locations/australia-southeast1/publishers/google/models/gemini-2.5-flash:generateContent` |
| Data | newly authored synthetic only; no product, patient, practice, historical, protected, licensed or external-corpus content |
| Request | one candidate, temperature `0`, `thinkingBudget: 1024`, `maxOutputTokens: 2048` |
| Size/time | request <= 8,192 bytes; response <= 16,384 bytes; provider error <= 65,536 bytes before digest-only reduction; HTTP timeout 45 seconds; generation <= 120 seconds |
| Calls | exactly one maximum; no retry, repair call, unchanged repeat or call after any attempt |
| Cost | USD 0.25 application ceiling, reserved once before dispatch |
| Provider features | no tools, functions, grounding, retrieval, code execution, explicit context cache or automatic fallback |

The cost reservation is deliberately conservative. Current published Standard
pricing observed on 2026-08-11 is USD 0.15 per million input tokens, USD 0.60
per million non-thinking output tokens and USD 3.50 per million thinking output
tokens. The fixed request/output ceilings remain far below USD 0.25; a pricing
or billing ambiguity still stops before transmission rather than weakening the
ceiling.

Google currently publishes `gemini-2.5-flash` as GA, includes
`australia-southeast1` for its regional ML-processing availability and records
retirement on 2026-10-16. Those facts must be rechecked immediately before the
call. The regional endpoint proves the configured and observed locational
request path only; it does not prove Australian physical or sovereign
processing.

## Human ADC boundary

Codex may not mutate credentials, IAM or cloud configuration. Yuri performs the
interactive authentication. AER-0029 requires the gcloud CLI credential store
and Application Default Credentials to be treated separately and prohibits the
account-qualified shortcut that reused an expired cached source credential.

The human commands are:

```powershell
gcloud auth login --force
gcloud auth application-default login --impersonate-service-account=emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com --project=bernie-emr4-dev --scopes=https://www.googleapis.com/auth/cloud-platform
```

After Yuri completes them, Sol may run sanitized read-only checks of both
stores. No token, credential path contents, authorization response or raw
cloud-control response may enter repository evidence or conversation output.

## Immutable generation and broker binding

AES-C4 adds one exact `provider_inference` grant to a new generation; it does
not amend an AES-C0 through C3 artifact. The manifest, lease and current state
must bind:

- one principal, purpose, Bureau and work-cell generation;
- capability `capability-aes-c4-sydney-vertex-provider-inference`;
- adapter `vertex-generate-content-broker-adapter-v1`;
- operation `generate-aes-c4-authored-synthetic-proof`;
- destination `vertex-sydney-gemini-25`;
- the exact POST method, JSON media type, prediction audience, authored-
  synthetic source class and closed request/release fields;
- one call, one destination, zero redirects and the exact byte, token, cost and
  elapsed-time ceilings; and
- the C0/C1/C2/C3, provider-envelope, broker-adapter, prompt-contract,
  proofreader-contract and runtime artifact digests.

The external broker, never candidate/model content, resolves provider, model,
project, identity, region, hostname, path, method, audience, credential
reference and cleanup target. The invocation candidate carries only a closed
synthetic packet and its digest. It cannot carry a URL, capability, lease,
adapter, destination, method, credential, path, SQL, executable, tool,
command route or policy amendment.

The broker repeats the exact C1 current-generation/current-authority/revocation/
budget intersection immediately before dispatch and atomically commits the
one-call and byte/cost reservation before network I/O. Any post-reservation
failure consumes the ledger; no rollback reopens it.

## Occupied request and two proofreader gates

The input is a new closed five-field authored-synthetic packet created only for
AES-C4. It contains its schema version, an opaque synthetic nonce, the admitted
manifest digest, three inert containment assertions and
`command_authority: false`. It contains no product semantics or copied
historical/provider material.

Before dispatch, a deterministic candidate proofreader verifies the exact
schema, nonce, manifest and frame digests, false command authority and absence
of forbidden selector/executable fields. Provider input is built only from the
broker-owned admitted packet.

The provider is asked for one closed JSON object with exactly:

- `decision_code`, fixed to `contained`;
- the exact `synthetic_nonce`;
- `summary_code`, fixed to `broker_boundary_confirmed`; and
- `command_authority`, fixed to `false`.

After the response, deterministic code rejects duplicate keys, non-JSON,
additional/missing fields, wrong types, wrong enum/nonce, command authority,
schema drift, provider tool/function parts, safety/finish ambiguity, truncated
or oversized content and any mismatch with the admitted frame or manifest.
Only those four exact fields may be released atomically. There is no semantic
repair, preferred-prose repair or second provider call. Failure returns
`intelligence_unavailable` and releases nothing.

## Preexecution gates

Every gate is serial and source-bound. Before prompt transmission:

1. repeat complete five-source rehydration and emit a fresh `pre_execution`
   receipt;
2. require exact task HEAD, clean tracked scope, accepted plan/envelope hashes,
   unchanged C0/C1/C2/C3 hashes and unchanged protected refs;
3. pass closed-schema, contract, hostile mutation, budget, replay and cleanup
   tests with zero provider calls;
4. prove the provider-free broker dry run from admission through both
   proofreaders and terminal cleanup with a distinct zero-call ledger;
5. obtain a fresh exact-HEAD independent security veto only after deterministic
   gates pass;
6. verify ADC and gcloud CLI credentials separately without outputting tokens;
7. read-only verify exact impersonated type, project/quota project, scope,
   enabled billing/API/service account, prediction-only role/binding/permission,
   Vertex Data Access audit, disabled-or-absent request/response logging,
   explicit provider in-memory cache disablement, zero user-managed service-
   account keys, current Sydney catalogue support, regional hostname and no
   fallback; and
8. require an unopened one-call/one-reservation ledger plus no task-owned
   process, listener, alias, token, temporary root or prior generation residue.

Any deterministic or independent failure means zero occupied calls. A cloud
control requiring mutation, unusable ADC, changed lifecycle/region, missing
permission, logging/cache uncertainty or residue is a terminal human-attention
stop; Codex does not repair cloud or credential state.

## Evidence and cleanup

External hash-chain evidence may retain only closed identifiers, digests,
decisions/reason codes, safe cumulative counts, provider/model/project/region/
hostname, HTTP status, finish reason, latency, safe token counts, cost bound and
cleanup dispositions. It must not retain the raw prompt, provider text, raw
response/error, thought content, credential, token, environment, unrestricted
log, patient/product value or exception message.

Every terminal path must:

- consume the generation lease, token alias and one-call ledger;
- revoke all further generation calls and mark budgets terminal;
- close the broker connection/listener and any task-owned process;
- remove only exact task-owned temporary paths;
- prove no reusable credential/capability was copied into the work cell;
- prove zero product, database/source, filesystem-capability, tool, command,
  deployment and protected operations; and
- preserve minimized incident evidence if containment or cleanup is uncertain.

Cleanup uncertainty is not a pass. It quarantines the generation and blocks any
new call.

## API Spine classification

This is an internal Access AI/provider invocation plus security/audit evidence.
It adds no HTTP route and no product capability or entitlement.

- GraphQL remains read-only and is never called.
- Events remain signals only and are never consumed.
- JSON manifests are declarative inputs; typed code enforces them.
- The model output is inert evidence with `command_authority: false`.
- REST/OpenAPI mutations remain separately authorized, human/policy-gated,
  idempotent, audited and deterministically read back; AES-C4 cannot prepare or
  confirm a product command.

## Owned artifacts

- this plan and its threat-model delta;
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/`;
- one AES-C4 broker/proofreader implementation and focused tests;
- exact preflight, dry-run, independent-review, occupied and cleanup evidence;
- exact Ariadne receipts and incident/recovery artifacts;
- closeout, Sol acceptance, Yuri mailbox summary, Continuity/Compass updater and
  continuity tests if the tranche passes; and
- narrow current-baton/implementation-plan bindings required by acceptance.

All 494 original untracked files are outside ownership, including
`docs/branding/` and the AES-C0 pre-push receipt/state pair. The AES-C4
rehydration receipts remain owned only if explicitly included at closeout.

## Forbidden surfaces and stop conditions

AES-C4 grants no protected evidence, historical Diary/PHI, patient, clinical,
product-derived, practice/operational, financial, licensed or external-corpus
data; product read; database/source/migration/watcher; filesystem capability;
provider-executed tool/function/grounding/retrieval/code; generic network;
shell/process command capability; product command/write; reusable broker or
adapter runtime; IAM/credential/cloud-configuration change; deployment;
production; release; Pages; or protected-ref movement.

Stop without a call or release on any scope expansion, selector-bearing model
content, stale/mismatched generation or authority, revocation, external kill,
digest mismatch, budget overflow, non-Sydney endpoint, redirect, alternate
provider/model/project/identity, API/static key path, hidden fallback, provider
tool part, logging/cache ambiguity, unbounded provider error, cost uncertainty,
proofreader failure, incomplete audit or cleanup uncertainty.

## Acceptance and claim boundary

AES-C4 passes only if provider-free tests, exact-head veto, human ADC, complete
read-only cloud preflight, one occupied attempt, deterministic typed admission,
monotone accounting and exact cleanup all pass in that order. A provider or
proofreader failure may close the tranche as accurately failed evidence but
cannot be promoted to the target pass.

Passing proves only one exact broker-admitted authored-synthetic Vertex request
and deterministic four-field release under this immutable generation, or the
fail-closed behavior exercised on its tested alternate paths. It does not prove
general model safety, semantic prompt-injection detection, Australian physical
or sovereign processing, patient/product-data safety, reusable runtime safety,
concurrency, command safety, deployment or production readiness.

AES-C5 remains separately closed pending its own privacy, identity, retention,
product-data and one-source/one-purpose authority. AES-C4 creates no automatic
product-runtime descendant.
