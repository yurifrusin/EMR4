# Bernie LC4V3 Fresh Certification Closeout

LC4V3 completed its one permitted aggregate baseline on 2026-07-15. The
evidence procedure is valid and deterministic, but the frozen product
thresholds return `certification_fail`.

The source commit is `c57a4d62dd1b633a0a1bb20f26b5bd0fd0a5d310`. The run
contains 24 groups, 288 fresh synthetic Gold/adjudicated scenarios, 72
multi-turn trajectories, two repeats, 576 samples, and 288 distinct coverage
cells. Its report hash is
`sha256:cdbb5967ea0c5e32f7176425b04efdd6600aca7c51f88e241139da15301a8b73`.
Repeat variance is zero and safety is 576/576.

Temporal relations, normalized values, and intended actions each passed
576/576. Complete composed contracts passed 494/576; entity semantics passed
494/576; interpretation and replay tool sequences each passed 496/576. The
worst aggregate slice was plain language at 0/82, while every other language
form passed completely. This discontinuity is consistent with a systematic
corpus-authoring or representation defect. It is not case-level evidence and
does not establish a parser gap.

The frozen decision rule therefore closes LC4V3 as a valid failed
certification. It forbids repair, relabelling, or a second run. Deterministic
parser repair remains complete against currently authorized ordinary
development evidence, not universally complete against all possible future
language. Deferred actions such as `check_in`, context-dependent states such
as text-only `mismatched`, and genuinely new language remain known product or
evidence gaps rather than proved parser regressions.

After consumption, 56 content-blind framework/handover tests and 132 ordinary
composed-evaluator tests passed serially. The two pre-declared immutable
historical report-regeneration nodes remained deselected. The aggregate-only
checker revalidated the report without touching protected content.

“Continuous learning” in this project means a controlled offline engineering
loop: safely collect de-identified candidate language, human-adjudicate it,
reproduce it in an ordinary development corpus, repair the responsible layer,
validate on untouched evidence, and deploy a versioned change. It does not
mean online self-modification, automatic learning from live patients, or
tuning directly against certification holdouts or live-model responses.

Holdouts v1, v2, and v3 are sealed. Only this closeout, the aggregate report,
and Sol acceptance may be used for planning. A later certification requires a
new Yuri decision authorizing a genuinely fresh holdout version or a reviewed
reuse policy. The recommended next path is a content-blind authoring-quality
tranche followed by a genuinely fresh v4, with no v3 case reuse.

T3.1-T3.4 remain intact and blocked by default. T3.5 provider adapters, live
calls, runtime wiring, deployment, and write authority remain deferred.

Authoritative decision:
`orchestration/agent_inbox/codex/lc4v3-sol-acceptance.md`.
