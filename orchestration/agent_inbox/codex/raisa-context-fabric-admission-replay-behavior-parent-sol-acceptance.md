# Sol acceptance — admission-replay behavior parent rebind

Date: 2026-08-08

Decision: accepted for exactly one disposable behavior attempt 047.

Exact candidate `116fcca713f804e8234e60b3cdff9ebac567f50d` binds
immutable parse reproduction SHA-256
`9ad82882150f8795789c332db8bed6e4b50d150986a6066ce832f12e48246d24`,
inert SQL SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
and render-manifest SHA-256
`2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`.
Canonical behavior-contract SHA-256 is
`43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`.

Fresh Gemini 3.6 Flash/high review receipt SHA-256
`32104bf427029ac726d68de7564aa1ca52a5fa75d994bb6b15646b5da84f2f15`
returns exactly `pass` with identical clean pre/post HEAD. It independently
verified the new parents and proved that scenario order, fixtures, outcomes,
SQLSTATEs, category counts `6/4/3/4/3`, containment and claim boundaries are
unchanged. BTR-I02 retains its three-transaction primary/conflict/replay proof.

This acceptance permits one no-argument attempt 047 in one newly owned,
pull-never, networkless, portless, mountless, tmpfs PostgreSQL 16 container
using only frozen authored-synthetic fixtures. Any failure must be preserved
and diagnosed without rerun. Any pass must be preserved immutably, the
historical mutable behavior alias restored byte-exact and exact-ID cleanup
verified. It grants no second attempt, applied migration, operational database,
persistence, watcher/feed, application/API/Diary wiring, product/patient/
clinical data, provider, deployment, release, Pages or protected-ref authority.
