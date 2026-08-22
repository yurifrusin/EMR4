# Threat-model delta: integrated-runner factory fixture import-path recovery

Date: 2026-08-22

Timestamp: 2026-08-22T19:15:38.4788019+10:00 (Australia/Brisbane)

Status: frozen provider-free delta

Operation: `deepseek-native-harness-provider-free-integrated-runner-factory-fixture-import-path-recovery`

## Changed surface

The tranche adds one distinct local Node fixture derived from the accepted
factory diagnostic. The new risks are silent semantic drift while copying the
fixture, an import path that escapes or selects the wrong package scope,
starting Node before both imports are proved, dynamic exception leakage and
accidental retry of either consumed identity.

## Controls

- A deterministic source-equivalence gate admits exactly one normalized
  difference: `package_root.parents[1]` becomes `package_root.parent`.
- Both derived imports must resolve strictly as regular files beneath exact
  `node_modules/@deepseek-ai` before the attempt identity is persisted.
- The controller uses installed `AgentRegistry.create` and one inert local
  factory; it never instantiates the native Harness or agent loop.
- The exact occupied runner and guard bytes are copied and hash-verified; the
  predecessor attempt and evidence remain immutable.
- Only an allowlisted guard code, fixed counters and booleans may enter the
  structured result. Raw message, stack, cause, path, environment, prompt,
  response, reasoning, session content and exception objects are forbidden.
- Provider, broker, network, database, Docker and target counters must remain
  zero.
- The process receives the five-key Windows minimum environment plus the exact
  Node directory in `PATH`; no provider key is supplied.
- Cleanup validates the exact disposable child before removal and rejects
  parent/root deletion, symlink traversal or cleanup outside that child.
- One process is permitted. Once started, any result consumes the distinct
  identity; retry, resume, fallback, second fixture and native Harness launch
  remain forbidden.

## Claim ceiling

A pass proves only that the path-corrected local fixture traversed installed
`AgentRegistry.create` and reproduced the exact occupied runner/guard
subcoordinate. It does not prove native Harness boot, a DeepSeek turn, provider
reachability, worker quality, product behavior, runtime safety, deployment or
production suitability.

Protected evidence, product/patient/clinical data, ordinary-practice changes,
deployment, release, Pages and protected-ref movement remain closed.
