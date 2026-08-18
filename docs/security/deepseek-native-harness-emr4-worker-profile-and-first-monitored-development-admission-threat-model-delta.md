# DeepSeek native Harness EMR4 worker profile and first monitored development admission threat-model delta

Date: 2026-08-18

Timestamp: 2026-08-18T15:46:46.3145392+10:00 (Australia/Brisbane)

Status: frozen

Reasoning level: high

## Scope

This delta covers the repository-owned native-Harness profile contract,
disposable rc.7 package/Harness homes, one sparse EMR4 worker worktree, one
occupied DeepSeek session and sanitized trace reduction. It changes no EMR4
application or clinical threat boundary.

## Assets

- exact EMR4 task-branch source and frozen owned-path work packet;
- normalized profile authority, canonical digest and package-source mapping;
- DeepSeek credential available only to the occupied process environment;
- raw DSH session/tool material retained only in the disposable root;
- sanitized candidate, usage, terminal, test and cleanup evidence;
- protected refs and preserved user untracked files.

## Threats and controls

### Profile drift or hidden authority

Threat: a package-native field, auxiliary route, fallback, retry, tool or
permission is enabled without representation in the EMR4 contract.

Controls: pin rc.7 registry identity; reject unknown normalized fields; map
each contract field against local pinned package source; hash the normalized
effective authority; disable title, compaction, telemetry, web, workflow,
skill, job and subagent routes; require provider-free `MISSING_CREDENTIAL`
preflight before occupied dispatch.

### Workspace overreach

Threat: the worker reads or edits unrelated EMR4, protected or user-owned
material.

Controls: new non-protected sparse worktree; only exact packet inputs present;
two owned output paths; workspace-write sandbox; approval `never`; minimized
tools; exact Git changed-path readback; reject any unexpected path. The main
worktree and `docs/branding/` never enter the Harness working directory.

### Shell and network overreach

Threat: PowerShell escapes the intended test role, accesses credentials or
contacts an unapproved network destination.

Controls: the prompt and profile admit PowerShell only for frozen focused test
commands; sparse workspace contains no product data; no web/browser/MCP/ACP
tool; process environment supplies only the required DeepSeek credential;
sanitized process/session readback exposes any ordered PowerShell call. Any
unexpected command or route rejects the candidate and ends the single attempt.

### Raw trace or credential persistence

Threat: reasoning, prompts, responses, tool payloads or credentials are copied
into EMR4 or left in a reusable home.

Controls: dedicated disposable npm cache and DSH home; no environment dump;
derive only sanitized structural/usage/tool/diff/test metadata; never stage raw
sessions; recoverably remove the exact disposable roots and verify absence.

### Hidden spend or runaway loop

Threat: the agent loops or retries beyond useful work.

Controls: Yuri's prepaid account credit is the monetary ceiling; EMR4 sets
zero automatic retry/fallback, one occupied fresh session, one parallel tool
call and a 15-minute wall clock. Session usage remains attributable. No local
turn-budget proxy is required and no terminal result is automatically rerun.

### Candidate self-certification

Threat: DeepSeek's summary is treated as acceptance or its partial result is
silently adopted.

Controls: DeepSeek receives no acceptance, recovery, Git publication or baton
authority. Sol independently reads the exact diff, hashes, tool trace and test
results; only Sol may admit, mechanically recover or reject the candidate.

### Session confusion or stale resume

Threat: a prior session, profile or tranche is resumed with stale authority.

Controls: fresh DSH home and session for this trial; session-pinned profile and
source HEAD; no resume after terminal; future resume allowed only for the same
explicitly interrupted operation with fresh latch/ref/profile validation.

## Deliberately closed

No application source, patient/product/clinical data, historical diary,
protected holdout, live product runtime, provider-executed product tool,
ordinary-practice action, deployment, production, release, Pages or protected
ref. No global installation, durable user Harness profile, credential/IAM
mutation or raw transcript retention.
