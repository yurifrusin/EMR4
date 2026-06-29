# Dummy's Guide to the EMR4 Development Environment

This guide explains how to set up EMR4 on a new Windows PC and how to get it
running again after a restart.

EMR4 development currently uses:

- GitHub for source control and agent handoff state
- Python virtual environment for the FastAPI backend
- Docker Desktop for PostgreSQL + pgvector
- ngrok for the public HTTPS tunnel used by Word Online / GitHub Pages
- Node/npm for the local taskpane dev server
- Google Cloud credentials for AI features

Do not commit `.env`, `gcp-key.json`, ngrok tokens, or real patient data.

---

## 1. Websites You May Need

| Purpose | Website |
|---|---|
| Git | <https://git-scm.com/download/win> |
| Python | <https://www.python.org/downloads/windows/> |
| Docker Desktop | <https://www.docker.com/products/docker-desktop/> |
| Node.js / npm | <https://nodejs.org/en/download> |
| ngrok download | <https://ngrok.com/download> |
| ngrok authtoken | <https://dashboard.ngrok.com/get-started/your-authtoken> |
| ngrok domains | <https://dashboard.ngrok.com/domains> |
| GitHub repo | <https://github.com/yurifrusin/EMR4> |

The ngrok login account currently used for this project is:

```text
sara.frushera@hotmail.com
```

The reserved ngrok domain expected by the project scripts is:

```text
property-cinch-backfield.ngrok-free.dev
```

---

## 2. Install Required Programs

Install these on the new PC:

1. Git for Windows
2. Python 3.13 or 3.14
3. Docker Desktop for Windows
4. Node.js LTS
5. ngrok

When installing Python, tick:

```text
Add python.exe to PATH
```

After installing, open a new PowerShell window and check:

```powershell
git --version
python --version
pip --version
docker --version
node --version
npm --version
ngrok version
```

Docker Desktop must be running before EMR4 starts.

---

## 3. Clone The Repository

Choose a folder, usually `Documents`:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents
git clone https://github.com/yurifrusin/EMR4.git
cd EMR4
```

Confirm you are on `master` and up to date:

```powershell
git status
git pull --ff-only origin master
```

---

## 4. Create The Python Virtual Environment

From the EMR4 folder:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try again:

```powershell
.venv\Scripts\Activate.ps1
```

When activated, the prompt should start with:

```text
(.venv)
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Quick check:

```powershell
python -c "import fastapi, sqlalchemy, alembic, pgvector; print('Python env OK')"
```

---

## 5. Create The `.env` File

Copy the example:

```powershell
Copy-Item .env.example .env
notepad .env
```

For normal local development, these are the important values:

```env
ENVIRONMENT=dev

DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev

SECRET_KEY=change-me-to-a-long-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

GCP_PROJECT=emr4-bernie-dev
GCP_LOCATION=australia-southeast1

DATA_STORE_ID=mbs-search-app_1780903132373
DATA_STORE_LOCATION=global

CLICKSEND_USERNAME=
CLICKSEND_API_KEY=

PATIENT_FILES_DIR=./patient_files
```

