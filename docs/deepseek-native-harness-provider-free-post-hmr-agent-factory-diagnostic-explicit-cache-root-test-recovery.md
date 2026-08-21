# DeepSeek native Harness agent-factory diagnostic explicit-cache-root test recovery

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

The first combined focused/evidence closeout test run failed before any native
process was created. Its provider-free wrapper correctly removed
`LOCALAPPDATA`, but the deterministic-check test omitted the function's
explicit `cache_root` parameter and therefore received the typed
`localappdata_missing` guard error.

The accepted execution source at
`33b4e061b1385abc91ecd170e4abdb563396c3ef` remains unchanged. An initial
attempt to alter the test was separately rejected and reversed under AER-0872.
The final correction is in the mutable closeout manifest: it runs the unchanged
focused test through no-conftest pytest, retaining the accepted host cache-
location binding without loading repository conftest or launching a native
process.
