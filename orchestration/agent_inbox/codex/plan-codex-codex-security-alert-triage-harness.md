# plan-codex-codex-security-alert-triage-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/security-alert-triage` |
| Source Task | `codex-security-alert-triage-harness` |
| Status | pending_plan_review |
| Created | 2026-06-24 12:56 +1000 |
| Source HEAD | `0cfaf1c` |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/security-alert-triage` |

## Plan Summary

Plan GitHub security alert triage harness

## My Understanding

After approval, create an Ariadne-facing GitHub Security alert triage harness for Sprint 21 using the EMR4 security-manager workflow and gh read-only queries. Inventory CodeQL/code-scanning, secret scanning, Dependabot, and recent security workflow state; classify alerts into fix-now/defer/noise; and identify alerts likely closed by current sprint code fixes. This plan gate submits coordination artifacts only and does not run alert inventory or implement the report yet.

## Intended Surface / Boundary

Security/orchestration documentation only. Intended output is an orchestration report such as orchestration/security_alert_triage.md, plus at most a safe cross-reference from existing security baseline notes if needed. No app, diary, taskpane, Command Centre, booking, waiting-room, cards, slots, stacking, panels, diary grid, booking slot, or appointment status surface is affected.

## Out Of Scope

No production app code; no app/routers/consultation.py edits owned by Claude; no Node/Office workflow triage owned by Antigravity; no UI assets; no migrations; no tests; no runtime docs outside the triage harness link if needed; no secret disclosure; no GitHub alert dismissal; no cloud/key rotation; no master/handoff integration.

## Files I Expect To Edit

Expected after approval: orchestration/security_alert_triage.md; optionally orchestration/security_baseline_review.md for a short discoverability link only. Plan gate files only: the generated plan packet and source task coordination notes/status.

## Implementation Steps

After explicit 'complete sprint task': confirm branch and clean status; run gh auth status; run the security-manager snapshot helper or equivalent metadata-only gh queries for code-scanning, secret-scanning, Dependabot, and recent workflow runs; redact/avoid secret values and capture only alert metadata/rules/paths/severity/state; classify each signal as fix-now/defer/noise/needs-Yuri with rationale and owner boundary; cross-check Claude consultation.py and Antigravity Node/workflow ownership without editing their areas; draft the Ariadne-facing triage harness with commands run, findings, recommended Sprint 21 decisions, and remaining risks; run git diff --check and any markdown/syntax sanity checks available; fill completion notes and submit with the task packet command.

## Visual / Behavioural Acceptance Checks

Plan packet includes codex-worker role, Cicero name, and codex/security-alert-triage branch. After approval, the report must be complete enough for Ariadne to prioritize Sprint 21, expose no secrets, include concrete alert IDs/rules/paths where safe, separate CodeQL/secret/Dependabot/workflow signals, name fix ownership boundaries, and make clear that no visual or behavioral product surface changed.

## Risks / Ambiguities

gh may lack auth or GitHub security-scope access; GitHub security APIs may omit secret details by design; open CodeQL alerts may overlap Claude-owned consultation.py fixes or Antigravity-owned Node workflow triage, so classification must avoid ownership drift; workflow failures may be transient until first post-Sprint-20 scheduled runs; any secret-scanning alert needs immediate Ariadne/Yuri judgment rather than committed details.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
