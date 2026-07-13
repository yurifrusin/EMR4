# S13 Dispatch Record

Status: prepared; worker not yet launched.

- Sol authorization: S13-S15 tranche approval recorded in the active task.
- Staging worktree: `C:\\Users\\sarashera\\EMR4-worktrees\\terra-validation-2`
  on `codex/terra-validation-2`, based on protected master `72b0999a`.
- Shared integration worktree remains `C:\\Users\\sarashera\\emr4` on
  `master`; it is not used for implementation.
- API Steward source pass completed against the ADR, programme, Bernie release
  gates, GraphQL/OpenAPI/manifest artifacts, API-Spine artifact tests, and the
  steward review checklist.
- Planned worker: exactly one `deepseek-flash-workers` instance at
  `deepseek-v4-flash` / `high`; no Conductor, verifier, Gemini, Claude, or
  additional worker is allocated for S13.
- Dispatch requires a fresh passed preflight receipt, a clean disposable worker
  worktree, shared Python/Node path injection, and a unique artifact owner
  lock. The accepted result is the canonical completion artifact and receipt,
  not terminal output.
