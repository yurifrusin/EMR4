# Historical Diary privacy gate — lay and technical summary

Date: 2026-08-24

Timestamp: 2026-08-24T01:51:25.4005323+10:00 (Australia/Brisbane)

## Lay summary

The privacy gate is now useful and working before we expose it to the archive.
On invented timestamp-spaced Diary snapshots, it replaced identity-bearing
details while preserving every one of 14 scheduling changes.

Importantly, it did not give itself an easy pass. A deliberately rare sequence
was still recognisable after the names were replaced, and the gate reported
that linkability. Its conclusion is only that we are ready to measure one
small local slice under strict controls—not that the historical data has
already been proved anonymous.

The next tranche can proceed without another ceremonial decision, but it must
first fix one real governance mismatch: the clockwork still forbids every kind
of historical data. It will make only our exact bounded local Diary exception
representable and will not inspect the archive. The following tranche can then
bind one folder/day and inspect no more than 80 files.

## Technical summary

Exact reviewed source is `1746cbf7a78d7d98597e6458f00953bd1ab193aa`.
All 46 new hostile tests and 40 unchanged historical Diary control tests pass.
Ruff, compilation, leakage lint, canonical policy rendering and whitespace
checks pass.

Six low-impact closeout inputs were rejected before mutation: a human-inbox
path was put into a narrower field; the clockwork then found an empty incident
list, scalar overflow, compact boundary aliases, a missing acceptance timestamp
and a missing exact conventional receipt. They are preserved as two incident
families and corrected in register revision 653.

The synthetic reading recovered 14/14 changes. Its seven-record population had
one unique record and one unique trajectory; record and trajectory linkage
each succeeded in 1/2 defined trials, and cross-release differencing succeeded
for 1/7 records. These are conditional synthetic measurements, not a universal
re-identification probability.

No historical Diary file was opened, listed, searched, sampled, hashed or
parsed. No private calibration, provider, network, product, database,
deployment, Pages or protected-ref surface opened. Yuri's attention is not
required and the bounded local measurement follows under standing authority.
