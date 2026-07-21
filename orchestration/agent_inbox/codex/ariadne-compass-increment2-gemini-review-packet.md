# Ariadne Compass Increment 2 — Independent Gemini Review Packet

Reviewer: Gemini 3.5 Flash (High) through a fresh Antigravity project

Implementation head: `dacae0b865c99cf565831e3842f5f2b2bc481105`

Source head: `54c094c2fa9f0885268041ae4497ed9a1ba8ad78`

Decision format: `DECISION: pass` or `DECISION: revision_required`

## Role and authority

Act only as an independent veto reviewer. Do not implement fixes, alter the
candidate, accept your own review, integrate, push, move protected refs, create
agents, call another model/provider or inspect protected/historical evidence.

Write only
`orchestration/agent_inbox/antigravity/ariadne-compass-increment2-final-review.md`
and commit that one review artifact to the fresh reviewer branch.

## Mandatory orientation

Read completely:

1. `AGENTS.md`, including the Current Baton, authority allocation, protected
   evidence boundaries and user decision boundaries;
2. `docs/ariadne-compass-increment2-plan.md`;
3. `docs/ariadne-compass-current.md`;
4. `orchestration/continuity/emr4-compass.json`;
5. `orchestration/continuity/ariadne-compass.schema.json`;
6. `scripts/ariadne_compass.py`;
7. `tests/test_ariadne_compass.py`;
8. `orchestration/continuity/emr4-continuity-graph.json`; and
9. the exact diff `54c094c2..dacae0b8`.

The five authoritative rehydration sources remain:

- `live_handover_current_baton`;
- `current_authority_allocation`;
- `active_plan_and_acceptance`;
- `protected_evidence_boundaries`; and
- `git_refs_and_worktree`.

Record the exact reviewer worktree, branch, carrier HEAD, implementation head
and source head. Do not treat conversation context as authority.

## Veto questions

Return `revision_required` for any material defect in the following:

1. **Strategic accuracy:** Does the report truthfully place the active work in
   Phase 2B and distinguish the current Reception One subgraph from the entire
   EMR4 programme?
2. **Lineage integrity:** Does it preserve the real combined-scope fork rather
   than fabricate a linear history? Can a false parent pass validation?
3. **Current-position integrity:** Must the current product node be real,
   accepted, terminal in the journey and continuity-clean?
4. **Decision integrity:** Are product and programme-support horizons visibly
   candidate/deferred/blocked, never silently accepted or selected? Are
   Yuri-owned decisions explicit?
5. **Authority containment:** Is the runtime genuinely read-only, with no
   network, process, filesystem-write, agent, Git, provider or EMR actuator?
   Does the Compass avoid granting authority?
6. **Provenance/privacy:** Are evidence references repository-relative,
   existing and non-sensitive? Does the canonical map avoid identity, secrets,
   transcripts, prompts, protected evidence and historical Diary content?
7. **Staleness/fail-closed behaviour:** Do graph revision drift, fabricated
   lineage, unknown boundaries, missing evidence and sensitive fields fail
   closed?
8. **Human usefulness:** Does the Markdown report plainly answer where we are,
   why this work came next, what it proved, what it unlocks, what it does not
   solve and what Yuri must decide?
9. **Claim width:** Does any wording imply production, release, representative
   staff, complete EMR4 mapping, workflow-executive or product-command evidence
   that was not proved?

## Required verification

Use the shared integration Python environment; do not create or install a new
environment. Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest `
  tests\test_ariadne_compass.py `
  tests\test_ariadne_continuity_engine.py `
  tests\test_ariadne_orchestrator_preflight.py `
  tests\test_ariadne_operating_model.py `
  tests\test_agents_handover_archive.py -q

C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check `
  scripts\ariadne_compass.py tests\test_ariadne_compass.py

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_continuity.py validate

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_compass.py validate

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_continuity.py audit --node ariadne-compass-increment2

git diff --check 54c094c2..dacae0b8
```

Also compare the generated Markdown output with
`docs/ariadne-compass-current.md`. Do not run the unrelated all-adapter sweep;
its fresh-worktree Node PTY dependency limitation is recorded in
`orchestration/agent_inbox/codex/ariadne-compass-increment2-broad-regression-observation.md`.

## Review artifact

The review must contain:

- the exact heads and worktree coordinates;
- tests and validators actually run with exact results;
- findings ordered by materiality;
- an explicit statement that no protected/historical evidence was inspected;
- any residual limitation that is not a veto; and
- a final exact decision line.
