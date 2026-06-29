# Access AI Setup Paths

Access AI setup paths are declarative YAML files that describe a teleological
goal such as:

- make a developer able to live-test Scribe and Bernie
- make a production runtime able to invoke Scribe without JSON keys
- make a clinic receptionist eligible for Bernie supervised booking review

The YAML owns the goal, property values, and ordered steps. The runner resolves
`${...}` references and executes each step only when explicitly asked.

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

## Current Paths

| Path | Purpose |
|---|---|
| `access_ai/setup_paths/dev-yuri-scribe-bernie.yaml` | Developer setup for Yuri to live-test Scribe and Bernie in the dev projects. |
| `access_ai/setup_paths/prod-clinic-scribe-bernie-template.yaml` | Production runtime template. Fill in real prod project IDs and service accounts before execution. |

