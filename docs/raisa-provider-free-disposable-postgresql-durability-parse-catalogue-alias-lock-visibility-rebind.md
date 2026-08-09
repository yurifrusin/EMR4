# Disposable PostgreSQL parse/catalogue alias-lock visibility rebind

Date: 2026-08-09

Status: characterization candidate only; exact acceptance remains closed

The fixed rehearsal is rebound to committed artifact source
`958f8178c872854ab0f8e1c56dbb9fe46afbea22`, artifact
`sha256:64cbc2b0e17276387c6815af02a2d0635fc538e3408995c1054ecbc708b5cbae`,
exactly 1,392,201 canonical LF bytes and statement count `413`.

The manifest population changes only from 44 to 45 RLS policies. The added
policy is the producer-scoped alias lock-visibility policy with a permanently
false write check. All other manifest populations remain unchanged.

The first descendant run is `characterization_only` with an empty expected
digest map. It must terminate as non-accepting, retain only minimized catalogue
digests and remove its one exact owned networkless container. A distinct exact
reproduction remains required before parse/catalogue acceptance or behavior
eligibility.

That characterization completed as attempt `575003a3542e56595336dd59`, changed
only the policy catalogue digest to
`sha256:51f697aeb94a50f432f6683c9e9c93412eee38853617a113c1ab020216a57168`,
and removed container `f3ed6c479e09672673c598e1d7095a3bfece136271c1dae1925f3c1a98f4a748`
with exact-ID absence verified. The contract now binds all fifteen
value-bearing catalogue digests for one distinct exact reproduction.

No migration, operational database, product/patient data, provider, function
behavior, application/API/Diary wiring, watcher/listener/feed, command,
deployment, release or protected-ref surface is opened.
