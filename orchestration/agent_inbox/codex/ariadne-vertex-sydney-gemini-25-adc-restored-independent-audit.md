# Independent Audit — Gemini 2.5 Flash Sydney ADC-Restored Continuation

Date: 2026-07-24
Mode: repository-read-only; no credential, Google Cloud, provider, network or
Docker lifecycle operation
Result:
`ariadne_vertex_sydney_gemini_25_adc_restored_independent_audit_pass`

The independent review accepts
`ariadne_vertex_sydney_gemini_25_cache_control_blocked` after three
repository-local repairs.

It verified 36 focused tests: seven preflight, five audit, ten Compass and
fourteen Continuity tests. The eight-event external audit chain and head
validate, every bound contract and artifact hash matches, Continuity graph
revision 37 and Compass map revision 24 are bound, and the rendered Compass is
exact.

The review found and caused repair of:

- the restored external audit was initially absent from the new Continuity
  node and Compass evidence;
- several texts overstated a failed explicit cache-disable check as positive
  evidence that caching was enabled; and
- key-material non-use was not clearly distinguished from the authorised
  read-only user-managed key inventory.

The accepted evidence states only that the read-only check did not verify
explicit `disableCache: true`. It does not claim that caching was positively
observed enabled. An externally authorised operator must determine the current
state and establish the required explicit disabled state if needed.

Historical rejected nodes remain immutable. Provider calls, retries, durable
rehearsal or occupied ledgers, containers, networks, images, broker processes
and temporary credential files are all zero. No sensitive raw content was
identified.

This review validates repository evidence integrity, sequencing, redaction and
successor-gate closure. It did not repeat credential refresh or cloud-control
reads and does not independently establish the underlying cloud observations.
It proves no provider inference, real isolation, typed release, Australian
physical processing or sovereign processing.
