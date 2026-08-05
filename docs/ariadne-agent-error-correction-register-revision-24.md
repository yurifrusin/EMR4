# Ariadne agent-error register revision 24

Date: 2026-08-06

Status: AER-0028 and AER-0029 corrected; no incident remains open

## AER-0028: Windows TCP teardown was mistaken for listener absence

The first C5 occupied attempt that reached the disposable target lifecycle
exposed a repository defect in the accepted implementation-readiness
candidate. After exact termination of generation 1, the owned process was
absent but Windows returned a reset and then timeouts rather than the required
literal `connection_refused`. The controller therefore failed closed before
provider admission. That attempt remains preserved with zero provider calls,
no product or cloud mutation and an inconclusive listener-cleanup predicate.

Bounded provider-free diagnostics showed that a TCP connection outcome is not
a dependable listener-absence oracle on this host. The corrected controller
requires exact owned-process absence plus successful no-sharing reacquisition
of the same loopback address and port. It sets `SO_EXCLUSIVEADDRUSE` before
every Windows bind, never sets `SO_REUSEADDR`, retries only address-in-use
during bounded teardown, counts every actual bind attempt and retains the
successful reservation through generation-2 inherited-socket handoff.
Rollback and cleanup now use the same endpoint-ownership proof.

A real provider-free Windows lifecycle passed generation 1, abrupt exact-child
termination, exclusive exact-port reacquisition, generation 2 and complete
cleanup. The outer occupied classifier correctly remained a terminal failure
because the provider fake was non-live and provider accounting was zero. This
corrects the repository defect without claiming the occupied C5 result.

## AER-0029: credential-restoration guidance conflated two stores

The initial human-gate guidance did not distinguish Application Default
Credentials from the gcloud CLI credential store. An account-qualified ADC
login reused an expired cached source credential, and the subsequent ADC-only
restoration left the CLI credential used by the billing check stale. Both
attempts failed closed before provider admission and remain preserved.

The corrected procedure restores and verifies the two stores separately,
forces genuinely fresh authentication when cached source credentials are
expired and runs sanitized read-only ADC plus cloud-control checks before the
next live attempt. The exact Sydney preflight subsequently passed without IAM
or cloud mutation. This is recorded as an orchestrator guidance error, not an
operator error and not a provider/model-quality claim.

Revision 24 contains 29 bounded incidents: 22 agent-behaviour observations,
three harness failures, two repository defects and two transport timeouts. No
incident is open. Counts remain workflow-improvement signals only and do not
establish model, provider, transport or role causation.
