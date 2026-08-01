# Raisa Cloud Run public access and Word Online verification plan

Date: 2026-07-31

Status: `authorised_exact_service_public_access_continuation`

## Authority

Yuri explicitly authorises disabling the Cloud Run Invoker IAM check only for
service `raisa-office-web-dev` in project `bernie-emr4-dev`, region
`australia-southeast1`, followed by the bounded public HTTPS, browser,
manifest and Word Online verification gates. No other service, IAM policy or
organisation policy may be changed.

## Exact mutation

The only authorised cloud mutation is:

```powershell
gcloud run services update raisa-office-web-dev `
  --project bernie-emr4-dev `
  --region australia-southeast1 `
  --no-invoker-iam-check
```

Before and after the mutation, verify the exact service URL, immutable image
digest, latest ready revision, runtime identity and frozen min-zero/max-one,
resource, origin, environment, no-secret, no-volume and no-VPC posture.
Require the `allUsers` IAM binding count to remain zero.

## Public verification

After the exact annotation is observed:

1. exercise `/health`, `/hosting-policy.js`, `/taskpane.html`, the native
   smoke Diary and the generated manifest;
2. require unknown, API, source-map, traversal and non-GET routes to fail
   closed;
3. perform one ordinary public browser load and observe zero EMR backend and
   provider requests;
4. validate a task-specific manifest bound to the exact public origin with
   `ReadDocument` only; and
5. use the user's existing authenticated Word Online session for one
   supervised, authored-synthetic, default-off companion check.

The Word exercise may use one new blank document and one temporary custom
manifest. Do not inspect or record document contents, document URL or
identifier, filename, tenant, account, cookies, storage, credentials or
authentication headers. Stop rather than changing an Office tenant catalogue,
central deployment, login, browser trust policy or account setting.

## Closed boundaries

Real, product-derived, patient, health, clinical and historical data remain
closed. Provider, backend, database, microphone, appointment command,
document-write, production and release authority remain false. The public
service contains only the accepted static development assets and grants its
zero-project-role runtime identity no new permission.

## Acceptance and closeout

The result must record the exact access-control posture, route matrix, browser
request classes, manifest permission and Word disposition without Office
identifiers or raw authored-synthetic request text. Increment Continuity and
Compass together, validate the rendered report, preserve unrelated worktree
changes and perform independent local residue checks. A platform or tenant
policy failure is a candid bounded result, not authority to weaken policy.

## Deterministic public-route repair

The first real public matrix found that Cloud Run intercepted `/healthz`
before the request reached the container. Google's published Cloud Run known
issues state that some paths ending in `z` are reserved. The repository-local
server therefore retains `/healthz` for historical local acceptance and adds
the equivalent `/health` public route. Rebuilding and redeploying the same
closed static image to the same exact service is admitted as an ordinary,
bounded request-contract repair. It changes no other service, IAM policy,
organisation policy, identity, region, data class or authority.
