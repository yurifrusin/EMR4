# LC4R8 Sol Recovery Amendment

Date: 2026-07-15

GPT Sol adopted DeepSeek V4 Flash revision `e646d40b` as an untrusted
candidate under the Ariadne recovery lease after focused tests passed. Sol's
independent diff review found three bounded verification defects:

1. `run_check` could raise on a non-dictionary record, a non-list records
   collection, or a missing required top-level section despite the fail-closed
   contract.
2. A directly changed recomputed `report_hash` field could pass because only
   canonical report content was compared with the frozen hash.
3. The order-invariance test retained selected fields plus `report_hash`, but
   did not retain explicit canonical representations of all three generated
   artifacts as evidence.

Sol amended only the LC4R8 verifier and focused tests. The recovery adds a
malformed-structure boundary returning `False`, verifies the supplied report's
own hash against its canonical content, adds four deterministic mutation
tests, and compares canonical full clarification, replay, and report artifacts
across original, fixed-seed shuffled, and reversed variant insertion order.

No taxonomy, frozen count/hash, generated fixture, runtime interpretation,
core scorer/replay, provider, route, database, UI, historical diary, protected
holdout, T3, or write-authority surface changed. Independent Gemini review is
required on the exact recovered source head before acceptance.