For development, `DATABASE_URL` should normally stay:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev
```

That matches the Docker Postgres container in `docker-compose.yml`.

---

## 6. Google Cloud Credentials

EMR4 AI development should use keyless Google Cloud authentication, not a local
service-account JSON key.

The current posture is:

- Cloud Identity organization: `littlestardigital.com`
- dev projects: `emr4-copilot-dev` and `emr4-bernie-dev`
- local dev account: `yuri@littlestardigital.com`
- local auth: Application Default Credentials plus service-account
  impersonation
- quota project: explicitly set with `gcloud auth application-default
  set-quota-project`

Do not set `GOOGLE_APPLICATION_CREDENTIALS` for normal local AI development.
Use the keyless runbook instead:

```text
docs/gcp-keyless-ai-setup.md
```

If keyless auth is not configured, the app can still run for diary, patient, and
database development, but live AI endpoints such as scribe/analyse may fail.

---

## 7. Configure ngrok

Install ngrok, then retrieve the authtoken from:

```text
https://dashboard.ngrok.com/get-started/your-authtoken
```

Log in using the project ngrok account:

```text
sara.frushera@hotmail.com
```

Then run:

```powershell
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN_HERE
ngrok config check
```

You do not normally start ngrok yourself. `run_dev.ps1` starts it.

The project expects this domain:

```text
property-cinch-backfield.ngrok-free.dev
```

If ngrok starts with a random URL instead, Word Online / GitHub Pages will point
at the wrong backend and the dev stack will not behave correctly.

---

## 8. Start The Dev Stack For The First Time

Make sure Docker Desktop is open and running.

From the EMR4 folder:

```powershell
.\run_dev.ps1
```

This script starts:

- Docker Postgres container: `gp-pms-postgres`
- FastAPI backend on `http://127.0.0.1:8001`
- ngrok tunnel on `https://property-cinch-backfield.ngrok-free.dev`
- npm dev server on `http://localhost:3000`

If the script says Docker is not responding, open Docker Desktop and wait for it
to finish starting, then run:

```powershell
.\run_dev.ps1
```

If the script says ngrok is not found, install ngrok or add it to PATH.

### Using Two PCs With One ngrok Domain

The reserved ngrok URL is public, so either PC can access it:

```text
https://property-cinch-backfield.ngrok-free.dev
```

However, the URL can point to only one running backend at a time. If PC A is
running ngrok, then Word Online / GitHub Pages on PC B will still talk to PC A's
backend through that URL.

`run_dev.ps1` checks this before starting ngrok. If the reserved domain is
already online from another PC, the script skips starting local ngrok and prints
a warning. This is fine when the second PC is only doing coding, tests, or agent
work. To make the second PC the active Word/diary test backend, stop ngrok on
the first PC, then rerun:

```powershell
.\run_dev.ps1
```

You can also deliberately skip ngrok on the second PC:

```powershell
.\run_dev.ps1 -NoNgrok
```

---

## 9. Run Migrations And Seed Data

Open a second PowerShell window:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m alembic upgrade head
python seed.py
```

This creates/updates database tables and adds the dev clinic data.

Dev login:

```text
dr.shera@emr4dev.local
Password1!
```

---

## 10. Daily Restart Routine

After rebooting the PC:

1. Open Docker Desktop and wait until it is running.
2. Open PowerShell.
3. Run:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4
git pull --ff-only origin master
.\run_dev.ps1
```

If migrations may have changed:

```powershell
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m alembic upgrade head
python seed.py
```

Usually `seed.py` is safe to rerun; it is intended to be mostly idempotent for
dev data.

---

## 11. Restart Only The Backend

If the diary/taskpane is already open and you only need the FastAPI backend to
pick up Python changes, stop the current backend terminal with:

```text
Ctrl+C
```

