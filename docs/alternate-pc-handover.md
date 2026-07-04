# EMR4 Alternate PC Handover - 2026-07-04

This is the short operational handover for moving the next EMR4 sprint to the
alternate Windows PC. It assumes the alternate PC has already run EMR4 before
and only needs to catch up to the current Git baton and re-check local auth.

## Current Status

- Last completed sprint before this handover refresh: Sprint D2 at `cc11b2c`
  (shared confirm evidence helper plus DeepSeek Flash worker experiment).
- After pulling, treat `origin/master` and `origin/handoff/current` as the
  source of truth. They should be at `cc11b2c` or newer.
- DeepSeek Flash via `codex-deepseek-bridge` is now the preferred low-cost
  replacement for the spawned Codex worker on bounded implementation/review
  lanes, while Ariadne remains OpenAI/Codex orchestrator.
- Recommended next work: choose between constraining/retiring raw compatibility
  write endpoints, continuing the bounded Diary domain module tail, or the next
  Bernie native-diary capability sprint.

## What You Need To Save From This PC

Anything committed and pushed to Git does not need copying.

Before this PC is unavailable, only check for local-only material:

- `.env`
- ngrok auth/config if the alternate PC does not already have it
- Google Cloud CLI login/ADC will normally need re-auth on the alternate PC
- Pushover notification environment values, if you want sprint-close pings there
- DeepSeek API key / Codex DeepSeek Bridge setup if you want low-cost Codex
  worker subagents on the alternate PC
- GitHub CLI auth, if the alternate PC is not already logged in
- Office add-in sideloading settings, if the alternate PC has not already been set up
- any intentionally retained local generated documents under `patient_files/`

Do not copy `.venv`, `node_modules`, service-account JSON keys, real patient
data, generated clinical documents, or agent session state through Git.

## Optional: DeepSeek Worker Subagents With Codex Tools

On 2026-07-04 we proved that DeepSeek Flash can run as a real Codex subagent
worker through `codex-deepseek-bridge`. This is useful for low-cost sprint
implementation/review lanes while Ariadne remains the OpenAI/Codex orchestrator
and final integrator.

The important discovery: a generic LiteLLM bridge can expose `/v1/responses`,
but it does not translate Codex `namespace` tool schemas correctly for
DeepSeek. `codex-deepseek-bridge` is the working method because it translates
Codex namespace tools to DeepSeek-compatible function tools and maps tool calls
back into Codex's expected response shape.

### DeepSeek Setup Steps

Run these in PowerShell on the alternate PC after installing/reopening Codex:

```powershell
# 1. Store a rotated DeepSeek key for future Codex/bridge processes.
setx DEEPSEEK_API_KEY "<your_deepseek_key>"

# 2. Restart Codex so the new environment variable is visible.

# 3. Back up Codex config before bridge setup.
$backupDir = "$env:USERPROFILE\.codex\backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item "$env:USERPROFILE\.codex\config.toml" `
  (Join-Path $backupDir "config-before-deepseek-bridge-$stamp.toml") -Force

# 4. Install the bridge locally under Codex home, not into the EMR4 repo.
$prefix = "$env:USERPROFILE\.codex\tools\codex-deepseek-bridge-npm"
New-Item -ItemType Directory -Force -Path $prefix | Out-Null
npm install --prefix $prefix github:JetXu-LLM/codex-deepseek-bridge

# 5. Configure bridge safely: no desktop patch, no Codex app install,
#    no update check, and no raw payload logs.
$env:DSCB_UPDATE_CHECK = "off"
$env:DSCB_LOG_DIR = "off"
$env:DSCB_DESKTOP_PATCH = "off"
& "$prefix\node_modules\.bin\codex-deepseek-bridge.cmd" setup `
  --no-desktop-patch --no-codex-app-install --no-upgrade-check `
  --no-log-payloads --yes
```

After setup, inspect `%USERPROFILE%\.codex\config.toml`. The bridge may add a
top-level default model block like this:

```toml
model = "deepseek-pro"
model_provider = "deepseek_bridge"
model_reasoning_effort = "xhigh"
```

For EMR4, remove those top-level defaults so Ariadne remains the normal Codex
orchestrator. Keep only the bridge provider/catalog entries, for example:

```toml
model_catalog_json = "C:\\Users\\<user>\\.codex\\codex-deepseek-bridge\\models.json"

