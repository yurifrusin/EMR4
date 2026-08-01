# Threat-model delta — Bureau cost-bounded occupied retry

Status: active
Recorded: 2026-07-31

## Added attack surfaces

- Repeated fresh provider attempts could silently exceed the authorised USD 1
  total.
- A retry could reuse a consumed ledger or unchanged request and obscure the
  true call count.
- The browser could submit before the exact appointment row is selected.
- A cost or proofreader failure could trigger deterministic fallback, a second
  provider call, or an unverified release.
- Child environments could inherit provider-key or Google credential
  configuration.
- A fixed-height result projection could hide later matching times behind the
  request bar or create a nested scroll trap that makes a valid result
  unreachable.

## Controls

- One hash-chained cumulative cost ledger includes the preceding HTTP 200 call,
  reserves USD 0.02 before every new call, and refuses a reservation that could
  cross USD 1.
- Each route dialogue is limited to one provider call; every new attempt uses
  distinct route, attempt and one-use ledger identifiers.
- A fresh call must follow a diagnosed change or exercise a new acceptance
  proof. Unchanged duplicate calls are denied.
- The browser must visibly click the exact disposable appointment row and
  verify `aria-selected=true` before selecting the isolated planner and
  submitting.
- The credential-free cell communicates only with the one-use broker; the
  broker alone may refresh the existing impersonated ADC and call the Sydney
  Vertex hostname.
- Provider/API-key variables and Google Cloud configuration are omitted from
  owned child environments without inspecting their host presence.
- The deterministic proofreader is the sole release gate. Failure returns no
  typed proposal and cannot invoke Standard fallback.
- Confirmation and write paths remain outside the occupied run.
- Result-heavy projections grow to a bounded desktop height. The result canvas
  alone owns stable, styled vertical overflow; provider-free browser evidence
  proves that the last authored-synthetic result remains reachable while the
  request bar stays visible and separate.
- Every attempt ends with independent container, image, network, token,
  process, temporary-directory, port and disposable-database residue checks.

## Residual risk

Google's token accounting and later billing statements remain provider-owned.
The ledger is an evidence-backed estimate using the provider's returned token
usage and current published Standard rates; the USD 0.02 pre-call reservation
adds headroom but is not a billing-system quota. Any usage ambiguity, missing
token metadata or possible unexpected charge stops the tranche.

The configured and observed `australia-southeast1` endpoint does not prove
Australian physical or sovereign processing.

The projection repair is Chromium evidence over an authored-synthetic fixture.
It does not establish every browser, zoom factor, operating-system scrollbar
mode or production data density.

## Closed gates

Real/product-derived/patient/health/clinical/historical data, API-key or static
key authentication, IAM or ADC changes, provider/model/project/identity/region
substitution, global inference, fallback, provider tools, grounding, retrieval,
cache creation, confirmation, writes, voice, Word, participants, production,
deployment and release remain closed.
