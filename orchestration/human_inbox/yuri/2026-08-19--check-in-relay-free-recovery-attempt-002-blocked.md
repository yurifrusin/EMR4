# Check-in relay-free recovery attempt 002 — blocked

## Lay summary

The new attempt ran once, exactly as authorised, and stopped safely before the
database started. It found two more inspection-rule problems rather than a
check-in transaction problem. Nothing was retried, no success was claimed, no
practice or product data was touched, and every temporary Docker object was
removed.

The useful part is that the cleanup repair worked: unlike the first attempt,
the newly created server object did not get stranded. The remaining blocker is
now narrower and visible. One rule asks Docker for a network identifier in a
field that is not populated in this Created-state shape; another rule
contradicts itself by requiring an ownership nonce label and simultaneously
forbidding that nonce from appearing in the inspected configuration.

This attempt cannot be rerun. My recommendation is a small, no-credential
Docker representation rehearsal and predicate correction before considering
another occupied database attempt.

## Technical summary

- Operation: `raisa-provider-free-check-in-relay-free-recovery-attempt-002`
- Execution source: `675d1b929fb97d2a0264682d86be95c65b12fd3d`
- Result: `failed_closed`
- Stage/code: `environment/server_profile_mismatch_cleaned`
- Failed predicates: `captured_network_id`, `secret_absent`
- Occupied executions: 1
- Retries: 0
- Success released: false
- PostgreSQL started: false
- Credential delivered: false
- SQL/transaction executed: false
- Ordinary/product effects: 0 / 0
- Cleanup: verified; zero matching containers and networks
- Failure SHA-256:
  `7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff`
- Envelope SHA-256:
  `6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40`
- Gemini: not dispatched because no passing candidate exists
- DeepSeek: not dispatched; native-Harness boot proof remains outstanding
- Protected refs: unchanged at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`
- `docs/branding/`: preserved and untracked

User attention is required before any separately frozen successor with another
occupied database execution.
