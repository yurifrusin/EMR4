# AES-C4 bounded occupied provider proof threat-model delta

Date: 2026-08-11

Status: frozen for the exact AES-C4 authored-synthetic Sydney Vertex envelope

Parent boundaries: the accepted Agent Execution Surface gate and AES-C0 through
AES-C3 threat models and contracts.

## New assets and trust crossings

AES-C4 is the first descendant to cross a real provider data plane. The new
assets are one immutable provider-inference generation, one call/cost
reservation, one short-lived impersonated access token held by the external
broker, one newly authored-synthetic packet, one untrusted provider result and
one minimized hash-chain evidence packet.

The only new external crossing is broker to
`australia-southeast1-aiplatform.googleapis.com` over the exact Vertex
`generateContent` path. Identity refresh may use only `oauth2.googleapis.com`
and `iamcredentials.googleapis.com`. The candidate/model cannot choose any
host, path, method, project, model, identity or credential.

## Threats and required controls

| Threat | Required control | Failure disposition |
|---|---|---|
| Expired or wrong cached identity | human fresh CLI auth and separate impersonated ADC login; sanitized read-only checks bind project, account, type and scope | stop before prompt |
| ADC/gcloud store confusion | AER-0029 procedure treats the stores independently and forbids account-qualified cached-login reuse | stop before prompt |
| Static key or API-key substitution | no key creation/read/mount; broker rejects API-key and service-account-key paths | revoke and stop |
| Endpoint, redirect or fallback escape | exact Sydney hostname/path, one destination, zero redirects and no alternate provider/model/region | consume ledger, quarantine and stop |
| Model/provider selects a tool | omit tool/function/grounding/retrieval/code declarations; reject any tool/function response part | no release; consume ledger |
| Candidate chooses operation identity | work-cell schema excludes capability, adapter, destination, URL, method, audience, credential and path; broker resolves immutable registry entry | deny before call |
| Stale authority or generation replay | exact C1 intersection plus dispatch-time generation, manifest, authority, revocation, supply-chain and budget recheck | terminal stop |
| Token or lease reaches the work cell | broker-only ADC/token custody; work cell receives only closed synthetic data and digests | revoke, quarantine and stop |
| Prompt/output exfiltration through logs or errors | no raw prompt/response/provider text/thought/error retention; digest-only bounded error reducer and closed audit fields | no release; incident evidence only |
| Encoded/chunked/oversized egress | shared response-byte accounting, bounded reads and one terminal budget | abort response; consume ledger |
| Cost/call replay | reserve USD 0.25 and one call atomically before dispatch; no retry and no ledger reopening | stop |
| Schema-valid but unsafe output | post-provider proofreader binds nonce/frame/manifest and exact four-field enums with `command_authority: false` | `intelligence_unavailable` |
| Cleanup ambiguity | externally owned kill/revocation, close exact broker/listener/process, remove only task paths and prove absence | quarantine; never pass |
| Regional claim overreach | evidence claims configured/observed Sydney path only | revision required |

## API and command boundary

The call is an internal Access AI provider invocation, not GraphQL and not a
product command. No route is added. The returned object is inert evidence and
cannot authorize a REST/OpenAPI mutation. Product writes, database access,
provider-executed tools and any reusable runtime remain denied.
GraphQL remains read-only and is never invoked by AES-C4.

## Residual risk and claim limit

The provider, operating system, authentication libraries and network remain
outside EMR4's full control. Deterministic admission constrains the exact
request but cannot prove the provider has no implementation vulnerability or
that Australian physical or sovereign processing occurred. The one synthetic
call therefore supports only the exact tested containment, typed-release,
accounting and cleanup claim; it is not patient/product, deployment or
production evidence.
