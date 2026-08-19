# Threat-model delta: provider-free effective-tool composition native-boot proof

Date: 2026-08-20

Timestamp: 2026-08-20T05:22:33.9249587+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof`

## New bounded execution surface

This tranche adds one local rc.7 native Harness process to the already accepted
provider-free HMR envelope. The process may mount one disposable preset into
one key-agnostic scoped context and run the accepted effective-tool guard. It
does not create an agent, session, turn, broker or provider request.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A child-scope registration bypasses inherited restriction | The child scope is freshly minted, the accepted guard rejects `knownNames - restrictableNames`, and the runner adds no scoped tool registration. |
| A preset supplies unexpected tools | The preset has exactly two frozen plugin rows; surplus inherited schemas are filtered by the one accepted restriction and the final exact view must be `edit`, `glob`, `read`. |
| The proof accidentally creates an agent/session or reaches a provider | The runner uses only `createScope` and `AgentPresets.mount`; agent/session/broker/model/provider counters must remain zero and no credential or request surface is supplied. |
| The controller fabricates HMR readiness | Only the in-process sentinel may observe both exact stock patch registrations; mutation before that event rejects. |
| Dynamic exceptions leak secrets or paths | The accepted sanitizer retains only a closed coordinate and safe tool-name detail; raw logs and transient files are deleted. |
| Network access escapes the provider-free claim | Credential/proxy environment is scrubbed and Node network primitives are denied and counted; any attempt rejects acceptance. |
| A failure is retried and erased | The first process start consumes `native-composition-attempt-001`; automatic/manual retry, resume and reclassification are forbidden. |
| A process or disposable tree survives | One controller owns terminate/kill/wait and exact-root deletion; acceptance requires process and root absence. |
| A successful writer projects a future target as current evidence | Closeout `current_position.outcome` must state this operation's measured terminal, never a successor objective; the mismatch is checked during closeout review. |
| The proof is misrepresented as model reliability | Evidence and closeout explicitly limit the claim to rc.7 native composition, terminal traceability and cleanup. |

## Unchanged closed surfaces

Protected holdouts and historical diary PHI remain inaccessible. Attempts 004
and the consumed native worker attempt 001 remain immutable; attempt 005 is not
created. Product, API, configuration, ordinary-practice, data, Docker/database,
production, deployment, release, Pages and protected-ref authority remain
closed. `docs/branding/` and all unrelated untracked files remain preserved.
