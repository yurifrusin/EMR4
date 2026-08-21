# Threat-model delta — native Harness bounded-worker attempt 005

Date: 2026-08-21
Timestamp: 2026-08-21T19:11:54.8870455+10:00 (Australia/Brisbane)
Status: `frozen`
Reasoning level: `high`

## Scope

This delta covers one disposable authored-synthetic native DeepSeek Harness
attempt. It adds no product runtime, command, database, ordinary-practice,
deployment, production, Pages or protected-ref surface.

## Assets and trust boundaries

- the task branch, active latch and clockwork lease;
- the exact attempt/work-order/lease identities;
- the disposable local synthetic Git workspace and pinned rc.7 package;
- the local loopback broker and one DeepSeek provider request boundary;
- the exact one-file edit tool and bounded terminal evidence;
- the protected local user environment, credentials and unrelated untracked
  files, which remain outside retained evidence.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| Stale or abbreviated Git authority | Machine-resolved full object IDs, ancestry, task/origin and protected-ref gates | Reject before preparation |
| Reuse of a consumed attempt | Exact disjoint attempt/work-order/lease IDs plus exclusive preparation/consumption files | Reject before launch |
| Duplicate Harness or provider execution | One launcher coordinate, one consumed lease, broker request ceiling 1, retry/resume/fallback 0 | Terminalize and stop |
| Tool-surface expansion | Effective view exactly `edit`, `glob`, `read`; work order allows one direct literal `edit` only | Broker/runner rejection |
| Product or sensitive-data exposure | Newly authored synthetic one-file workspace; no repository/product data in the task; forbidden-surface digest | Reject admission or terminalize |
| Credential/session/raw-output retention | Credentials remain broker-side; retain only closed digests/counts; delete raw streams, environment/session artifacts and root | Failed-closed cleanup terminal |
| Malicious or malformed model output | Broker validates the single request/tool shape; exact expected bytes and 4+3 synthetic cases gate success | `failed_closed` |
| HMR/plugin-tree failure before model I/O | Structured pre-HMR diagnostic selection with raw messages/stacks/paths omitted | Bounded sanitized terminal |
| Ambiguous timeout or process state | 300-second upstream and 420-second native ceilings; terminate owned processes; prove absence | `failed_closed`, no retry |
| Evidence written inside disposable root | Terminal path must be under the repository evidence root and outside the disposable root before cleanup | Reject terminalization |
| LLM-authored control vocabulary drift | Closed schemas and clockwork/preflight admission choose or validate exact enum tokens before publication/dispatch | Reject before state transition |
| Unrelated-worktree damage | Exact root-parent validation, explicit-path staging and preservation checks for `docs/branding/` and all unrelated untracked files | Reject/stop without broad cleanup |

## Claims deliberately unavailable

Even a passing terminal proves only one bounded authored-synthetic attempt. It
does not establish generic DeepSeek or Harness reliability, product
suitability, ordinary-practice safety, patient-data safety, production
readiness, deployment authority or protected integration.
