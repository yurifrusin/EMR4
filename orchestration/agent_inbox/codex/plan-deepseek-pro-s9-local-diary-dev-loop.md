# DeepSeek Pro Conductor — S9 Local Diary Development Loop Plan

**Date:** 2026-07-13
**Conductor:** DeepSeek 4 Pro / high (routine Conductor role)
**Artifact:** `orchestration/agent_inbox/codex/plan-deepseek-pro-s9-local-diary-dev-loop.md`

---

## Direction Disposition

No Sol consultation required. The defect is deterministic and the fix is
mechanically bounded — this is not a direction-dispute sprint. Sol may issue one
rejoinder for a material executability concern.

Current complete-settings fingerprint:
`sha256:d755fec02ca84a0f1f6ab21782dda31219cb0ec65d0340fb9f806b32c6775679`
(unchanged from S8H — this sprint touches only dev-tool configuration, not
runtime settings).

---

## Rejoinder Disposition (Sol, 2026-07-13)

The first S9 plan was rejected for two material harness-contract errors. This
revision corrects both without changing the well-supported webpack static-hosting
direction:

1. **Authority corrected.** DeepSeek Pro is the Conductor only. It has final
   sprint-definition and allocation authority but no review acceptance,
   integration, `master`, push, or `handoff/current` authority. Sol owns
   candidate acceptance, integration, checkpoints, and closeout.
2. **Worker channel corrected.** DeepSeek workers use the current DeepCode
   real-PTY adapter in disposable packet worktrees, not the retired "direct
   Codex deepseek-worker spawning" path. The detached supervisor and injected
   shared Python/Node paths are mandatory.
3. **Cleanliness statement corrected.** Prior S8 sessions are complete and no
   S9 worker process is active; old worktrees may remain as archived evidence.
   The one-lane mechanical allocation is preserved.
4. **Independent acceptance assigned to Sol.** Sol's deterministic tests and
   diff review provide independent acceptance, not the Conductor.

---

## Defect / Evidence

### Symptom

When the full local dev stack is started via `run_dev.ps1` (which launches the
webpack dev-server on port 3000), clicking the Diary button in the taskpane
opens `https://localhost:3000/diary/diary.html` — but the webpack dev-server
returns 404 because it does not serve the `docs/diary/` directory.

### Root Cause

`EMR4 Sidebar/webpack.config.js` line 84–93 configures `devServer` with only
CORS headers and HTTPS setup. It has no `static` (or legacy `contentBase`)
configuration to serve the `docs/diary/` or `docs/images/` directories as static
content.

Meanwhile, `EMR4 Sidebar/src/taskpane/taskpane.js` lines 1023–1028
(`resolveDiaryUrl`) correctly resolves `location.origin + "/diary/diary.html"`
when on port 3000 — but the dev-server never serves that path.

The `docs/diary/diary.html` line 17 references
`<img src="../images/emr_cube1.png">`, which resolves to `/images/emr_cube1.png`
relative to the page URL `/diary/diary.html`. The dev-server also does not serve
`docs/images/`.

### Evidence Chain

1. `run_dev.ps1` line 61, 470–472: starts webpack dev-server via
   `npm run dev-server` on port 3000.
2. `webpack.config.js` lines 84–93: `devServer` block has `headers` and
   `server` only — no `static` directories.
3. `taskpane.js` lines 1023–1028: `resolveDiaryUrl` returns
   `location.origin + "/diary/diary.html"` for port 3000.
4. `diary.html` line 17: references `../images/emr_cube1.png`.
5. `review/test_taskpane_diary_launch.py` line 129: existing test asserts the
   URL resolver returns `http://localhost:3000/diary/diary.html`, but no test
   verifies the dev-server can actually serve that path.

### Impact

The local Diary development loop is broken. Developers who run `run_dev.ps1` and
click the Diary button see a 404 in the Diary dialog. The Command Centre
(`openCommandCentre`) is not affected because it always uses the deployed
GitHub Pages URL (taskpane.js line 1137).

---

## Bounded Implementation Surface

### In Scope

| File | Change | Rationale |
|---|---|---|
| `EMR4 Sidebar/webpack.config.js` | Add `devServer.static` array serving `../docs/diary/` at public path `/diary` and `../docs/images/` at public path `/images` | This makes the webpack dev-server serve the Diary HTML/JS/CSS and shared image assets, closing the gap between `resolveDiaryUrl` and the dev-server's actual served paths |
| `review/test_taskpane_diary_launch.py` | Add a test that verifies the dev-server (when running) serves `/diary/diary.html` with HTTP 200, or add a static configuration assertion that the `static` directories are present in the webpack config | Regression evidence that the Diary is reachable through the dev-server |

### Out of Scope (pinned closed)

- Provider / live-provider boundaries
- Database / schema migrations
- External patient-client surfaces
- H15 / H-series profiles
- Historical diary trove
- Memory / RAG / GraphRAG
- Bernie D5 / interpretation harness runtime wiring
- Terminal-to-active appointment-status policy (user-owned)
- New model-write gates
- Production deployment authority
- `docs/command-centre/` (uses deployed Pages URL — not affected)
- `sync_taskpane.py` (correctly patches the deployed `docs/taskpane/taskpane.js`;
  the source `EMR4 Sidebar/src/taskpane/taskpane.js` resolver is correct)
- `diary.js` backend URL logic (correctly resolves to `http://localhost:8001` on
  port 3000 — the backend port, not the frontend port)

