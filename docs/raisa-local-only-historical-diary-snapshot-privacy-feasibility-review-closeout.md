# Raisa local-only historical Diary snapshot privacy feasibility review — closeout

Date: 2026-08-24

Timestamp: 2026-08-24T01:51:25.4005323+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed source: `1746cbf7a78d7d98597e6458f00953bd1ab193aa`

## Lay outcome

The privacy gate now exists before any historical Diary file is touched. On an
invented sequence of four timestamp-spaced Diary snapshots, it replaced names,
contacts, record labels and resource labels with safe treatments while keeping
the scheduling sequence intact. It recovered all 14 additions, removals and
changes.

The gate also demonstrated why replacement alone is not enough. One deliberately
rare trajectory remained unique, and a defined attacker could link it. The
mechanism reports that risk openly. Its result is therefore “ready to measure
one bounded local slice,” not “the archive is anonymous.”

## Technical outcome

- all 18 admitted fields have one typed privacy treatment;
- HMAC stand-ins are stable within a release, domain-separated and changed by
  independent ephemeral keys;
- contact values are dropped, notes become closed buckets and original paths,
  filenames and timestamps cannot enter the projection;
- relative observations are censored into 30-second intervals;
- exact adjacent add/remove/change recovery passes across irregular gaps;
- equivalence, uniqueness, rarity, record linkage, trajectory linkage and
  multi-release differencing carry exact trials and successes;
- 46 hostile tests and 40 unchanged historical Diary controls pass; and
- existing H5/H15 source and approval remain unchanged.

Six closeout input lapses were rejected before state change: one inadmissible
human-inbox evidence root, followed by an empty incident list, scalar overflow,
compact boundary aliases, a missing acceptance timestamp and a missing exact
conventional pre-verifier receipt. The latter five form one clockwork-interface
incident; all rejected inputs and corrections are in register revision 653.

The data-free future subgate admits only one leaf root, one dense day, 80 files,
128 MiB total and 8 MiB per file. It forbids recursion, provider/network/model
use, persisted mappings and committed private content. Its strongest possible
result is an ignored local research candidate with no downstream authority.

No historical Diary, private calibration, protected evidence, provider, model,
network, product, database, deployment, Pages or protected ref was accessed or
changed.

## Next tranche

Proceed immediately to
`raisa-local-only-historical-diary-access-boundary-convergence`. The clockwork's
mandatory floor still forbids all historical data. The successor must make the
authorised, exact local Diary subgate representable without weakening the
denial of product, patient, appointment, clinical or protected data. It will
not read the archive. Only a later freshly frozen tranche may bind a root and
take the 80-file measurement.
