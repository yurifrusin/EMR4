# EMR4 New PC Transfer Guide

This guide is for moving EMR4 development to a new Windows PC while keeping the
current PC as a safe fallback. For the July 2026 alternate-PC switch, use the
shorter current runbook first:

```text
docs/alternate-pc-handover.md
```

The clean baton is always `origin/master` plus `origin/handoff/current`. At the
time this guide was refreshed, the last code-sprint commit before the handover
docs was:

- `b896582` - Sprint 103 Bernie compact request auto preview

The actual current commit after pulling may be newer because this documentation
handover is committed on top of that code sprint.

Do not delete or reset the old PC until the new PC can clone, audit, run the
focused checks, and start the local development environment.

## 1. Clone the repo fresh

Run these commands in PowerShell on the new PC:

```powershell
mkdir C:\Users\YuriFrusin\Documents -Force
cd C:\Users\YuriFrusin\Documents

git clone https://github.com/yurifrusin/EMR4.git EMR4
cd C:\Users\YuriFrusin\Documents\EMR4

git fetch origin
git switch master
git pull --ff-only origin master
```

Confirm the clean baton:

```powershell
git rev-parse --short HEAD
git ls-remote --heads origin master handoff/current codex/current claude/current antigravity/current
```

Expected result: `master`, `handoff/current`, and the durable mirror refs should
point to the same current baton commit, or to intentionally submitted worker
branches awaiting Ariadne review. Do not use the older `e53b283` baton.

Create local tracking branches for the handoff and durable mirrors:

```powershell
git branch -f handoff/current origin/handoff/current
git branch -f codex/current origin/codex/current
git branch -f claude/current origin/claude/current
git branch -f antigravity/current origin/antigravity/current

git status --short --branch
```

Expected result: `master` is clean and aligned with `origin/master`.

## 2. Recreate agent worktrees

From the integration repo:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4
python scripts\agent_worktrees.py setup
python scripts\agent_worktrees.py audit --fetch
```

Expected result: the integration worktree and durable agent mirrors are clean.
If the audit reports dirty files immediately after a fresh clone, stop and ask
Ariadne to inspect before continuing.

## 3. Recreate Python environment

Use a fresh virtual environment rather than copying `.venv` from the old PC:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If Python 3.12 is not installed, install it first or ask Ariadne to check the
project's current supported Python version before substituting another version.

## 4. Recreate frontend dependencies if needed

If frontend or diary checks need Node packages:

```powershell
cd "C:\Users\YuriFrusin\Documents\EMR4\EMR4 Sidebar"
npm install
cd C:\Users\YuriFrusin\Documents\EMR4
```

Do not copy `node_modules` from the old PC.

## 5. Restore local-only configuration carefully

Copy these only through a secure channel, not through Git:

- `.env`
- ngrok auth/config
- Pushover notification environment values
- GitHub CLI authentication
- Codex, Claude, and Antigravity local auth/settings
- Office add-in sideloading configuration
- `patient_files/` only if intentionally needed for local dev continuity

Do not commit secrets, real patient data, generated clinical documents, `.venv`,
`node_modules`, or agent session state.

## 6. Google auth expectations

Expect to reauthorise Google user credentials on the new PC if EMR4 uses local
Application Default Credentials. ADC tokens live under the Windows user profile,
so they normally do not move with a Git clone.

Typical reauthorisation commands:

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud auth application-default print-access-token
```

EMR4 AI development now prefers keyless Google Cloud authentication. Do not copy
service-account JSON keys to a new PC for normal development.

Use the runbook:

```text
docs/gcp-keyless-ai-setup.md
```

The short version is:

```powershell
gcloud auth login yuri@littlestardigital.com
.\scripts\use_bernie_adc.ps1
```

For Bernie and Scribe/Copilot, separate service accounts are preferred because they
make permissions, audit trails, quota attribution, and future production
separation clearer.

## 7. GitHub CLI auth

If GitHub CLI is installed:

```powershell
gh auth login
gh auth status
```

This is useful for security review, workflow inspection, and future automation.

## 8. First smoke checks

After dependencies and local config are in place:

```powershell
cd C:\Users\YuriFrusin\Documents\EMR4

.\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\services\bernie_booking_interpreter.py
.\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py -q --tb=short -p no:randomly
python scripts\agent_worktrees.py audit --fetch
```

If these pass, ask Ariadne to run the broader local environment checks before
resuming sprint orchestration.

## 9. Resume with Ariadne

Once the new PC is ready, start a Codex thread from the new PC. Prefer the
current prompt in `docs/alternate-pc-handover.md`. The older minimal prompt is:

```text
Resume EMR4 sprint orchestration from C:\Users\YuriFrusin\Documents\EMR4 after new PC migration. Audit first. The clean baton should be origin/master and origin/handoff/current at the same current commit.
```

Ariadne should audit the repo, verify the baton, check local tooling, and only
then resume sprint work.

## 10. Keep the old PC as fallback

Before switching fully:

- Confirm the old PC repo is clean and pushed.
- Confirm the new PC repo is clean and audited.
- Keep the old `.env` and service-account material available until the new PC
  has passed local API and AI-provider checks.
- Do not run competing sprint orchestration loops on both PCs at the same time.

The safest operating model is: old PC paused, new PC audited, then only the new
PC resumes orchestration.
