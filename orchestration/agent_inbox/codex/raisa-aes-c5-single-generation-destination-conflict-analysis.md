# AES-C5 single-generation destination conflict analysis

Date: 2026-08-11

## Disposition

`revision_required`

## Observation

The first frozen AES-C5 plan placed the authenticated local source read and the
Sydney Vertex request in one immutable generation with two distinct
destinations. The accepted AES-C0 schema fixes
`EgressBudget.max_distinct_destinations` to exactly one and the accepted
architecture contract repeats that one-destination-per-generation ceiling.

The first DeepSeek provider-free candidate exposed the conflict accurately in
its return receipt but then called the AES-C1 evaluator without first calling
the AES-C1 schema validator. Its hand-built manifest used a ceiling of two, so
the local tests exercised evaluation logic over a packet that was not an
admissible AES-C0/AES-C1 message. Sol rejected the candidate as acceptance
evidence. No product route, database, provider, credential, cloud or external
operation occurred.

The same review found two independent exact-route mismatches before any local
source execution: `roleLabel` is optional and `defaultLocation` is nullable or
a closed `{id, name}` object, whereas the first pure fixture required both to be
non-empty strings.

## Correction

AES-C5 now uses two separately immutable, non-overlapping generations. The
source generation contains only the exact `authoritative_read` grant and one
destination. After its single operation exhausts and the generation is
revoked, a provider generation may be created containing only the exact
`provider_inference` grant and one destination; its manifest binds the fresh
`ContextFrameSet` digest. No grant, lease, credential or AES-C0 budget transfers
between generations. A separate external attempt ledger enforces the aggregate
one-read/one-call/two-operation ceiling without enlarging either generation.

Both attempts must pass `c1.validate_attempt` with zero errors before
`c1.evaluate_attempt` may run. The exact route validator is rebound to the
actual Pydantic response contract, while still dropping all
`defaultLocation`, UUID and `active` values before the work-cell/provider
boundary.

## Prevention

Every descendant plan that composes more than one capability destination must
run the complete inherited message-schema validator against its proposed
manifest before freezing. Pure fixtures must be derived from the exact current
route schema, including nullable and nested field types, rather than from field
names alone.