[model_providers.deepseek_bridge]
name = "DeepSeek (via Codex DeepSeek Bridge)"
base_url = "http://127.0.0.1:8787/v1"
wire_api = "responses"
supports_websockets = false
requires_openai_auth = false
```

Create or update `%USERPROFILE%\.codex\agents\deepseek-worker.toml`:

```toml
name = "deepseek-worker"
description = "Cost-conscious EMR4 sprint worker for read-heavy planning, review, and bounded implementation."
model_provider = "deepseek_bridge"
model = "deepseek-flash"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"

developer_instructions = """
You are a worker on EMR4, not the orchestrator.
Follow AGENTS.md and the current task packet exactly.
Do not move master, handoff/current, or durable mirror branches.
Do not implement production code during a plan gate.
Prefer read-heavy review, focused plans, and concise findings.
Submit tangible repo artifacts when asked.
"""
nickname_candidates = ["DeepSeek Worker", "Shen", "Delta"]
```

Restart Codex again after editing the agent/provider config. Then run a dry run
from Ariadne:

```text
Ariadne, dry-run the DeepSeek worker.

Spawn the `deepseek-worker` subagent for a read-only EMR4 protocol and
capability check. Do not ask it to implement or edit anything.
```

Expected result: the worker can read repo files, run shell commands, see the
expected tools/skills, and report the current EMR4 baton state. If the worker
errors with `tools[n].type: unknown variant namespace`, Codex is not going
through `codex-deepseek-bridge`; check the `deepseek_bridge` provider and
`deepseek-worker.toml` model provider. If it reports an invalid key, restart the
bridge/Codex after rotating `DEEPSEEK_API_KEY`.

### DeepSeek Operating Policy

- Keep Ariadne on the normal OpenAI/Codex model for orchestration,
  integration, branch movement, closeout, and high-risk judgement.
- Claude is allowed to do real implementation work as well as planning when
  quota is healthy. Prefer ordinary Claude sprint models for implementation and
  reserve Fable/high-cost modes for architecture consulting, plan arbitration,
  or unusually hard reviews.
- Antigravity/Gemini is not just a UX lane. When Gemini quota is healthy, use it
  for independent backend/domain-policy critique, test design, fixture/harness
  work, architecture dissent, and small bounded implementation lanes. Because
  Antigravity CLI stdout can be blank, every prompt must demand a tangible repo
  artifact and Ariadne must verify via git/file inspection.
- Use DeepSeek Flash first for bounded backend-internal worker lanes and
  read-heavy reviews. On this PC, Sprint D2 cost roughly US$0.08 in DeepSeek
  tokens after setup, and D3 proved Flash could implement a real backend sprint
  branch with Ariadne review/polish.
- Try DeepSeek Pro only when the work seems reasoning-depth limited rather than
  diff-hygiene limited; Pro is roughly 3x Flash cost.
- DeepSeek workers must use dedicated branches and tight file boundaries.
  Prompts should explicitly forbid deleting existing tests unless requested,
  require UTF-8 without BOM, top-level imports, no `.tmp`/`.bak` leftovers,
  `git diff --stat`, `git status --short --branch`, and exact tests/results
  before handback.
- Two DeepSeek workers may run at once if, and only if, they have disjoint
  branches, disjoint file ownership, independent verification, and an explicit
  Ariadne integration order. Do not run parallel DeepSeek agents against the
  same files or the same behavioural contract.
- Native OpenAI/Codex subagents remain available. When OpenAI usage credit is
  healthy, Ariadne may combine Claude, Antigravity, DeepSeek, and native Codex
  subagents in the same sprint, or split truly independent work into parallel
  sprints, as long as the ownership and merge gates are explicit.
- Ariadne must still review every worker diff, run verification, and integrate.

## Ariadne-v2 DeepSeek Pro Experiment

The low-cost worker setup above is distinct from running the main Codex composer as DeepSeek Pro. Controlled model-picker switching is documented in [Codex Model Switching and DeepSeek Ariadne Experiment](codex-model-switching-deepseek.md).

Current safety point before the Ariadne-v2 experiment:

- Branch: `safety/ariadne-v1-before-deepseek`
- Tag: `safety/ariadne-v1-before-deepseek-20260704-182049`
- Commit: `9d74c849e35cdd3e17984392ee8030622391f2a2`

On the alternate PC, do not assume the model switch scripts exist. Recreate or securely copy the local scripts under `%USERPROFILE%\.codex\tools\model-switch\`, then fully exit/restart Codex and start a fresh conversation after each switch. Existing prompt windows may stay pinned to the old model/catalog. Do not commit DeepSeek keys, bridge key files, Codex auth, or bridge logs.
## Pull The Current Baton On The Alternate PC

Run in PowerShell:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4

git fetch origin
git switch master
git pull --ff-only origin master

git branch -f handoff/current origin/handoff/current
git branch -f codex/current origin/codex/current
git branch -f claude/current origin/claude/current
git branch -f antigravity/current origin/antigravity/current

git status --short --branch
git log --oneline -5 --decorate
python scripts\agent_worktrees.py setup
python scripts\agent_worktrees.py audit --fetch
```

