# A3/B3 Sydney Vertex broker reuse analysis

Date: 2026-08-04

Role: bounded native advisory analysis only; no acceptance, implementation,
provider-call, credential, cloud, Docker, database, test, Git or integration
authority

Source HEAD: `2de467e23ce44574395ad6115e7205ca27c96fb2`

Plan reviewed:
`docs/emr4-model-required-bureau-a3-b3-occupied-rehearsal-plan.md`

## Conclusion

Reuse the established Sydney isolation topology and exact identity-binding
checks, but do not extend either historical occupied runner in place. Add one
small A3/B3-specific coordinator, a closed lane policy/contract module and an
A3/B3-specific broker facade over the proven cell/relay topology. Use a fresh
single-use attempt ledger for every primary or correction turn and one separate
hash-chained tranche cost ledger spanning both lanes. Run A3 and B3 serially,
with full task-scoped teardown and residue readback between turns.

This is the smallest pattern that preserves the exact Vertex boundary while
avoiding historical attempt IDs, request allowlists, proofreader semantics,
cost predecessor accounting and durable audit fields leaking into the new
tranche.

## Exact reusable boundary

The following binding is consistently frozen in the current plan,
`AGENTS.md`, `scripts/ariadne_vertex_sydney_gemini_25_preflight.py`, the
historical broker policy and the occupied evidence:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: existing keyless impersonated service-account ADC only;
- OAuth scope: `https://www.googleapis.com/auth/cloud-platform`;
- location: `australia-southeast1`;
- data-plane hostname:
  `australia-southeast1-aiplatform.googleapis.com`;
- exact regional `generateContent` resource path for the named project,
  location, publisher and model;
- no global endpoint, API key, service-account key, provider/model/region
  fallback, tool use, function calling, grounding, retrieval or explicit
  context cache.

The historical success proves this configured and observed regional request
path only. It does not establish Australian physical or sovereign processing,
production fitness or authority for real/product/patient/clinical data.

## Reuse matrix

| Existing component | Recommendation | Required A3/B3 treatment |
|---|---|---|
| `ariadne_vertex_sydney_gemini_25_preflight.py` | Reuse its read-only checks | Parameterize or wrap it with an exact A3/B3 policy hash, request hash, cost-ledger hash and short expiry. Require exact model-resource matching rather than substring matching. Record the US control-plane cache-config read separately from the Sydney inference/data-plane boundary. |
| Historical broker-policy fields | Reuse the identity, endpoint and negative-feature invariants | Issue a new closed policy ID. Freeze per-request byte/token/output limits, redirect behavior, four-call cumulative ceiling and the two lane-specific proofreader contracts. Do not amend the historical policy. |
| `ariadne_vertex_sydney_gemini_25_cell.py` | Reuse the credential-free one-request client shape | Supply only the exact lane request. Keep no mounts, secrets, provider coordinates, product access or general-purpose network. A correction gets a fresh cell, not a conversation-resident cell. |
| `ariadne_vertex_sydney_gemini_25_relay.py` | Reuse the exact-path relay shape | Keep its one fixed host/port/path and ephemeral bearer attachment. It must not become an arbitrary HTTP proxy. Use a fresh relay/token for every turn. |
| isolation manifest and launcher constraints | Reuse the read-only root, non-root user, internal network, resource caps, no ports, no capabilities and exact build-context allowlist | Parameterize task names with lane and turn, verify effective Docker state before execution, and require the pinned base image locally before the occupied phase. Build with network disabled and no pull during occupied execution. |
| historical one-use broker | Reuse exact request comparison, safe ADC discovery/refresh, URL construction, byte bounds, hash-chained events and deterministic release gate | Create a small A3/B3 broker facade. Replace the historical Project Lark and Reception One contracts, attempt allowlists and proofreaders. Use a non-threaded server or a lock so `served` cannot race. Reject redirects and verify the final URL/host. |
| `read_and_hash_provider_error` from the original broker | Reuse | Hash the complete discarded error stream, parse only a bounded prefix, and retain no provider free-text message. Durable error evidence should contain only allowlisted status/code/field paths, byte count and hash. |
| `reception_one_vertex_cost_budget.py` | Reuse its hash-chain, reservation-before-call, settlement and unknown-usage fail-closed ideas | Do not reuse its historical policy or ledger schema as-is: they contain predecessor-specific accounting and terminal-success behavior. Add a clean A3/B3 tranche ledger with per-lane and cumulative counters. |
| historical rehearsal cleanup | Reuse task-scoped deletion and readback | Add explicit pre-residue evidence and inter-turn residue evidence. Preserve unrelated Docker/process state and never daemon-prune. Cleanup failure stops all later turns. |

