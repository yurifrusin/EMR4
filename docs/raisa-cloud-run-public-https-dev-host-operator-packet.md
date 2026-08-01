# Raisa public-HTTPS development host operator packet

Date: 2026-07-31

Status: `prepared_not_authorised_for_external_execution`

## Frozen target

| Field | Exact value |
|---|---|
| Project | `bernie-emr4-dev` |
| Region | `australia-southeast1` |
| Cloud Run service | `raisa-office-web-dev` |
| Artifact Registry repository | `raisa-office-web-dev` |
| Runtime service account | `raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com` |
| Initial URL | exact Cloud Run `run.app` origin |
| Data | authored-synthetic only |
| Cloud runtime authority | static files only; no project role |

Do not use the Bernie Vertex prediction service account as the runtime or
deployment identity. Do not configure a secret, provider credential, database
URL, VPC connector, volume, custom domain, minimum warm instance, backend
route or production traffic.

## Operator sequence

The sequence below is frozen for a later separately authorised external
tranche. It must not be executed merely because this packet exists.

### 1. Read-only preflight

An authorised Google Cloud operator first verifies:

```powershell
$Project = 'bernie-emr4-dev'
$Region = 'australia-southeast1'
$Service = 'raisa-office-web-dev'
$Repository = 'raisa-office-web-dev'
$RuntimeSa = 'raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com'

gcloud services list --enabled --project $Project `
  --filter='name:(run.googleapis.com OR artifactregistry.googleapis.com)' `
  --format='value(name)'

gcloud artifacts repositories describe $Repository `
  --project $Project --location $Region --format=json

gcloud iam service-accounts describe $RuntimeSa `
  --project $Project --format=json

gcloud run services describe $Service `
  --project $Project --region $Region --format=json
```

`NOT_FOUND` is an expected preflight result for resources that have not yet
been created. A disabled API, missing runtime identity, missing repository or
missing service is not to be repaired until Yuri explicitly authorises the
corresponding external creation or enablement.

### 2. Minimal resource creation

Only after that authority, create:

1. one Docker-format Artifact Registry repository in Sydney;
2. one dedicated runtime service account with no project role; and
3. one public Cloud Run development service.

If either required API is disabled, stop and obtain explicit API-enablement
authority before enabling it. Creation and public invocation change Google
Cloud and IAM state.

The future service posture is:

- request-based billing;
- minimum instances `0`, maximum instances `1`;
- `1` CPU, `256Mi` memory, concurrency `20`, timeout `60s`;
- CPU throttling enabled;
- ingress `all` because Word Online must reach the public static page;
- unauthenticated invocation for these static development assets only;
- the dedicated no-project-role runtime service account;
- no secrets, volumes, VPC, session affinity or HTTP/2;
- `RAISA_HOSTING_MODE=public_https_development`; and
- `EXPECTED_PUBLIC_ORIGIN` equal to the exact resulting `run.app` origin.

### 3. Build, push and deploy by digest

From a clean generated context:

```powershell
npm.cmd --prefix 'EMR4 Sidebar' run build

.\.venv\Scripts\python.exe scripts\prepare_raisa_office_web_dev_context.py `
  --output '<fresh-temporary-context>' `
  --origin '<exact-run-app-origin>'

docker build --pull --tag '<regional-image-tag>' '<fresh-temporary-context>'
docker push '<regional-image-tag>'
```

Resolve the pushed digest from Artifact Registry, then deploy the immutable
`image@sha256:...`, not a mutable tag. The command must freeze the posture
above and must not use `--source`, because that would introduce a Cloud Build
path not admitted by this packet.

### 4. Post-deployment gates

Before uploading the generated Office manifest:

1. verify the exact service URL and active revision;
2. verify the runtime service account and zero project-role posture;
3. verify min/max instances, resources, ingress, public invocation and the two
   exact environment variables;
4. fetch `/healthz`, `/hosting-policy.js` and the taskpane security headers;
5. require unknown, `/api`, source-map, traversal and non-GET routes to fail;
6. observe one ordinary browser load and require zero EMR backend and provider
   requests;
7. run the repository, Office manifest, API Spine and Compass gates again; and
8. retain no credential, build-context or temporary manifest residue.

Only then may Yuri conduct the separately supervised authored-synthetic Word
Online check. Real or product-derived patient, health, clinical and historical
data remain prohibited.

## Stop conditions

Stop for Yuri if the operator encounters a disabled API, new billable or IAM
surface beyond the frozen resources, organisation-policy conflict, inability
to use an unprivileged runtime identity, non-Sydney deployment, non-`run.app`
origin, custom-domain requirement, Office tenant change, credential
reconfiguration, backend/provider need, or any request for real data.

## Evidence limit

Cloud Run provides an HTTPS service URL and can run in Sydney, but that does
not establish the processing location of Microsoft Word Online, Australian
physical processing or sovereign processing. Sydney also does not currently
support direct Cloud Run domain mapping, so the first exercise uses the
service's `run.app` URL.
