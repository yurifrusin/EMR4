# GCP Dev AI Projects Service Account Setup

This is the repeatable Windows/PowerShell runbook for setting up EMR4's dev AI
projects without JSON service-account keys.

Current Little Star Digital dev projects:

```text
scribe-emr4-dev
bernie-emr4-dev
```

Target posture:

```text
human Google account -> service account impersonation -> narrow AI service account -> Vertex AI
```

Do not create or download JSON API keys for these service accounts.

## Accounts And Projects

Recommended human accounts:

| Account | Use |
|---|---|
| `admin@littlestardigital.com` | Cloud Identity / organization administration |
| `yuri@littlestardigital.com` | Daily GCP and EMR4 development |

Recommended runtime service accounts:

| Project | Service account |
|---|---|
| `scribe-emr4-dev` | `emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com` |
| `bernie-emr4-dev` | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` |

## Key Distinctions

`gcloud auth login` authenticates the CLI for setup/admin commands.

`gcloud auth application-default login` creates Application Default Credentials
for local app/library calls.

ADC is a single local active credential. If you create ADC for Scribe and then
create ADC for Bernie, the Bernie ADC replaces the Scribe ADC. Switch ADC only
when you switch the thing you are testing.

In PowerShell, environment variables use this syntax:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "scribe-emr4-dev"
$env:VERTEX_AI_LOCATION = "australia-southeast1"
```

Do not use Bash syntax such as `GOOGLE_CLOUD_PROJECT=scribe-emr4-dev` in
PowerShell.

## 0. Authenticate gcloud On Windows

Run this once, or whenever your local gcloud account is wrong:

```powershell
gcloud auth login yuri@littlestardigital.com
gcloud config set account yuri@littlestardigital.com
gcloud auth list
```

Confirm both projects are visible:

```powershell
gcloud projects describe scribe-emr4-dev
gcloud projects describe bernie-emr4-dev
```

## 1. Enable Required APIs

Run for Scribe:

```powershell
gcloud config set project scribe-emr4-dev

gcloud services enable `
  aiplatform.googleapis.com `
  iamcredentials.googleapis.com `
  serviceusage.googleapis.com `
  cloudresourcemanager.googleapis.com `
  logging.googleapis.com `
  monitoring.googleapis.com `
  --project scribe-emr4-dev
```

Run for Bernie:

```powershell
gcloud config set project bernie-emr4-dev

gcloud services enable `
  aiplatform.googleapis.com `
  iamcredentials.googleapis.com `
  serviceusage.googleapis.com `
  cloudresourcemanager.googleapis.com `
  logging.googleapis.com `
  monitoring.googleapis.com `
  --project bernie-emr4-dev
```

`iamcredentials.googleapis.com` is required for service account impersonation.
`aiplatform.googleapis.com` is required for Vertex AI / Gemini calls.

## 2. Create Runtime Service Accounts

Run for Scribe:

```powershell
gcloud iam service-accounts create emr4-scribe-ai-dev `
  --display-name "EMR4 Scribe AI Dev" `
  --project scribe-emr4-dev
```

Run for Bernie:

```powershell
gcloud iam service-accounts create emr4-bernie-ai-dev `
  --display-name "EMR4 Bernie AI Dev" `
  --project bernie-emr4-dev
```

If a service account already exists, `gcloud` will report that. Continue with the
IAM checks/bindings below.

## 3. Grant Vertex AI Invocation Permission

For dev, start with Google's predefined Vertex AI user role. Later, tighten this
to a custom role once the exact permissions are measured.

Run for Scribe:

```powershell
gcloud projects add-iam-policy-binding scribe-emr4-dev `
  --member "serviceAccount:emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com" `
  --role "roles/aiplatform.user"
```

Run for Bernie:

```powershell
gcloud projects add-iam-policy-binding bernie-emr4-dev `
  --member "serviceAccount:emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com" `
  --role "roles/aiplatform.user"
```

For prompt/generation calls the underlying fine-grained permission of interest
is `aiplatform.endpoints.predict`, but `roles/aiplatform.user` is acceptable for
initial dev setup.

## 4. Grant Human Impersonation Rights

Grant `roles/iam.serviceAccountTokenCreator` on each service account to the
human account or Cloud Identity group that should be allowed to run local live
smokes.

Run for Scribe:

```powershell
gcloud iam service-accounts add-iam-policy-binding `
  emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com `
  --project scribe-emr4-dev `
  --member "user:yuri@littlestardigital.com" `
  --role "roles/iam.serviceAccountTokenCreator"
```

Run for Bernie:

```powershell
gcloud iam service-accounts add-iam-policy-binding `
  emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com `
  --project bernie-emr4-dev `
  --member "user:yuri@littlestardigital.com" `
  --role "roles/iam.serviceAccountTokenCreator"
```

