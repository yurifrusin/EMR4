# Sol acceptance — admission-lock behavior rebind

Date: 2026-08-08

Decision: accepted for exactly one disposable behavior attempt 038.

Exact reviewed candidate
`8ae67f6b0150ce7621f49c92c2f83bde1d46418e` contains the behavior-rebind
source `3cbaa4cb68acb78370183947a315f946f8d0ddaa`, revision 183 register
recovery and no database-semantic change after that source.

Fresh Gemini 3.6 Flash/high review receipt SHA-256
`aa65188ed36bfe660bb5f5039c5461559f8afe39ca07d3329534bc9b28c5176a`
returns exactly `pass` with identical clean pre/post HEAD. It independently
passed 556 tests across eleven exact files, Ruff, diff hygiene and all
admission-lock, authority, parent, parse, behavior, register and protected-
boundary challenges.

The accepted behavior contract remains canonical digest
`sha256:a16769b43c8345b3c79cc79d1ca26e4cd0b2d7095515d2b13bc7e21cb27b5b8e`,
with exactly twenty scenarios in unchanged order and category counts
`6/4/3/4/3`. BTR-R03 now contains eight fresh denial connections, including a
direct coordinator admission UPDATE that must fail `42501`. The coordinator
retains zero direct table DML; `pol_cf_04_update_lock` supplies only exact
bound `FOR UPDATE` visibility and its `WITH CHECK` ends `AND FALSE`.

This acceptance permits one no-argument harness run in one newly owned,
pull-never, networkless, portless, mountless, tmpfs PostgreSQL 16 container
using only the frozen authored-synthetic fixture. It grants no second attempt
without evidence-backed diagnosis/recovery, no applied migration, operational
database or credentials, persistence, watcher/listener/feed, application/API/
Diary surface, product/patient/clinical data, provider, deployment,
production, release, Pages or protected-ref authority.
