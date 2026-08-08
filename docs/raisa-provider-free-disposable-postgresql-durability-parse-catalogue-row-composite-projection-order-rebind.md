# Disposable PostgreSQL parse/catalogue row-projection rebind

Date: 2026-08-08

Status: provider-free corrected-artifact parse/catalogue runtime passed; final
evidence acceptance remains pending a fresh exact-HEAD veto

## Parent recovery

Behavior attempt 015 stopped before admitting a scenario at `BTR-E01` with
SQLSTATE `22P02` and the exact allowlisted coordinate
`emr4_context_fabric.register_observer_generation_v1` line 36. The accepted
bounded source recovery restores complete binding and aggregate-alias row
projections to the physical PostgreSQL table-composite order and adds a
renderer invariant that rejects future positional drift before SQL rendering.

The corrected source is exact commit
`0931f3e658f06e02e7de4c5ea02238184da9e767`. The regenerated inert SQL remains
1,404,420 canonical UTF-8/LF bytes and statement count `412`, with SHA-256
`sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`.
The render manifest binds that same byte count, statement population and SQL
digest.

## Exact rebind

The existing disposable PostgreSQL parse/catalogue harness is rebound only to
that corrected source head and inert artifact digest. Its fixed image,
networkless/no-port/no-mount containment, two-database rollback-before-success
sequence, exact catalogue queries and digests, authenticated PostgreSQL 16
readiness, minimized evidence and exact-ID cleanup remain unchanged.

The physical catalogue is expected to remain identical because the recovery
changes only the order of complete expressions inside function bodies, not any
relation, column, type, role, policy, privilege, function signature or trigger
declaration. That is a claim to test, not an accepted runtime result.

## Evidence chronology

The predecessor parse/catalogue pass remains immutable evidence for inert SQL
`sha256:9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`.
It cannot prove the corrected artifact. Before the first corrected-artifact
container run, the predecessor evidence must be preserved under an explicit
historical filename, the rebound contract and tests must pass, and a fresh
read-only exact-HEAD Gemini 3.6 Flash/high veto must accept the candidate.

After the exact candidate passed its deterministic packet and a fresh r96
Gemini 3.6 Flash/high veto, one newly owned `postgres:16-bookworm` container ran
the exact rollback and success sequence. PostgreSQL admitted the corrected
artifact, all exact catalogue digests matched, and the exact captured container
ID was removed with absence verified. The runtime evidence is not final until
its exact committed evidence packet receives a separate fresh veto.

## Closed boundary

This rebind opens no behavior scenario, applied application migration,
operational database, durable storage, watcher/listener/feed, product/API/Diary
wiring, patient/clinical/product/protected data, provider call, tool, command or
product write, deployment, production, release, Pages or protected-ref
movement. The later behavior contract and twenty-scenario runtime remain
separately closed until this corrected parse/catalogue proof passes and the
behavior packet is rebound and independently accepted.