If you are doing setup as `admin@littlestardigital.com`, either grant the same
bindings to `admin@...` temporarily or switch to `yuri@...` after these bindings
exist.

Cleaner later: create a group such as
`access-ai-dev-operators@littlestardigital.com` and grant impersonation to the
group instead of individual users.

## 5. Create Local ADC Using Impersonation

Run only one of these sets at a time.

### Use Scribe ADC

Use this when testing Scribe/Copilot:

```powershell
gcloud config set project scribe-emr4-dev

gcloud auth application-default revoke

gcloud auth application-default login `
  --impersonate-service-account=emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com `
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

Set PowerShell environment variables for the current terminal:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "scribe-emr4-dev"
$env:VERTEX_AI_LOCATION = "australia-southeast1"
```

### Use Bernie ADC

Use this when testing Bernie:

```powershell
gcloud config set project bernie-emr4-dev

gcloud auth application-default revoke

gcloud auth application-default login `
  --impersonate-service-account=emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com `
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

Set PowerShell environment variables for the current terminal:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "bernie-emr4-dev"
$env:BERNIE_AI_PROJECT = "bernie-emr4-dev"
$env:VERTEX_AI_LOCATION = "australia-southeast1"
$env:BERNIE_AI_LOCATION = "australia-southeast1"
```

Do not run both Scribe and Bernie ADC commands back-to-back unless you are
intentionally switching. The later command replaces the earlier ADC.

## 6. Verify ADC

Check that ADC can mint a token:

```powershell
gcloud auth application-default print-access-token
```

Check active CLI project:

```powershell
gcloud config get-value project
```

Check PowerShell environment variables:

```powershell
echo $env:GOOGLE_CLOUD_PROJECT
echo $env:VERTEX_AI_LOCATION
echo $env:BERNIE_AI_PROJECT
echo $env:BERNIE_AI_LOCATION
```

Blank `BERNIE_*` values are fine when testing Scribe.

## 7. EMR4 Runtime Settings

Do not set `GOOGLE_APPLICATION_CREDENTIALS` for normal local AI dev.

Scribe/Copilot local terminal:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "scribe-emr4-dev"
$env:VERTEX_AI_LOCATION = "australia-southeast1"
```

Bernie local terminal:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "bernie-emr4-dev"
$env:BERNIE_AI_PROJECT = "bernie-emr4-dev"
$env:VERTEX_AI_LOCATION = "australia-southeast1"
$env:BERNIE_AI_LOCATION = "australia-southeast1"
$env:BERNIE_BOOKING_INTERPRETER_PROVIDER = "gemini_vertex"
```

Keep fake providers as the default for ordinary automated tests.

## 8. Common Warnings And Fixes

### Active project does not match ADC quota project

This warning appears when your `gcloud config set project ...` value differs
from the quota project in user ADC.

For normal user ADC, this can be fixed with:

```powershell
gcloud auth application-default set-quota-project scribe-emr4-dev
```

or:

```powershell
gcloud auth application-default set-quota-project bernie-emr4-dev
```

For impersonated ADC, `set-quota-project` may fail with:

```text
The application default credentials are not user credentials, quota project cannot be added.
```

That is expected. Recreate ADC with the correct service account for the project
you are testing instead of trying to edit the ADC file.

### PowerShell says GOOGLE_CLOUD_PROJECT is not recognized

Use PowerShell syntax:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "scribe-emr4-dev"
```

Do not use:

```text
GOOGLE_CLOUD_PROJECT=scribe-emr4-dev
```

That is Bash syntax, not PowerShell.

### Permission denied while impersonating

Confirm the human account has `roles/iam.serviceAccountTokenCreator` on the
service account:

```powershell
gcloud iam service-accounts get-iam-policy `
  emr4-scribe-ai-dev@scribe-emr4-dev.iam.gserviceaccount.com `
  --project scribe-emr4-dev
```

or:

```powershell
gcloud iam service-accounts get-iam-policy `
  emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com `
  --project bernie-emr4-dev
```

## 9. Optional Hardening

Once the flow is working, consider:

- enable organization policy `constraints/iam.disableServiceAccountKeyCreation`
  on the Dev folder to prevent accidental JSON key creation
- grant impersonation through Cloud Identity groups, not individual users
- add low budget alerts on both dev projects
- enable relevant Cloud Audit Logs for Vertex AI provider calls
- replace `roles/aiplatform.user` with a custom role containing only measured
  permissions needed for invocation

## 10. Safe Repeat Order

When rebuilding from scratch:

1. `gcloud auth login yuri@littlestardigital.com`
2. enable APIs in both projects
3. create service accounts in both projects
4. grant each service account `roles/aiplatform.user`
5. grant `yuri@littlestardigital.com` Token Creator on each service account
6. create ADC for either Scribe or Bernie, not both at once
7. set PowerShell `$env:` variables for that terminal
8. run non-PHI live smoke only after fake tests pass

