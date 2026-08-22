# Threat-model delta: native-Harness integrated-runner first controlled development rehearsal

Date: 2026-08-22

Status: `frozen`

## Added surface

One disposable local Git workspace, one pinned rc.7 native-Harness process,
one loopback one-request broker and one authored-synthetic Python file are
temporarily introduced. The exact accepted integrated runner is rebound to the
disposable target without widening its edit, tool, provider or lifecycle
controls.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Product or sensitive data enters the request | The workspace is synthesized from frozen source bytes and contains exactly one non-product file; path inventory and hashes are checked before launch. |
| Model reads or changes another path | Effective tools are exactly `edit`, `glob`, `read`; the task instructs one edit; the pre-execute gate admits only one top-level edit at the exact target with non-empty unequal literal strings and no `replace_all`. Changed paths must equal the one synthetic path. |
| Runner adaptation silently weakens controls | The derived runner must equal the accepted bytes after only the exact target-literal substitution and two redundant compatibility-reading insertions; typed-control source fragments and digests are revalidated. |
| More than one provider request or hidden retry occurs | The loopback broker allows one request; Harness retry plugin is disabled; provider retry count is zero; controller and terminal require zero retry/resume/fallback. The consumed lease prevents relaunch. |
| A plausible but wrong edit is accepted | Exact expected bytes, four public cases and three separately held controller cases must all pass. A surviving candidate also receives an independent Gemini veto. |
| Raw model or credential material persists | Raw prompt, response, reasoning, streams, environment, session and credentials remain in the disposable envelope only and are destroyed; retained evidence contains hashes, counts and closed coordinates. |
| Loopback broker becomes a general network relay | Exact loopback port/token, model identity, request ceiling and broker lifecycle are bound before launch; broker and Harness must be absent after terminalization. |
| Failure causes an iterative occupied loop | Attempt identity is written consumed before launch. Any terminal result ends the attempt; no retry, resume, fallback, second worker or reclassification is permitted. |
| Governance machinery hides its own cost | Every prelaunch rejection and occupied count/timing is retained, and the efficacy decision requires useful behavioral output rather than merely a valid closeout. |
| Protected refs or unrelated untracked files move | Exact ref checks run before and after; all staging is explicit-path; unrelated untracked files, especially `docs/branding/`, are excluded. |

## Residual risk

One synthetic success would demonstrate controlled usefulness only for this
single-edit task. It would not establish general model reliability, multi-file
development authority, ordinary-practice safety, production suitability or a
right to use real patient or clinical data.
