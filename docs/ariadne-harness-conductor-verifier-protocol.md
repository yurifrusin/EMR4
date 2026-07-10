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
