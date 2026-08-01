# Raisa Cloud Run public-HTTPS development-host deployment plan

Date: 2026-07-31

Status: `authorised_exact_external_deployment`

## Authority

Yuri authorises the next frozen boundary from the accepted operator packet:

1. create one Docker-format Artifact Registry repository named
   `raisa-office-web-dev` in `australia-southeast1`;
2. build the already accepted closed static context and push its image to that
   repository;
3. resolve and deploy the immutable image digest as one Cloud Run development
   service named `raisa-office-web-dev`;
4. use only
   `raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com`;
5. make the verified static service publicly invokable; and
6. run the operator packet's post-deployment HTTP, browser, IAM, configuration,
   audit and cleanup gates.

## Exact target and posture

- Project: `bernie-emr4-dev`
- Region: `australia-southeast1`
- Repository: `raisa-office-web-dev`
- Service: `raisa-office-web-dev`
- Initial origin class: exact service `https://*.run.app` origin
- Workload: authored-synthetic static taskpane and native Diary assets only
- Runtime service account project roles: zero
- Billing: request based
- Minimum instances: `0`
- Maximum instances: `1`
- CPU: `1`
- Memory: `256Mi`
- Concurrency: `20`
- Timeout: `60s`
- CPU throttling: enabled
- Ingress: `all`
- Session affinity: disabled
- HTTP/2: disabled
- Secrets, volumes, VPC connector and custom domain: none
- `RAISA_HOSTING_MODE`: `public_https_development`
- `EXPECTED_PUBLIC_ORIGIN`: exact resulting service origin

The first deployment remains private until its returned service origin,
runtime identity, immutable digest and bounded configuration are verified.
Public invocation may be granted only after the final exact-origin revision is
ready. If the precomputed canonical origin differs from the returned origin,
keep the service private, rebuild the same closed context for the returned
origin, deploy that new immutable digest, verify it, and only then grant public
invocation.

## Credential and build boundary

Use the current non-interactive Google Cloud operator session without printing
or recording its human identity or tokens. Docker authentication must use a
task-owned temporary `DOCKER_CONFIG`; remove it after the push. Do not use the
Bernie Vertex service account, an API key, a service-account key, Cloud Build
or `--source`.

The build context must be generated into a validated task-owned temporary
directory from the accepted 20-file allowlist. It must contain no repository
root, `.git`, evidence, environment file, source map, local data, patient data
or credential.

## Closed boundaries

This authority does not permit another project, region, repository, service,
runtime identity or hosting platform; a provider call; backend or database
connectivity; microphone, command or document-write authority; patient,
product-derived, health, clinical or historical data; custom domain; Office
tenant mutation; production; or release.

## Acceptance

- Repository is exact, Docker format and Sydney located.
- Pushed image digest is resolved from Artifact Registry.
- Active Cloud Run revision uses the immutable digest and exact runtime
  identity.
- Min/max, CPU, memory, concurrency, timeout, throttling, ingress, environment
  and absent secret/volume/VPC settings match.
- The exact runtime identity retains zero project roles and zero user-managed
  keys.
- `allUsers` receives only `roles/run.invoker` on the exact service.
- The HTTPS health, policy, taskpane and Diary routes pass; unsafe, API,
  source-map, traversal and non-GET routes fail closed.
- An ordinary browser load observes no EMR backend or provider request.
- The materialized Office manifest remains `ReadDocument` and validates.
- Task-owned local container, image tag, build context, Docker credential
  directory, listener and browser residue is removed.
