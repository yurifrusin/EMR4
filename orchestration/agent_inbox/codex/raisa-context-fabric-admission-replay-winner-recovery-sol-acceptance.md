# Sol acceptance — admission replay winner recovery

Date: 2026-08-08

Decision: accepted for fresh disposable parse/catalogue characterization and
exact reproduction; behavior execution remains closed.

Exact reviewed candidate
`5a9a7ae907308aa0a8a4256e9043b833f8c416ae` contains renderer 2.0.20 and
the sealed `NORMALIZE_ADMISSION_RELOAD_WINNER_PREDICATES` operation. It
removes only `admitted_at = transaction_timestamp()` from the three
admission reload-winner predicates. It preserves `admitted_at` insertion,
storage and return, the exact conflict key, all stable winner comparisons,
roles, capabilities, RLS, SQLSTATE and transaction/command boundaries.

Fresh Gemini 3.6 Flash/high review receipt SHA-256
`d897a75e7346de93cb89dcd22e3958781c8a2464ca7a50111b8fdc732b6b58b9`
returns exactly `pass` with identical clean pre/post HEAD. It independently
verified attempt 046's immutable failure and diagnosis, the scoped renderer
operation, 424 statements, 1,436,664 LF bytes, SQL SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`,
render-manifest canonical SHA-256
`2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`,
all requested checks and a clean postcondition.

This acceptance permits one bounded parse/catalogue characterization in one
newly owned, pull-never, networkless, portless, mountless, tmpfs PostgreSQL 16
container using only the frozen authored-synthetic fixture. After evidence-
backed contract rebinding it permits one separate exact parse reproduction.
Each run requires a distinct fresh preexecution receipt, immutable evidence,
verified cleanup and restoration of the protected mutable parse alias. It
does not permit a behavior attempt until the new parse evidence is accepted
and the behavior contract is rebound and independently vetoed. It grants no
operational database, watcher/listener/feed, application/API/Diary wiring,
product/patient/clinical data, provider, deployment, production, release,
Pages or protected-ref authority.
