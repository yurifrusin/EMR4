# Reception One Bureau runtime UI wiring closeout

Status: accepted provider-free development result
Recorded: 2026-07-30
Result: `reception_one_bureau_runtime_ui_provider_free_pass`

## Result

Reception One now exposes a compact planner selector only behind the explicit
authored-synthetic development gate. Standard deterministic planning remains
the default. Selecting Isolated model sends only the closed
`isolated_vertex` planner value and remains subject to the backend's separate
default-off model gate.

The browser renders only proofreader-admitted typed proposal fields and the
bounded provenance tuple:

- planner mode;
- proofreader disposition;
- provider-call count; and
- opaque runtime audit reference, when supplied.

Raw prompts, raw provider responses, credentials, hidden reasoning,
unverified drafts, provider configuration and raw database identifiers do not
enter this UI contract.

## Live-local acceptance

The non-intercepted browser/FastAPI/PostgreSQL acceptance passed with
authored-synthetic data:

- an ordinary Bureau load did not expose the development control;
- the explicitly gated Bureau exposed the selector and defaulted to Standard;
- the deterministic request returned HTTP 200 and an admitted proposal;
- the displayed provenance was `Standard planner`, `Proofreader admitted`,
  `0 provider calls`;
- the response remained proposal-only and required confirmation;
- no confirmation or appointment write occurred;
- database counts and canonical hashes were unchanged;
- selecting Isolated model with its backend gate disabled returned HTTP 403
  before context or provider use;
- the failed request cleared the earlier provenance and did not fall back;
- browser acceptance traffic was loopback-only;
- no provider environment or API-key path was forwarded;
- credential reads and provider calls were both zero; and
- the exact disposable database, child processes and temporary runtime state
  were removed.

Evidence:

- `orchestration/prototypes/reception-one-bureau-runtime-ui-wiring/live-local-browser-backend-postgres-evidence.json`;
- `orchestration/prototypes/reception-one-bureau-runtime-ui-wiring/database-cleanup-evidence.json`;
- `orchestration/prototypes/reception-one-bureau-runtime-ui-wiring/deterministic-admitted-desktop.png`;
- `orchestration/prototypes/reception-one-bureau-runtime-ui-wiring/deterministic-admitted-compact.png`; and
- `orchestration/prototypes/reception-one-bureau-runtime-ui-wiring/isolated-gate-closed.png`.

## Verification

- 136 focused UI, dual-planner, proposal-runtime, availability-reconciliation, functional meta-grid,
  integrated Bureau, API Spine and Compass tests passed.
- Python compilation passed for the acceptance harness and focused tests.
- JavaScript syntax checks passed for `diary.js` and `meta-grid.js`.
- The live-local acceptance used no route interception.
- An independent in-app static visual pass reproduced the standard-planner
  projection and its bounded provenance. It found no application console
  errors; the only log was the expected Office.js warning outside an Office
  host.
- JSON, YAML, Compass rendering, repository diff and residue checks form part
  of the final pre-acceptance matrix.

## Candid claim boundary

This proves a development-only, authored-synthetic UI selection and provenance
surface over the accepted proposal route. It proves that the deterministic
default works with zero provider calls and that a disabled isolated mode fails
closed without fallback or stale provenance.

It does not prove a live model response through this browser control, safety
for product-derived or patient data, production suitability, representative
receptionist usability, appointment mutation, voice, Word integration,
deployment or release. It makes no claim about Australian physical or
sovereign processing because no provider call occurred.

## Remaining authority gates

A live isolated-planner request initiated from the Bureau would be a new
occupied-provider result and requires a fresh exact call authority and
pre-attempt gate. Product-derived, patient, health, clinical or historical
data; confirmation; writes; participant sessions; voice; Word; production;
deployment; and release remain closed.
