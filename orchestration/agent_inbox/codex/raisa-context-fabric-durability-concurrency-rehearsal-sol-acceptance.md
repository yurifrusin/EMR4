# Sol acceptance — Context Fabric durability concurrency rehearsal

Date: 2026-08-11

Decision: `accepted`

Sol accepts immutable attempt 004 result
`raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass`
at runtime source `fed81847b4155d49cf997905e79cf31808ceb017` and exact
independently reviewed functional source
`43f168f3d5d1f71ec0f9071c40fadf14b6107621`.

Acceptance binds:

- immutable evidence SHA-256
  `7dd7372a8f45b6a049aca4f835057a33ab37952be98088bbbf34ed94875dd0e4`;
- exactly six expected, observed and passing scenarios in frozen contract
  order;
- exact `Timeout/PgSleep` leader and `Lock` contender overlap in all six
  scenarios;
- contract, inert SQL and manifest SHA-256
  `96b3fb92d302206eb757f51203044c2aeeb76248a6844422404d13c79b785391`,
  `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
  and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`;
- exact winner/loser SQLSTATEs, monotone producer positions, admission
  identity, native receipt replay and outer-rollback readback;
- 12 participant transactions, 11 preconditions and zero retries;
- exact-ID container removal, absence and zero remaining exact-label
  containers;
- whole-document evidence schema validation; and
- the final fresh Gemini 3.6 Flash/high pass with 254 focused tests and zero
  external operations.

Attempts 001-003 remain immutable rejected evidence. AER-0269 through AER-0272
are corrected at register revision 239.

This accepts only the selected provider-free two-session database concurrency
slice. Crash/restart and unknown-commit recovery, arbitrary retry/deadlock/load
behavior, key rotation, retention/purge, applied migration, operational
persistence/source access, application wiring, real data, providers, tools,
commands, deployment, Pages and protected refs remain closed.
