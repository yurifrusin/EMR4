# Provider-free default-off check-in environment-manifest and secret-posture architecture

Date: 2026-08-19

Status: source-bound architecture; no manifest instance or enablement

Source HEAD: `8cc8aaf5e52c97ed46b868afb0ee6038eb1cf40a`

## Outcome

The future ordinary check-in lane now has one precise answer to “which
environment, role and credential-custody evidence is being asserted?” without
placing a credential or an ordinary-practice grant in the repository.

The architecture separates three things that are easy to conflate:

- a non-secret environment manifest describes exact identity and references;
- operational evidence later proves the referenced role, rotation and custody
  facts; and
- the accepted admission evaluator decides whether all gates permit a future
  active record.

None substitutes for either of the others. The current population is empty and
therefore denied.

## One normalized reading

The normative architecture contract and future normalized manifest schema live
under
`orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/`.
YAML may be the human-authored API Spine format later, but typed code must first
normalize it to this exact closed reading. Unknown keys and permissive YAML
features cannot become runtime authority.

A future manifest binds one environment identifier, class, snapshot generation,
resolved full Git object and opaque server-owned practice reference. It also
binds the exact logical role `appointment_check_in_ordinary_runtime_v1`, one
non-secret physical role identifier and the evidence reference that later
attests non-owner, `NOBYPASSRLS`, exact-tenant behavior.

## Reference, not value

The three slots are the database connection credential, application token
signing key and admission-snapshot verification key. A binding carries only an
opaque non-secret reference and key metadata. It does not carry a database URL,
password, token, private key, environment-variable value, secret material hash,
secret-manager endpoint or provider credential.

That distinction is machine checked by a closed schema plus a recursive
forbidden-field validator. The repository can therefore reason about custody
without possessing custody.

## Rotation as evidence

“Rotated” is not a Boolean supplied by the manifest author. Each slot binds a
separate evidence artifact by opaque reference, artifact digest, resolved full
Git object, exact slot/environment/key/version/generation, observation time,
freshness expiry, monotonic sequence and independent verifier reference.

The future evaluator must verify those artifacts and times. A changed key
version invalidates old evidence. Self-verification, missing freshness, stale
evidence, cross-environment reuse and a seven-character Git abbreviation deny.
The cadence itself belongs to a separately versioned operations policy.

## Break glass only removes authority

This architecture does not create an emergency bypass. Its break-glass state is
deny-only:

- `inactive` allows the evidence evaluation to continue;
- `engaged_deny` denies the ordinary lane; and
- `retired` denies the ordinary lane.

Absence or malformed posture also denies. No state supplies credentials,
attests a role, activates a practice, clears a kill switch or bypasses an
expired rotation. Recovery requires a new manifest generation and independent
evidence. There is no automatic clear or stale last-known-good fallback.

## Evaluation order

The future evaluator must:

1. validate closed shape, digest, full-object resolution, exact environment,
   uniqueness and freshness;
2. require one exact role binding and three distinct ordered secret-reference
   slots;
3. verify current independent role and rotation evidence against the same
   environment and snapshot generation;
4. deny unless break glass is exactly inactive; and
5. return only `evidence_gate_satisfied` or a closed denial reason.

That reading has no check-in, route, database, secret-resolution, practice-
activation or command capability. Even a satisfied future reading remains only
one prerequisite of the accepted ordinary-admission evaluator.

## Current and future claims

Today there are zero manifests, selected practices, runtime-role bindings,
secret references and operational evidence artifacts. Product configuration
still contains only the unchanged default-off authored-synthetic A5.1 controls.

Passing this tranche proves that the environment/secret evidence can be
represented without secret values and with fail-closed semantics. It does not
prove any ordinary environment, real role, secret custody, key rotation,
tenant isolation, database behavior, rollback recovery, deployment or
production posture.

The next useful proof is a separately authorized disposable-PostgreSQL
runtime-role and tenant-isolation rehearsal using authored-synthetic,
ephemeral identifiers. It must bind the same manifest type; it cannot turn this
architecture into ordinary-practice authority.
