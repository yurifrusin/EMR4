# Threat-model delta: top-level-XID insert/reload recovery

Date: 2026-08-09
Parent: provider-free disposable PostgreSQL durability behavior rehearsal

| Threat | Recovery control | Residual boundary |
|---|---|---|
| Renderer silently authors a relevant tuple in a PL/pgSQL exception subtransaction | All twenty-one `INSERT_OR_RELOAD_COMPARE` writes move outside exception blocks; exact top-level `xmin` equality remains unchanged. | Caller savepoints/subtransactions remain forbidden and rejected rather than normalized. |
| Untargeted `ON CONFLICT DO NOTHING` suppresses an unrelated uniqueness failure | Every lowering names the one constraint derived from the typed conflict key using `ON CONFLICT ON CONSTRAINT`; any other uniqueness error propagates. | PostgreSQL constraint identity is re-proved by exact parse/catalogue rehearsal before behavior eligibility. |
| Conflict path admits a non-equivalent or ambiguous winner | `NOT FOUND` alone enters a read-only exact-key plus winner-predicate reload; `INTO STRICT` maps zero or multiple rows to stable `CF004`. | No claim is made beyond the typed winner predicate frozen in the body contract. |
| Repair broadens current-transaction provenance to include subtransactions | The exact PostgreSQL-16 top-level XID32 expression and all nineteen typed consumers are unchanged. | A no-write savepoint remains non-observable; the application path is still required to contain no savepoint/nested transaction. |
| New conflict syntax evades static review | The recognizer counts all `ON CONFLICT` clauses, requires the exact targeted form, validates every named constraint against the rendered catalogue and rejects generic or wrong-target mutations. | Later PostgreSQL-version changes remain a separate gate. |

No provider, network, product/patient data, application runtime, operational
database, deployment, release, Pages or protected-ref boundary changes.
