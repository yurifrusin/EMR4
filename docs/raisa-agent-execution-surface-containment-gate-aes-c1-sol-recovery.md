# Raisa AES-C1 provider-free admission rehearsal — Sol recovery

Date: 2026-08-11

## Disposition

`recovery_result: deterministic_candidate_pass`

The initial blue candidate `fadecf47a24ee1837047ffddbd5ab306a30f2c8c`
admitted undeclared candidate fields and accepted mutable/open nested contract
rules. The single bounded DeepSeek revision
`cb950e4b048956435c0412cacbb2675ae8c99a09` repaired those findings, but exact
Sol readback found one residual: changing the value of an existing inherited
AES-C0 digest still returned no `validate_contract()` error. The later full
report rejected the mismatch against the file, but the contract validator and
schema were not themselves exact as frozen acceptance requires.

The bounded blue revision lease was consumed. Under the orchestrator recovery
lease, Sol adopted both blue commits as untrusted source and made only this
amendment:

- bind all three inherited AES-C0 paths and digest values as one exact constant
  map in the evaluator;
- bind each digest to its exact `const` in the closed contract schema;
- mutate an existing inherited digest in both focused and hostile regression
  coverage; and
- regenerate deterministic provider-free evidence.

The independent reproduction now returns both a schema `const` error and
`inherited_artifact_digests:not_exact`. All eight hostile contract mutations
are rejected with zero admitted, while the frozen 45 scenarios remain 2 allow,
25 deny and 18 stop. The 59-test AES-C1/AES-C0/API Spine packet and Ruff pass.

This recovery adds no runtime, adapter, provider/model call, product or patient
data, source/database/watcher, credential/IAM/network, executable tool,
command/write, deployment, production, release, Pages or protected-ref
authority. Fresh exact-HEAD Gemini red/veto review remains required after the
full deterministic gate.
