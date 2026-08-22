# Clockwork tick attempt 001 corrective rollback

Date: 2026-08-22

Timestamp: 2026-08-22T12:25:38.6169090+10:00 (Australia/Brisbane)

Status: **byte-exact rollback passed**

The first live closeout generation used a caller-authored descriptive acceptance
label instead of the closed `Current DeepSeek native Harness acceptance` rolling
slot. The clockwork therefore inserted a second live acceptance row. The broad
post-publication governance test rejected that state with
`tick_baton_compaction_unindexed`.

The first publication evidence is preserved under the `attempt-001` names. The
clockwork rollback restored generation
`gen-f421ab28dbae0bb7ed44925c9c50ed675e1b43ee285bd07371a4bafafa556431`
byte exactly and advanced the writer lease to 153. No Harness, worker, provider,
product, data or protected-ref process ran.

The corrected intent uses the exact rolling label. The clockwork compactor now
also rejects any acceptance label absent from the closed active-label manifest
before rendering, so a future descriptive label cannot create a second live row.
