# LC4V8D1 Gemini Pre-Baseline Review Packet

## Workspace and source

- Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v8d1-gemini-prebaseline`
- Branch: `antigravity/lc4v8d1-prebaseline-review`
- Frozen authored evidence commit: `08c27c61`
- Review target: the exact contract, incident record, fixture bytes, and
  authorship test committed at `08c27c61`; later packet/receipt-only commits do
  not amend that evidence.

## Role and authority

You are Gemini 3.5 Flash in a fresh Antigravity project. Independently veto the
fresh ordinary-development authorship before any product baseline. You have no
implementation, remediation, acceptance, integration, baton, or push authority.
Do not execute Bernie parser/policy code.

## Exact readable files

- `AGENTS.md`
- `orchestration/agent_inbox/codex/lc4v8d1-sol-contract.md`
- `orchestration/agent_inbox/codex/lc4v8d1-preauthoring-protected-search-incident.md`
- `tests/fixtures/bernie_lc4v8d1_development/probes.json`
- `tests/test_bernie_lc4v8d1_authorship.py`
- this packet

Do not read, list, enumerate, search, import, execute, hash-check, or inspect any
protected V8 fixture, evaluator, implementation, authoring module, manifest,
seal, marker, test, report internals, or per-case surface. Do not use broad
repository discovery. Holdouts v1-v8 remain sealed.

## Review questions

1. Does the fixture contain exactly 24 fresh inspectable cases in four 6-case
   families, with independently understandable utterances and Gold?
2. Is the canonical policy projection exact, JSON-safe, lossless with respect
   to the typed ordinary policy result, and free of omitted/null or tuple/list
   ambiguity?
3. Do the separate semantic invariants distinguish genuine policy behavior
   from exact projection mismatch without allowing fail-open classification?
4. Are the Gold policy semantics and exact projection cross-field consistent,
   including clarification, refusal, no-action, mutation, diary conflict,
   identity, tools, deltas, and simulated-write state?
5. Are the time forms and relations independently adjudicable without relying
   on V8 cases or aggregate-slice inference?
6. Does the authorship test fail closed and avoid importing/executing product
   code?
7. Does the incident containment remain adequate, with no case-level V8
   information or D1 contamination?

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4v8d1_authorship.py tests/test_agents_handover_archive.py -q
git diff --check
```

## Owned artifact and decision

Create only
`orchestration/agent_inbox/antigravity/lc4v8d1-prebaseline-review.md`.
Record exact source/branch, test counts, fixture raw hash, review findings,
scope audit, and one final line:

- `DECISION: pass`; or
- `DECISION: revision_required` with concrete authored defects.

Commit the review artifact to your task branch. Do not push protected refs.
