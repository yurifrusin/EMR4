# Raisa provider-free native-Diary application-session practitioner composition design

Date: 2026-08-03

Status: architecture-only static contract

Parent: `bernie_davida_parallel_seam_pass`

## Boundary classification

`default_off_deterministic_native_diary_composition_over_shared_application_session_product_read_bridge`

The composition is a deterministic consumer branch, not an agent. It receives
no model interpretation and passes through neither Bernie, Davida nor either
agent proofreader. It reuses only the lower application-session and authorized
product-read bridge. It does not reuse the Office consumer's one-use terminal
reload/logout lifecycle because the native Diary is a long-lived browser
surface.

## Topology

```text
native Diary long-lived browser surface
  -> (feature off, default) existing bearer-authenticated GraphQL read
     + existing REST fallback, byte-for-byte unchanged
  -> (feature on, future bounded step) deterministic composition
       -> lower application-session/product-read bridge only
            -> Surface.NATIVE_DIARY session, CSRF, exact origin
            -> endpoint-owned policy
                 practice-practitioner-directory-read.v1
                 action practice.practitioner-directory.read
                 resource practitioner_directory
            -> fresh practice-scoped read
                 Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)
                 { id displayName roleLabel active defaultLocation { id name } }
  -> backend remains sole database and command authority
```

## Static contract binding

- `surface`: exactly `Surface.NATIVE_DIARY` (`native_diary`).
- `policy`: `practice-practitioner-directory-read.v1`.
- `action`: `practice.practitioner-directory.read`.
- `resource`: `practitioner_directory`.
- `read`: `Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)`.
- `projection`: exactly `{id, displayName, roleLabel, active, defaultLocation {id, name}}`.
- The composition permits only an authenticated, practice-scoped fresh read.
  Session artifacts, authority envelopes and raw identifiers are never UI data.

## Default-off preservation

The composition is unmounted and default-off. When the feature is off, the
current native Diary bearer-auth GraphQL read and its existing REST fallback
remain byte-for-byte unmodified and behaviourally unchanged. The contract
declares this as an invariant, not a default convenience. No Diary HTML/JS/CSS,
shared auth, model, migration, route or composition-root change is made.

## Failure behaviour (fail-closed)

- Mismatch (wrong surface, missing/invalid session, cross-practice scope,
  inactive-enumeration request): fail closed with generic denial and no
  practitioner row released.
- Stale/superseded response: a response produced against an older session,
  generation or revision is rejected before any UI update; the consumer must
  issue a fresh read. No cached or superseded directory data is rendered.
- Privacy: session artifacts, authority envelopes and raw identifiers never
  enter UI copy or durable evidence. Evidence carries counts and fixed
  authored-synthetic labels only.
- Audit unavailability: the bridge releases no directory data when the
  required authorization audit cannot be admitted.

## Deterministic acceptance cases

1. Exact `Surface.NATIVE_DIARY` and policy/action/resource binding.
2. Exact read query, variables and display-safe projection.
3. Off-path byte-for-byte preservation of the current bearer GraphQL read and
   REST fallback.
4. Fail-closed mismatch and stale/superseded rejection.
5. Privacy: no session artifacts, authority envelopes or raw identifiers as UI
   data.
6. Forbidden dependency absence (Bernie, Davida, probabilistic interpretation,
   agent proofreader, Office one-use terminal lifecycle).
7. API Spine remains scoped read-only: no mutation, command tunnel, new REST
   surface or event actuator.

## Residual risks

- Native-Diary UI wiring and the unmounted provider-free composition runtime
  are later lane steps; this tranche claims no runtime or usability result.
- Long-lived surface session revocation and stale reconciliation are design
  obligations for a later step.
- General application-session GraphQL mounting is not opened; only the exact
  practitioner-directory composition is described.
- Real identity, production and release suitability are not established.

## Safe implementation handoff

The next bounded lane step is the provider-free unmounted composition contract
plus direct HTTP/PostgreSQL evidence, with no native Diary asset edit and no
`app.main` mounting. Every write, provider, real identity, deployment and
default-on switch remains closed. This design is advisory and review-oriented;
it opens no blocked gate.

## API Spine conformance

GraphQL remains a named, scoped read/context graph only. The composition
introduces no mutation, command tunnel, new REST surface or event actuator.
Any auditable or state-changing work would remain an explicit REST/OpenAPI
command under separate authority. YAML manifests remain declarative inputs,
never executable policy engines.
