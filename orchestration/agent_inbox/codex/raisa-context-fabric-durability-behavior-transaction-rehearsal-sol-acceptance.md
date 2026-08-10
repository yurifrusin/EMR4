# Sol acceptance — Context Fabric durability behavior/transaction rehearsal

Date: 2026-08-08

Decision: `accepted`

Sol accepts the immutable attempt-048 result
`raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_pass`
at independently reviewed source
`f3383dc4099b4ee590014bea62dddb146f5d2a16`.

Acceptance binds:

- immutable evidence SHA-256
  `26c6dec802e46dec055c1c42aecc97df9942180014fc9fa410f96e1305798200`;
- exactly 20 expected, observed and passing scenarios in frozen contract order;
- behavior contract, inert SQL and manifest SHA-256
  `43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`,
  `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
  and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`;
- exact cross-transaction replay and fixed outer-rollback readback;
- exact-ID container removal and absence;
- restored mutable behavior alias SHA-256
  `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`;
- whole-document evidence schema validation after the bounded AER-0238 schema
  correction; and
- the final clean Gemini 3.6 Flash/high pass with 498/498 focused tests.

This accepts only the selected provider-free serial database behavior slice.
Concurrency, restart/unknown-commit recovery, key rotation, retention execution,
applied migration, operational persistence/source access, application/runtime
wiring, real data, providers, tools, commands, deployment, Pages and protected
refs remain closed.
