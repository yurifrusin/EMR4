# Threat-model delta: provider-free shadow clockwork / DeepSeek broker gear rehearsal

Date: 2026-08-19  
Scope: private-shadow orchestration evidence only

## Added assets

- One derived four-event causal tick: request/admission, WorkOrder lease transfer, terminal broker result, Ariadne acknowledgement.
- An immutable fourteen-case procedural-failure gauge ledger.
- A complete private shadow generation and its efficacy reading.

These are repository-local synthetic orchestration artifacts. They contain no prompt, reasoning, secret, provider credential, product payload, patient, practice, health, clinical or historical data.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| Caller retypes a binding, including an abbreviated Git OID | Public generation API accepts paths only; the engine derives binding fields and requires full 40-character OIDs | Zero caller binding fields; abbreviated/stale OID probes rejected |
| Ariadne and broker advance the same tick concurrently | Single-owner lease state machine; WorkOrder transfers ownership and acknowledgement returns it | Concurrent writer and Ariadne-before-ack probes rejected |
| Broker replays or forks work | Exact parent, sequence, attempt, WorkOrder digest and one-terminal constraints | Replay, stale-parent, gap and duplicate-terminal probes rejected |
| Preset or tool selection silently changes authority | Package, profile, permission preset and minimized tool-view digests are WorkOrder bindings; policy remains the authority | Profile, preset, package and tool-digest mutations rejected |
| Provider or product effect leaks into a provider-free rehearsal | Only `shadow_generation_write` is admitted; result must report zero provider calls; closed paths and commands are validated | Provider, candidate, Git, protected-ref, product and runtime probes rejected |
| A partial generation becomes evidence | Validate complete staged generation, fsync files, then one sibling-directory rename; failed staging is removed | Injected write failure leaves no target and no staging residue |
| Mutable live state is copied into tests | Tests validate latch shape or immutable supplied fixtures, never current values | New mutable-current fixture count remains zero |
| Rerun reduction hides lost controls | Every comparator failure is an immutable hostile gauge with a named rejection rule and expected phase | Fourteen of fourteen gauges rejected before publication |
| Timing becomes an authority shortcut | Monotonic timing is reported separately and excluded from hashes and admission | Repeated runs have identical authoritative digest despite different timing |
| Self-reported efficacy is accepted | Engine calculates counts from contract, fixtures, generated trace and filesystem readback | Caller-supplied metric probe rejected; report matches evidence |
| Private shadow silently becomes live | Target must be a non-current, non-protected private-shadow path; canonical controls remain unmodified | Closed-surface checks and unchanged protected refs |

## Residual risk

This rehearsal does not prove the installed DeepSeek Harness can boot stock headlessly into the custom runner, authenticate, survive provider faults, or honour its runtime sandbox. Those remain prerequisites to any occupied run. It also does not prove the clockwork is ready to replace current controls. The result is limited to deterministic, provider-free representability and measured procedural coverage.

