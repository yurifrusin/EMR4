# Ariadne Harness Bootstrapper Strategy

Date: 2026-07-11

## Purpose

The bootstrapper is a conversational initial agent, not the conductor or
orchestrator. It helps an end user configure a new project through an existing
LLM platform while generating the Markdown and YAML protocol artifacts behind
the scenes. The user should not need to hand-edit those files.

## Operating Model

```text
bootstrap conversation
  -> read-only environment discovery
  -> plain-language setup interview
  -> proposed configuration summary
  -> user approves scoped writes
  -> generated settings and validation report
  -> dry-run allocation/packet flow
  -> handoff to conductor and orchestrator
```

The initial agent asks only meaningful questions: project root and Git state,
orchestrator/conductor/verifier preferences, available subscriptions/API worker
pools, budgets and instance ceilings, desired assurance mode, master credential
owner, and required manual platform steps.

## Write And Secret Boundaries

| Action | Bootstrap posture |
|---|---|
| Read local project state and generate a proposed plan | Automatic, read-only |
| Create new harness folders, YAML, Markdown, and validation reports | Ask for scoped local-write approval |
| Modify an existing repository, create worktrees, install packages, or configure a bridge | Ask for explicit approval |
| Browser login, OAuth, API-key entry, billing, administrator actions, sandbox account/VM setup | Give precise manual instructions only |
| Push, change branch protection, expose secrets, or grant master credentials | Never automatic |

Secrets are never written to project YAML. Settings may contain only credential
references such as `environment`, `system_keychain`, or `manual_operator_step`.

## Generated Project Artifacts

```text
orchestration/harness_settings/
  project.yaml
  worker_pool.yaml
  role_preferences.yaml
  user_overrides.yaml
  security_mode.yaml
  setup_summary.md
```

The bootstrapper writes these from versioned templates, validates them after
each change, and presents `setup_summary.md` as the user-facing explanation.

## EMR4 First Pilot

Do not run the first bootstrap against the active EMR4 integration checkout.

1. Build a dry-run bootstrap protocol with templates, schema validation, and a
   generated summary.
2. Run read-only discovery against the known working EMR4 environment and
   compare the proposal with current documented configuration.
3. Generate a fresh disposable EMR4 clone/workspace with no master credential
   and no production secrets.
4. Verify reconstruction of development prerequisites, worker-pool settings,
   inbox conventions, and rehydration state. Emit manual runbook steps for
   logins, API keys, Office tooling, and sandbox setup.
5. Only after the reconstructed environment is accepted should the bootstrapper
   be treated as a reusable new-project setup path.

The first implementation is documentation/templates plus a portable validator,
not a live installer, agent launcher, or sandbox provisioner.