---

## Worker Allocation

### Sprint Classification

This is a tiny, mechanical dev-tool configuration fix. Per protocol alerts
2026-07-07 and 2026-07-08: a single implementation lane with Conductor
sprint-definition authority is appropriate. Claude and Antigravity lanes would
add ceremony without producing distinct integrable artifact surfaces on a
one-file config change.

### Lane Assignments

| Lane | Role | Channel | Artifact Surface |
|---|---|---|---|
| **DeepSeek Flash** | Implementation owner | DeepCode real-PTY adapter in disposable packet worktree `deepcode-s9-worker`, with detached supervisor and injected shared Python/Node paths | Candidate branch `deepcode/s9-diary-dev-loop` with webpack.config.js change + test addition; submit via packet protocol |

### Authority Boundary (Corrected)

| Authority | Owner |
|---|---|
| Sprint definition and worker allocation | DeepSeek Pro Conductor (this plan) |
| Implementation | DeepSeek Flash worker (disposable packet worktree) |
| Candidate acceptance | Sol (deterministic tests + diff review) |
| Integration, merge to `master`, advance `handoff/current` | Sol |
| Checkpoints and closeout | Sol |

The Conductor does **not** review, accept, integrate, merge to `master`, push,
or advance `handoff/current`. This plan defines the sprint and allocates the
worker; Sol owns everything downstream of worker submission.

### Worker Cleanliness

Prior S8 sessions are complete and no S9 worker process is active. Old
worktrees may remain as archived evidence from S8. The worker will be launched
in a fresh disposable packet worktree `deepcode-s9-worker`.

Claude and Antigravity worktrees are not engaged for this sprint (tiny
mechanical scope).

### Injected Shared Tool Paths (Mandatory)

The worker's disposable packet worktree dispatch must include these exact paths:

```
Shared Python: C:\Users\sarashera\emr4\.venv\Scripts\python.exe
Shared Node:   C:\Program Files\nodejs\node.exe
```

The detached supervisor must inject these paths before the worker may claim
Python or Node are unavailable.

---

## Acceptance Evidence

### Worker Verification (Pre-Submit)

1. `node --check "EMR4 Sidebar/webpack.config.js"` — syntax check passes
2. Start the webpack dev-server: `cd "EMR4 Sidebar" && npm run dev-server`
3. Verify `curl -k https://localhost:3000/diary/diary.html` returns HTTP 200
   with diary HTML content
4. Verify `curl -k https://localhost:3000/images/emr_cube1.png` returns the
   image
5. Run `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_taskpane_diary_launch.py -q` — all existing URL-resolver tests pass
6. Run new static-config test (or manual verification above if test is structural)

### Sol Independent Acceptance (Post-Submit)

Sol's deterministic tests and diff review provide independent acceptance:

1. `git diff --stat` — only `EMR4 Sidebar/webpack.config.js` and
   `review/test_taskpane_diary_launch.py` changed
2. `git diff --check` — no whitespace violations
3. `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review/test_taskpane_diary_launch.py -q` — all tests pass
4. Sol owns final integration, merge to `master`, advance of `handoff/current`,
   mirror realignment, and closeout.

### End-to-End (Post-Integration, Optional Deferred)

Full `run_dev.ps1` with ngrok tunnel and Word Online / desktop sideloading —
this is the definitive end-to-end test but requires Word UI. It may be deferred
to S10 (end-to-end receptionist workflow) as part of the broader workflow
verification.

---

## Review Posture

- The Conductor defines the sprint and allocates the worker. The Conductor does
  not review or integrate the worker's output.
- Sol provides independent acceptance through deterministic tests and diff
  review.
- No independent adversarial review lane (one-file mechanical config change).
- The existing `review/test_taskpane_diary_launch.py` test suite provides
  structural coverage of the Diary URL resolver.
- If the worker finds the webpack-dev-server version does not support the
  `static` array config (v4+), fall back to a simpler single-directory approach.

---

## Commit / Push Checkpoints

1. **Conductor** publishes this plan artifact (this turn only — no product code
   or test edits).
2. **Conductor** dispatches the worker packet to DeepCode's inbox for the
   disposable packet worktree `deepcode-s9-worker`, with injected shared
   Python/Node paths.
3. **Worker** creates branch `deepcode/s9-diary-dev-loop` from `handoff/current`
   in the disposable packet worktree.
4. **Worker** implements webpack.config.js change + test, runs verification,
   commits, and submits via packet protocol.
5. **Sol** reviews diff, runs deterministic tests, integrates to `master`,
   advances `handoff/current`, realigns clean mirrors, and closes out the
   sprint.

---

## Closed Gates (No Change)

| Gate | Status |
|---|---|
| Provider / live-provider | Closed |
| Database / schema migration | Closed |
| External patient client | Closed |
| H15 / H-series profiles | Closed |
| Historical diary trove | Closed |
| Memory / RAG / GraphRAG | Closed |
| Bernie D5 / interpretation harness runtime | Closed |
| Terminal-to-active status policy | Closed (user-owned) |
| New model-write gates | Closed |
| Production deployment authority | Closed |
| Monetary or wall-clock caps | None active — unrestricted |

---

## Sprint Engine State

`sprint engine continuing` — Conductor publishes this corrected plan artifact,
then Sol proceeds through worker dispatch, acceptance, integration, and
closeout.

STATUS: complete
