# S16-S18 Compact-Ledger Pilot Closeout

Decision: accepted for exact protected integration.

## EMR4 Result

Registered-envelope validation now rejects unsupported, misspelled, case-
changed, or whitespace-changed envelope types before action resolution. Tests
cover every current direct capability and every registered grammar alias across
all four envelope types, including declared/undeclared authors and staff-only
confirmation aliases. Unknown actions and planned unregistered verbs preserve
their valid-envelope pass-through behavior.

Final acceptance collected 485 tests: 469 passed and 16 skipped because two
capabilities declare every available author. Compilation and diff checks passed.
No route, provider, database, UI, deployment, or write authority changed.

## Process Result

- DeepSeek V4 Pro/high implemented and tested the candidate through Claude Code
  bare mode. Reported API cost: US$2.906; 79,602 input, 24,466 output, and
  3,774,208 cached-read tokens. Its commit followed about 11.6 minutes after
  process start.
- Sol found two acceptance gaps: case normalization contradicted the contract,
  and the alias matrix was not drift-sensitive. One correction commit fixed
  both before independent review.
- Gemini 3.5 Flash/high found a real test defect: unauthorized-author tests
  parameterized four envelope types but ignored that parameter. Its correction
  made the proof genuinely cross-envelope.
- The first Antigravity attempt reused its historical project/worktree despite
  the supplied shell cwd. It was stopped after live evidence exposed the wrong
  target; one generated `uv.lock` was removed. `--new-project` plus an explicit
  `--add-dir` bound the successful retry to the correct staging worktree.
- The first DeepSeek observer command timed out, but the worker process survived
  and continued. No duplicate lane was launched; the local receipt completed.
- DeepSeek Flash and Terra were not used because no distinct implementation
  surface or fallback trigger remained.

## Economy

Routine committed evidence is limited to the 42-line tranche contract, this
closeout, and one compact JSON manifest. Worker packets and receipts stayed
ignored under `local_data/`. Product/test change is 417 added and 13 removed
lines. The compact process eliminated the repeated sprint plans, dispatch
records, worker completion markdown, per-sprint reviews, and per-sprint
manifests used in S13-S15.

The process was substantially less document-heavy, but not yet operationally
smooth: Sol correction remained necessary, and Antigravity requires explicit
new-project binding. DeepSeek Pro was effective but costlier than expected for
this small tranche, so future packets should reduce broad reads and test-output
verbosity while preserving bare mode.
