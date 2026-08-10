# Context Fabric parse characterization evidence-routing recovery threat-model delta

Date: 2026-08-10

This recovery changes no application, API, Diary, migration or operational
database surface. It separates the disposable parse harness's three evidence
classes so a deliberately non-accepting characterization cannot overwrite
either the last accepted pass or an immutable historical exact-rerun failure.

The relevant failure mode is evidence confusion: a valid characterization
result could erase a different protected failure record because both were
routed by the same broad non-pass branch. The control is exact result-class
routing to three distinct repository paths, backed by a mutation-oriented test
that pre-populates all three targets and proves that each write changes only its
own target. The current characterization and the restored historical files are
also hash-bound before any fresh database contact.

This does not make database failure impossible. It makes the evidence path
fail-closed and auditable, preserving the information required to diagnose and
recover from a failure without promoting characterization into acceptance.
Provider calls, product/patient/clinical data, source listeners, runtime wiring,
applied migrations, deployment, production, release, Pages and protected-ref
movement remain closed.
