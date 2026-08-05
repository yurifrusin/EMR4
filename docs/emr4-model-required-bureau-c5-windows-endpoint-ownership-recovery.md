# C5 Windows endpoint-ownership recovery

Date: 2026-08-06

Status: provider-free repository defect corrected; occupied rehearsal remains
behind fresh deterministic, exact-HEAD independent and pre-execution gates

## Finding

The first C5 live attempt that reached the disposable target lifecycle exposed
an invalid platform assumption in the accepted implementation-readiness
candidate. It required a literal `connection_refused` result after terminating
the exact generation-1 process. On this Windows host, the process was absent
but new TCP connections reset once and then timed out during teardown. A second
bounded diagnostic against an unused loopback port also showed that refusal was
not a dependable absence oracle here.

The failed occupied attempt stopped before provider admission. It made zero
provider calls, performed no product or cloud mutation and preserved its
inconclusive cleanup evidence. The historical implementation-readiness
closeout remains an accurate record of the earlier accepted candidate, but its
connection-refused post-fault claim is superseded by this correction.

## Corrected invariant

C5 now proves the transition using two independent properties:

1. the exact controller-owned process handle is absent; and
2. the controller successfully binds the same `127.0.0.1` port without address
   sharing and retains that reservation through the generation-2 inherited-
   socket handoff.

On Windows each candidate socket sets `SO_EXCLUSIVEADDRUSE` before bind. C5
never sets `SO_REUSEADDR`, retries only exact address-in-use during a bounded
two-second teardown interval, counts every failed and successful bind attempt,
and treats reset or timeout only as diagnostic transport evidence. Rollback and
cleanup use the same exact-port ownership proof instead of inferring absence
from an HTTP exception.

## Provider-free verification

A real local Windows lifecycle using the exact process, HTTP, loopback-port and
task-directory adapters passed generation 1, abrupt owned-process termination,
exact exclusive endpoint reacquisition, retained reservation handoff,
generation 2 and complete cleanup. The provider adapter was deliberately a
non-live authored-synthetic fake, so provider accounting remained exactly zero
and the outer occupied-result classifier correctly failed closed rather than
claim a C5 pass.

The sanitized diagnostic receipt is
`orchestration/agent_inbox/codex/model-required-bureau-c5-windows-teardown-diagnostic-receipt.json`.
Focused contract, controller and live-runner tests cover Windows option order,
the prohibition on address sharing, bounded address-in-use-only retry, bind-
attempt accounting, exact reservation identity and cleanup behavior.

No patient, clinical, product-derived or protected data, product runtime,
provider call, deployment, release, Pages action or protected-ref movement is
established or authorised by this correction.
