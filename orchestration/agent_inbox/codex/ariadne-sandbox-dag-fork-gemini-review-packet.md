# Ariadne Sandbox DAG Fork — Independent Gemini Review Packet

Reviewer: Gemini 3.5 Flash (High) through a fresh Antigravity project

Implementation head: `a7eeaa58bcc2080b71e4db9d6fff9e147f3470c6`

Source head: `ec6d0145376f7c945b43b1fbf4338e4cb78e3000`

Decision format: `DECISION: pass` or `DECISION: revision_required`

## Role and authority

Act only as an independent veto reviewer. Do not implement fixes, alter the
candidate, accept your own review, integrate, push, move protected refs, create
agents, call another model/provider or inspect protected/historical evidence.

Write only
`orchestration/agent_inbox/antigravity/ariadne-sandbox-dag-fork-final-review.md`
and commit that one review artifact to the fresh reviewer branch.

## Mandatory orientation

Read completely:

1. `AGENTS.md`, including the Current Baton, authority allocation, protected
   evidence boundaries and user decision boundaries;
2. `docs/ariadne-sandbox-dag-fork-plan.md`;
3. `docs/ariadne-sandbox-dag-protocol-design.md`;
4. `scripts/ariadne_sandbox_dag.py`;
5. `orchestration/continuity/ariadne-sandbox-dag.schema.json`;
6. `orchestration/continuity/ariadne-sandbox-dag-example.json`;
7. `tests/test_ariadne_sandbox_dag.py`;
8. `orchestration/continuity/emr4-continuity-graph.json`;
9. `orchestration/continuity/emr4-compass.json`;
10. `orchestration/continuity/ariadne-sandbox-dag-fork-evidence.json`; and
11. the exact diff `ec6d0145..a7eeaa58`.

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

1. **DAG integrity:** Are all runtime messages forward edges? Does the context
   source request causally follow the leaf request, and does the continuation
   use a later immutable leaf attempt rather than a cycle or rewritten state?
2. **Synaptic isolation:** Can a direct sandbox message pass only when both the
   sender's outbound and recipient's inbound start-up policies name the exact
   peer instance, channel and frame? Is ambient or unilateral communication
   rejected?
3. **Restart integrity:** Is policy immutable within one container generation?
   Does amendment require a later generation, higher revision and exact restart
   lineage while preserving the earlier generation?
4. **Control boundary:** Is the orchestrator a control plane without becoming a
   compulsory data relay? Are direct peer links limited to data rather than
   context, command or authority control?
5. **Capability containment:** Is the catalogue strictly inert and analytical?
   Can a leaf invent or amplify a network, filesystem-write, process, provider,
   database, Git or EMR-command capability?
6. **Human authority:** Must a command-shaped candidate stop at exactly one
   terminal `awaiting-human-authority` gate? Can any confirmed, committed,
   dispatched or executed state pass?
7. **Provenance/privacy:** Are frames, properties, provenance, freshness and
   source messages checked? Is the example authored-synthetic and free of PII,
   prompts, transcripts, secrets, historical material and protected evidence?
8. **Runtime reality:** Does static and behavioural evidence support the claim
   that there is no model call, container operation, product read/write, API,
   database, subprocess or network actuator?
9. **Continuity isolation:** Is `ariadne-sandbox-dag-fork` a real
   `forked_from` branch that audits cleanly without moving the Reception One
   Compass journey/current position or reopening closed product boundaries?
10. **Claim width:** Does any prose or evidence imply a functioning container
    mesh, executor, EMR integration, provider, PII, production, deployment or
    release capability that was not proved?

## Required verification

Use the shared integration Python environment; do not create or install a new
environment. Run serially:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest `
  tests\test_ariadne_sandbox_dag.py `
  tests\test_ariadne_continuity_engine.py `
  tests\test_ariadne_compass.py `
  tests\test_ariadne_orchestrator_preflight.py `
  tests\test_ariadne_operating_model.py `
  tests\test_agents_handover_archive.py -q

C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check `
  scripts\ariadne_sandbox_dag.py tests\test_ariadne_sandbox_dag.py

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_sandbox_dag.py validate

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_continuity.py validate

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_continuity.py audit --node ariadne-sandbox-dag-fork

C:\Users\sarashera\emr4\.venv\Scripts\python.exe `
  scripts\ariadne_compass.py validate

git diff --check ec6d0145..a7eeaa58
```

Inspect the AST/imports and CLI surface rather than relying only on the stated
non-executing intent. Do not run repository-wide discovery or any product,
browser, PostgreSQL, provider, protected or historical test population.

## Review artifact

The review must contain:

- the exact heads and worktree coordinates;
- tests and validators actually run with exact results;
- findings ordered by materiality;
- an explicit statement that no protected/historical evidence was inspected;
- any residual limitation that is not a veto; and
- a final exact decision line.
