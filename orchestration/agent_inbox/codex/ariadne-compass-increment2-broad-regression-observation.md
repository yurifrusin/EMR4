# Ariadne Compass Increment 2 — Broad Regression Observation

Date: 2026-07-21

Candidate worktree: `C:\Users\sarashera\EMR4-worktrees\ariadne-compass-increment2`

Source head: `54c094c2fa9f0885268041ae4497ed9a1ba8ad78`

## Canonical result

The frozen Compass, Continuity Engine, orchestrator-preflight, operating-model
and handover-archive population passes 43/43. The skill and plugin validators,
Compass/continuity validation, Compass node audit, Python compilation, Ruff and
Git whitespace checks also pass.

## Deliberately broader observation

An exploratory sweep over every `test_ariadne_*.py` file plus the handover
archive produced 236 passes and 14 failures. All 14 failures are confined to
the pre-existing Deep Code PTY/runtime-observability adapter population. In the
fresh task worktree, its Node helper exits with `ERR_MODULE_NOT_FOUND` before it
can write the expected receipt because that worktree has no installed Node PTY
dependency tree.

The exact first failing node,
`tests/test_ariadne_deepcode_pty.py::test_pty_adapter_accepts_worker_completion_artifact[completion]`,
passes unchanged in the integration/source checkout at the same source commit,
where the established Node dependency tree exists. No Compass file changes the
Deep Code adapter, its tests or Node dependencies.

This observation is not relabelled as a full-suite pass and does not broaden
the frozen acceptance population. It records an environment-only worktree
dependency limitation so it is not misattributed to the Compass candidate.