Expected result: `master`, `origin/master`, `handoff/current`, and the durable
worker mirrors are clean and aligned. The commit should be `cc11b2c` or newer, not the older `b896582` code-sprint commit.

## Re-Auth Google / Gemini If Needed

Google ADC is local to the Windows user profile, so expect to re-auth if live
Gemini/Vertex calls fail or if `gcloud auth list` does not show the right
account.

Check:

```powershell
gcloud auth list
gcloud config list account project
gcloud auth application-default print-access-token
```

For live *bernie* Diary testing:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4
gcloud auth login yuri@littlestardigital.com
.\scripts\use_bernie_adc.ps1
.\run_dev.ps1 -LiveAiSurface Diary
```

For live Scribe/Copilot taskpane testing:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4
gcloud auth login yuri@littlestardigital.com
.\scripts\use_scribe_adc.ps1
.\run_dev.ps1 -LiveAiSurface Taskpane
```

If ADC is already impersonating the matching service account, use the faster
variants:

```powershell
.\run_dev.ps1 -LiveAiSurface Diary -SkipAdcLogin
.\run_dev.ps1 -LiveAiSurface Taskpane -SkipAdcLogin
```

Only one local ADC profile is active at a time. Switch to Diary for Bernie work
and Taskpane for Scribe/Copilot work.

## Quick Local Checks

After pulling and before starting the next sprint:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4

node --check docs\diary\diary.js
python scripts\check_frontend_versions.py
.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "sprint103"
python scripts\agent_worktrees.py audit --fetch
```

If `.venv` is missing on the alternate PC, recreate it rather than copying it:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Prompt For The New Codex Chat

Paste this into the new Codex chat on the alternate PC:

```text
Ariadne, resume EMR4 from C:\Users\YuriFrusin\Documents\EMR4 on the alternate PC.

First read AGENTS.md, orchestration/sprint_closeout.md, orchestration/bernie_interaction_model.md, orchestration/event_driven_statechart_architecture.md, orchestration/parallel_workstreams.md, and docs/alternate-pc-handover.md.

Audit before doing any implementation:

git status --short --branch
git log --oneline -5 --decorate
python scripts\agent_worktrees.py audit --fetch

Do not launch implementation until you have reported repo/auth status. Current intended next work should be chosen from the latest sprint closeout: constrain/retire raw compatibility write endpoints, continue the bounded Diary domain module tail, or pick the next Bernie native-diary capability sprint. Use DeepSeek Flash via `codex-deepseek-bridge` in place of the spawned Codex worker where appropriate, while Ariadne remains orchestrator/integrator.

The key design decisions to preserve are:
- continue agentic Diary/Taskpane state-machine/API-pattern sprints before the broad root-to-branch API review;
- model Bernie as an event-driven workflow with explicit state machine memory;
- prompt input should become a chat/clarification turn surface, not a stale single prompt;
- diary navigation, Today, Refresh, candidate selection, and confirmation are state transitions;
- patient recognition is separate from patient details verification;
- after patient recognition, fetch compact patient_booking_context rather than dumping broad diary context;
- no-slot states should say no times are available and offer useful clickable alternatives;
- limited Bernie auto-mode is a future architecture branch only, not Sprint 104 implementation.

After the audit, tell me whether the alternate PC needs Google ADC re-auth for Bernie or Scribe, whether the repo is clean, whether DeepSeek worker setup is available, and whether you are ready to dispatch the next sprint as HANDIN READY.
```

