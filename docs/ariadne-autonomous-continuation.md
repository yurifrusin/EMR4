# Ariadne Autonomous Continuation

Status: standing programme authority active by Yuri decision, 2026-08-04.

An active verified sprint and every dependency-satisfied successor gate in the
live accepted programme continue without another user permission request while
their complete material boundaries are already frozen and no user-owned choice
or human-only input is required. Ordinary gate transitions, worker, transport,
test and verifier-revision states are execution states, not permission gates.

A gate counts as planned and executable only when an active Current Baton plan
or accepted descendant fixes its objective, inputs, outputs, data/provider/cost
posture where applicable, allowed side effects, forbidden surfaces, evidence
labels, acceptance criteria and stop conditions. A generic future candidate or
an explicitly closed boundary is not self-authorising merely because it appears
later in a sequence.

The orchestrator records observable failure evidence and asks the Conductor to
replan. The Conductor retains exclusive authority to revise lanes and worker
assignments. A verifier checks the plan delta before the orchestrator resumes.
The orchestrator cannot silently substitute a worker, expand scope, or relabel
a failed result as successful.

Continuation is bounded. Repeated attempts require a distinct remediation and
remain inside the frozen recovery contract. User input is reserved for an
unplanned material fork, a missing user-owned choice or human-only input,
conflicting evidence that changes acceptance meaning, exhausted bounded
recovery, scope outside the accepted plan, or an explicit user pause. A new
security, write, provider, data, deployment, release or protected action needs
attention only when its exact material boundary is not already frozen and
authorised by the active accepted plan.

The machine-readable policy is
`orchestration/harness_settings/autonomous_continuation.yaml`.

## Task Lifecycle

Autonomous authority is ineffective if the orchestrator ends its task at every
internal checkpoint. While no user decision is required, status messages are
progress updates only and the orchestrator continues issuing tools in the same
task. It must not send a terminal handback merely because a plan was committed,
a worker or verifier is pending, or the next step is known.

A passing gate is not a terminal handback point when its next dependency-
satisfied planned gate is executable. A terminal handback is valid only when
the whole currently planned sequence or explicitly requested bounded block is
complete, a listed user-attention condition is active, Yuri explicitly pauses
or redirects, or the host platform has an unrecoverable interruption and a
durable automatic-resume checkpoint has been written. That checkpoint names the
active sprint, completed and next executable stages, retry counters, and
settings fingerprint.
