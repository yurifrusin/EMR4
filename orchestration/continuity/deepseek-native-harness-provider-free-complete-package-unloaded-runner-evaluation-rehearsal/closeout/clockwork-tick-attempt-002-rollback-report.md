# Clockwork tick attempt 002 corrective rollback

Date: 2026-08-22

Timestamp: 2026-08-22T12:32:01.7811299+10:00 (Australia/Brisbane)

Status: **byte-exact rollback passed**

The corrected rolling-label generation carried a broader combined
ordinary-practice restriction but omitted the exact closed
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`
floor token required by the Baton consistency contract. The post-publication
suite rejected the successor latch.

The second publication evidence is preserved under the `attempt-002` names.
The clockwork restored generation
`gen-f421ab28dbae0bb7ed44925c9c50ed675e1b43ee285bd07371a4bafafa556431`
byte exactly and advanced the writer lease to 155. No Harness, worker, provider,
product, data or protected-ref process ran.

The exact ordinary-practice and product/data floor tokens now belong to the
clockwork validator, not to an author's memory. The corrected intent also keeps
the separate generic-status `Arrived` prohibition.
