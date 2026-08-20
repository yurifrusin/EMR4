# Check-in relay-free recovery attempt 005 — paired closeout

Date: 2026-08-20

Timestamp: 2026-08-20T14:15:35.7847894+10:00 (Australia/Brisbane)

## Lay summary

The safety machinery worked, but the attempted proof did not. The one local
synthetic PostgreSQL run reached a successful readiness check and then found
that its database server had stopped. It released nothing, retried nothing and
cleaned up every temporary resource. We now know the failure is specifically a
stopped server—not the previously combined "stopped or identity mismatch"
possibility.

The first real DeepSeek-Harness worker opportunity also stopped safely before
DeepSeek received a request because the Harness could not mount its bounded
preset. That cost no DeepSeek tokens and changed no files. Sol completed the
small adapter/test package directly.

The practical next step is a narrow, no-provider and initially no-database
repair: make the server's safe exit state observable and prove whether the
attached input channel is ending the server. Your attention is not required;
standing authority covers that diagnostic successor.

## Technical summary

- execution source: `905184b76f576006232fcfdc78da71d98fcf0ca0`;
- database terminal: `environment/server_not_running_after_readiness`;
- database executions/retries: `1/0`;
- attestation: absent; ambiguous success/ordinary/product releases: `0/0/0`;
- cleanup: verified, zero labelled containers or networks;
- DeepSeek worker: one consumed pre-provider preset-mount failure, zero
  requests/model steps/tools/tests/edits/retries;
- deterministic gates: 239 postcommit and 240 postexecution provider-free
  tests, Ruff, compile and full clockwork regression pass;
- Gemini: not dispatched because occupied success was not achieved; and
- protected refs: all remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Deliberately closed: ordinary check-in enablement, generic-status `Arrived`,
route/flag/allowlist/grammar/client/waiting-area changes, product/patient/
clinical data, live provider, production, deployment, release, Pages and
protected-ref movement.

Next tranche:
`raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair`.
