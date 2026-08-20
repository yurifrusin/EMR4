# DeepSeek native Harness complete-composition boot — Yuri summary

Date: 2026-08-20

Timestamp: 2026-08-20T11:55:38.3228395+10:00 (Australia/Brisbane)

## Lay summary

The native DeepSeek harness has now passed the important missing test. In one
real, tightly isolated boot it found the exact bounded-worker preset, waited
for all three required internal services, mounted the preset, applied our
guard and ended with only the three intended file capabilities: read, edit and
file-pattern matching. It contacted no model or provider and left no process
or temporary home behind.

This is a materially stronger result than the earlier source-only checks. The
harness's composition machinery is no longer merely plausible: the exact
pieces worked together in its real rc.7 boot path. Gemini independently checked
the committed evidence and passed the candidate on its first and only review.

Two workflow mistakes are being recorded rather than disguised. I ran a wider
historical test set whose three mock tests launch Node, even though this plan
said unit tests must not do that. They did not launch the Harness or affect its
result, so Gemini judged this a contained procedure error rather than a reason
to discard the successful boot. Then Gemini described the right kind of error
but named the wrong three test files. I corrected the names from the source and
did not spend another provider call merely to restate the same conclusion.

The practical controls are straightforward: execution-sensitive manifests
will identify and exclude process-spawning tests unless the plan explicitly
allows them, and verifier packets will bind exact incident filenames so the
reviewer cannot substitute nearby names.

We can now move from testing the harness's plumbing to giving it a genuinely
bounded EMR4 worker assignment. Fresh rehydration caught one important
bookkeeping error before that happened: I had pointed the next-work latch back
to the check-in route-adapter tranche, but that work had already passed on 18
August. The clockwork restored the previous generation byte-for-byte. Its new
interlock checks the Continuity graph itself and will reject any already
recorded operation before publication, instead of relying on a hard-coded
Markdown expectation.

The genuine next assignment is the separately named fifth relay-free recovery
attempt. It will first receive its own exact one-run plan and broker-limited
native-Harness WorkOrder. Attempt 004 remains consumed; no rerun or product
enablement is hidden inside the correction.

## Technical summary

- Accepted candidate:
  `6ef058b87a2c927efd9d9d2027b59d6ad279fec5`.
- Attempt: `complete-composition-native-boot-recovery-attempt-001`; one native
  process, zero retries.
- Readiness: exact `sentinel_activated`, `stock_headless_hmr_ready`.
- Dependency gate: exact ordered `hmr`, `agentPresets`, `tools` in loader and
  module declarations.
- Preset: 158 bytes, SHA-256
  `3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1`.
- Terminal: `EFFECTIVE_TOOL_COMPOSITION_PASSED`; exact tools `edit`, `glob`,
  `read`; exit 0; 9316 ms.
- Boundaries: zero network, agent/session/turn, broker, model/provider,
  occupied-worker, Docker and database counts.
- Cleanup: exact process and disposable-root absence.
- Evidence SHA-256:
  `9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0`.
- Independent veto: Gemini 3.7 Flash/high `pass`; 10/10 commands, 86 tests,
  unchanged clean worktree; receipt SHA-256
  `1460bf909f42348059b9590bd309fbb6e5a8928b836f1c27d8941bac322da7b4`.
- Incidents: six ancillary mock Node processes across two widened suites; one
  verifier narrative with three incorrect module names; and one omitted exact
  legacy next-latch token caught by the 630-test postpublication session.
  Lease 58 was rolled back byte-for-byte at lease 59 before correction; all
  three incidents enter clockwork intake. The corrected closeout also retains
  the stale accepted-successor selection, one invalid parallelism enum in the
  first recovery receipt, and the hard-coded historical successor guard.
- Successor recovery: stale lease 60 preserved; rollback lease 61 byte-exact;
  general graph-identity interlock added before publication.
- Protected refs: local/origin `master` and `handoff/current` remain exact
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Next: freeze
`raisa-provider-free-check-in-relay-free-recovery-attempt-005` with one exact
brokered native-Harness DeepSeek implementation package, one-run execution
authority only after deterministic admission, and the existing default-off,
authored-synthetic, product-data and protected-ref boundaries unchanged.

The first non-PHI continuing Pushover notification succeeded with request
`ec01f12b-6fec-4680-95b5-02391ce84d65`; its stale next-work line is superseded
by the corrective notification recorded after corrected clockwork publication.