## Minimal lifecycle

1. **Freeze source and policies.** Bind the plan, A3/B3 contract, provider
   policy, isolation manifest, synthetic frame, output schema, proofreader and
   cost policy by canonical hashes. The lane and turn ordinal are explicit.
2. **Provider-free admission.** Validate the exact request and run the same
   broker/proofreader path with a fixture. Prove that cross-lane context,
   invented identifiers, stale revisions, confirmation, write/success claims,
   retry drift, fallback and retained raw material fail closed.
3. **Pre-residue readback.** Require zero task-owned containers, networks,
   images, broker processes, tokens, contexts and open attempt ledgers. Do not
   touch unrelated resources.
4. **Source-only veto.** Complete the separately specified Gemini 3.6
   Flash/high review before any occupied call. Account for this non-zero review
   transport separately from A3/B3 candidate-runtime calls.
5. **Just-in-time read-only cloud preflight.** Immediately before each
   occupied turn, verify the unchanged impersonated ADC, exact project and
   target account, scope, prediction-only role/binding, API and billing state,
   audit posture, absence of user-managed keys, exact model resource, disabled
   request/response logging, disabled provider cache and exact regional
   endpoint. The preflight performs zero inference calls and no state change.
6. **Atomic admission.** Under one coordinator lock, validate the global and
   per-lane ceilings, reserve cost, create and consume a fresh call-slot ledger,
   and bind both records to the exact request/policy/context/correction-ticket
   hashes. Never reopen or rename a consumed ledger.
7. **Fresh one-task cell.** Create only the exact allowlisted build context,
   ephemeral token, credential-free cell, exact relay and host broker. The host
   broker alone discovers and refreshes the existing ADC and may contact only
   the regional endpoint.
8. **Transient parsing and proofreading.** Build prompt text only in memory.
   Parse the bounded response into the lane's closed candidate, proofread it,
   and persist only hashes, allowlisted provider metadata and usage,
   proofreader disposition/reason codes and admitted typed fields. Delete
   references to raw request/response buffers and rejected candidate content
   before durable evidence is written.
9. **Settlement and teardown.** Settle known HTTP usage; if call occurrence or
   usage is ambiguous, conservatively consume the reservation and block the
   tranche. Terminate the broker and remove only owned cell, relay, network,
   images, token and temporary context. Close any still-open attempt ledger
   with a zero-call terminal disposition.
10. **Residue gate.** Verify absence of all task-owned residue, no raw prompt or
    response text in durable artifacts, a valid audit/cost hash chain and no
    call after the first admitted result. Only then may the next serial turn
    begin.

The order is A3 primary, optional A3 correction, B3 primary, optional B3
correction. A correction is eligible only from the deterministic proofreader's
closed schema/contract-conformance ticket. It receives the same frame revision,
utterance, task semantics and authority ceiling plus the exact ticket; it is a
new attempt, ledger, reservation, cell, broker and preflight. A3 admission
skips its correction. B3 admission skips its correction. A shared identity,
policy, cache, audit, transport or residue failure stops every remaining turn;
a lane-local semantic rejection is terminal for that lane but need not prevent
the other lane's independently regated primary turn.

## Ledger and cost invariants

Use two distinct durable records:

1. A fresh **attempt ledger** for each possible turn, containing only the lane,
   ordinal, attempt/ledger IDs, exact policy/request/context/schema hashes,
   optional correction-ticket hash, reservation ID, status, call-slot
   consumption and bounded outcome. Distinguish `call_slot_consumed`,
   `provider_request_started`, `http_response_observed` and
   `provider_call_count`; the older `provider_calls_consumed` field conflates
   reservation with observed provider contact.
2. One **tranche cost ledger** with an append-only hash chain, USD 1 ceiling,
   maximum two turns per lane and four overall, no outstanding reservation at
   closeout, and exact linkage to every attempt ledger. Reservation must occur
   before the inference broker's credential acquisition and request
   transmission; the earlier read-only ADC preflight remains a zero-inference
   control check. Unknown occurrence/usage consumes the full reservation and
   closes further calls.

