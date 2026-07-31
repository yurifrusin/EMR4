# Raisa Cloud Run public-HTTPS development-host readiness plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_repository_local_readiness_only`

## 1. Objective and authority

Prepare and locally verify the smallest public-HTTPS hosting package needed for
the next authored-synthetic Word Online exercise. The candidate external
resource is:

| Field | Frozen value |
|---|---|
| Google Cloud project | `bernie-emr4-dev` |
| Cloud Run service | `raisa-office-web-dev` |
| Region | `australia-southeast1` |
| Initial hostname class | exact Cloud Run `run.app` service hostname |
| Workload | static Clinician One taskpane and native Diary development assets |
| Data classification | authored-synthetic only |
| Production status | development only |

This tranche may change repository-local source, packaging, tests and
continuity evidence and may build/run a disposable local container. It may
read public vendor documentation and public container metadata.

It may not:

- enable a Google API;
- create or change a Google Cloud project, Cloud Run service, Artifact Registry
  repository, service account, IAM policy, billing control or custom domain;
- submit a cloud build, push an image or deploy a revision;
- use the Bernie prediction-only impersonated ADC for infrastructure work;
- read or change any Google credential;
- use product-derived, patient, health, clinical or historical data; or
- open backend, provider, microphone, command, document-write, production or
  release authority.

## 2. API Spine classification

This is a deployment-manifest and client-capability readiness increment. It
does not add a GraphQL read, REST command, async event, provider invocation or
database operation.

The existing `current_consult_note` frame remains typed, minimal,
source-labelled, single-use, non-authoritative and in memory. The static host
must not acquire an API, database, provider or credential path.

## 3. Package boundary

The build context must be generated from an explicit allowlist into a fresh
temporary directory. The repository root, `.git`, local data, tests, evidence,
credentials, environment files, source maps and unrelated Diary study assets
must not enter the image context.

The image may contain only:

- the production-built Office taskpane HTML, CSS, JavaScript and exact image
  assets needed by that page;
- the six current native Diary files:
  `diary.html`, `diary.css`, `diary.js`, `meta-grid.css`, `meta-grid.js` and
  `office-bootstrap.js`;
- `images/emr_cube1.png`;
- the dependency-free static server; and
- non-secret build provenance.

The container:

- uses a digest-pinned official Node base;
- runs as a numeric non-root user;
- listens on the Cloud Run `PORT`;
- has no package-install step or runtime dependency;
- exposes no directory listing or source map;
- rejects unallowlisted routes and path traversal;
- records no request query, body, headers or user content;
- serves a dynamic, exact-origin synthetic-only policy document;
- applies no-store caching and bounded browser security headers; and
- provides only an inert `/healthz` response.

## 4. Hosted synthetic-only policy

The checked-in ordinary hosting policy is disabled. The Cloud Run server may
enable the hosted policy only when all exact fields match:

- contract version;
- `public_https_development` mode;
- `authored_synthetic` data class;
- exact expected origin;
- `provider_authority=false`;
- `backend_authority=false`;
- `credential_authority=false`;
- `microphone_authority=false`;
- `command_authority=false`;
- `document_write_authority=false`; and
- `production_authority=false`.

The taskpane must accept `clinician_one_context_demo=true` on a non-loopback
host only under that exact policy. In this mode it must show only the bounded
Clinician One selection card, bypass ordinary sign-in, and make every backend
or provider route unavailable.

The native Diary is packaged for same-origin dialog readiness only. This
tranche does not exercise it in Word Online or grant it backend authorization.

## 5. Deployment posture to freeze, not execute

The future operator packet must require:

- a dedicated runtime service account with no project roles;
- public invocation for static assets only;
- request-based billing;
- minimum instances `0`;
- maximum instances `1`;
- low CPU and memory limits;
- no secret, volume, VPC connector, provider credential or database
  configuration;
- exact `EXPECTED_PUBLIC_ORIGIN`;
- exact synthetic-only hosting mode;
- an immutable image digest;
- `run.app` initially, not a custom domain; and
- a separate manifest generated only after the final service origin is known.

The Bernie AI service account is prohibited as the Cloud Run runtime or
deployment identity.

## 6. Acceptance gates

### Gate A — rehydration and preservation

- All five mandatory Ariadne sources pass.
- HEAD and the four protected refs are recorded.
- Every unrelated user change remains preserved.

### Gate B — deterministic build

- The taskpane production build passes.
- The packaging script rejects symlinks, missing assets, source maps,
  unexpected files and an unsafe origin.
- Two clean package generations have an identical content manifest.
- The context contains only the frozen allowlist.

### Gate C — local container

- The digest-pinned image builds.
- The container runs non-root with a read-only root filesystem, dropped
  capabilities, no-new-privileges, bounded memory, CPU and processes, and no
  host networking or mounts.
- The exact health, taskpane, hosting-policy, Diary and image routes pass.
- Unknown, traversal, API and source-map routes fail closed.
- Required security headers are present.
- The packaged page makes no backend or provider request in a route-observed
  browser check.

### Gate D — Office and API Spine

- The deployment manifest template remains `ReadDocument`.
- All source locations use one exact placeholder origin and HTTPS after
  materialisation.
- Existing Clinician One, Word, Reception One and API Spine tests pass.
- No GraphQL, REST, async, database or provider contract changes.

### Gate E — cleanup and closeout

- The disposable container, image, network, temporary contexts and browser
  processes are removed.
- Independent residue checks pass.
- JSON, XML, Python, JavaScript, Compass, continuity and `git diff --check`
  pass.
- The operator packet distinguishes preparation from external authorization.

## 7. Stop conditions

Stop and request Yuri's explicit external authority if progress requires:

- Cloud Run, Artifact Registry, Cloud Build or another API to be enabled;
- a Google Cloud resource, service account, IAM binding or billing change;
- an image push, public endpoint, deployment or custom domain;
- use of the Bernie impersonated ADC for infrastructure;
- another project, provider, region or hosting platform;
- patient, clinical, product-derived or historical data;
- backend or provider connectivity; or
- production or release action.

## 8. Candid evidence limit

A pass proves only that a minimal synthetic-only Office/Diary static image can
be built and exercised locally under Cloud Run-compatible constraints. It does
not prove that Cloud Run is enabled or entitled, that the image can be pushed,
that Word Online can load or authorize the add-in, that Microsoft or Google
processing has a particular physical or sovereign location, or that the
surface is safe for real clinical data, production, deployment or release.
