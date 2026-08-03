# Ariadne handover and verifier workflow optimization plan

Date: 2026-08-03

Status: authorised and frozen

## Objective

Reduce repeated context and verification cost without weakening authority,
provenance or independent review. This is a repository-local orchestration
control tranche. It does not change product behaviour or open any product,
provider, identity, deployment, production, release or protected-ref boundary.

## Accepted change surface

1. Move historical and inactive Current Baton acceptance lookup rows out of
   `AGENTS.md` into one dedicated ledger. Preserve each moved Markdown row
   exactly and bind the ledger with a checked SHA-256 manifest. Keep current
   authority, active product state, active acceptance, boundaries and next work
   in the live handover.
2. Make the generic orchestrator receipt emit `rehydrated_from_receipt`, the
   exact five `rehydration_sources`, and non-empty `source_evidence` directly.
   Every configured continuation event must fail closed when a source or its
   evidence is missing.
3. Add a versioned deterministic-first verification policy. An external model
   review is eligible only after the exact candidate, authority packet, focused
   tests, static checks, settings fingerprint and clean-worktree gates pass.
4. Encode the three-lane operating profile: Sol owns architecture, acceptance,
   recovery and integration at High for routine bounded decisions and Extra
   High for material decisions; DeepSeek V4 Flash/high owns bounded separable
   implementation/test artifacts; Gemini 3.6 Flash/high owns fresh independent
   review only.
5. Keep every pytest process loading the repository `conftest.py` serial.
   Parallel execution is limited to independent static or filesystem-only
   checks and isolated browser checks that do not share mutable runtime state.

## Deterministic acceptance

- The pre-compaction live handover is 170,970 bytes with SHA-256
  `f8bbfbafc9c2da981f0aef91628828c39783da97e78bfda02bd77bde43dcdd1e` at
  source HEAD `167618a9806cfb5431f0c55ddaa4dcef5b51e8b6`.
- The acceptance-index manifest records the source hash, source HEAD, exact
  moved labels, row count, ledger byte/line count and ledger SHA-256.
- Tests prove no moved row is lost, the ledger hash is exact, active live
  labels remain present and the live handover is materially smaller.
- Tests prove native five-source receipt emission for every configured event,
  rejection of missing source evidence and compatibility with explicitly
  prefixed primary-session evidence.
- YAML tests prove lane/model/reasoning ownership, deterministic-before-model
  ordering, exact single-decision admission and serial PostgreSQL execution.
- Focused pytest, Ruff, Python compilation, YAML parsing and `git diff --check`
  pass before any external reviewer is called.
- One fresh Antigravity project using exact model `gemini-3.6-flash-high`,
  explicit `high` effort, plan mode and an exact clean non-protected candidate
  worktree returns exactly one terminal decision without changing the candidate.

## Stop conditions

Stop on lost or altered Baton rows, an unverifiable ledger hash, absent source
evidence, deterministic-gate failure, model fallback, candidate mutation,
duplicate/missing verifier decision, protected-ref movement, branding-path
collision or any scope requiring product or deployment authority.

## Closeout

Only explicit task paths may be staged. `docs/branding/` must never appear in
the index, test scope, staged set or commit. Push only the non-protected task
branch. Protected integration remains a separate authority gate.
