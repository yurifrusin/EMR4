# Context Fabric admission replay winner recovery

Date: 2026-08-08

Status: bounded provider-free renderer candidate; runtime remains closed

Renderer `2.0.20` adds one sealed effective recovery operation,
`NORMALIZE_ADMISSION_RELOAD_WINNER_PREDICATES`, for the three admission
`INSERT_OR_RELOAD_COMPARE` nodes. The operation removes only the volatile
`admitted_at = transaction_timestamp()` term used when reloading an already
committed winner.

The change deliberately preserves:

- the exact eight-column primary/conflict key;
- every stable caller-derived and semantic winner comparison;
- database-authored `admitted_at` insertion;
- immutable storage and return of the original `admitted_at` value;
- all roles, capabilities, RLS, SQLSTATE, transaction and command boundaries;
- the immutable structural and body parent contracts.

The regenerated inert artifact remains 424 statements and is now 1,436,664 LF
bytes with SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`.
The render manifest canonical SHA-256 is
`2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`.

No PostgreSQL/Docker run, application migration, operational database,
watcher/feed, application/API/Diary wiring, provider, patient/clinical/product
data, deployment, release, Pages or protected-ref movement is opened by this
candidate. The changed function catalogue requires fresh disposable
parse/catalogue characterization and exact reproduction after independent
review, before any newly numbered behavior rehearsal.
