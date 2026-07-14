# LC4R5 DW1 — Explanation Clarification/Action Semantics

You are the bounded implementation/test worker for LC4R5. Work only in the
disposable worktree and branch supplied as your current working directory.
The protected GPT Sol session is Conductor, acceptance/recovery owner, and
integrator. You have no planning, acceptance, integration, or push authority.

Read `AGENTS.md` and
`orchestration/agent_inbox/codex/lc4r5-explanation-clarification-contract.md`
completely, then implement that contract exactly.

Constraints:

- Use DeepSeek V4 Flash/high only through this Claude Code bare session.
- Do not open, enumerate, list, search, import, run, regenerate, hash-check, or
  inspect any protected holdout fixture, support module, seal, receipt, or
  report. Do not use broad repository file listings.
- Use only the ordinary LC4 development loader and authored synthetic tests.
- Do not edit generated fixtures, generators, AGENTS.md, scenario schemas,
  audit/replay policy, action grammar/route contracts, providers, routes/API,
  database, UI, deployment, T3 gates, or historical-diary surfaces.
- Never copy expected scenario fields into interpretation.
- Do not broaden explanation action-detection patterns in this sprint.
- Preserve exact `tomorrow at 3pm`, lossless normalization, T3.1-T3.4, and all
  live/write deferrals.

Required work:

1. Repair only the post-recognition `explain_schedule` clarification rule in
   `app/services/bernie/semantic_extraction.py`: a resolved practitioner is
   sufficient read-only context, while the existing resolved-patient behavior
   remains supported.
2. Preserve clarification for ambiguous and context-free explanations, and add
   narrow authored tests for practitioner exact/corrected, `some doctor`,
   omitted context, patient-specific preservation, generic calendar and
   availability anti-overmatch, safety, tools/authority, exact time, lossless
   normalization, and oracle independence.
3. Add `scripts/bernie_lc4r5_report.py` with `--check` mode,
   `docs/bernie-lc4r5-report.json`, and a concise
   `docs/bernie-lc4r5-implementation-note.md`.
4. Reproduce the frozen repair target `84`, hash `b69abbcbc6febe29`, and the
   preserved ambiguous set `12`, hash `34c95db64c716f56`. Confirm full semantic
   counts `880/814/628/101/300/782` for intended action, action semantics,
   temporal relation, normalized values, entity semantics, and clarification,
   plus safety `1152/1152` and zero repeat variance.
5. Write `orchestration/agent_inbox/codex/lc4r5-dw1-completion.md` with scope,
   commands/results, hashes/counts, boundaries, and exact candidate commit.
6. Run `git diff --check`, commit all owned candidate changes on your worker
   branch, and finish with a single-line `DECISION: pass` or
   `DECISION: revision_required`. Do not push.

Use `C:\Users\sarashera\emr4\.venv\Scripts\python.exe` for Python and pytest.
If a frozen count or classification appears wrong, do not silently redefine
it: preserve the evidence and return `revision_required` with the exact
discrepancy.
