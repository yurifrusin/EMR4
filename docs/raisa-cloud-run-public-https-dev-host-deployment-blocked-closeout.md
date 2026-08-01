# Raisa Cloud Run public-HTTPS development-host deployment blocked closeout

Date: 2026-07-31

Result: `blocked_organization_policy_public_invocation`

## Completed work

The authorised Sydney deployment reached a ready private service:

- Docker-format Artifact Registry repository `raisa-office-web-dev`;
- immutable image digest
  `sha256:6696b3c97682ba8d02d3b18bab3d5d3d131f8c56c613c1adfca32400f94b3f5d`;
- Cloud Run service `raisa-office-web-dev`;
- exact URL
  `https://raisa-office-web-dev-nnbntbx5yq-ts.a.run.app`; and
- ready revision `raisa-office-web-dev-00003-9vg`.

The returned hash-based URL differed from the precomputed number-based URL.
The first revision remained private, the exact returned origin was
materialised, the rebuilt static image retained the same digest, and the final
private revision is bound to the exact returned origin.

## Verified private posture

The latest revision receives 100 percent of traffic and uses the exact
immutable digest and dedicated runtime identity. That identity retains zero
project roles and zero user-managed keys.

The service and revision both have minimum instances zero and maximum
instances one. It uses 1 CPU, 256 MiB, concurrency 20, timeout 60 seconds,
request-time CPU throttling, no startup CPU boost, HTTP/1 and ingress `all`.
It contains exactly the two admitted environment variables and no secret,
volume, VPC connector or Cloud SQL configuration.

## Blocking gate

The attempted exact `allUsers` / `roles/run.invoker` binding returned
`FAILED_PRECONDITION` under effective Domain Restricted Sharing organisation
policy. The binding was not created and the service remains private.

Google documents two public Cloud Run mechanisms and recommends disabling the
Cloud Run Invoker IAM check when Domain Restricted Sharing prevents an
`allUsers` binding:
`https://docs.cloud.google.com/run/docs/authenticating/public`.

That alternative changes the frozen access-control mechanism and was not
executed. Yuri must explicitly authorise
`gcloud run services update raisa-office-web-dev --no-invoker-iam-check`
for this exact project, service and region, or arrange a broader organisation
policy exception through an authorised Google Cloud administrator.

## Deferred verification

Because the service is private, no unauthenticated route or browser acceptance
was attempted. Word Online remains untested. The public HTTP, browser, Office
manifest and final release gates remain open.

## Cleanup and costs

All task-owned local image tags, contexts, temporary Docker credentials and
raw error working files were removed. The authorised repository, stored image
digest and private min-zero Cloud Run service remain. Artifact storage can
incur ongoing cost; the private service has no minimum warm instance.

No provider, backend, database, patient data, custom domain, production or
release action occurred.

## Verification and continuity

The deployment-specific and Compass suite passes 20 tests. The broader
inherited Word, Reception One and API Spine gate passes 137 tests. Python
compilation, JavaScript syntax, JSON parsing, Continuity validation, Compass
schema and semantic validation, rendered Compass generation and
`git diff --check` pass.

A final read-only cloud observation confirms the exact service URL, latest
ready revision and runtime identity; the `allUsers` binding count is zero, the
Invoker IAM check remains enabled and the service remains private.

Continuity graph revision 178 and Compass map revision 159 bind this accepted
blocked closeout. No commit, push, protected-ref movement, pull request or
external-worker dispatch occurred.
