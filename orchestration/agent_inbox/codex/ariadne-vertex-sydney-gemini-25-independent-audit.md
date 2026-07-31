# Independent Audit — Ariadne Sydney Vertex Gemini 2.5 Flash

Date: 2026-07-24
Mode: repository-read-only; no credential, Google Cloud, Docker or provider
operation
Result: `ariadne_vertex_sydney_gemini_25_independent_audit_pass`

The independent review accepts the Tranche 3 fail-closed disposition after
repository-local repairs. It verified 24 provider-blocked tests, 6 preflight
tests, 10 Compass tests, all 11 bound Tranche 2 hashes, revision-bound
Continuity/Compass, exact rendered Compass, zero occupied calls/retries, one
consumed temporary provider-free test ledger, zero durable rehearsal/occupied
ledgers, and a bound task-scoped residue record.

The review found and caused repair of the following before acceptance:

- arbitrary provider error text and untyped provider codes could survive;
- an oversized provider error would have hashed only its retained prefix;
- ADC discovery/refresh exceptions could escape as raw diagnostics;
- provider training and abuse-retention controls were not explicitly marked
  unverified;
- no inert provider-blocked launcher contract or exact launch plan existed;
- launcher/broker/relay/cell source hashes and residue evidence were not fully
  bound; and
- test-ledger wording did not distinguish temporary and durable ledgers.

No provider response, token or credential exposure occurred: the provider path
never opened and the actual ADC failure was safely reduced. All defects were
repository-local and repaired without external state change.

The launcher remains intentionally inert. It proves the exact future command
plan and containment policy, not Docker sequencing, broker start-up, cleanup or
real isolation. The durable Tranche 3 record is a sanitized operator
attestation that the configured impersonated type, project, target service
account and scope were identified and that two permitted non-interactive
refresh paths returned no usable token. This review validates redaction,
fail-closed sequencing and successor-gate closure; it did not repeat credential
operations or independently establish the underlying cloud response.

No entitlement, IAM/audit/logging/cache posture, provider acceptance,
inference, typed release, Australian physical processing or sovereign
processing is proved.
