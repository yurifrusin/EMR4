# Status-confirm kernel adapter contract — lay and technical closeout

Date: 2026-08-12

## Lay summary

We now have the safe plug shape between a staff member's signed status
confirmation and the transaction rules proved in the preceding tranche. It
accepts authority and current appointment facts only from the server, rejects
stale or mismatched confirmation material, and cannot itself change anything.
If a reply is lost after a future commit, retry must return the stored receipt
rather than repeat the change.

Waiting-area changes stay outside this narrow status contract, and reopening a
terminal appointment remains deliberately blocked pending an explicit policy.

## Technical summary

- source `30a49015d23bfcf069be0af838df7091032a40be`;
- 15 cases, eight result mappings, 37 hostile mutations;
- 11 focused, 59 dependency/API, 36 API Spine, 58 closeout and 191 canonical
  tests pass;
- no application file changed; and
- AER-0291 transparently records and corrects a protected-scope discovery
  breach before planning, with the exposed content excluded from evidence.

The live handover also tripped its own size guard. I removed thirteen inactive
lookup rows from mandatory rehydration while preserving their artifacts and
the immutable indexed ledger; all active rows remain and the baton is back
under both compactness ceilings.

No runtime, database, provider, data, command, deployment or release opened.
Next is the read-only status-confirm runtime-gap admission review; Yuri's
attention is not required.
