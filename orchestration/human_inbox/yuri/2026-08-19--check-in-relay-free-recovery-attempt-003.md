# Check-in relay-free recovery attempt 003 — lay and technical summary

Date: 2026-08-19

Status: `blocked safely; continuing to the narrow repair`

## Lay summary

The third database rehearsal did exactly one run, failed safely, and will not
be retried. It found a simple deterministic wiring mistake: the strengthened
Docker safety check now needs the network name, but two real callers were not
updated to provide it.

The failure happened before the container started. No password was delivered,
PostgreSQL never ran, no clinical or product data was involved, and no success
was reported. One never-started test container remained because the error
happened before it entered the normal cleanup registry. Sol verified that it
was the single exact owned test container, removed it, and confirmed that no
matching container or network remains.

The useful conclusion is precise: repeating the run would only repeat the same
bug. The next work is to fix both callers, add a test that exercises their real
function signature, and strengthen cleanup for errors that happen before
registry admission. Under your standing authority that repair proceeds now;
only after it passes will a separately named attempt 004 be frozen.

## Technical summary

- execution source: `19e4414fec067fcbb6af12818e432953432878be`;
- failure: `unexpected_controller_failure` at `attempt_003_execution`;
- exact cause: missing `network_name` keyword at `_create_server` and
  `_run_sidecar` calls to `_container_profile_predicates`;
- execution count: 1; retry count: 0; success release: false;
- pre-recovery state: `created`, `Running=false`;
- credential delivery, PostgreSQL start, SQL and transaction counts: zero;
- cleanup: exact candidate cardinality one, exact ownership profile verified,
  exact captured removal, zero matching owned residue;
- failure SHA-256:
  `e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b`;
- envelope SHA-256:
  `91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75`;
- cleanup SHA-256:
  `048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71`;
- Gemini not dispatched; DeepSeek/native lanes remained declined; and
- protected refs remain exact
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No product/API/client/configuration behavior, ordinary-practice admission,
patient or clinical data, production, deployment, release, Pages or protected
ref changed. `docs/branding/` and unrelated untracked files remain preserved.
