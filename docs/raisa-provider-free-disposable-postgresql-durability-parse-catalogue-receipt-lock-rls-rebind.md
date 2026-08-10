# Disposable PostgreSQL parse/catalogue receipt-lock RLS rebind

Date: 2026-08-08

Status: characterization candidate only; exact digest admission pending.

The fixed parse/catalogue contract now binds inert SQL commit
`1b37d217779a5d7c3a9876a50db8f2f7099dfb23`, artifact
`sha256:bfd8fd924a1771ea03a2395fbd1f154253f098a3e488188a2f77778c197d7f38`,
1,437,022 LF bytes and 424 statements. The manifest predicts 48 forced-RLS
policies, exactly one more than the accepted outbox-select parent.

The first disposable run is characterization-only. It may establish the fresh
bounded catalogue digests but cannot pass acceptance. After immutable cleanup
evidence is preserved, the contract must bind those exact digests and a second
fresh disposable run must reproduce them before the parse descendant passes.

Both runs remain networkless, provider-free, disposable and authored-synthetic.
They prove PostgreSQL 16 parse, atomic installation and bounded catalogue shape
only—not function behavior, RLS enforcement behavior, operational persistence,
product/patient data suitability, application wiring, deployment, release,
Pages or protected-ref authority.
