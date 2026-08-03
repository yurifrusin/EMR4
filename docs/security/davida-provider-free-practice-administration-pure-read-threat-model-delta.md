# Threat-model delta: Davida provider-free practice-administration pure-read

Date: 2026-08-03

Status: provider-free, unmounted, non-executing, authored-synthetic

## Boundary change

No product or data boundary opens. This delta freezes the first pure-read
projection and minimal context-desk implementation of the accepted Davida
practice-administration boundary. The new active-location projection is a pure
side-effect-free read, and the context desk composes only caller-supplied
already-authorized projections plus opaque backend resource references.

| Threat | Control | Failure outcome |
|---|---|---|
| A new location read is sourced from a handler that normalizes or commits | Active-location projection is a pure read: exact `PracticeLocation.id`/`.name`, `db.no_autoflush`, no commit/flush/add/delete/normalization | Context source is ineligible; service purity gate fails |
| The active-location schema becomes permissive and leaks administrative fields | `ActivePracticeLocationOut` is strict extra-forbid with only `id` and bounded `name` | Schema admission fails |
| Room/waiting GET paths that normalize and commit are reused as context sources | `GET /diary/rooms` and `GET /diary/waiting-areas` remain blocked | Context source is ineligible |
| The live appointment waiting-room queue leaks patient-linked context | `GET /appointments/waiting-room` remains blocked as patient/clinical closed data | Context source is ineligible |
| The context desk emits an internal UUID to the model cell | Every internal UUID (including default-location IDs) is replaced with a registered opaque reference | Frame admission fails; no UUID emitted |
| Missing, duplicate, wrong-kind or cross-practice resource bindings reach the frame | Immutable bounded `ResourceReferenceRegistry` fails closed on construction/resolution | Composition fails closed before frame release |
| The frame is used as command, confirmation, write, proposal/apply, provider or event authority | `authority_ceiling` fields are all literal false; frames are minimal and non-authoritative | Schema admission fails |
| Model output or a composed frame becomes database or roster truth | Database truth remains authoritative; frames are non-authoritative context only | No frame is authoritative |
| Non-deterministic composition hides stale/duplicate context | Fixed inputs produce identical frames and one SHA-256 content revision | Repeated inputs yield the same frame/hash |
| Naive time or unsupported values enter the frame | The composer requires a timezone-aware `observed_at` and bounded opaque refs/correlation | Composition fails closed |
| The machine contract schema is permissive (the earlier defect) | `context-contract.schema.json` uses required fields and `additionalProperties: false` throughout, with adversarial mutation tests | Mutated authority/shape-bearing contract fails validation |
| The acceptance evidence leaks DSN, role names, passwords, IDs or names | Evidence persists only counts, booleans, hashes and safe fixed labels; sensitive-match guard fails the run | Evidence is rejected |
| The acceptance leaves a database or roles behind | Disposable database and the two finite product-read roles are dropped and absence verified even on failure | Cleanup gate fails |
| Concurrent tests corrupt the shared PostgreSQL test schema | Repository pytest and shared PostgreSQL processes remain serial | Dispatch scheduler withholds the conflicting test run |
| Convenience staging captures the user-owned branding directory | Explicit-path staging only; `git add -A`/`.` and helper commit-message staging are forbidden | Pre-commit gate fails |
| Worker authority is mistaken for acceptance/integration authority | Worker implements only; reviewers return one decision; root Sol alone accepts and integrates | Candidate remains non-authoritative |
| Standing tranche authority silently expands to providers, real data or deployment | Explicit stop conditions and closed-gate list survive every lane packet | Root pauses for Yuri |

## Residual gates

Live providers, memory/RAG/GraphRAG, real identity, patient/clinical/document
data, autonomous/model-to-database writes, GraphQL mutations, REST command
credentials, proposal/apply authority, external identity writes, cloud/IAM,
deployment, production, release, protected evidence and protected refs remain
separately closed. No runtime claim is made.
