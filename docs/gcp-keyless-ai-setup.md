# GCP Keyless AI Setup For EMR4

This runbook replaces the old local `gcp-key.json` posture for EMR4 AI work.
The target is keyless Google Cloud access through Cloud Identity, service
account impersonation, and explicit quota-project configuration.

## Identity Layout

Preferred organization:

```text
littlestardigital.com
```

Recommended human accounts:

| Account | Purpose |
|---|---|
| `admin@littlestardigital.com` | Break-glass Cloud Identity super admin |
| `yuri@littlestardigital.com` | Daily Google Cloud and EMR4 dev account |
| `yurifrusin@gmail.com` | Transitional billing-history/recovery helper only |
| `sara.frushera@gmail.com` | Retire from EMR4 Google Cloud access |

Enable MFA on all human accounts that can administer Google Cloud.

## Project Layout

Create projects under the Little Star Digital organization, preferably inside:

```text
EMR4/
  Dev/
  Prod/
```

Initial dev projects:

```text
emr4-copilot-dev
emr4-bernie-dev
```

Later production projects:

```text
emr4-copilot-prod
emr4-bernie-prod
```

Do not use Google's auto-created `My First Project` for EMR4 runtime work.

## Required APIs

Enable these APIs in each AI project:

```text
aiplatform.googleapis.com
iamcredentials.googleapis.com
serviceusage.googleapis.com
cloudresourcemanager.googleapis.com
logging.googleapis.com
monitoring.googleapis.com
secretmanager.googleapis.com
```

`secretmanager.googleapis.com` is optional until EMR4 stores runtime secrets in
GCP, but enabling it early is reasonable.

## Service Accounts

Create one runtime service account per product/project:

```text
emr4-copilot-dev-runner@emr4-copilot-dev.iam.gserviceaccount.com
emr4-bernie-dev-runner@emr4-bernie-dev.iam.gserviceaccount.com
```

Grant each runner only the minimum provider role needed to call Vertex AI. Start
with Vertex AI User for dev, then tighten to custom roles if needed after the
exact permissions are measured.

Grant `yuri@littlestardigital.com` service-account impersonation rights on each
dev runner. Do not grant this broadly at organization level unless there is a
clear reason.

## Local Dev Authentication

Install or update the Google Cloud CLI, then authenticate as the daily user:

```powershell
gcloud auth login yuri@littlestardigital.com
gcloud config set account yuri@littlestardigital.com
```

Set the working project for the capability you are testing:

```powershell
gcloud config set project emr4-bernie-dev
```

Create Application Default Credentials:

```powershell
gcloud auth application-default login
```

Set the ADC quota project explicitly:

```powershell
gcloud auth application-default set-quota-project emr4-bernie-dev
```

For local commands that need to run as the service account, use impersonation:

```powershell
gcloud config set auth/impersonate_service_account emr4-bernie-dev-runner@emr4-bernie-dev.iam.gserviceaccount.com
```

To stop impersonating:

```powershell
gcloud config unset auth/impersonate_service_account
```

## EMR4 `.env`

Use project/location/provider settings. Do not set
`GOOGLE_APPLICATION_CREDENTIALS` for normal local AI development.

Example Bernie dev settings:

```env
GCP_PROJECT=emr4-bernie-dev
GCP_LOCATION=australia-southeast1
BERNIE_BOOKING_INTERPRETER_PROVIDER=fake
```

For an explicit non-PHI live smoke only:

```env
BERNIE_BOOKING_INTERPRETER_PROVIDER=gemini_vertex
```

Keep fake provider defaults for ordinary tests and review harnesses.

## Smoke Order

Run fake first:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider fake --reference-date 2026-06-28 --expect-result interpreted
```

Then run live only after impersonation, quota project, budget alerts, and API
enablement are confirmed:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider gemini_vertex --allow-live --reference-date 2026-06-28 --expect-result interpreted
```

The live smoke must use non-PHI dummy input.

## Budget And Quota Safety

Before repeated live provider testing:

- create a low monthly budget on the billing account
- set alerts at 25%, 50%, 75%, 90%, and 100%
- confirm the Vertex AI quota region, especially `australia-southeast1`
- keep live smoke traffic low and deliberate

## Retiring JSON Keys

If old service-account keys exist:

1. Identify every key and the service account it belongs to.
2. Disable the key first.
3. Run fake and live non-PHI smokes.
4. Confirm no runtime still uses `GOOGLE_APPLICATION_CREDENTIALS`.
5. Delete the key.
6. Remove old IAM bindings for retired accounts.

Do not commit JSON keys, `.env` secrets, or local ADC files to the repository.