The A3/B3 cost policy must freeze one coherent set of maximum input/output
tokens, rates or deliberately conservative per-call reservation, and rounding.
Do not combine the original broker policy's historical prices and 256-token
output cap with the later Reception One cost policy's different rates,
3,072-token output cap and predecessor accounting. A conservative fixed
reservation that makes four admitted calls remain at or below USD 1 is safer
than dynamically trusting an unfrozen price lookup; observed token usage and an
estimated charge may still be recorded as bounded metadata.

## Raw-material and audit boundary

- The canonical authored-synthetic typed frames may be repository evidence;
  rendered provider prompt text may not be.
- Never write request authorization headers, ADC/token material, raw HTTP
  request bodies, raw provider response bodies, rejected candidate fields or
  free-form provider error messages.
- Durable response metadata should be limited to HTTP status, latency, exact
  model-version string if allowlisted, candidate/part counts, allowlisted finish
  reasons, token counts, full discarded-body hash and byte count.
- Persist an admitted candidate only after deterministic proofreading and only
  in its closed release schema. Persist rejected or correction-eligible
  candidates by hash and reason codes, not content. The closed correction
  ticket itself may be durable because it is deterministic and separately
  schema-bound.
- Avoid exception messages or subprocess output that can include provider
  bodies. Evidence writers should accept already-sanitized structures only.
- The original broker's complete-stream error hashing is preferable to the
  newer Reception One broker's bounded read, which can hash only a prefix. The
  newer broker's durable `typed_program`/operator/receptionist text fields must
  not be copied into rejected A3/B3 audit evidence.

## Important hardening before occupied execution

- Replace `urlopen`'s default redirect behavior with an explicit no-redirect
  handler; otherwise an HTTP redirect can escape the exact hostname policy
  even when the original URL passes its prefix check.
- Make the broker truly single-threaded or guard the `served` transition and
  ledger consumption with a lock. `ThreadingHTTPServer` plus an unguarded
  boolean is not a sufficient one-use primitive on its own.
- Bind the cloud-preflight evidence to the exact candidate and enforce a short
  validity window. A preflight from a prior tranche or before a material source
  change is ineligible.
- Require exact model-catalogue equality after normalization. The historical
  `MODEL_ID in name` test is too broad for an exact model boundary.
- Make every durable output path exact. Do not discover the current external
  audit or ledger through broad globs where historical files can satisfy the
  lookup.
- Prove that the pinned base image is already local before the occupied phase,
  and prohibit registry pulls/build network access during occupied execution.
- Preserve the historical base-image state. Never use daemon-wide Docker
  cleanup.

## Unresolved risks

1. The most recently recorded broad-cohort preflight stopped at
   `impersonated_adc_refresh_failed`. The new plan allows read-only refresh and
   inspection but not credential creation, replacement or reconfiguration. If
   the exact existing ADC still cannot refresh, A3/B3 must stop before any
   cell, call ledger, prompt or provider request and report the human-only
   recovery.
2. The plan freezes USD 1 and four calls but not one exact price/rate,
   input/output-token and reservation schedule. The implementation should
   choose and freeze a conservative internally consistent policy before
   deterministic acceptance; changing that policy after review invalidates
   preflight and reservations.
3. Read-only cache configuration is historically obtained from a
   `us-central1` control-plane hostname. It must remain explicitly classified
   as a payload-free control read and must never be confused with or used as an
   inference fallback.
4. Python cannot prove physical erasure of transient in-process bytes. The
   enforceable claim is bounded non-persistence: no raw content in files,
   logs, exception output, audit events or child-process output, followed by
   process/container teardown.
5. Docker/host networking provides the relay with bridge egress. Safety relies
   on the fixed relay program, exact host target, ephemeral bearer and exact
   broker endpoint enforcement; it is not a general network sandbox proof.

## Recommendation

Proceed with a dedicated A3/B3 coordinator and contract module that reuse the
proven isolation topology and preflight checks, while adding exact no-redirect
egress, race-free one-use admission, a clean four-call/USD-1 tranche ledger,
lane-specific proofreaders, exact-path evidence and inter-turn residue gates.
Do not call either historical occupied runner directly and do not reuse its
historical cost or attempt ledgers. Occupied execution is safe to admit only
after deterministic dry-runs, fresh source-only veto, exact just-in-time
preflight and zero-residue readback all pass.

No provider, credential, cloud, Docker, database, test, deployment or Git
operation was performed by this advisory lane.
