# Codex Model Switching and DeepSeek Ariadne Experiment

This runbook records the controlled setup for switching the Codex Desktop model picker between the native OpenAI/Codex model list and the local DeepSeek bridge catalog.

EMR4 now uses DeepSeek in two distinct ways:

1. Low-cost worker lanes through the `deepseek-worker` subagent.
2. Experimental Ariadne-v2 orchestration, where Yuri may deliberately run the main Codex composer on DeepSeek Pro.

The second mode is experimental. Keep the git safety point below until the experiment has proved itself.

## Current Safety Point

Before enabling the Ariadne-v2 DeepSeek Pro experiment, Ariadne created and pushed a remote safety point at the current D7 codebase state:

| Item | Value |
|---|---|
| Commit | `9d74c849e35cdd3e17984392ee8030622391f2a2` |
| Branch | `safety/ariadne-v1-before-deepseek` |
| Tag | `safety/ariadne-v1-before-deepseek-20260704-182049` |

To inspect or restore that point later:

```powershell
git fetch origin --tags
git show --stat safety/ariadne-v1-before-deepseek-20260704-182049
git switch master
git reset --hard safety/ariadne-v1-before-deepseek-20260704-182049
# Push only after Yuri explicitly approves replacing remote master.
# git push origin master --force-with-lease
```

Do not force-push this rollback unless Yuri explicitly asks for it. For normal recovery, create a new branch from the safety tag and compare or repair first.

## What The Bridge Changes

The local bridge setup uses `model_catalog_json` in `%USERPROFILE%\.codex\config.toml` to point Codex Desktop at:

```text
%USERPROFILE%\.codex\codex-deepseek-bridge\models.json
```

That catalog currently advertises DeepSeek models to the Codex model picker. In practice, Codex Desktop does not merge this custom catalog with the native OpenAI picker list. Therefore this setup is a controlled mode switch, not a single mixed dropdown:

- DeepSeek mode: the composer/picker shows the DeepSeek bridge catalog, e.g. `DeepSeek Pro`.
- OpenAI-native mode: the `model_catalog_json` override is removed, so Codex falls back to the native OpenAI/Codex model list.

The switch does not remove the DeepSeek provider or `deepseek-worker` agent. It only changes which model catalog the Desktop picker uses. Restart or reload Codex after switching modes so the dropdown refreshes.

## Switch Scripts

The scripts live outside the repo because they modify local Codex configuration:

```text
%USERPROFILE%\.codex\tools\model-switch\Show-CodexModelMode.ps1
%USERPROFILE%\.codex\tools\model-switch\Use-DeepSeekCodex.ps1
%USERPROFILE%\.codex\tools\model-switch\Use-OpenAICodex.ps1
```

Every switch script writes a timestamped backup under:

```text
%USERPROFILE%\.codex\backups\model-switch\
```

Check current mode:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\tools\model-switch\Show-CodexModelMode.ps1"
```

Switch the Codex picker to DeepSeek bridge mode:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\tools\model-switch\Use-DeepSeekCodex.ps1"
```

Switch the Codex picker back to OpenAI-native mode:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\tools\model-switch\Use-OpenAICodex.ps1"
```

After either switch, restart or reload Codex before trusting the visible model selector.

## Current Local Bridge State

The working bridge process is expected at:

```text
http://127.0.0.1:8787/v1
```

The DeepSeek provider block in `%USERPROFILE%\.codex\config.toml` should be:

```toml
[model_providers.deepseek_bridge]
name = "DeepSeek (via Codex DeepSeek Bridge)"
base_url = "http://127.0.0.1:8787/v1"
wire_api = "responses"
supports_websockets = false
requires_openai_auth = false
```

The worker agent remains:

```toml
# %USERPROFILE%\.codex\agents\deepseek-worker.toml
name = "deepseek-worker"
model_provider = "deepseek_bridge"
model = "deepseek-flash"
model_reasoning_effort = "medium"
```

## Operating Policy

Use DeepSeek in increasing-risk tiers:

1. `deepseek-worker` Flash for bounded, low-cost read-heavy review or narrow implementation lanes.
2. `deepseek-worker` Pro only when reasoning depth is the bottleneck.
3. Main-composer DeepSeek Pro Ariadne-v2 only as an explicit experiment with a git safety point and no automatic master promotion.

When testing Ariadne-v2 on DeepSeek Pro:

- Start with small review or planning tasks.
- Prefer local review branches and do not push to `master` until Yuri approves.
- Run `git status --short --branch` and `git log --oneline -5 --decorate` before and after work.
- Keep Claude, Antigravity/Gemini, and/or OpenAI Ariadne available as reviewers if the DeepSeek result seems overconfident or underspecified.
- Watch the DeepSeek and OpenAI usage meters after each sprint to confirm which model actually did the work.

## Reverting Codex Model Configuration

To return Codex to OpenAI-native picker mode:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\tools\model-switch\Use-OpenAICodex.ps1"
```

If a switch script goes wrong, restore one of the timestamped backups:

```powershell
Copy-Item "$env:USERPROFILE\.codex\backups\model-switch\<backup-file>.toml" "$env:USERPROFILE\.codex\config.toml" -Force
```

Then restart Codex.

## Alternate PC Notes

The model-switch scripts are local files, not repo-tracked executables. On the alternate PC, recreate them from Ariadne if needed or copy them through a secure local channel together with the DeepSeek bridge setup. Do not commit API keys, bridge key files, Codex auth, or local logs.
