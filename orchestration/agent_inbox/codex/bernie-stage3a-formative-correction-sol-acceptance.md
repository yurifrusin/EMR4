# Bernie Stage 3A Formative Correction — Extra High Sol Acceptance

Date: 2026-07-20

Reasoning level: `Sol Extra High`

Decision: `revision_required_pending_bounded_rerun_and_s3a06`

Claim scope: `local_authored_synthetic_stage3a_instrument_correction`

## Decision

The bounded correction tranche passes its implementation and verification
gates, but Stage 3A itself does not yet pass. Yuri's first export is genuine
formative evidence and supports continuing the product direction; it is not a
clean final scenario population because the original instrument allowed state
carryover and incomplete routes/fixture sequences.

Exactly seven affected scenarios require a corrected Yuri rerun. The separate
S3A-06 `live_local_browser_backend_postgres` safety check also remains open.

## Gate decision

| Gate | Result | Evidence |
|---|---|---|
| Rehydration | pass | fresh post-compaction receipt with all five named sources; five aligned Git refs |
| Export safety | pass | exact SHA-256; 14 structured observations; prompt/transcript flag false; no uncontrolled free text or sensitive field |
| Trigger traceability | pass | every correction is mapped to its triggering observation and rerun scenario |
| State isolation | pass | clean scenario baseline, route disabling, grid-date and attention reset |
| Projection semantics | pass | chronological patient/practitioner ordering and authored availability |
| Attention semantics | pass | exact per-scenario sequences, dated notice, replay/stale/scope suppression, current-read projection guard |
| Observation boundary | pass | allowlisted codes only; no prompt, transcript, free-text, backend, telemetry or browser persistence |
| Deterministic verification | pass | 11 focused and 60 combined tests; Node, Ruff and whitespace checks |
| Rendered verification | pass | desktop target paths plus 375-pixel no-overflow QA; zero console warnings/errors |
| Final Stage 3A | open | seven-scenario Yuri rerun and separate authoritative S3A-06 check remain |

No failed gate was overridden.

## Exact identities

| Artifact | SHA-256 |
|---|---|
| Yuri v1 export | `2e162be00132e2a8cf149d506de24015a571011b98206e5078c6db9eff5da3ba` |
| `docs/diary/stage3a/index.html` | `adf1560ece03d521932a0e2b7541f951565bd3f125e6e3c2b77e3d657c360755` |
| `docs/diary/stage3a/stage3a-data.js` | `1c2e681905c620a808951890e8709e4ea240b8a19e7aa994cb414aa6ba26acef` |
| `docs/diary/stage3a/stage3a-core.js` | `26ffdfa3e1ad24cefebdd0c95e5d4432a051d409a6256089dbef26b7b6d60b18` |
| `docs/diary/stage3a/stage3a.js` | `e1c2aecf800f55ad6606f4a7a749958bb06513b81ab2d065ebdfd52e5b7f9d34` |
| `docs/diary/stage3a/stage3a.css` | `207f2dc6c351257d41895323168d4ebd3bb5804c6ec393b612e9bc1c9129cd53` |
| `tests/test_bernie_stage3a_study_artifacts.py` | `f8d11381ed2d67eca82ac49585980f79cd77cd43cab9069ca19d018baf5eb1b1` |
| post-compaction runtime state | `878466fe81dea507daa1b11381d8003449b6e4dce5ed8c433e3dea7321f2a15e` |
| post-compaction receipt | `592ac54c731ae9f552e3786d80733c695fca4b0f81d2d9ed9b3084fc8c99e800` |

## Evidence boundary and next action

All correction interaction evidence is
`authored_synthetic_fixture_browser`. It is not live-backend, event-runtime,
provider, production, or representative-staff evidence.

Yuri now reruns S3A-03, S3A-04, S3A-06, S3A-11, S3A-12, S3A-13, and S3A-14,
downloads the v2 export, and returns it. Sol then executes the separate visible
local S3A-06 confirmation and exact PostgreSQL readback before returning the
final Stage 3A result.
