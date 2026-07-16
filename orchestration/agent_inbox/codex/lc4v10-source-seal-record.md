# LC4V10 Protected Source and Seal Record

Date: 2026-07-17

Decision: `source_bound_seal_unconsumed_one_shot_ready`

Sol alone authored the fresh V10 corpus after every external session closed.
The corpus has 24 groups, 288 scenarios, 72 two-turn trajectories, 216
one-turn scenarios, 288 distinct coverage cells, and 288 unique synthetic
patient identities. Every action has four groups; every group has two cases
for each of the six fixed language forms. Authoring validation calls no
product extraction, policy, interpretation, replay, or ordinary observer.

The exact source commit is
`d07b0c80c0e4834116167e280099bcfaaf681997`. Bound artifacts are:

- fixture SHA-256
  `6e04bb6100fe50dec5cfd2b9c06ee980cbe2fffc824f9e3870cbf1268a38efa2`;
- thresholds SHA-256
  `71be796a80a84b553000547b6da6607eaf64053332e02cce3508b93b816f02cf`;
- manifest SHA-256
  `d9467d100775f99a001fe371b691ca796fbb3d36f07b55686b152dff3dcd1516`;
- unconsumed seal SHA-256
  `650f58a570ae8147720f7511f8760a324fd779604308853c37dbc2a275e197bd`.

The manifest binds the exact fixture, accepted framework/evaluator, and
threshold bytes plus their Git blobs at the source commit. The source commit
is an ancestor of the sealing head. The combined pre-execution authoring,
sealing, and content-blind framework suite passes 37/37, and the broader
framework/taxonomy check immediately before source freeze passed 46/46.

The attempt marker and aggregate report are absent. The seal state is
`unconsumed`. No product observation has executed against V10 content. The
recorded Sol metadata-only filename enumeration incident exposed no earlier
content and grants no reuse authority.

The next and only authorized product action is the sole LC4V10 one-shot from
the protected integration worktree. Any exit after marker creation consumes
the attempt. V1-V9 remain sealed; all T3/provider/product/write boundaries
remain unchanged.
