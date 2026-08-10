# Disposable PostgreSQL parse/catalogue outbox-select RLS rebind

Date: 2026-08-08

Status: characterization and exact reproduction pass.

The fixed no-argument, networkless, tmpfs-backed PostgreSQL 16 harness now
binds inert source commit `497a4d1fe5b58fa4bcc03747abb3d389c3b51899`,
SQL `sha256:265ce41ec4c3b318cc42c544ab06ebb0fcc67904072b0f8406af4ec8ddec6b0a`,
1,436,481 LF bytes and 423 statements.

The first candidate contract was
`sha256:8dea0bebfe6644975b4eaf5b6e5b9095f66778de3d8d0f4e2a726f389afa7163`
in `characterization_only` mode with no expected catalogue digests. It cannot
produce an acceptance pass. Attempt `5f15d3b6444fa2b76d3a432c` established that
only the `policies` digest changed from the preceding admission-lock evidence,
to `sha256:32f7416e38351c706d93ac235d8a1f19f4d67a3d691a86a17e8bb3032a72e4c0`.
It removed exact owned container `a786d6cb144400cd9668734dac91f749e31bb623e9a120ffdbfccb5d572c2ed1`
with absence verified. Immutable evidence SHA-256 is
`e053ac337a7b6db258b94bd56d0d55a0bd7c7ea42e428899bd566b154ba6c724`.

The resealed exact-bound contract is
`sha256:f74edcc816fb5794272352a482c1ae699f1dce822d301d86cb56ad6831cc2d8f`.
It binds all fifteen characterized digests. Attempt
`04deaadd7c685cbdd4d597c8` passed the rollback proof, atomic installation and
exact catalogue match, then removed exact owned container
`437a3a1238ed96323e963a0652b27725a9b9786615f1306b4b804ef2fa895e04`
with absence verified. Immutable pass evidence SHA-256 is
`b0ce639981a5822e9e66ebbb81cab74009b3ebe368f3d9e6efd75cfd32453386`.

Every run must address only its captured owned container ID, verify its removal
and restore the protected mutable evidence file after routing a new immutable
copy. It grants no operational database, persistence, migration application,
product or patient data, watcher/listener/feed, runtime wiring, provider call,
command authority, deployment, Pages rebuild, release or protected-ref
movement.
