# Ariadne Sydney Vertex Gemini 2.5 Flash — Threat Model Delta

Date: 2026-07-24
Scope: one authored-synthetic, Sydney-region Vertex rehearsal
Authority: `docs/ariadne-vertex-sydney-gemini-25-flash-authority-delta.md`

## Protected assets

- the existing keyless impersonated Application Default Credentials boundary;
- short-lived OAuth access tokens obtained from that boundary;
- the exact Bernie project, service account, custom role and regional endpoint;
- authored-synthetic request and typed response integrity;
- single-use ledger state and the external audit hash chain;
- the product, database, clinical, command and human-release boundaries.

## Trust boundaries

The occupied work cell is credential-free and attached only to a task-internal
Docker network. It sends the exact typed Ariadne request to a purpose-built
relay. The relay possesses only a one-use broker bearer token and forwards only
the exact `/v1/execute` exchange to the host broker. The host broker alone may
use `google.auth.default()` and call the exact Sydney Vertex data-plane URL.
Control inspection is read-only, transmits no rehearsal prompt and cannot
change Google Cloud state.

## Threats and deterministic controls

| Threat | Control | Failure disposition |
|---|---|---|
| Credential or provider detail enters the cell | Exact request-field allowlist; exact build context; no ADC, OAuth, CLI, provider or service-account material mounted or forwarded | Reject before container start |
| Cell reaches the Internet or host directly | Internal-only Docker network; no published port; no host network; only the relay spans networks | Abort and clean up |
| Relay becomes an unrestricted proxy | Exact method, path, body-size, token and one-use checks; fixed host broker target | Reject and consume no extra provider call |
| Broker calls a global, alternate-region or alternate-provider endpoint | Frozen hostname, path, provider, project, identity and model checks; no caller-controlled URL | Abort; no fallback |
| API/static key is used or disclosed | No key fields or key environment forwarding; no key-file path; static source checks; audit records only `api_key_authentication_used: false` | Abort on any non-ADC path |
| Service-account key is introduced | Read-only key inventory requires zero user-managed keys; no key creation, copy, mount or inspection | Stop for Yuri |
| Prompt or raw response is retained | Durable evidence contains only hashes, allowlisted audit fields and schema-admitted authored-synthetic release values | Fail audit acceptance |
| Provider error leaks prompt, credential or unconstrained message | Bounded sanitizer permits status/code, allowlisted field paths, scanned message <=2 KiB and raw-error hash only | Redact or fail closed |
| Model invents or issues a command | Exact output schema plus deterministic grounding/type/command proofreader | Edge abort; no draft release |
| Safe repair changes meaning | Repairs limited to whitespace, canonical enum casing and deterministic ordering | Edge abort |
| Retry exceeds authority | Distinct exact ledgers; one primary and one contract-defect-only retry; no automatic retry | Stop after frozen ceiling |
| Provider-managed retention exceeds admission | Read-only project cache and request-response logging checks must prove disabled/absent before the call | Stop for Yuri |
| Residual container, network, image, token file or broker remains | `finally` cleanup plus independent post-run Docker/process/file inspection | Close failed; no further call |

## Residual claims

The local container can constrain capabilities and egress. It cannot establish
the provider's physical processing location. The strongest permitted location
claim is the combination of Google's published locational-endpoint contract,
the configured Sydney hostname, and the independently observed request path.
No sovereign-processing claim is authorised.
