# LC4V9 Sol Framework Recovery

Date: 2026-07-16
Authority: `docs/ariadne-orchestrator-recovery-lease.md`

DeepSeek V4 Flash/high ran once through Claude Code `--bare` from source
`f14f86a4b9a32f0083b10204bc8e4d4481a312fd`. The external session is closed.
It left an uncommitted candidate and an incomplete candidate receipt; GPT Sol
preserved the exact untrusted files in commit
`dfe7210433ceeb4aeae10eb615a37bda71a1f85b` without representing that commit as
worker-authored provenance.

Exact preserved SHA-256 values:

- framework: `87c00ea82e8b80dd35730714344017d89b84ab47343c53704b1e360c5c5f23fe`;
- focused tests: `476e3c742fb1d3f13efbdc713357bc2e556735dca7199716778b4fa7b5b9614f`;
- worker candidate receipt: `76bc8571dadb0774d4cc956d81a52c311fe07e23dfe13a429e69978fafd26725`.

The worker receipt reports 89,488 input, 8,076,672 cache-read, and 117,826
output tokens, with a non-authoritative adapter estimate of USD 7.443606. Sol
independently reproduced 68/68 focused plus taxonomy tests.

## Rejection

`DECISION: candidate_rejected_conceptual`

The green tests encode several fail-open acceptance errors:

1. evidence failures before marker creation raise and leave the attempt
   reusable instead of returning `certification_invalid` from a consumed
   attempt;
2. marker creation is split into exclusive creation and a fallible overwrite,
   while consumption-write errors are swallowed;
3. scenario and Gold required schemas omit fields needed for all fourteen
   independent dimensions;
4. coverage-cell identity is silently equated with scenario ID;
5. evaluator result IDs, repeats, exact fields, and membership in the fixture
   are not bound, and `complete` is not checked as the conjunction of every
   dimension;
6. threshold values are accepted even when they differ from the frozen rule;
7. policy dimension misses are incorrectly converted into policy-failure
   counters, making the policy dimensions effectively require 576/576 despite
   the frozen 548/576 dimension gate;
8. the exact loaded evaluator path is not matched to a manifest path; and
9. report persistence has no deterministic complete-byte hash contract.

These are category/acceptance defects, not a bounded mechanical omission.
Under the Flash complexity rule there is no same-lane correction loop.

## Sol amendments

Sol will retain only useful structural ideas and replace the acceptance state
machine, schemas, bindings, result validation, counter semantics, deterministic
reporting, and focused tests. The recovered implementation must independently
prove:

- durable consumed-marker creation before any protected input read;
- `certification_invalid` on every post-consumption evidence failure;
- exact fixed schemas and frozen threshold values;
- explicit coverage-cell identity and all Gold fields required for fourteen
  dimensions;
- exact evaluator source path/hash/blob binding;
- exact 288-by-two result identity, repeat, conjunction, and variance checks;
- separate semantic misses from explicit policy/integration failure counters;
  and
- canonical aggregate report bytes with a returned SHA-256.

Fresh Gemini pre-content veto remains mandatory after the recovered head is
committed. No V9 corpus, evaluator, authoring module, thresholds, manifest,
seal, marker, report, or protected content exists during recovery.

## Recovery result

Sol replaced the injected evidence authorities with framework-owned SHA-256,
UTF-8 JSON parsing, `inspect.getsourcefile` checks for both the loaded framework
and evaluator, repository-relative path enforcement, real Git ancestry/blob
commands, and binary exclusive durable marker/report writes with exact-byte
readback. The marker is created directly in `consumed` state before any
protected input read. Invalid launch IDs consume the fixed marker path, marker
collisions stop before protected input access, and an unsealed report path is
never written.

The exact fixture/group/scenario/Gold/projection/threshold/manifest/seal/
evaluator-result/report schemas now fail closed. Coverage-cell identity is
explicit and separate from scenario ID. Results must contain every one of 288
fixture scenarios at repeats zero and one exactly once, `complete` must equal
the fourteen-dimension conjunction, repeat variance must be zero, and frozen
threshold values cannot be weakened. Semantic dimension misses remain separate
from explicit policy and integration failure counters.

Sol's recovered focused gate passes 61/61 including twelve ordinary taxonomy
tests. The ordinary runtime-isolation selection passes 2/2 after deselecting
only the documented pre-existing blocked-gate equality node. Python compilation
and `git diff --check` pass. No actual V9 content or protected artifact exists.
