# Raisa Cloud Run public health-route repair

Date: 2026-07-31

Status: `bounded_repository_and_same_service_repair`

The first public route matrix observed:

- all static positive routes except `/healthz` returned 200;
- `/healthz` returned a Google edge 404 without the application's security
  headers;
- an encoded traversal redirected within the same origin and terminated at
  the allowlist's 404;
- a bodyless POST was rejected by the Google edge before the container; and
- the explicit curl `--request HEAD` probe incorrectly waited for a body.

Google's Cloud Run known-issues documentation states that some paths ending in
`z` are reserved and recommends avoiding all such paths. The server now admits
`/health` in addition to the retained historical local `/healthz` route.

The repair may rebuild the same closed context, push one new immutable digest
to the existing Sydney repository and update only the existing
`raisa-office-web-dev` service. The exact origin, runtime identity, public
Invoker-IAM-check posture, min-zero/max-one limits, no-secret/no-volume/no-VPC
posture and authored-synthetic zero-authority policy must remain unchanged.

The first ordinary public browser load then showed the normal login surface
because the Reception One companion flag remained loopback-only. The existing
hosted admission predicate already requires the exact HTTPS `run.app` origin,
the closed public hosting policy, authored-synthetic classification and all
seven authority fields false. The companion predicate now admits that same
hosted predicate in addition to loopback; it does not admit an arbitrary
remote host or add backend, credential, provider, command or write authority.
