# Context Fabric behavior receipt-lock parent rebind

Date: 2026-08-08

Status: deterministic candidate; disposable behavior runtime remains closed
pending a fresh exact-HEAD independent veto.

Attempt 042 remains immutable failure evidence. It stopped at `BTR-I03` with
`CF004` when the coordinator's replay path could read the exact receipt but
could not acquire its required `FOR UPDATE` lock under forced RLS. The bounded
repair adds exactly one coordinator-scoped `UPDATE USING` lock-visibility
policy with a permanently false `WITH CHECK`; it adds no coordinator direct
table DML grant and cannot authorize a row change.

The frozen twenty-scenario behavior contract is rebound to:

- exact receipt-lock parse reproduction source
  `662fcae68308061faf09f4b3a8820baeaa417d88`, SHA-256
  `sha256:67a490639840e217b740474afc331ab8aced5fb84871329099df6f504739288b`;
- inert SQL and render-manifest source
  `1b37d217779a5d7c3a9876a50db8f2f7099dfb23`, with 1,437,022 LF bytes,
  424 statements, SQL SHA-256
  `sha256:bfd8fd924a1771ea03a2395fbd1f154253f098a3e488188a2f77778c197d7f38`
  and manifest file SHA-256
  `sha256:dd4d98a8760487b17c0a70b08ef290c45607c71284a7cef804db126faac17cc6`;
- structural source `a1af31e89c13a0eea72fd90a2934a0c8e0154175`;
- typed body source `206803a26767d7be02b45514dd02c56cce773a46`; and
- the unchanged authored-synthetic prerequisite source
  `1fd3445aea5839b7aa889fc962faa8ad2be0c95e`.

All twenty scenario objects, their order, category counts `6/4/3/4/3`,
principals, fixtures, expected SQLSTATEs, result markers, rollback rules,
allowed change sets, forbidden effects and containment rules remain unchanged.
Their canonical scenario-set SHA-256 remains
`d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`.
The rebound canonical behavior-contract digest is
`sha256:ee44dbf39c2458fdabc94768e3c3e8cdcc0372c10ae7f0a35709b55301c5d596`.

Before attempt 043, the complete deterministic and hostile packet must pass
and one genuinely fresh Gemini 3.6 Flash/high exact-HEAD veto must accept the
candidate. Only then may Sol run one newly owned, pull-never, networkless,
mountless, portless, tmpfs-backed local PostgreSQL 16 container with exact-ID
cleanup. Any failure remains evidence for the accepted diagnose-repair-rerun
sequence and cannot authorize scenario weakening, RLS disablement, elevated
runtime identity or parent mutation.

This rebind grants no applied migration, operational database or credentials,
watcher/listener/feed, application/API/Diary wiring, provider, patient,
clinical, product or protected data, command/write authority, deployment,
production, release, Pages or protected-ref movement. `docs/branding/` and all
unrelated untracked files remain preserved and excluded.
