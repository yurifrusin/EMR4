# Ariadne Conductor-Verifier Protocol

Date: 2026-07-11

The harness is a Markdown/YAML/script protocol, not a platform or agent runtime.

| Role | Authority | Explicit prohibition |
|---|---|---|
| Conductor | Plans sprints and assigns workers from project settings | Cannot integrate submissions, modify `master`, commit, or push |
| Verifier | Checks a conductor plan against YAML settings and protocol rules | Cannot reassign workers, grant authority, integrate, commit, or push |
| Orchestrator | Vets/amends worker submissions, integrates, tests, commits, and pushes `master` | Cannot change verifier-passed assignments or bypass verifier rejection |
| Worker | Performs its bounded packet and submits output | Cannot modify `master`, self-expand scope, or assign workers |

The user controls mandates, settings, availability declarations, and overrides.
If the orchestrator cannot safely execute a verified plan, it returns it to the
conductor with evidence. If availability changes, the conductor replans and the
verifier checks the revision; the orchestrator does not improvise a replacement.

## Workspace Preflight

Transport reachability and workspace readiness are separate facts. A reachable
CLI or local Codex spawn does not establish that the assigned worker has the
current mandate, settings, or code. Before the Conductor or a worker reads a
packet, it must supply a workspace receipt containing its target worktree,
expected agent branch, cleanliness, relation to `handoff/current`, and any
recorded divergence.

If a clean worker mirror must be realigned, the realignment command runs from
that target worker worktree. A command issued from the integration checkout is
supposed to refuse when the branch does not match the requested agent; that is
a guardrail, not a transport failure. A missing, stale, dirty, or mis-targeted
receipt requires plan revision before packet dispatch.

## Artifact Flow

```text
YAML settings + user override
  -> conductor plan Markdown + allocation record
  -> verifier result Markdown (pass | revision_required)
  -> orchestrator dispatches existing packets
  -> workers submit through existing inbox/outbox/worktree processes
  -> orchestrator integrates and publishes master
```

Suggested project-local settings:

```yaml
schema_version: ariadne.project_settings.v1
roles:
  conductor:
    preferred_resources: [claude_fable, claude_opus]
  verifier:
    preferred_resources: [deepseek_4_flash]
  orchestrator:
    preferred_resources: [gpt_terra, deepseek_4_pro]
master_authority:
  exclusive_role: orchestrator
  conductor_can_commit: false
  verifier_can_commit: false
allocation:
  user_override_required_to_change_verified_assignment: true
  replan_required_when_resource_availability_changes: true
```

Fable then Opus and DeepSeek Flash are ranked preferences, not permanent model
stereotypes. The user may change them by project or sprint.

The verifier checks settings schema, explicit overrides, availability and
concurrency evidence, role coverage/generalist fallback, packet scope,
independence labels, fallback reasons, and the authority split. It returns only
`pass` or `revision_required`. A pass establishes configuration conformity, not
runtime, write, provider, deployment, or release permission.

The first practice remains manual packets via the existing worker channels. No
harness script launches an agent; only the orchestrator can integrate and push.

## Initial Worker Mix

Claude Fable is the preferred conductor and Claude Opus is its ordinary
fallback. The conductor reads the committed settings under
`orchestration/harness_settings/`, particularly `sprint_worker_policy.yaml`.
For a normal substantive sprint it chooses whether the Antigravity platform,
currently using Gemini Flash 3.5, has a distinct artifact or veto surface, then
assigns between one and three DeepSeek Flash worker lanes according to
separability, file/review ownership, and verification need. One DeepSeek Flash
lane is the minimum worker posture; additional lanes are not ceremonial and
require distinct bounded packets. Future Gemini models or additional Flash
instances require distinct worker-pool entries and explicit capacity settings.

DeepSeek Flash as verifier checks the plan against those same settings. It does
not decide the worker mix, alter it, or integrate work. The present S4b
allocator proves settings-and-synthetic-probe assignment only; a later approved
verifier command is required before this becomes a machine-executed plan check.

## High-Assurance Write Protection

The preferred cross-platform security model is brokered patch delivery from an
isolated worker sandbox. A worker receives a read-only repository snapshot (or
read-only mount), a writable scratch/output directory, a Markdown task packet,
and YAML scope settings. It receives no canonical checkout, `master` worktree,
Git push credential, production secret, or authority to apply changes.

It returns only artifact files:

```text
plan.md
change.patch
verification.json
handover.md
```

The verifier checks the patch against allowed paths, settings, packet scope,
and evidence. The protected orchestrator, under a separate identity, is the
only process that applies a verifier-passed patch to the integration worktree,
runs final checks, commits, and pushes `master`.

```text
isolated worker sandbox -> patch and evidence
  -> verifier pass | revision_required
  -> protected orchestrator applies, verifies, commits, pushes master
```

This protocol is independent of model and transport: a Claude CLI worker,
Antigravity, DeepSeek bridge, Codex, CI job, hosted agent, or human can return
the same artifact set. The security boundary is capability, not the model:
workers have no write access to the canonical checkout and no credential that
can publish it.

Platform implementations may use rootless containers or dedicated users with
read-only mounts on Linux, sandbox/VM or dedicated-user isolation on macOS, and
Windows Sandbox, Hyper-V, or dedicated local accounts with NTFS ACLs on Windows.
Remote workers receive disposable clones without remote write tokens.

Separate worktrees and sparse checkouts remain useful compatibility tools, but
they are not hard write protection. The harness must label local shared-user
worktrees as `lower_assurance_local_mode`. High-assurance mode is required for
workers that receive sensitive scope, broad write scope, or untrusted execution.
