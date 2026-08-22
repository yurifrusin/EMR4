# Threat-model delta: integrated-runner factory-subcoordinate diagnostic recovery

Date: 2026-08-22

Timestamp: 2026-08-22T18:51:53.2135364+10:00 (Australia/Brisbane)

Status: frozen provider-free delta

Operation: `deepseek-native-harness-provider-free-integrated-runner-factory-subcoordinate-diagnostic-recovery`

## New attack and evidence surfaces

The tranche adds one disposable local Node fixture that imports accepted rc.7
package bytes and the exact occupied runner/guard pair. Its principal risks are
accidental model/provider dispatch, dynamic exception leakage, accepted-source
mutation, a misleading fixture that bypasses the installed registry boundary,
and unsafe cleanup of a broad path.

## Controls

- The fixture uses the installed `AgentRegistry.create` method and an inert
  local factory; it never instantiates the native Harness or agent loop.
- The factory calls the runner-supplied setup callback exactly once and releases
  only an allowlisted guard code plus fixed counts and booleans.
- No raw error message, stack, cause, path, environment value, prompt, response,
  reasoning or session content may enter evidence.
- The preset service, private agent context, model-selection and hook surfaces
  are proxies with exact access counters; unexpected access rejects.
- Provider, broker, network, database and Docker counters must remain zero.
- The process has a five-key Windows minimum environment plus the exact Node
  directory in `PATH`; no provider key is supplied.
- Accepted source and package bytes are copied read-only into an exact child of
  the established disposable worker root and verified before execution.
- Cleanup resolves and validates the exact child path before recursive removal;
  parent/root deletion, symlink traversal and cleanup outside that child reject.
- One process is permitted. After it starts, any result consumes the identity
  and no retry, resume, fallback or Harness launch follows.

## Claim ceiling

A pass attributes the consumed broad `factory` terminal to the exact occupied
runner/guard interface mismatch and selects an already derived provider-free
correction graph. It does not prove native-Harness agent creation, a DeepSeek
turn, provider reachability, worker quality, product behavior, runtime safety,
deployment or production suitability.

Protected evidence, product/patient/clinical data, ordinary-practice changes,
deployment, release, Pages and protected-ref movement remain closed.
