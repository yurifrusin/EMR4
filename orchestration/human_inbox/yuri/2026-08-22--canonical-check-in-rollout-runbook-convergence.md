# Canonical check-in rollout runbook convergence

Date: 2026-08-22

Timestamp: 2026-08-22T23:19:52.9249303+10:00 (Australia/Brisbane)

## Lay summary

This is a direct step forward rather than another diagnostic circle. The exact
safe default-off procedure for a future check-in rollout, emergency stop and
rollback is now present as a single machine-checkable API-Spine record.

It does not switch check-in on. It states that activation is still forbidden,
the kill switch is engaged, an uncertain result must not be called successful
or blindly retried, and the source of truth must be read back. That gives later
work one canonical procedure instead of another implicit promise.

Three small procedural mistakes were caught locally: one PowerShell parse
error, one unregistered receipt label and one graph classification that would
have inherited unrelated product contracts. None triggered a model, provider,
database or product rerun. The candidate itself and all its tests passed first
time. This is the useful pattern for the clockwork, although we should continue
moving its vocabulary constraints into forms where invalid choices are
impossible to enter.

Your attention is not required. The next small concrete step is the matching
default-off non-PHI observability manifest: five accepted metric families and
six alerts that cannot take automatic action.

## Technical summary

- Exact reviewed source: `149e377344fab671927682e428af7825e9a0e143`.
- Canonical manifest: 2,331 exact bytes.
- SHA-256: `dbd765ef3afe2ffe283a07befff44f745b21a8ec474c58d5a6d944fe3a9c8448`.
- Focused checks: 5 passed; integrated checks: 98 passed; full closeout packet:
  143 passed.
- Request/response, route, OpenAPI/GraphQL, app/configuration and clients:
  unchanged.
- Ordinary enablement/activation: false; active ordinary records: zero.
- DeepSeek/Gemini/native subagents: declined; no external worker or provider
  run.
- Database/Docker/runtime/deployment/Pages/protected refs: unchanged.
- Preserved: `docs/branding/` and all unrelated untracked files.
- Next:
  `raisa-provider-free-default-off-canonical-check-in-non-phi-observability-manifest-convergence-rehearsal`.

The next tranche may add only the accepted default-off declarative
observability manifest and focused tests. It authorises no telemetry runtime,
alert transport, automatic control, identifiers, product data or activation.
