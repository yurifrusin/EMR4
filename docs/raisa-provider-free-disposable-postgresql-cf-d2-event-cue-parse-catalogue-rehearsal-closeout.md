# Provider-free disposable PostgreSQL CF-D2 event and cue parse/catalogue rehearsal closeout

Date: 2026-08-13

Timestamp: 2026-08-13T19:56:16+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `579e9e0e86bd92469d82eb1199e8b3120808844e`

Result: `raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_pass`

## Outcome

PostgreSQL 16 accepted the exact 12,022-byte `.sql.inert` artifact in one
newly created networkless, portless, tmpfs-backed container. The resulting
catalogue matched the accepted CF-D2 representation exactly:

- one dedicated schema;
- three domains and three validated domain checks;
- seven ordinary tables and fifty ordered columns with exact physical types,
  nullability and no defaults;
- seven primary keys, three unique keys, eighteen validated table checks and
  seven foreign keys;
- only the terminal-receipt-to-obligation reference deferrable and initially
  deferred; and
- zero functions, procedures, triggers, views, materialized views, sequences,
  policies, non-internal rules, row-security tables or explicit object ACLs.

All seven table row counts were zero. The exact captured container ID was
reverified, removed and proven absent. No image, volume, network, workspace
path or unrelated Docker object was removed.

## Issue found and resolved

Attempt 001 stopped safely inside readiness. `pg_isready` accepted the socket
before the immediately following authenticated server-major query was stable;
the harness incorrectly treated that transient as terminal. The artifact was
never executed and exact cleanup passed.

AER-0293 preserves the failure. The only correction keeps the authenticated
query inside the bounded readiness loop: a nonzero or malformed result resets
the consecutive-observation counter, and only three consecutive paired
socket/authenticated PostgreSQL-16 results admit SQL. Focused tests passed
before attempt 002, which completed successfully in a fresh owned container.

The lineage gate also exposed a stale test that assumed the live operation
latch must remain forever paused. It now verifies the latch's actual validated
state and terminal-response projection, so accepted workflow advancement no
longer invalidates the historical control.

## Verification

- six exact parent source bindings and the 12,022-byte artifact hash passed;
- all 64 hostile closed-contract mutations failed admission;
- 12 focused harness/contract/catalogue/containment tests passed;
- 245 combined register and focused tests passed after AER-0293;
- 126 CF-D2 lineage, latch, baton and Compass checks passed apart from the
  identified stale-latch assertion, then the repaired 48-test latch suite
  passed;
- the canonical fast profile passed Ruff, compilation of 209 maintained Python
  sources, 193 focused API Spine/handover/receipt/maintenance tests, Diary
  JavaScript syntax and Git whitespace; and
- exact source and origin task branch published at
  `579e9e0e86bd92469d82eb1199e8b3120808844e`, while local/origin `master` and
  `handoff/current` remained exactly protected
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No subagent, external worker, independent verifier or provider was selected.
Sol owned the small serial database harness, repair and acceptance under the
worker-economy rule.

## Claim boundary

This proves only that PostgreSQL 16 parses the exact artifact and creates the
frozen empty catalogue shape. `psql --single-transaction` contained the schema
installation; it does not prove any of CF-D2's five transaction protocols.
Validated constraints are catalogue facts, not a claim about all hostile row
behavior.

Events and cues remain acceleration hints. They cannot update Reception One,
establish freshness, confirm an appointment or authorize a command. Consumers
still perform fresh authorised source reads, and consequential commands still
recheck current authority and source truth.

## Next tranche

The next dependency-satisfied candidate is the narrowest provider-free
disposable PostgreSQL behavior/transaction rehearsal for the five already
frozen protocols: terminal admission, pending coalescing, contiguous
checkpoint advance, dispatch recording and reconciliation. Its scenarios,
lock/rollback observations and exact claim boundary must be derived and frozen
before execution.

Concurrency, restart, unknown commit, watcher/source access, runtime/product
wiring, operational persistence/retention, patient/product data, provider,
command/write, deployment, production, release, Pages and protected refs
remain closed. Yuri's attention is not required.
