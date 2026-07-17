# Bernie Synthetic Silver V2 Course Closeout

Date: 2026-07-18

Decision: `synthetic_course_complete`

## Outcome

The authorized development-only synthetic Silver v2 course is complete. The
final population contains 96 coherent dialogue-free anchors and 192 admitted
receptionist-to-Bernie dialogues, balanced across six actions, eight dialogue
forms, and medium/high noise. The unchanged deterministic interpretation,
replay, and scoring path ran twice per candidate: all 192 candidates are
complete, safety is 384/384, and variance is zero.

This is a bounded ordinary-development result. It is not Gold, real-world
receptionist evidence, a protected certification, clinical validation,
production readiness, provider/runtime activation, or write authority.

## Course progression

The first DeepSeek anchor candidate was conceptually rejected because its
clarifications, corrections, local-recovery forms, and delta shapes did not
satisfy the frozen contract. Sol preserved it under the recovery lease and
recovered the anchor implementation without a conceptual correction loop.

The first coherent generated population exposed both corpus defects and
supported extraction gaps. The successive frozen results were:

- initial product baseline: 6/192 complete, safety 356/384, zero variance;
- after explicit patient-alternative and whole-action reversal repair: 16/192,
  safety 384/384, zero variance;
- after independent oracle/surface repair and bounded schedule extraction:
  138/192, safety 384/384, zero variance; and
- after executable diary-state selection, approximate-time normalization,
  noise-marker repair, and final-turn status recovery: 192/192, safety
  384/384, zero variance.

No clarification policy was relaxed. Replay, scorer, certification, provider,
runtime, API, database, UI, confirmation, deployment, release, and product
write surfaces were unchanged. The final parser changes are limited to
surfaced patient alternatives, explicit named-request reversals, schedule-show
shorthand, and final-turn status evidence after an explicit restart.

## Exact evidence

- source implementation head: `b90b50b434b5020d424ffc7c106e53a1bf4a6081`;
- anchor manifest: `sha256:8609cdd7cab00281c7c2061cf24291be91ca225c5e26c41f8aa5411729f47b23`;
- candidate records: `sha256:1dd79a3209f87e46dbdb2a375c2f2c82a654e9208105f6ee28b4cb5ce4b4d46e`;
- admission: `sha256:a3f2ba35e5526d5b4529d37a77214b7034cb11f29517b4a5a3f1df044c5346e0`;
- robustness report: `sha256:ea4217943fa3a2ec83ec4afcff12cd7eebeba520f225d4e0fb290abb7850dedd`;
- focused final gate: 70/70; and
- broader preservation gate: 365/365 after deselecting exactly two immutable
  historical report-equality nodes and the unrelated pre-existing
  terminal-create replay contradiction.

The historical reports were not regenerated. Protected holdouts v1-v10,
historical diary data, the provenance-blocked appointment-call corpus, and all
other external dialogue corpora were not accessed.

## Independent veto

A fresh Gemini 3.5 Flash Antigravity project reviewed every anchor and
candidate, reproduced all four hashes and all 70 focused tests, inspected the
bounded parser diff, and returned:

```text
DECISION: pass
PRODUCT_COMPLETE: 192/192
SAFETY: 384/384
VARIANCE: 0
POLICY_REPLAY_SCORER_CHANGES: false
PROTECTED_ACCESS: false
```

Its durable report is
`orchestration/agent_inbox/antigravity/synthetic-silver-v2-final-review.md`.

During protected-PR integration, GitHub CodeQL identified two unused imports.
Sol removed only those imports; no behavior, fixture, evidence binding, or
canonical hash changed.

## Disposition

Preserve v1 as historical partial/quarantined Silver and v2 as the current
balanced ordinary-development Silver corpus. The frozen v2 population now
supplies no residual supported parser target, so another synthetic refinement
is not justified by this evidence. Yuri's standing successive-refinement
authorization is complete and grants no synthetic v3 or new protected
certification. The next product track is a new user decision.

All protected holdout, T3/provider/runtime, external-data, policy,
replay/scorer, API/database/UI, confirmation, deployment/release, and write
boundaries remain closed.
