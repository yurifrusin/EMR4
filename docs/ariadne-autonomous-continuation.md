# Ariadne Autonomous Continuation

An active verified sprint continues without another user permission request
while all work remains inside its mandate and no user-owned decision is
required. Ordinary worker, transport, test, and verifier-revision failures are
execution states, not permission gates.

The orchestrator records observable failure evidence and asks the Conductor to
replan. The Conductor retains exclusive authority to revise lanes and worker
assignments. A verifier checks the plan delta before the orchestrator resumes.
The orchestrator cannot silently substitute a worker, expand scope, or relabel
a failed result as successful.

Continuation is bounded. Repeated attempts require a distinct remediation and
remain within configured retry limits. User input is reserved for mandate
expansion, material product choices, new security/write/deployment/release
authority, conflicting evidence, exhausted recovery, irreconcilable planning,
or a genuinely human-only external action.

The machine-readable policy is
`orchestration/harness_settings/autonomous_continuation.yaml`.

## Task Lifecycle

Autonomous authority is ineffective if the orchestrator ends its task at every
internal checkpoint. While no user decision is required, status messages are
progress updates only and the orchestrator continues issuing tools in the same
task. It must not send a terminal handback merely because a plan was committed,
a worker or verifier is pending, or the next step is known.

A terminal handback is valid only when the requested sprint/block is complete,
a listed user-owned pause condition is active, or the host platform has an
unrecoverable interruption and a durable automatic-resume checkpoint has been
written. That checkpoint names the active sprint, completed and next executable
stages, retry counters, and settings fingerprint.
