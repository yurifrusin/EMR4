# Raisa Cloud Run API and runtime-identity enablement plan

Date: 2026-07-31

Status: `authorised_exact_external_mutation`

## Authority

Yuri authorises exactly:

1. enable `run.googleapis.com` in `bernie-emr4-dev`;
2. enable `artifactregistry.googleapis.com` in `bernie-emr4-dev`;
3. create
   `raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com`;
4. grant that runtime identity no project role; and
5. repeat the frozen read-only Sydney repository, Cloud Run service, runtime
   identity and public-invocation checks.

## Frozen boundary

- Project: `bernie-emr4-dev`
- Region: `australia-southeast1`
- Repository candidate: `raisa-office-web-dev`
- Cloud Run service candidate: `raisa-office-web-dev`
- Runtime identity:
  `raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com`
- Runtime project roles: exactly zero
- Data and payload transmission: none

This authority does not permit creating the Artifact Registry repository,
creating or deploying the Cloud Run service, granting public invocation,
building or pushing an image, changing billing, changing another IAM binding,
creating a key, configuring a secret, custom domain, backend, provider,
database, production or release surface, or inspecting or recording operator
identity or credentials.

## Execution and acceptance

- Recheck each target immediately before mutation and avoid duplicate work.
- Enable only the two exact services.
- Create only the exact service account if it remains absent.
- Do not add a project IAM binding for the runtime identity.
- Verify both APIs enabled, the service account active, and the exact runtime
  member absent from all project-role bindings.
- Repeat exact repository and Cloud Run service `describe` checks.
- If either resource remains absent, record `not_found`; do not create it.
- Record only sanitized outcomes and no raw authentication response.
