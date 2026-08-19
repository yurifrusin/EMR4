# Provider-free default-off check-in environment-manifest and secret-posture architecture plan

Date: 2026-08-19

Timestamp: 2026-08-19T15:14:32.6382318+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `8cc8aaf5e52c97ed46b868afb0ee6038eb1cf40a`

Accepted successor-resolution source: `f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e`

Accepted readiness source: `27101faa86b5aa3850e90bc4ded8600e5f8d7dc9`

Accepted admission architecture source: `752b521c59f5b44bf46de0cf776a33ac74b8134d`

Accepted unmounted kernel source: `4204ec6348abb0f92b1a30314699d4a469fa860a`

Target result:
`raisa_provider_free_default_off_check_in_environment_manifest_secret_posture_architecture_pass`

Reasoning level: Extra High freezes a future environment and credential-custody
boundary. High is sufficient for the bounded contract, schemas, deterministic
validator, hostile proof and closeout while this plan remains unchanged.

## Objective

Close the architecture portion of the accepted
`environment_manifest_and_operational_secret_posture` evidence gap. Freeze one
non-secret manifest type for a future ordinary check-in environment, one exact
logical runtime-role binding, three opaque secret/key-reference slots, current
rotation-evidence references and a deny-only break-glass posture.

The canonical current population remains empty. This tranche creates no
manifest instance, secret, key, database role, database connection, practice
selection, admission record or runtime configuration. Its output is not
operational evidence and cannot satisfy the ordinary-admission gate by itself.

## Exact source boundary

The validator decodes strict UTF-8, normalizes CRLF to LF, rejects remaining
bare CR bytes and compares SHA-256 over canonical LF bytes before releasing any
claim.

| SHA-256 | Exact source |
|---|---|
| `630e2745beebeff184ed48861c86607f3b68d764ad023f688c63a509f3d13edb` | `docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md` |
| `75812ad3f92fd7c8cbaa5b50492b6ac23edadfd0cc06bd312870fb19a18ebbab` | `orchestration/continuity/raisa-provider-free-clockwork-governed-check-in-successor-resolution/successor-resolution-report.md` |
| `3bffad89188d3f700e769d4d39301b8f440d763b21d0e4b7c64fe67354ed78ba` | `docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md` |
| `81a4a92e4f1f7e539282a646d59474420309f2f93785fe2c007e413ef26c297f` | `orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review/admission-readiness-review-report.md` |
| `744c175e18b335bd02cb954e501d6d3cba99744b052fc1e34f4b445050cc49f1` | `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture-plan.md` |
| `ce520b9d8c90d46aba7cb5bad1c59585d508d9d1849051443c5a45e1a68371ab` | `docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture.md` |
| `505120968572362a7df8d67ab1d95947ed1cd467df0fbc520aca73a704755ba9` | `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json` |
| `9223066a1a0d7413c449e3916953f0b0e04db389fc5fea8c3283eb917471a807` | `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/architecture-report.md` |
| `4a2a4a4c0a926a8362f62d77353ae88b3dc2778cf4701a56282915c88cb37391` | `docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-plan.md` |
| `d2ad88328ae235d5eb5b059087c7bf896b37d93f66f8ed379677c7a5ba1c1511` | `orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/contract.json` |
| `10f619e4dc8d10228e1f4c06c0b98da45cf073a2715fdbde30cf1aa0fb3f0233` | `orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/kernel-rehearsal-report.md` |
| `c31eb51ece0eb8c49054ce76cee57f64c21fe50c07da716c112cdc01627a0ebe` | `.env.example` |
| `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` | `app/config.py` |
| `2da2b2d584391755a1d9de4e274d59f05dcc24b6b5a3737a35efae49c7f6b117` | `app/database.py` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |

After this freeze, implementation reads are limited to those sources, this
plan, its architecture/threat documents and owned outputs. The local `.env`,
secret stores, process environment, database, network, provider and product
runtime are outside the read boundary.

## Frozen manifest type

The future typed manifest is declarative input under the API Spine YAML
manifest layer; typed code remains the enforcing authority. The contract owns
one closed JSON Schema for the equivalent normalized reading. A YAML loader is
not implemented here.

Every future instance must bind exactly:

1. one manifest identifier, environment class and environment identifier;
2. one monotonically versioned admission-snapshot generation;
3. one resolved lowercase 40-character authority Git object;
4. one server-owned opaque practice-scope reference;
5. one exact logical runtime-role binding;
6. the three ordered opaque secret/key-reference slots;
7. one current rotation-evidence reference per slot;
8. one deny-only break-glass posture; and
9. issued-at and expiry timestamps.

Unknown fields, missing bindings, wrong order, duplicates, abbreviations,
wrong-environment reuse, stale instances and multiple current manifests deny.
The manifest never constitutes ordinary-practice activation authority.

## Runtime-role binding

The exact logical role is
`appointment_check_in_ordinary_runtime_v1`. A future instance supplies a
non-secret physical database-role identifier and a credential reference; it
must also bind an independent tenant-role attestation reference.

The required claims are non-owner, `NOBYPASSRLS`, no product-relation
ownership, exact-environment identity and cross-tenant denial. They are
expectations only in this architecture. This tranche creates no role and
asserts none of those claims operationally.

