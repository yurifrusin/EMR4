# Ariadne Sydney Vertex Gemini 2.5 Flash — Provider-Blocked Contract Closeout

Date: 2026-07-24
Tranche: 2
Result: `ariadne_vertex_sydney_gemini_25_provider_blocked_contract_pass`

The repository-local launcher boundary, purpose-built one-use broker, typed
cell request, typed release schema, fixed Vertex request constructor,
deterministic proofreader, bounded provider-error reducer, policy manifest,
isolation manifest, relay and audit-chain contracts pass without using ADC,
contacting Google Cloud or making a provider call.

The cell request contains authored-synthetic evidence and a non-secret policy
identifier only. It contains no provider, project, region, endpoint,
service-account, ADC, OAuth, API-key or Google Cloud CLI material. The broker
constructs the only provider request and pins it to:

`https://australia-southeast1-aiplatform.googleapis.com/v1/projects/bernie-emr4-dev/locations/australia-southeast1/publishers/google/models/gemini-2.5-flash:generateContent`

The request contains no tools, function calling, grounding, retrieval,
explicit context cache or automatic routing. Gemini 2.5 Flash thinking is
disabled with `thinkingBudget: 0`; output is bounded to 256 tokens and the
provider response schema admits only the four frozen authored-synthetic
fields.

The proofreader admits exact grounding and types, performs only whitespace,
canonical enum-casing and deterministic-order repairs, and atomically releases
only admitted fields. All other defects edge-abort. The provider-error reducer
retains only the frozen allowlist and discards raw error bytes after hashing.

The focused provider-blocked suite passes 24 tests. Static checks prove the
broker does not read API-key environment variables. The in-process dry-run
proves exact one-use ledger consumption, provider-free fixture handling,
hash-chain integrity and rejection of a second exchange.

Independent review identified that the first repository-only error reducer
could copy a neutral free-form provider message. No provider error or provider
call had occurred. The reducer was hardened before acceptance: it now always
discards free-form messages, admits only a bounded numeric code, strict
normalized status and allowlisted field paths, and retains the discarded raw
bytes only as a hash. A focused regression proves arbitrary message and
untyped-code content cannot survive.

This tranche does not prove ADC usability, cloud-control posture, project
entitlement, real container isolation, provider request acceptance or
Australian physical processing. It opens only the read-only ADC and
entitlement preflight.
