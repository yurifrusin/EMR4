# Sol acceptance — behavior attempt 043 missing-source SQLSTATE correction

Date: 2026-08-08

Decision: **accepted**

Exact candidate `77afc48114328061c6cd3deef12b46fdf2a51ae6` is accepted for the
bounded correction that aligns BTR-E06 with the accepted exact-row lowering:
an absent required source row raises `F_CARDINALITY` / `CF004` before the later
present-source membership-digest assertion `F_ADMISSION_SOURCE` / `CF201`.

The fresh Gemini 3.6 Flash/high Antigravity veto used exactly one reviewer-model
call, returned structured `pass`, ran 298 focused tests plus Ruff and exact diff
checks, and left r172 clean at the exact candidate. The accepted database body,
structural contract, DDL renderer, inert SQL, manifest, parse evidence and all
six behavior parents are byte-unchanged. Current canonical behavior contract is
`sha256:897e07895116eecedaf8a2506ad10f9f5e5207b7e78e68ab79afb09347018a57`;
current scenario seal is
`e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb`.

This acceptance authorises no provider/product call, patient or product data,
operational database, watcher/feed, application/API/Diary wiring, command/write,
deployment, release, Pages or protected-ref movement. It is not a runtime pass.
Exactly one fresh owned authored-synthetic disposable PostgreSQL attempt 044 is
the next planned action after a separate complete five-source preexecution
receipt and a byte-exact protected mutable-evidence backup. An identical rerun
of attempt 043 is forbidden.
