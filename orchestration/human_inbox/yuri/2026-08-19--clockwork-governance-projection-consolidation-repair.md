# Clockwork governance projection repair — paired summary

Date: 2026-08-19
Timestamp: 2026-08-19T09:49:44.1344800+10:00 (Australia/Brisbane)

## Lay summary

The clockwork repair has passed. It now takes one authoritative reading and produces the surrounding administrative records from that reading, instead of requiring us to remember and copy the same hashes, counts, statuses and links into several places.

It caught every one of the 22 representative historical and surrounding failure cases before publication and reduced the number of hand-maintained governance surfaces from 10 to 4. The independently reviewed build cost was 13 reruns; eight post-review closeout corrections make the final end-to-end cost 21. At the measured saving of 9 reruns per representative closeout, it pays for itself after about 3 future closeouts, or 4 when the predecessor experiment's 13 sunk reruns are included.

The first independent review caught a real read-only-interface defect: running the validator without a publication flag still rewrote evidence. That attempt was rejected with no decision. The defect was fixed and regression-tested; a genuinely fresh Gemini review then passed with a clean, unchanged worktree.

Nothing has been switched over yet. The existing controls remain authoritative until you choose whether to authorize a separate live migration/retirement rehearsal or keep the new mechanism in shadow while product work resumes.

## Technical summary

- Exact reviewed candidate: `a0bb86b78bfc011066142740c82d5c25cab7b9c8`.
- Deterministic evidence source: `de777641a060766a12c429f4891f8d638f18e1bc`.
- Bundle: `07d5f807deb9ad810982ef551506b38ef3d66acb23ba452970083535506acabe`.
- Coverage: 13/13 preserved rerun probes; 9/9 surrounding-workflow probes.
- Steady-state projection: 0 surrounding reruns per representative closeout.
- Maintained surfaces: 10 -> 4 (60% reduction).
- Final implementation/test growth: 849 / 850 lines; the exact reviewed candidate was 850 / 850 before terminal-latch replay decoupling.
- Cost: 13 reruns in reviewed evidence plus 8 post-review closeout reruns, 21 end to end; predecessor sunk cost 13; payback 3 repair-only or 4 cumulative closeouts.
- Regression: default runner leaves evidence/report byte-identical; `--publish` is required for all persistent writes.
- Independent review: first attempt rejected without decision; fresh Gemini 3.7 Flash/high retry passed 10/10 commands and 8/8 focused tests at clean unchanged HEAD.
- Register: revision 561, 651 incidents, all corrected/contained, none open.
- Protected refs: local/origin `master` and `handoff/current` unchanged at `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
- No live adoption, control retirement, DeepSeek/HMR, Claude fallback, product/practice/data/runtime/deployment/release/Pages or protected-ref action.
