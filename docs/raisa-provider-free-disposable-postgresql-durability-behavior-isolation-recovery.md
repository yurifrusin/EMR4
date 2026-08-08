# Provider-free behavior rehearsal isolation recovery

Date: 2026-08-08

Status: deterministic repair candidate; runtime closed pending fresh veto

Attempt 012 reached fixed scenario `BTR-E01` and returned SQLSTATE `CF303`.
Exact readback of the accepted parent SQL shows that generation registration
and coordinator transition entry points deliberately fail closed unless the
top-level transaction is `SERIALIZABLE`. The later behavior design had instead
flattened every behavior-changing scenario to `READ COMMITTED`.

The parent SQL is not weakened. `BTR-E01`, `BTR-E04`, `BTR-I03` and `BTR-B03`
now use `SERIALIZABLE`, matching the lifecycle/coordinator guards. Every other
producer, observer, trigger, RLS and rollback scenario stays `READ COMMITTED`,
with the existing read-only flag retained for `BTR-R01`. Evidence records and
validates the observed isolation for every scenario. This is still a
single-session serial proof and does not claim concurrent anomaly or retry
coverage.