Then restart it from the EMR4 folder:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```

If you started everything through `run_dev.ps1` and want the launcher to stop
and restart the whole dev stack, use:

```powershell
.\run_dev.ps1 -Down
.\run_dev.ps1
```

Use the full launcher restart when ngrok, the npm dev server, or the terminal
windows themselves are confused. Use the direct `uvicorn` restart when only
backend Python code has changed.

---

## 12. Stopping The Dev Stack

To stop uvicorn, ngrok, and the npm dev server:

```powershell
.\run_dev.ps1 -Down
```

This intentionally leaves the Docker Postgres container running.

To stop Postgres too:

```powershell
docker stop gp-pms-postgres
```

To start only Postgres later:

```powershell
docker start gp-pms-postgres
```

---

## 13. Agent Worktrees On A New PC

After cloning the repo and setting up the environment, create the agent worktrees:

```powershell
python scripts\agent_worktrees.py setup
```

Then sync:

```powershell
python scripts\agent_worktrees.py sync --fetch
```

Agent worktrees will live under:

```text
C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4-worktrees\
```

Typical paths:

```text
...\EMR4-worktrees\claude
...\EMR4-worktrees\antigravity
...\EMR4-worktrees\codex
```

Before starting an agent session in a worker worktree:

```powershell
python scripts\agent_worktrees.py handin
```

Only one computer should actively work on a given durable branch at once. For
example, do not run Claude on `claude/current` on both PCs at the same time.

It is OK to split a sprint across computers if each worker has its own branch.

---

## 14. Check The Live Taskpane Version

When taskpane changes are pushed, the HTML should advertise the newest
cache-buster version, for example:

```text
taskpane.js?v=53
```

In the Chrome DevTools Console for the Word taskpane frame, run:

```javascript
[...document.scripts].map(s => s.src).filter(src => src.includes("taskpane.js"))
```

For CSS:

```javascript
[...document.styleSheets].map(s => s.href).filter(href => href && href.includes("taskpane.css"))
```

If either command returns an empty array, DevTools is probably inspecting the
Word document page rather than the taskpane iframe. Use the Console frame
dropdown near the top-left and choose the taskpane frame, then run the command
again.

To check what GitHub Pages is serving directly, run this in the console:

```javascript
fetch("https://yurifrusin.github.io/EMR4/taskpane/taskpane.html?probe=" + Date.now(), { cache: "no-store" })
  .then(r => r.text())
  .then(t => console.log(t.match(/taskpane\.js\?v=\d+/)?.[0]))
```

The result should match the version in `docs/taskpane/taskpane.html` on
`master`. If GitHub Pages reports an older version, check GitHub Actions /
Pages deployments. Pages should deploy only the canonical `master` branch; stale
worker branches such as `claude/current`, `antigravity/current`, or
`codex/current` can overwrite the live Pages artifact if manually deployed.

### GitHub Pages Auto-Deploy

The repository includes `.github/workflows/pages.yml`, which deploys the `docs/`
folder whenever `master` changes deployed static files. To use it reliably:

1. Open GitHub: `https://github.com/yurifrusin/EMR4/settings/pages`.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. After Codex pushes `master`, open
   `https://github.com/yurifrusin/EMR4/actions/workflows/pages.yml`.
4. Confirm the newest **Deploy GitHub Pages** run completed successfully.

If the live taskpane or diary still serves an old `?v=N`, use the workflow page's
**Run workflow** button on `master`. Avoid changing the Pages source branch to a
worker mirror; that was the cause of stale deployments after parallel-agent work.

---

## 15. Check The Live Diary Version

When diary changes are pushed, the HTML should advertise the newest cache-buster
version, for example:

```text
diary.js?v=66
```

In the Chrome DevTools Console for the open diary window, run:

```javascript
[...document.scripts].map(s => s.src).filter(src => src.includes("diary.js"))
```

For CSS:

```javascript
[...document.styleSheets].map(s => s.href).filter(href => href && href.includes("diary.css"))
```

To check what GitHub Pages is serving directly, run this in the console:

```javascript
fetch("https://yurifrusin.github.io/EMR4/diary/diary.html?probe=" + Date.now(), { cache: "no-store" })
  .then(r => r.text())
  .then(t => console.log(t.match(/diary\.js\?v=\d+/)?.[0]))
```

The result should match the version in `docs/diary/diary.html` on `master`.
If the diary window shows a different version from the direct GitHub Pages
probe, hard refresh the diary window. If GitHub Pages itself reports an older
version, check the Pages deployment branch in GitHub Actions.

### Open Diary Smoke Mode

Smoke mode is an auth-free visual fixture for quick diary layout checks. It uses
mock appointments, mock patients, and mock locations, so it is useful for UI
review but does not prove live backend/auth behaviour.

Deployed smoke URL:

```text
https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true
```

Local file path if you are opening the static file directly:

```text
docs/diary/diary.html?smoke=true
```

---

## 16. Query The API And Database Safely

Use this section when you want to inspect dev data, check whether a record exists,
or confirm what the backend is returning. Prefer the API first because it uses the
same practice scoping and permissions as the real app. Use direct database queries
when you need to diagnose seeded/dev data.

### API Login

