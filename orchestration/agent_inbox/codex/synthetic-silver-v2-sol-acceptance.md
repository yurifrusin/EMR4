# Synthetic Silver V2 Course — Sol Acceptance

Date: 2026-07-18

Decision: `pass_synthetic_course_complete`

Sol accepts source head `b90b50b434b5020d424ffc7c106e53a1bf4a6081` and
the fresh independent Gemini veto as the completed ordinary-development
synthetic Silver v2 course.

The final 96-anchor/192-candidate population regenerates exactly. All 192
candidates pass the complete deterministic interpretation/replay/scoring path
twice, safety is 384/384, and variance is zero. Exact hashes are:

- anchor: `sha256:8609cdd7cab00281c7c2061cf24291be91ca225c5e26c41f8aa5411729f47b23`;
- candidates: `sha256:1dd79a3209f87e46dbdb2a375c2f2c82a654e9208105f6ee28b4cb5ce4b4d46e`;
- admission: `sha256:a3f2ba35e5526d5b4529d37a77214b7034cb11f29517b4a5a3f1df044c5346e0`;
  and
- robustness: `sha256:ea4217943fa3a2ec83ec4afcff12cd7eebeba520f225d4e0fb290abb7850dedd`.

Gemini independently reviewed all 96 anchors and 192 candidates, reproduced
70/70 focused tests, and returned `DECISION: pass`, with
`POLICY_REPLAY_SCORER_CHANGES: false` and `PROTECTED_ACCESS: false`.

This acceptance is Silver/pending ordinary-development evidence only. It makes
no real-world, Gold, protected-certification, clinical-safety, production,
provider/runtime, API, database, UI, confirmation, deployment/release, or
write-authority claim. No residual supported parser target remains in the
frozen population. The standing v2 refinement authorization is exhausted; a
new product track requires Yuri's decision.
