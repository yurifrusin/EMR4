# Threat-model delta — check-in native Harness preset-row service-path recovery

Date: 2026-08-20

Timestamp: 2026-08-20T17:42:05.9062693+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery`

## Changed attack and failure surface

This tranche reads retained rc.7 profile-composition, home-path and preset
discovery sources; builds disposable authored-synthetic root fixtures; and may,
only after exact candidate review plus a separate clockwork checkpoint, run one
provider-disabled no-agent native service-row confirmation. It introduces no
provider, product or data access.

| Risk | Fail-closed control |
|---|---|
| A passing direct root scan is mistaken for the native service's effective inputs | Bind `composeProfile()` overlay order and `AgentPresets.resolvedRoots`; evidence must distinguish configured, forced shipped and derived user roots. |
| An earlier configured root is incorrectly reported as effective | Prove rc.7's final native overlay replaces `roots` with the shipped root; arbitrary-root fixtures must be rejected as displaced. |
| Re-enabling the user root silently broadens the roster | Require exactly two roots in order: shipped `system`, then disposable `$DSH_HOME/.agent-presets` `user`; require an enumerated shipped roster and exactly one EMR4 row. |
| User trust is mislabelled as system trust | The corrected row must carry exact `user` trust; schemas and tests reject `system`, missing or invented trust. |
| A shipped duplicate shadows the intended user preset | First-root-wins is tested explicitly; any shipped `emr4-bounded-worker` duplicate fails closed instead of accepting the later row. |
| A real machine home leaks into the result | Every fixture and later native process binds a disposable `DSH_HOME`; absolute paths are sanitized to enumerated roles and cleanup requires root absence. |
| Package or installed Harness source is mutated to make the test pass | Retained source/package/lockfile digests are checked before and after; only repository controller, tests and evidence may change. |
| Package-only analysis quietly boots the Harness or reaches the network | Imports are pinned and local, the network-denial guard remains active, no CLI/native service graph is assembled, and process/request counters are exact. |
| The later native probe drifts into agent creation or a provider request | Static runner gates forbid agent, mount, session, turn and model APIs; provider environment is scrubbed and broker/model/provider/network counts remain zero. |
| A failed native process is retried | First creation consumes the separately checkpointed allowance; retry count is zero and the terminal is immutable. |
| Raw errors or machine paths leak into durable evidence | Persist only closed coordinates, role-labelled paths, counts and digests; discard raw exceptions and stdout/stderr. |
| Diagnostic correction is mistaken for product or occupied-worker readiness | Claim and schema boundaries explicitly exclude product configuration, mount, tools, DeepSeek performance, attempt 006 and production. |

## Claim boundary

Passing deterministic evidence may prove the exact rc.7 root-overlay cause and
that the minimal diagnostic-profile correction yields shipped-plus-user roots
with one healthy user-trust EMR4 row. A separately checkpointed native pass may
add only provider-disabled native service-row convergence. It proves no preset
mount, agent, tool, DeepSeek request, coding performance, attempt 006, database
or product behavior, production suitability or deployment authority.