Start from the EMR4 folder with the backend running:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4

$base = "http://localhost:8001/api/v1"
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "$base/auth/login" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=dr.shera%40emr4dev.local&password=Password1!"

$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }
```

If `$token` is empty, the login failed. Do not continue until login works.

### Search Patients Through The API

```powershell
Invoke-RestMethod `
  -Uri "$base/patients/search?q=billy" `
  -Headers $headers |
  Select-Object id,first_name,last_name,date_of_birth,medicare_number,medicare_irn
```

Try a fuller query if needed:

```powershell
Invoke-RestMethod `
  -Uri "$base/patients/search?q=Billy%20Frusin" `
  -Headers $headers |
  Select-Object id,first_name,last_name,date_of_birth,medicare_number,medicare_irn
```

### Find Likely Duplicate Patients In The Dev Database

Use the read-only helper first. It lists likely duplicate patient groups and shows
how many linked records each patient has, so you do not need to write ad hoc SQL
before deciding what to inspect next.

```powershell
python scripts\audit_patient_duplicates.py
```

To limit the check to one practice:

```powershell
python scripts\audit_patient_duplicates.py --practice-id PRACTICE_ID_HERE
```

To inspect the full reference-count table for every duplicate patient:

```powershell
python scripts\audit_patient_duplicates.py --show-zero
```

The helper is evidence-only. It does not delete, merge, relink, or update any
records. If the database is unavailable or misconfigured, it should fail with a
plain error and confirm that no records were changed.

### Before Deleting A Duplicate

Do not delete duplicate patient rows manually. A duplicate may already be linked
to appointments, encounters, documents, billing, reminders, messages, kiosk
check-ins, or generated patient files.

Safer short-term workflow:

1. Run `python scripts\audit_patient_duplicates.py`.
2. Decide which record appears to be the keeper based on identifiers, document
   URL presence, creation dates, and linked reference counts.
3. Ask Codex to design or review the exact merge/delete plan, or wait until EMR4
   has a proper admin merge-patient workflow.

Manual `psql` reads are a fallback only:

```powershell
docker exec -it gp-pms-postgres psql -U postgres -d gp_pms_dev
```

Do not run `DELETE`, `UPDATE`, or manual foreign-key rewrites in the dev database
unless the exact record-level merge plan has been reviewed.

Longer term, EMR4 should have a receptionist/admin duplicate-resolution workflow
that merges references, preserves audit history, and never silently destroys a
clinical record.

---

## 17. Common Problems

### PowerShell Will Not Activate `.venv`

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then:

```powershell
.venv\Scripts\Activate.ps1
```

### Docker Is Not Responding

Open Docker Desktop and wait until it says the engine is running.

Then:

```powershell
docker ps
.\run_dev.ps1
```

### ngrok Uses The Wrong URL

Stop the stack:

```powershell
.\run_dev.ps1 -Down
```

Check the authtoken:

```powershell
ngrok config check
```

Confirm the account owns:

```text
property-cinch-backfield.ngrok-free.dev
```

Then restart:

```powershell
.\run_dev.ps1
```

### Backend Starts But Database Fails

Check Postgres:

```powershell
docker ps
docker logs gp-pms-postgres --tail 50
```

Then rerun migrations:

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
```

### AI Features Fail

Check keyless Google Cloud auth first:

```powershell
gcloud auth list
gcloud config list account project auth/impersonate_service_account
gcloud auth application-default print-access-token
```

Confirm `.env` uses the intended project and location:

```env
GCP_PROJECT=emr4-bernie-dev
GCP_LOCATION=australia-southeast1
```

Then follow `docs/gcp-keyless-ai-setup.md` if ADC, impersonation, or quota
project setup is missing.

Restart backend:

```powershell
.\run_dev.ps1 -Down
.\run_dev.ps1
```

---

## 18. Starting A Fresh Agent Chat

Use these prompts when starting a new chat/thread so the agent rehydrates the
project state from the repository rather than from memory.

### Codex Skills

