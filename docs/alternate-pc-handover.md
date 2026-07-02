# EMR4 Alternate PC Handover - 2026-07-02

This is the short operational handover for moving the next EMR4 sprint to the
alternate Windows PC. It assumes the alternate PC has already run EMR4 before
and only needs to catch up to the current Git baton and re-check local auth.

## Current Status

- Last code sprint commit before this handover documentation: `b896582`
  (`Sprint 103 Bernie compact request auto preview`).
- This handover commit will be newer. After pulling, treat `origin/master` and
  `origin/handoff/current` as the source of truth.
- Sprint 104 is not launched yet.
- Recommended next sprint: *bernie* conversational state memory and
  clarification-turn statechart, with Claude, Antigravity/Gemini, and a Codex
  worker brought in through the normal plan gate.

## What You Need To Save From This PC

Anything committed and pushed to Git does not need copying.

Before this PC is unavailable, only check for local-only material:

- `.env`
- ngrok auth/config if the alternate PC does not already have it
- Google Cloud CLI login/ADC will normally need re-auth on the alternate PC
- Pushover notification environment values, if you want sprint-close pings there
- GitHub CLI auth, if the alternate PC is not already logged in
- Office add-in sideloading settings, if the alternate PC has not already been set up
- any intentionally retained local generated documents under `patient_files/`

Do not copy `.venv`, `node_modules`, service-account JSON keys, real patient
data, generated clinical documents, or agent session state through Git.

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
worker mirrors are clean and aligned. The commit should be this handover commit
or newer, not the older `b896582` code-sprint commit.

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

Do not launch Sprint 104 yet until you have reported repo/auth status. Current intended next sprint is Sprint 104: Bernie conversational state memory and clarification-turn statechart. It should probably be plan-gated with Claude, Antigravity/Gemini, and a Codex worker.

The key design decisions to preserve are:
- continue agentic Diary/Taskpane state-machine/API-pattern sprints before the broad root-to-branch API review;
- model Bernie as an event-driven workflow with explicit state machine memory;
- prompt input should become a chat/clarification turn surface, not a stale single prompt;
- diary navigation, Today, Refresh, candidate selection, and confirmation are state transitions;
- patient recognition is separate from patient details verification;
- after patient recognition, fetch compact patient_booking_context rather than dumping broad diary context;
- no-slot states should say no times are available and offer useful clickable alternatives;
- limited Bernie auto-mode is a future architecture branch only, not Sprint 104 implementation.

After the audit, tell me whether the alternate PC needs Google ADC re-auth for Bernie or Scribe, whether the repo is clean, and whether you are ready to dispatch Sprint 104 as HANDIN READY.
```

