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
