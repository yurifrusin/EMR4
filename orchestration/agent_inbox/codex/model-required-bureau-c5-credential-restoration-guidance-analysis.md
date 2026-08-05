# C5 credential-restoration guidance analysis

Date: 2026-08-06

Status: corrected; every failed attempt remains preserved and zero-call

The first restoration guidance did not distinguish Google's Application
Default Credentials from the separate gcloud CLI credential store. An account-
qualified ADC login reused an expired cached source credential, and the next
ADC-only restoration left the CLI credential needed by the billing control
stale. The two ensuing pre-execution attempts therefore failed closed before
provider admission.

The corrected procedure treated the stores independently: force a genuinely
fresh interactive ADC authentication when cached ADC source credentials are
expired, restore gcloud CLI authentication separately, then verify both with
sanitized read-only refresh and exact cloud-control checks. The later read-only
Sydney preflight passed for the frozen project, impersonated identity, region,
endpoint and model without transmitting a C5 prompt or changing IAM or cloud
configuration.

This was an orchestrator guidance error, not an operator error and not evidence
about provider or model quality. It retained no credential or token. The
preserved failed evidence records zero provider calls and no external mutation.
