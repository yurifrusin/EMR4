# Compatibility-consumer and kernel-convergence admission review

Date: 2026-08-12

## Lay summary

The repository's ordinary Diary no longer uses the old direct appointment
write routes, and no other committed product, import, recovery or migration
tool calls them either. We still cannot know whether an outside integration
uses them, so they remain available and unchanged.

The remaining in-repository users are tests. They are valuable because they
describe what legacy callers currently see. Most are healthy, but 45 have
aged: some book fixed dates that are now in the past, while others omit a
proposal retry key that the API now correctly requires. We will repair those
test fixtures next rather than weaken the real safety rules.

Status changes are still the best first family for the later common mutation
kernel. The safe approach is to prove the confirmed-status transaction first;
we will not push the raw status route through the kernel by inventing missing
confirmation or freshness evidence.

## Technical summary

- zero committed product/runtime/import/recovery/migration/operational raw
  HTTP consumers;
- 126 direct calls across 21 conformance test/review files;
- four direct authored-synthetic/development database fixture writers,
  classified separately;
- external consumer posture remains unknown;
- exact create `201`, update/status `200`, delete `204`, audit, compatibility
  signal and helper commit behavior frozen;
- all current raw routes remain ineligible for the future kernel because
  precondition, separate confirmation and idempotency identity are absent;
- status confirm-first selected before delete, update and create;
- seven tranche, 167 dependency, 184 current behavior and canonical 191 fast-
  profile tests pass; and
- 45 of 311 broad legacy tests are explicitly classified for the next test-only
  repair.

No route, runtime behavior, database, provider, patient/product data, command,
deployment, Pages or protected ref changed.

Next under standing authority: repair only the stale temporal fixtures and
missing proposal idempotency headers, prove all 311 tests green, then continue
to the unmounted status transaction-kernel protocol rehearsal.
