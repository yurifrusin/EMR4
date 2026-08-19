# Check-in relay-free recovery attempt 004 — lay and technical summary

Date: 2026-08-20

Status: `blocked safely; continuing to the narrow repair`

## Lay summary

The fourth database rehearsal ran exactly once and failed safely. It will not
be retried. This time PostgreSQL became reachable from its isolated internal
test network, but immediately afterwards the controller released the local
process that was attached to the server and then found that either the server
was no longer running or one of its exact safety-identity checks had changed.

The retained evidence combines those two possibilities, so choosing one would
be guesswork. No clinical or product data was used, no success was reported,
and no ordinary product action was enabled. The test sidecar, server and network
were removed and independent checks find nothing left behind.

The next work is deliberately not another database attempt. It will make the
two failure branches separately observable, keep the server attachment alive
until normal final cleanup unless an early release is proved safe, and exercise
that lifecycle with deterministic fakes. Only then can a separately named fifth
attempt be considered.

## Technical summary

- execution source: `932ae6ce02e0e973a22dfe999601087295001d1b`;
- retained evidence source: `4908bf53265e1356a9c5dac84a05b05702ad6d34`;
- failure: `server_not_ready_or_identity_mismatch` at `environment`;
- last proved stage: readiness sidecar terminal success;
- execution count: 1; retry count: 0;
- intended transaction execution: zero;
- ambiguous success, ordinary admission and product records: zero;
- cleanup: verified, zero matching containers and networks;
- failure SHA-256:
  `1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3`;
- envelope SHA-256:
  `415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5`;
- no Gemini or DeepSeek model call; and
- protected refs remain exact
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The clockwork stopped a provisional Git-ID transcription and an overlength
checkpoint before either could alter continuity. Those controls worked, while
also showing that the next efficiency gain is to generate bounded checkpoint
readings and machine-inject object IDs instead of hand-authoring them.

No product/API/client/configuration behavior, feature flag, authored-synthetic
allowlist, generic-status `Arrived`, action grammar, waiting-area movement,
patient or clinical data, production, deployment, release, Pages or protected
ref changed. `docs/branding/` and unrelated untracked files remain preserved.

The non-PHI continuing Pushover notification succeeded with request
`9fe662fa-a647-45bf-a2ad-b3b7d7d447d2`.
