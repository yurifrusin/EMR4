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

GCP_PROJECT=emr4-copilot
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json

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

AI features need a local Google credentials file called:

```text
gcp-key.json
```

Place it in the EMR4 repo root:

```text
C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4\gcp-key.json
```

The `.env` line should then be:

```env
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json
```

If `gcp-key.json` is missing, the app can still run for diary, patient, and
database development, but AI endpoints such as scribe/analyse may fail.

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

## 11. Stopping The Dev Stack

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

## 12. Agent Worktrees On A New PC

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

## 13. Check The Live Taskpane Version

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

---

## 14. Common Problems

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

Check that this file exists:

```text
C:\Users\YOUR_WINDOWS_USERNAME\Documents\EMR4\gcp-key.json
```

Check `.env`:

```env
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json
```

Restart backend:

```powershell
.\run_dev.ps1 -Down
.\run_dev.ps1
```

---

## 14. Minimal Command Checklist

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