## Secret/key-reference slots

Exactly three ordered slots are frozen:

1. `database_connection_credential`;
2. `application_token_signing_key`; and
3. `admission_snapshot_verification_key`.

Each future binding carries only a provider namespace, opaque `secret-ref:`
identifier, non-secret key identifier, version, rotation-policy reference and
rotation-evidence reference. Raw values, passwords, tokens, connection URLs,
private keys, environment-variable values, secret material hashes and secret
manager endpoints are forbidden. Slot reuse, key reuse across slots and
cross-environment reference reuse deny.

## Rotation evidence

Every slot requires a separate immutable evidence reference, SHA-256 artifact
digest, full resolved authority Git object, observation time, freshness expiry,
monotonic rotation sequence, exact environment/slot/key binding and independent
verifier reference. The future evaluator compares the evidence rather than
trusting a manifest claim. Missing, stale, self-verified, wrong-version or
wrong-generation evidence denies. The rotation cadence remains a referenced
operations policy; this architecture does not invent or enact a custody
schedule.

## Deny-only break glass

Break glass can only reduce authority. The represented states are `inactive`,
`engaged_deny` and `retired`. Missing or malformed posture denies. Only exact
`inactive` permits the environment evidence gate to continue; every other
state denies the ordinary lane. Break glass cannot supply a secret, skip
rotation, attest a role, activate a practice, clear the global kill switch or
grant command authority. Recovery requires a new manifest generation and fresh
independent evidence; automatic clear and last-known-good fallback are absent.

## Evaluation boundary

The future evaluator validates shape, digest, full-object resolution,
environment, uniqueness and freshness; binds the exact role and three slots;
requires current independent rotation/role evidence; denies on break-glass
posture; then returns only an operational-evidence-gate reading. It cannot
admit a practice or execute check-in. The existing feature flag, synthetic
allowlist, admission state machine, kill switch and route/kernel remain
unchanged and independently mandatory.

The canonical current posture has zero environment manifests, zero selected
practices, zero role bindings, zero secret references and zero operational
evidence artifacts. Its result is exact default denial.

## Exact owned outputs

Sol may create or update only:

- this plan and its architecture/threat documents;
- one normative architecture contract, its closed schema and one closed future
  environment-manifest schema under the named Continuity directory;
- one provider-free deterministic validator, focused tests and derived
  evidence/report;
- required Ariadne receipts and exact-candidate review artifacts; and
- closeout, Sol acceptance, Yuri summary and clockwork-owned canonical
  closeout surfaces if the tranche passes.

No existing `.env*`, `app/**`, migration, API/OpenAPI/GraphQL, product test,
database, client, deployment or provider source is editable.

## Deterministic acceptance

Pass requires:

1. the fresh five-source receipt and all three lane dispositions pass;
2. all sixteen exact source hashes match before semantic validation;
3. one closed architecture schema validates one normative contract and one
   closed environment-manifest schema validates its bounded synthetic shape;
4. canonical instance, practice, role, secret-reference and operational-
   evidence counts remain zero;
5. the exact logical runtime role and all non-owner/`NOBYPASSRLS` expectations
   are frozen without an attestation claim;
6. the three ordered reference slots permit no raw secret/value/URL endpoint
   field and cannot be reused across slot or environment;
7. every slot requires fresh immutable independently verified rotation evidence
   bound to exact environment, key, version, generation and full Git object;
8. break glass is deny-only, missing posture denies and no state can increase
   authority;
9. the future evaluator returns only an evidence-gate reading and cannot admit,
   mutate, connect, resolve a secret or execute a command;
10. a seven-character object, stale evidence, duplicate slot, wrong
    environment, secret-value field and break-glass bypass fail closed;
11. at least 160 architecture-contract and 48 future-manifest hostile
    mutations fail with zero escapes;
12. focused tests, accepted kernel/readiness tests, latch, Baton, register,
    compilation, Ruff and `git diff --check` pass;
13. one fresh Gemini 3.7 Flash/high exact-candidate read-only veto passes with a
    clean unchanged review worktree; and
14. the third live clockwork tick publishes exactly once with no bespoke
    updater, while protected refs stay exact and all unrelated untracked paths
    remain preserved.

## Parallelism assessment

- **DeepSeek:** declined. This is one serial normative authority contract;
  occupied native-Harness EMR4 work remains behind its HMR boot proof and
  Claude Code is not a fallback.
- **Gemini:** reserved for one independent exact-candidate read-only veto after
  deterministic admission.
- **Native subagents:** declined under current developer policy and because the
  contract, schemas and validator form one indivisible semantic boundary.

## Claim and successor

Passing closes only the architecture portion of the environment/secret-posture
gap. Operational evidence remains absent. The next dependency-satisfied
tranche is a provider-free disposable-PostgreSQL check-in runtime-role and
tenant-isolation attestation rehearsal using authored-synthetic identifiers and
an ephemeral manifest fixture. It must separately authorize any database use.

No ordinary-practice enablement, feature/allowlist change, product/config/API
change, route mount, generic-status `Arrived`, grammar/client change,
waiting-area movement, product/patient/clinical/protected data, live secret,
production runtime, deployment, release, Pages or protected-ref movement is
authorized. Preserve `docs/branding/`; stage explicit paths only.
