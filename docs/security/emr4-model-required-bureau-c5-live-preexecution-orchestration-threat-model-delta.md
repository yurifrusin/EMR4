# Threat-model delta: C5 live pre-execution orchestration

Date: 2026-08-05

Status: provider-free source candidate; no live capability opens until exact-
HEAD deterministic and independent gates pass

Parents:

- `docs/security/emr4-model-required-bureau-c5-disposable-live-development-recovery-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c5-live-preexecution-orchestration-boundary.md`

## New boundary

The descendant adds one C5-only Vertex provider cell and one serial coordinator
around the already accepted controller. The provider cell may hold the existing
impersonated ADC token transiently in memory for one exact HTTPS request. The
controller/actuator receives no credential object or token, and the disposable
child receives the existing minimal credential-free environment.

No product route, GraphQL field, database, ordinary service, external worker,
container or background runtime is added. The API Spine contract remains
documentation-only and unmounted.

## New threats and controls

### Unreviewed or changed source reaches live execution

Controls: the pre-execution receipt binds the exact clean non-protected HEAD,
fresh Gemini 3.6 Flash/high pass, Ariadne five-source pre-sprint receipt, all
four protected refs, frozen plan/policy/catalog digests and a canonical hash
set of every runner, controller, target, schema, plan, threat and API artifact.
The runner rehashes every item and rechecks Git state and receipt expiry before
preflight or live capability construction.

### A stale generic review or generic continuation receipt is substituted

Controls: source review must be `completed`, use the exact Antigravity fresh-
project read-only transport, exact model/effort, exact identical before/after
HEAD, one `pass` and `dirty_after: false`. The Ariadne receipt must be
`pre_sprint_planning`, name exactly
`execute_frozen_serial_c5_live_rehearsal`, and contain the five exact mandatory
rehydration sources. Its separately hash-bound runtime state must contain the
same five source-evidence entries, exact current branch/HEAD/protected refs and
a bounded creation/expiry interval. The runner rereads both files, compares
their shared source evidence and rejects stale or substituted authority state
immediately before execution. All three evidence files are repository-scoped
and hash-bound.

### Provider routing follows a proxy or redirect

Controls: the request URL is constructed only from the frozen project, region,
endpoint and model; the opener has an empty proxy map and rejects redirects;
the final URL and HTTP status must match exactly. There is no fallback.

### Wrong ADC, service account or project is used

Controls: the existing read-only Sydney cloud preflight verifies the exact
project, model catalogue, endpoint, billing/API posture, disabled cache/logging
posture, no user-managed key and exact prediction-only identity. The provider
cell separately rejects `GOOGLE_APPLICATION_CREDENTIALS`, requires the
impersonated-credential class, exact ADC project, target service account and
cloud-platform target scope, then refreshes non-interactively. Codex performs
no credential, IAM or cloud mutation.

### Prompt, response, thoughts, error text or credentials persist

Controls: provider payloads and response bytes exist only in local variables
and are cleared after strict extraction. Durable attempt metadata passes a
closed allowlist of booleans, counts, hashes, finish reason, part kinds, safe
token counts and exact model version. Unknown keys, raw text and credential-
shaped fields are dropped. HTTP error bodies are discarded after hash/size
accounting. Final evidence stores only frame/candidate/proofreader/approval/
execution digests and sanitized receipts.

### Structured output schema becomes executable authority

Controls: the response schema contains no command, path, URL, port, PID,
executable, module, environment or credential field. The model selects only the
fixed runbook id. Local strict parsing, executable/product/credential/
sovereignty scans, deterministic evidence grounding, authority revalidation
and one-use evidence remain mandatory. The response never reaches the process
adapter directly.

### Correction silently becomes a generic retry

Controls: only a schema-valid primary candidate rejected by the deterministic
proofreader can create the closed ticket. The second request carries only the
same frame plus ticket id, field paths and reason codes; it cannot include the
prior response or preferred prose. Shared provider state verifies the ticket,
rejects unchanged candidates, increments the second call even on correction
transport/schema failure, and closes permanently. Cost accounting reserves
USD 0.25 per attempt, limits total calls to two and total reservation to USD
0.50.

### Fake-provider evidence is mistaken for an occupied pass

Controls: provider effects count only when the fixed live-capability adapter
reports contact. A provider-free fake can exercise the serial state machine but
must terminate as accounting failure rather than emit the occupied pass. The
focused regression proves this property.

### Child startup or Windows socket teardown race causes false evidence

Controls: only connection-refused is retried, against the same exact host/port/
path, for at most two seconds. Any response or different exception terminates
the startup wait. Post-fault, rollback and cleanup do not infer absence from an
HTTP exception: the exact owned process must be absent and the controller must
successfully reacquire the same address/port without `SO_REUSEADDR`. On Windows
every candidate socket sets `SO_EXCLUSIVEADDRUSE` before bind and only exact
address-in-use may be retried for at most two seconds. The successful reservation
is retained through generation 2, closing the substitution race. Reset and
timeout remain truthful diagnostic states and never prove absence.

### The terminated generation-1 process handle leaks or is confused with
generation 2

Controls: exact-port reacquisition is part of the absence proof. The controller
retains that reservation, then closes the exact terminated generation-1 handle
before provider admission. The later generation-2 handle replaces it only
inside the one-use execution critical section. Cleanup stops and closes the
remaining exact owned handle and proves the port can again be exclusively bound.

### Terminal failure leaves live resources or an open ledger

Controls: every path enters one `finally` cleanup. It closes cost reservations,
provider state and issued evidence, stops/closes owned processes, closes the
reservation, removes only the marker-bound directory and freshly proves no
process, listener, directory, open ledger or reusable capability. Cleanup
inconclusive can never be promoted to pass.

## Residual closed risks

This source does not prove product recovery, ordinary-service recovery,
database recovery, cross-host locks, durable production audit, service-manager
permissions, production identity separation, deployment, release, operational
incident response or sovereign processing. Those remain separate descendants.

Patient, clinical, participant, product-derived, protected and production data;
real practice databases; provider tools/retrieval; credential/IAM mutation;
deployment; production; release; Pages; protected evidence; protected refs and
Context Fabric runtime remain closed.
