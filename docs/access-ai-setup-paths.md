# Access AI Setup Paths

Access AI setup paths are declarative YAML files that describe a teleological
goal such as:

- make a developer able to live-test Scribe and Bernie
- make a production runtime able to invoke Scribe without JSON keys
- make a clinic receptionist eligible for Bernie supervised booking review

The YAML owns the goal, property values, and ordered steps. The runner resolves
`${...}` references and executes each step only when explicitly asked.

## Davida Practice Management Copilot

Davida is the proposed first-party EMR4 general practice management copilot.
Setup and onboarding should be Davida's first serious skill, but not her whole
identity. Over time she should help practice managers configure, operate, audit,
and safely improve the practice-management system.

Davida should not become a second source of truth. For setup, Davida is a
conversational guide over the same setup-path YAML, schemas, helper scripts,
dry-run output, and verification results that a human operator or external agent
can inspect directly.

The long-term setup model is:

```text
YAML setup path
  = canonical desired-state contract

Runner
  = deterministic executor and verifier

Helper scripts
  = small idempotent actions

Davida
  = first-party practice management copilot over manifests, APIs, and runners

External agents
  = allowed to read YAML, docs, schemas, dry-run JSON, and verification output
```

For setup, Davida's job is to ask for missing values, explain risky steps, open
the right helper documents or GCP console pages, ingest CSVs where appropriate,
and guide a practice manager or implementation lead to a successful setup
without forcing them into raw cloud-console navigation.

Later Davida skills may include practice/resource configuration, staff
onboarding, Access AI role changes, operational audit review, setup drift
monitoring, and safe administrative change proposals for owner confirmation.

External agents should also be supported. The setup path format must remain
agent-readable, deterministic, and dry-run friendly so a practice's own IT agent
can inspect the same plan, identify missing values, and run or delegate approved
steps. The first-party Davida experience and external-agent workflow should both
consume the same manifests.

## Safe Default

The runner defaults to dry-run:

```powershell
python -m access_ai.runner.run_setup_path access_ai/setup_paths/dev-yuri-scribe-bernie.yaml
```

Use `--execute` only after reviewing the generated command list:

```powershell
python -m access_ai.runner.run_setup_path access_ai/setup_paths/dev-yuri-scribe-bernie.yaml --execute
```

JSON output is available for automation:

```powershell
python -m access_ai.runner.run_setup_path access_ai/setup_paths/dev-yuri-scribe-bernie.yaml --json
```

## Shape

```yaml
goal: setup_access_ai_dev_user_for_scribe_and_bernie

context:
  environment: dev
  region: australia-southeast1
  user_email: yuri@littlestardigital.com

projects:
  scribe:
    project_id: scribe-emr4-dev
    service_account: emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com

steps:
  - id: enable_scribe_vertex_ai
    executable: gcloud
    args:
      - services
      - enable
      - aiplatform.googleapis.com
      - --project
      - ${projects.scribe.project_id}
```

## Design Rules

- Keep YAML declarative. Put imperative logic in small scripts or `gcloud`
  commands.
- Prefer idempotent steps: enabling an already-enabled API or adding an existing
  IAM binding should be harmless.
- Keep production paths keyless. Production should use platform-managed identity,
  not local ADC or JSON service-account keys.
- Treat GCP IAM and Access AI authorization as separate layers. GCP IAM lets the
  runtime call providers; Access AI decides which user or role may invoke a
  capability.
- Always add verification for setup steps that touch cloud state.
- Prefer dev-to-prod continuity. Code should stay stable while YAML property
  values, service identities, runtime auth mode, project IDs, and environment
  policies change.
- Each step should eventually expose helper metadata that Davida, a terminal
  runner, or an external agent can surface before execution:

```yaml
help:
  summary: Enable Vertex AI for the Scribe project.
  why: Scribe uses Gemini through Vertex AI.
  pitfalls:
    - Billing must be attached before API enablement succeeds.
    - Organization policy may block service activation.
    - Regional quota may differ from global API enablement.
  links:
    - label: Vertex AI API
      url: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
    - label: IAM service accounts
      url: https://console.cloud.google.com/iam-admin/serviceaccounts
```

## Production Onboarding Direction

Production setup is where this approach should pay off most. A future practice
manager should be able to sit down with Davida and provide:

- practice identity and billing details
- locations, rooms, waiting areas, and diary resources
- practitioner and staff details, directly or via CSV
- preferred AI providers and regions
- GCP organization/project/billing account details
- consent, audit, and PHI-handling policy choices

Davida should then produce a dry-run setup path, explain each material action,
request confirmation before any billing/IAM/API side effect, execute approved
steps, and verify the resulting system state. The same path should remain
readable by outside copilots.

This follows the intended dev-to-prod posture: production should not fork EMR4
application code. Production should differ through declared values, managed
identity, policy, and provider configuration.

## Current Paths

| Path | Purpose |
|---|---|
| `access_ai/setup_paths/dev-yuri-scribe-bernie.yaml` | Developer setup for Yuri to live-test Scribe and Bernie in the dev projects. |
| `access_ai/setup_paths/prod-clinic-scribe-bernie-template.yaml` | Production runtime template. Fill in real prod project IDs and service accounts before execution. |