Codex has local EMR4 skills installed under `C:\Users\YuriFrusin\.codex\skills`.
After adding or editing skills, restart Codex so the new skill list is loaded.

Use a skill name explicitly in the first prompt of a fresh Codex chat. This is
not required for every prompt, but it helps a new chat load the right operating
ritual immediately.

Available EMR4 skills:

- `$emr4-orchestrator` — use for Ariadne/orchestrator work: repo audit, polling,
  sprint planning, plan review, integration, mirror realignment, and closeout.
- `$emr4-dev-environment` — use for dev-stack work: `run_dev.ps1`, Docker,
  ngrok, GitHub Pages deployment, taskpane/diary version checks, API snippets,
  migrations, seed data, and duplicate-audit commands.

Example fresh Codex prompt:

```text
Use $emr4-orchestrator.

Read AGENTS.md, orchestration/protocol_alerts.md, orchestration/parallel_workstreams.md, orchestration/integration_log.md, and orchestration/sprint_closeout.md.

You are Ariadne, the Codex orchestrator for EMR4. Audit the current repo/worktree state before acting. Do not dispatch or integrate until you understand the current sprint state.
```

Example dev-stack prompt:

```text
Use $emr4-dev-environment to help me restart the EMR4 stack and verify the deployed taskpane and diary versions.
```

### Codex Orchestrator

Use this when starting a new Codex/Ariadne orchestration chat:

```text
Use $emr4-orchestrator.

Read AGENTS.md, orchestration/protocol_alerts.md, orchestration/parallel_workstreams.md, orchestration/integration_log.md, and orchestration/sprint_closeout.md.

You are Ariadne, the Codex orchestrator for EMR4. Audit the current repo/worktree state before acting. Do not dispatch or integrate until you understand the current sprint state.
```

### Claude Code

Use this when starting a new Claude Code chat:

```text
Read AGENTS.md, CLAUDE.md, orchestration/protocol_alerts.md, orchestration/parallel_workstreams.md, and your current task packet from handin.

You are Claude Code working in the EMR4 multi-agent protocol. Do not move master or handoff/current. Follow the plan-gated workflow: if this is a new sprint task, produce and submit an implementation plan first, then stop until I say "complete sprint task".
```

### Antigravity

Use this when starting a new Antigravity chat:

```text
Read AGENTS.md, orchestration/protocol_alerts.md, orchestration/parallel_workstreams.md, and your current task packet from handin.

You are Antigravity working in the EMR4 multi-agent protocol. Do not move master or handoff/current. Follow the plan-gated workflow: if this is a new sprint task, produce and submit an implementation plan first, then stop until I say "complete sprint task".

Important: during the plan gate, you may create, commit, and push the
implementation-plan packet and minimum coordination-file status changes required
to submit that plan to Codex's inbox. This is not approval to change production
code. Do not edit app code, diary UI code, taskpane code, migrations, tests, or
runtime docs unless the task explicitly says the plan itself belongs in docs.
If artifact review asks for approval, treat approval as permission to submit the
plan packet only, not permission to implement. Do not auto-proceed from the plan
artifact into code changes unless I explicitly say "complete sprint task".
```

Notes:

- `AGENTS.md` is the shared source of truth for all agents.
- `CLAUDE.md` is additional Claude-specific guidance, not a replacement for `AGENTS.md`.
- For worker agents, run `handin` after the chat starts so they read the current task packet.
- Keep Ariadne/orchestrator Codex separate from Codex worker/subagents. Ariadne
  runs on the integration worktree; Codex workers use explicit task branches,
  never `master`, and Codex plan packets should mark `Role` as `orchestrator`
  or `codex-worker`.

---

## 19. Minimal Command Checklist

First-time setup after installing Git/Python/Docker/Node/ngrok:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents
git clone https://github.com/yurifrusin/EMR4.git
cd EMR4
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN_HERE
.\run_dev.ps1
```

Then in a second PowerShell:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m alembic upgrade head
python seed.py
```

After a normal restart:

```powershell
cd C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4
git pull --ff-only origin master
.\run_dev.ps1
```
