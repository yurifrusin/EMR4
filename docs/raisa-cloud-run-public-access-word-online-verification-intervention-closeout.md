# Raisa Cloud Run public access and Word Online verification — intervention closeout

## Result

Accepted partial result: the exact Cloud Run public-access, HTTPS route,
security-policy, hosted-browser and Office-manifest gates pass. The Word Online
developer-manifest gate stopped before transmission because the ChatGPT Chrome
Extension does not currently expose local file selection.

## Cloud and public host

- Project: `bernie-emr4-dev`
- Region: `australia-southeast1`
- Service: `raisa-office-web-dev`
- Revision: `raisa-office-web-dev-00005-w82`
- Invoker IAM check: disabled on this service only
- `allUsers` IAM bindings: zero
- Traffic: 100% to the exact ready revision
- Runtime identity: the existing dedicated zero-project-role, keyless service
  account

The accepted route matrix covers public health, policy, taskpane, synthetic
Diary and content-manifest resources, plus HEAD, unknown-route, API,
source-map, unsupported-method and encoded-traversal fail-closed cases.

The `/healthz` spelling was replaced by `/health` for the public acceptance
probe because Google documents that some URL paths ending in `z` are reserved
on Cloud Run. Both repository routes remain supported for local compatibility.

The public hosted companion required one narrow repair: the existing
authored-synthetic hosted-policy gate now admits the companion demo on the
exact frozen HTTPS origin as well as localhost. It still requires the exact
policy identifier, authored-synthetic classification and seven false authority
flags.

## Office manifest and Word Online

The task-specific manifest validates. Its source location, AppDomain and both
icons return HTTP 200, and its permission is `ReadDocument`.

A fresh blank personal Word Online document reached:

1. Add-ins;
2. More Add-ins;
3. My Add-ins;
4. Manage My Add-ins;
5. Upload My Add-in; and
6. the developer `Upload Add-in` dialog.

The visible Browse control and its direct file input both failed to expose a
file chooser to the controlled Chrome session. Therefore:

- no manifest was uploaded;
- no add-in was loaded;
- no authored-synthetic request was submitted;
- no Office dialog was opened;
- no document body was read or written; and
- no provider, backend, database, confirmation or command path ran.

Yuri must enable **Allow access to file URLs** for the ChatGPT Chrome Extension
before this exact gate can resume. No cloud, IAM, service or manifest change is
required.

## Residue

All task-owned local build directories, local repair image tags, containers and
networks were removed. The Cloud Run service remains intentionally deployed at
the accepted revision. Two blank task-created Word documents contain no
authored content; one is preserved as the live handoff and one closed document
may remain in personal storage. Both must be deleted after the terminal Word
result.

## What this proves

It proves the exact service-only Cloud Run public-access mechanism, public
static route and policy behavior, hosted companion admission, and the validity
and reachability of the Office manifest resources.

It does not prove Word Online add-in execution, Office dialog behavior,
authenticated Office identity, clinician-role authorization, safety for real
or product data, processing geography, production fitness or release
readiness.
