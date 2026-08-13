# Provider-free unmounted status-confirm product-adapter rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T10:12:35+10:00 (Australia/Brisbane)

Status: frozen

Revision: 2 — proposal-time version binding recovery

Source HEAD: `3c5d69512358cf7308c80e0da070d6650acb7f73`

## Objective

Close the four coupled application-owned blockers accepted by the route-mounting
readiness re-review without mounting or calling a route and without executing a
database. One new product adapter must translate authenticated status-confirm
input into the accepted unmounted composition while preserving its physical
transaction, receipt and public-response contracts.

## Exact input boundary

After freeze, implementation and review may read or content-search only these
exact existing sources and the newly owned outputs below:

| Existing source | SHA-256 |
|---|---|
| `app/services/appointment_status_composition.py` | `42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a` |
| `app/services/appointment_status_physical.py` | `4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b` |
| `app/models/appointments.py` | `d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915` |
| `app/models/tenancy.py` | `6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431` |
| `app/schemas/appointments.py` | `d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d` |
| `app/services/diary/confirm_actions.py` | `7b37dce383b5f36fa831e6b3221d5cd897bc24bb0c6fd9637b11a7a6bc9b2561` |
| `app/services/bernie_turn_evidence.py` | `e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467` |
| `app/services/auth_service.py` | `c7380e744bc42be006b34546769b76eb3b8f010b8602513a64f3865c76c1f33c` |
| `app/dependencies.py` | `d44f777f742074f0ee4717d599d7ee71dd6343c7096c87793149c727c1c4b0a9` |
| `app/routers/appointments.py` | `59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb` |
| `docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-closeout.md` | `c75c7c707ab0023cf8d4bf4a90dfe638c36179fbd1a87b81397cda51fea5e10f` |
| `orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview/route-mounting-readiness-rereview-contract.json` | `f472b722c3a7fcffb81d901b64a5c2d5135c201b6361d31a213d098197021b46` |
| `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal/provider-free-composition-evidence.json` | `694d8bc0302feb9b8b99013634ab80b9b60ce0919759dad8f16c1a2382c3e306` |

No repository-wide or directory-wide search is permitted after this freeze.
Existing application, model, schema, route, migration and API Spine sources are
read-only. The adapter must not be imported by a router.

## Owned outputs

- `app/services/appointment_status_product_adapter.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal/` containing one closed contract, schema and generated evidence;
- `scripts/raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal.py`;
- `tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py` and one focused plan/evidence test; and
- closeout, Sol acceptance, Yuri summary and continuity artifacts after the
  implementation gate passes.

## Frozen adapter responsibilities

1. **Authenticated server session.** Accept the raw bearer value only as a
   server dependency output, require a positive explicit HMAC secret and expose
   only a 64-character session reference. Never copy, store, log or release the
   bearer value and never accept a client-chosen session identity.
2. **Fresh command session and current authority.** Use an injected fresh
   command-session factory so the accepted physical `db.begin()` does not nest
   inside the request dependency's transaction. Before each RLS-protected
   operation, restore exact transaction-local `app.current_practice_id`; re-read
   the actor and require active, exact practice, exact role and exact target
   practice on both physical authority checks.
3. **Status-only admission.** Accept only
   `AppointmentStatusProposalOut` / `update_appointment_status` and reject the
   waiting-area proposal family before constructing or entering the physical
   transaction. Preserve explicit confirmation, signed evidence, idempotency and
   exact warning acknowledgement.
4. **Proposal-time state/version binding and locked policy reconstruction.**
   Verify the signed proposal-time state independently of the later current
   appointment. Because the accepted evidence envelope omits
   `appointment_state_version`, require a separate opaque server-minted HMAC
   binding over that exact evidence signature and positive proposal-time
   version. This keeps the initial kernel request byte-stable after a successful
   write and permits response-loss replay without weakening stale-generation
   detection. Rebuild appointment state and freshness from the locked
   appointment, require its actual positive version to match the bound request
   generation through locked-request equality, recompute exact warning codes
   and block same-state or terminal re-transition. The binding is an off-route
   adapter contract only; the unchanged product route neither emits nor accepts
   it in this tranche.
5. **Atomic effect and audit identity.** Mutate only the locked appointment's
   status/reason/waiting-area fields, stage exactly one attributable
   `AppointmentAuditLog` bound to the physical command and session reference,
   flush/refresh the database-owned adjacent version and return the audit
   identity plus the complete existing public envelope to the accepted
   composition.

## Rehearsal and acceptance

The deterministic rehearsal uses authored-synthetic Python objects, an injected
fake command session and an injected fake transaction factory. It must not load
configuration, `SessionLocal`, a server or a real database.

It must prove at least these cases:

- clean execute and byte-identical replay through the accepted composition;
- bearer minimisation and distinct-token/session separation;
- empty bearer, short secret, inactive actor, role/practice mismatch and
  authority revocation before and after idempotency classification;
- waiting-area-family rejection before transaction entry;
- exact status-only command/operation/route binding;
- same-state, terminal re-transition, warning mismatch, signed-evidence failure,
  stale freshness and changed locked generation stops with zero effect;
- missing, malformed, tampered or cross-evidence proposal-version bindings stop
  before transaction entry;
- one mutation, one audit, command/audit/session correlation and adjacent
  version on success;
- corrupt effect target, missing audit identity, wrong public projection and
  incomplete receipt fail closed; and
- response-loss retry releases the exact stored canonical bytes without a
  second effect.

At least 80 hostile contract mutations must be rejected. Focused tests, the
canonical fast profile, baton checks and Git whitespace must pass. All thirteen
input hashes must remain exact and `app/routers/appointments.py` must remain
unchanged and contain no product-adapter import.

## Claim and non-authority

Passing proves only an unmounted application-owned adapter contract and its
authored-synthetic in-process behavior. It does not prove an HTTP route,
dependency wiring, real transaction/RLS behavior, product database operation,
concurrency, restart, unknown commit or UI behavior.

No route edit/mount/call, real database/source, product/patient data,
provider/ADC/credential/IAM/browser/network, executable tool, command/write,
deployment, production, release, Pages or protected-ref movement is authorised.

## Revision-2 recovery rationale

Implementation discovery found that a proposal-time source version cannot be
reconstructed safely from the accepted signed status evidence after a
successful write: the appointment has advanced, while the evidence binds only
the state fields used by the existing freshness identifier. Using the fresh
post-write version before idempotency classification would change the request
digest and defeat exact lost-response replay; ignoring the version would weaken
the frozen-generation check. Revision 2 therefore adds the narrowest off-route
server-minted version binding. It changes no existing schema or route and leaves
its future HTTP carriage as part of the already-classified route-transport
partial.
