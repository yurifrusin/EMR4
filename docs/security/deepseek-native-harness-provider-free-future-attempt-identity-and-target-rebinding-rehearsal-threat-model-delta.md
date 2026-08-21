# Threat-model delta — native Harness future-attempt identity and target rebinding

Date: 2026-08-21

Timestamp: 2026-08-21T22:49:59.5125472+10:00 (Australia/Brisbane)

Status: `frozen`

Reasoning level: `high`

## Scope

This delta covers one Python-only transformation from the exact accepted
materialised future-runner bundle to one fresh fixture identity and one inert
authored-synthetic relative target. It opens no JavaScript execution, Harness,
broker, worker, model, provider, target-file, product, data, command, deployment,
release, Pages or protected-ref surface.

## Threats and controls

| Threat | Control | Fail-closed result |
|---|---|---|
| A shortened or narrated candidate identity enters the helper | Full-OID schema plus machine-resolved planning source | Reject contract or helper |
| Only one of operation, attempt or candidate is rebound | Regenerate helper from one typed identity object and test every partial substitution | Reject binding |
| Consumed attempt-005 target survives unnoticed | Require old JSON literal exactly once, replace once, assert old bytes absent and reverse to accepted hash | Reject runner |
| New target names a real host/repository path or escapes the workspace | Exact two-component relative allowlist, no drive/UNC/absolute/backslash/traversal/environment input | Reject target |
| Neighbouring runner/helper/controller/target hashes are copied into the wrong field | Separately computed named bindings plus distinctness checks | Reject bundle |
| Bundle identity differs from source identity | Exact helper/runner readings and bundle identity equality before terminal assembly | Reject materialisation |
| Terminal narrates a descriptive state or changes a binding | Closed coordinate vocabulary and exact bundle-to-terminal copy | Reject terminal |
| Rebinding accidentally authorises execution or target use | Exact false authority/raw fields in contract, bundle, terminal and evidence | Reject artifact |
| Partial or replaced tree is read as complete | Exact six-path roster, exclusive writes, canonical bytes, hash readback and symlink checks | Reject tree |
| LLM invents a count, path, state or Git value | Typed schemas and completed machine readings own every finite value | Reject artifact or statement |
| Provider-free rehearsal starts an executable surface | Fixed zero process/request counters and no JavaScript invocation path | Reject tranche |
| Unrelated worktree content is staged | Explicit-path staging and preserved-untracked checks | Stop before commit |

## Residual boundary

Passing evidence will prove a fresh, closed, provider-free identity and inert
target transformation only. It will not prove JavaScript parsing, native
loading, stock-headless-to-custom-runner HMR boot, a real target file, DeepSeek
behavior, provider reachability or occupied Harness readiness for EMR4 work.
