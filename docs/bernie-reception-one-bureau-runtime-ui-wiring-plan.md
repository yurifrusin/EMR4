# Reception One Bureau runtime UI wiring plan

Status: authorised provider-free development tranche
Recorded: 2026-07-30
Predecessor: `reception-one-default-off-dual-planner-runtime-occupied-result`

## Objective

Connect the existing Reception One Bureau request surface to the accepted
default-off dual-planner proposal route without changing the current projection
design, deterministic default, proofreader authority or appointment boundary.

This tranche is provider-free. It will not call Vertex, read ADC, open a ledger
or represent fixture output as a live model result.

## User surface

The ordinary Bureau remains unchanged. A compact planner selector appears only
when all of these local development conditions are explicit:

- `smoke=true`;
- `bureau_runtime_ui=true`; and
- the existing authored-synthetic product-context route is selected.

The selector offers:

- **Standard** — `deterministic`, selected by default; and
- **Isolated model** — `isolated_vertex`, visibly a development option and
  still subject to the backend's separate default-off gate.

Choosing a label changes only the request's closed `planner_mode`. It cannot
set provider, model, project, identity, region, hostname, credential, cost,
fallback or data-class fields.

## Typed UI contract

The Diary bridge will send `planner_mode` to
`composeReceptionOneProductContextProposal`. A successful projection may
retain and display only:

- planner mode;
- proofreader disposition;
- bounded provider-call count;
- opaque runtime audit reference, when supplied; and
- the already admitted typed proposal fields.

It must not retain or display raw prompts, provider responses, credentials,
chain-of-thought, unverified drafts, raw database identifiers or provider
binding details.

When the selected planner fails or its gate is closed, the UI must discard any
earlier provenance and render the existing fail-closed projection. It must not
fall back to the deterministic planner.

## API Spine boundary

This remains an authenticated command-style read that prepares a proposal.
The backend owns practice scope, current context, identity resolution,
availability, freshness, proofreader admission and proposal adapters.

The browser gains no confirmation or write command. Every admitted result keeps:

- `requires_confirmation=true`;
- `proposal_only=true`;
- `write_performed=false`;
- `confirmation_performed=false`; and
- `model_database_access=false`.

## Provider-free acceptance

1. The planner controls are absent from an ordinary Diary/Bureau load.
2. The development selector is visible only under the explicit authored-
   synthetic query gate and defaults to Standard.
3. A real non-intercepted browser/FastAPI/PostgreSQL Standard request sends
   `planner_mode=deterministic`, returns HTTP 200, renders admitted provenance,
   makes zero provider calls and leaves database truth unchanged.
4. Selecting Isolated model while the backend gate is disabled sends
   `planner_mode=isolated_vertex`, returns the backend's fail-closed response
   before context read or provider contact, displays no stale provenance and
   makes no fallback call.
5. Browser traffic remains loopback-only and no provider credential or API-key
   environment is forwarded.
6. Desktop and compact-width layouts preserve the current appointment-sheet
   hierarchy and keyboard behavior.
7. Focused UI, API Spine, proposal runtime and JavaScript checks pass.
8. All child processes, temporary directories and disposable database state are
   removed.

## Evidence labels

The accepted browser run must be labelled
`live_local_browser_backend_postgres` because it uses no route interception and
reaches the real local backend and disposable PostgreSQL database. Any static
fixture check remains separately labelled `route_intercepted_browser` or
`authored_synthetic_client_fixture` and cannot support a live-route claim.

## Closed gates

No Vertex call, ADC read, API key, provider fallback, real or product-derived
patient data, historical Diary material, model-to-database access, appointment
confirmation, write, participant session, Word, voice, production, deployment
or release is authorised. No Australian physical or sovereign processing claim
is relevant to this provider-free tranche.
