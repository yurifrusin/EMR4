# Raisa Cloud Run API and runtime-identity enablement closeout

Date: 2026-07-31

Result: `raisa_cloud_run_api_runtime_identity_enablement_pass`

## Outcome

The exact authorised Google Cloud control-plane increment completed in project
`bernie-emr4-dev`:

- `run.googleapis.com` is enabled;
- `artifactregistry.googleapis.com` is enabled; and
- `raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com` exists
  and is active.

The dedicated runtime identity has zero project roles and zero user-managed
keys. No project role or key was requested or created for it.

## Repeated resource preflight

With both APIs enabled, the resource results are now authoritative:

- the `raisa-office-web-dev` Docker repository does not exist in
  `australia-southeast1`; and
- the `raisa-office-web-dev` Cloud Run service does not exist in
  `australia-southeast1`.

Public invocation is therefore not applicable.

## Preserved boundaries

No repository, service, image, revision, public IAM binding, secret, volume,
VPC connector, custom domain or deployment was created. Billing was not
changed. No interactive authentication occurred, and no operator identity,
credential, token or raw authentication response was recorded.

Enabling Google APIs can cause Google to provision provider-managed service
agents as a platform side effect. This tranche did not enumerate or modify
those identities; its least-privilege assertion is limited to the dedicated
Raisa runtime identity.

Continuity graph revision 177 and Compass map revision 158 bind the result.
Seventeen focused cloud-foundation, static-host and Compass tests pass, and the
continuity graph, rendered Compass, JSON, Python compilation and
`git diff --check` gates pass.

## Next gate

The next external action requires new authority to create the exact Sydney
Artifact Registry repository and Cloud Run service, push an immutable image,
and configure public static invocation under the frozen operator packet.
Nothing in this closeout authorises those actions.
