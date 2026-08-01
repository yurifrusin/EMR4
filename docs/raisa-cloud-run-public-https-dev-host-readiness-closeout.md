# Raisa Cloud Run public-HTTPS development-host readiness closeout

Date: 2026-07-31

Result: `raisa_cloud_run_public_https_dev_host_readiness_pass`

## Outcome

The next Word Online dependency is now prepared without creating it. The
repository contains a minimal Cloud Run-compatible static host for the
compiled Office taskpane and the current native Diary development assets, an
origin-bound synthetic-only hosting policy, a `ReadDocument` manifest template
and an external-operator packet.

An ordinary production-build defect was repaired: the taskpane no longer loads
both copied and bundled copies of its runtime. Production source maps are
disabled and the obsolete placeholder deployment origin is gone.

## Closed package and runtime

The generated Docker context is built from an explicit 20-file allowlist. It
does not contain the repository, `.git`, tests, evidence, environment files,
credentials, source maps or unrelated Diary studies. The dependency-free
server accepts only `GET` and `HEAD`, exposes no API, rejects unlisted and
unsafe paths, logs no request content and emits no-store and browser-security
headers.

The image uses the digest-pinned official Node 24 slim base and passed with:

- numeric non-root user `65532:65532`;
- read-only root filesystem;
- no host mounts;
- all Linux capabilities dropped;
- no-new-privileges;
- bounded CPU, memory and process count; and
- one internal-only Docker network.

Both local-acceptance and exact simulated Sydney `run.app` policy modes passed.
The public-mode simulation rejected a wrong host and wrong forwarded protocol.
It was not a real Cloud Run endpoint.

## Rendered and contract evidence

The in-app browser rendered only the bounded Clinician One authored-synthetic
selection card at 480×720 and 360×780. Its checkbox was operable and its action
remained disabled without a Word host. Console errors and application warnings
were zero.

Observed page assets were the same-origin static package and Microsoft Office
runtime assets. No EMR backend, Vertex or other provider request was observed.
The generated HTTPS fixture manifest passed Microsoft's Office manifest
validator with `ReadDocument`.

Ninety-eight focused Word, Raisa, Reception One and API Spine tests pass.

## API Spine and protected boundaries

This increment changes a deployment manifest and client capability gate only.
It adds no GraphQL read, REST command, asynchronous event, Access AI call,
database operation or appointment authority. The existing
`current_consult_note` frame remains explicit, single-use, client-local,
source-labelled and non-authoritative.

Provider, credential, backend, database, microphone, document-write, clinical,
command, production and release counts are zero. No Google Cloud API, service,
repository, service account, IAM policy, billing setting, custom domain or
Office tenant state was created or changed.

## Cleanup

Every task container, internal network, image, temporary build context,
materialized fixture manifest, listener and browser tab was removed. There is
no task-specific container, network, image, listener, temporary-context or
credential residue.

Continuity graph revision 176 and Compass map revision 157 bind the result.

## Evidence limit

This proves a local Cloud Run-compatible synthetic-only static package,
origin-bound policy and valid Office manifest shape. It does not prove:

- Cloud Run or Artifact Registry enablement, entitlement or deployment;
- public IAM or organisation-policy compatibility;
- authenticated Word Online loading, Office identity or clinician
  authorization;
- safety for real or product-derived patient, health, clinical or historical
  data;
- Microsoft or Google physical or sovereign processing location;
- backend or provider integration; or
- production or release readiness.

## Next external decision

The repository-local work is complete. The next tranche would be the exact
read-only cloud preflight followed, only with Yuri's explicit external
authority, by creation of the dedicated no-project-role runtime identity,
Sydney Artifact Registry repository and public `raisa-office-web-dev` Cloud
Run service. The supervised Word Online exercise remains a later gate after
deployment verification.
