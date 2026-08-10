# Sol acceptance — behavior attempt 044 bounded not-null telemetry

Date: 2026-08-08

Decision: **accepted**

Exact candidate `d19de28f91fbdc05aeec96cabcb329ee7002a7f4` is accepted for the
bounded diagnostic correction following immutable behavior attempt 044. The
rehearsal may now record a relation/column coordinate only for exact SQLSTATE
`23502`, only when both values belong to the one accepted scenario relation and
its closed 20-column allowlist. Every rejection class retains its safe SQLSTATE;
hostile or unlisted coordinates and raw stderr are never released.

The fresh Gemini 3.6 Flash/high Antigravity veto used exactly one reviewer-model
call, returned structured `pass`, ran 1083 focused tests plus Ruff and exact diff
checks, and left r173 clean at the exact candidate. Immutable attempt-044 failure
evidence remains SHA-256
`0bacbe855a818c4dbb6bfa5c95ffbdb4fd5a91ac9ace431153669d17cb277345`.
The accepted database body, structural contract, DDL renderer, inert SQL,
behavior contract, fixture registry, scenarios and all six behavior parents are
unchanged. Current canonical behavior contract is
`sha256:897e07895116eecedaf8a2506ad10f9f5e5207b7e78e68ab79afb09347018a57`;
current scenario seal is
`e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb`.

This acceptance authorises no provider/product call, patient or product data,
operational database, watcher/feed, application/API/Diary wiring, command/write,
deployment, release, Pages or protected-ref movement. It is not a runtime pass.
Exactly one fresh owned authored-synthetic disposable PostgreSQL attempt 045 is
the next planned action after a separate complete five-source preexecution
receipt and a byte-exact protected mutable-evidence backup. An identical rerun
of attempt 044 is forbidden.
