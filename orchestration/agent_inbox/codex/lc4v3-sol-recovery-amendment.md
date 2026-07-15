# LC4V3 Sol Framework Recovery Amendment

## Rejected candidate

DeepSeek V4 Flash/high through Claude Code `--bare` produced candidate commit
`7392b951954bb7590d15f0002c050c9c26d94a0a` from frozen contract head
`31333192936215b144f02c5d3d76be352d3baeb7`. Its 69 focused tests and five
handover tests passed, and protected master remained clean. The candidate is
preserved on branch `claude/lc4v3-content-blind-framework` with its durable
launcher receipt in the disposable worktree.

Sol rejects the candidate's `DECISION: candidate_complete`. The defects are
conceptual rather than mechanical, so the Ariadne Flash rule forbids a
same-lane correction loop.

## Acceptance failures

1. `build_manifest` checks file and variant counts but does not validate the
   `ReceptionScenarioSpec` records, unique namespaced IDs, explicit outcomes,
   lossless source spans, Gold/adjudicated provenance, or explicitly synthetic
   diary state. Several purported negative tests merely document acceptance
   and end with unconditional success.
2. `baseline-once` loads a seal but never reconstructs the current manifest or
   calls `verify_seal`. A fabricated, stale, already-consumed, or unrelated
   seal can authorize evaluation.
3. Source-commit detection fails open to `unknown-commit`, the CLI accepts an
   arbitrary source-commit override, and seal verification does not bind the
   seal to the live frozen HEAD.
4. The aggregate report omits the manifest hash, corpus hash, and source commit
   required to bind the result to the frozen corpus.
5. Post-consumption validation checks only five top-level counts plus report
   hash. It does not enforce the exact report schema, per-dimension totals,
   failure-layer keys/ranges, variance, slice-axis totals/vocabulary, or safe
   identity hashes.
6. Forbidden-key lint compares only exact singular names and can admit obvious
   plural or qualified case-level structures.
7. Report writes are not exclusive at the filesystem operation, and input/
   output path aliasing is not rejected.

## Sol recovery lease

Sol adopts the source only as an untrusted candidate and owns every amendment:

- validate every group and scenario before manifest creation;
- make manifest reconstruction strict and bind safe file identities;
- make source identity a strict 40-hex Git commit with no production override;
- require `baseline-once` to rebuild the manifest, verify the frozen seal and
  unconsumed state against live HEAD, and use exclusive distinct outputs;
- bind source, manifest, and corpus hashes into the aggregate report;
- enforce exact aggregate schema, dimensions, totals, variance, slices, and
  safe vocabularies without corpus access after consumption;
- strengthen recursive leakage lint; and
- replace false-positive tests with real fail-closed assertions.

No real LC4V3 content may be created during recovery. Gemini must review the
exact recovered framework head before Sol authors any holdout case.
