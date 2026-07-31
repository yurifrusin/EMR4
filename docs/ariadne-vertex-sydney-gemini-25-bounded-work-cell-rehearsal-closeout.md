# Ariadne Sydney Vertex Gemini 2.5 Flash Rehearsal — Closeout

Date: 2026-07-24
Result: `ariadne_vertex_sydney_gemini_25_adc_preflight_blocked`
Terminal gate: Tranche 3, existing ADC and entitlement preflight

## Result

Yuri's Gemini 2.5 Flash reorientation was preserved as a fresh Continuity
descendant. Tranche 1 passed because current official Google documentation
publishes the exact GA model ID `gemini-2.5-flash` for both model availability
and ML processing in `australia-southeast1`. Tranche 2 passed its repository-
only typed contracts and made no provider or authentication call.

Tranche 3 then failed closed at its first credential gate. Both local
inspection and `google.auth.default()` identify impersonated credentials bound
to:

- project `bernie-emr4-dev`;
- target service account
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`; and
- the cloud-platform target scope.

The first non-interactive refresh through `google.auth.default()` failed. A
second bounded check using the existing gcloud Application Default Credentials
refresh path also failed. Neither check returned a usable short-lived token.
No token, raw authentication response, credential file, API-key information,
billing identifier or unapproved human identifier was printed, hashed or
persisted.

This is an explicit Yuri-intervention condition. Codex did not revoke, replace
or recreate ADC; run an interactive login; change the active human account;
change IAM, API, billing, project or service-account state; introduce a
service-account key; or use an API-key, static-key, provider, model, region or
endpoint fallback.

## Gate accounting

| Gate | Result |
|---|---|
| 1. Provider/residency admission | pass |
| 2. Provider-blocked contracts | pass |
| 3. Existing ADC/entitlement | blocked at non-interactive refresh |
| 4. Provider-free real isolation | not opened |
| 5. Occupied Vertex rehearsal | not opened |
| 6. Proofreader/release | not opened |
| 7. External audit/closeout | completed for the failed sequence |

No durable rehearsal or occupied ledger was opened. No rehearsal prompt was transmitted. No
Google Cloud control metadata was read because refresh failed first. No
container, relay, broker server, task network or task image was started. No
provider data-plane endpoint was contacted. Occupied-call count is zero,
retry count is zero and application cost attributable to a model call is USD
0.

## Cleanup and residue

There was no runtime isolation state to tear down. A sanitized, task-scoped
residue record independently reports zero containers, networks, images,
broker processes and temporary credential files. It records only counts and
inspection methods, not process command lines, environment values or
credential paths. The only broker execution was an in-process provider-free
unit test using a temporary directory; that one temporary test ledger was
consumed within the test and pytest removed the temporary state. No durable
rehearsal ledger exists.

## What the evidence proves

The evidence proves current documentary Sydney admission for Gemini 2.5
Flash; exact repository request, output, proofreader, audit, error and one-use
contracts; the configured ADC type/project/target/scope binding; deterministic
refusal to proceed when a short-lived token cannot be refreshed; zero provider
calls; and zero task-scoped container residue.

It does not prove usable ADC, cloud-control posture, project model entitlement,
request-response logging or cache configuration, a real isolated runtime,
provider request acceptance, inference, a model draft, proofreader release,
latency, token usage, Australian physical processing or sovereign processing.
The container design can constrain local capabilities, but it cannot determine
the remote provider's processing geography.

The durable external audit contains a seven-event self-verifying hash chain
covering authority, documentary admission, provider-blocked contracts,
configured ADC binding, failed refresh, successor-gate closure and residue.
Because no occupied attempt opened, latency, token usage, provider status,
admitted output fields and released values are correctly absent. The
independent review accepts the fail-closed result after repository-only
hardening.

The Tranche 3 record remains a sanitized operator attestation. Independent
review verified redaction structure, sequencing, hash binding and successor
closure but did not repeat credential operations or independently establish
the underlying cloud response.

## Unresolved gate and intervention

Yuri must restore or make usable the already authorised exact Bernie
impersonated ADC through an appropriate external credential workflow. After
that external action, continuation requires a fresh five-source rehydration
and a new read-only preflight. No prior conditional call authority has been
consumed, but this closed run cannot silently resume or substitute a
credential mechanism.
