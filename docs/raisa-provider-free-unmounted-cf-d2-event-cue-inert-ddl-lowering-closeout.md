# Provider-free unmounted CF-D2 event and cue inert-DDL lowering closeout

Date: 2026-08-13

Timestamp: 2026-08-13T18:45:10+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `cd890647d327a3d9bf4f60e5e1d6f9a1924bab29`

Result: `raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering_pass`

## Outcome

The accepted seven-relation event/cue representation now has one deterministic
PostgreSQL-16-shaped text artifact. It contains one dedicated schema, three
scalar domains, seven tables with fifty exact fields, seven primary keys,
three unique keys, eighteen row-check bindings and seven foreign keys. The
nineteenth accepted check label—`coordinate_is_non_authoritative`—is preserved
honestly as a semantic annotation because a row constraint cannot enforce
authority meaning.

All seven exact mutable-field declarations are retained with
`ddl_enforced=false`. The five transaction protocols and current source/
command authority remain explicitly unlowered. No trigger, function,
procedure, role, privilege or false atomicity claim was introduced.

## Verification

- the exact representation contract SHA-256 and source commit bind before
  rendering;
- two isolated renders are byte-identical;
- the canonical static recognizer accepts the exact `.sql.inert` artifact;
- all 65 removed, renamed, widened, payload-bearing, executable and
  overclaiming hostile variants fail closed;
- canonical SQL and manifest bytes remain unchanged through hostile checks;
- all 142 CF-D2/source-truth/API/latch lineage checks pass;
- Ruff and Git whitespace pass;
- the canonical fast profile passes 193 tests and compilation of 209
  maintained Python sources plus Diary JavaScript syntax; and
- exact source and origin task branch are published at
  `cd890647d327a3d9bf4f60e5e1d6f9a1924bab29`, while local/origin `master` and
  `handoff/current` remain unchanged at protected
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No external worker, independent verifier or provider was selected. Sol owned
the small tightly coupled parent binding, renderer, recognizer and acceptance.

## Issue resolved

The expanded lineage run found three historical tests that required the
active-operation latch to remain forever on the representation tranche. They
now test each immutable contract's declared next descendant instead. This
preserves historical evidence while allowing the current latch to advance
without repeatedly invalidating already-accepted tranches.

## Claim boundary

This proves deterministic structural text lowering only. The `.sql.inert`
file was not submitted to PostgreSQL and is not a migration. It proves no SQL
parse, catalogue creation, constraint behavior, transaction, lock, isolation,
concurrency, restart, unknown commit, delivery, retention, rotation, purge,
performance, source observation, application wiring, deployment or production
behavior.

Events and cues remain acceleration hints. They cannot update Reception One or
authorize a command. A consumer still performs a fresh authorised read, and
every consequential command still checks current authority and source truth.

## Pause and next tranche

Yuri explicitly requested a brief pause before the next tranche so Sol can
read and discuss `2509.26507v1.pdf`. The next dependency-satisfied tranche,
when resumed, is the provider-free disposable PostgreSQL-16 parse-and-catalogue
admission of this exact artifact. It remains separately gated and adds no
transaction behavior, runtime or product wiring.

Protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient clients, real identity, provider/ADC, credentials/IAM/network,
commands/writes, deployment, production, release, Pages and protected refs
remain closed. `docs/branding/` and all unrelated untracked files remain
preserved and excluded.
