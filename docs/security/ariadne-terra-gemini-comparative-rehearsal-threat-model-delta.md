# Threat-model delta: Terra/Gemini comparative work-cell rehearsal

Date: 2026-07-24
Parent boundaries: Ariadne bounded agent-admission and cognitive work-cell
protocols; EMR4 API Spine

## New assets and trust boundaries

- two one-use provider authorities and credentials;
- a provider-neutral sealed cognition task;
- one private work-cell/broker network per lane;
- one provider-egress broker per lane;
- sanitised comparison evidence.

The model and provider are untrusted. The broker is a narrow protocol adapter,
not a policy or acceptance authority. The host schema gate and deterministic
proofreader remain the trusted egress boundary.

## Threats and controls

| Threat | Control |
|---|---|
| Provider key reaches model cell | Key is broker-only; cell environment and mounts are inspected before ledger consumption |
| Cell reaches general Internet | Cell joins only an internal network; only broker also joins an egress network |
| Broker becomes a general proxy | One method/path, exact provider/model, exact request hashes, no redirects, one-call counter |
| Model or prompt enables a tool | No tools are declared; cell contains no provider CLI/SDK; full output has no command authority |
| Prompt injection in request text | Request is labelled synthetic evidence; immutable system contract outranks it; output is schema/proofreader gated |
| Cross-model contamination | Byte-identical prompt; sequential teardown; no output or verdict enters the second prompt |
| Provider output or prompt leaks to evidence/logs | Raw values remain in memory; only hashes, sizes, fixed codes, and numeric usage persist |
| Schema-subset mismatch weakens safety | Common provider schema is only an early gate; the accepted full schema and proofreader remain mandatory |
| Retry or fallback spends new authority | Independent per-lane consumed ledger; broker rejects a second call; no fallback model |
| Terra failure biases Gemini | Ordinary cognition/provider failure does not enter Gemini context; only a fixed boundary-stop code can suppress Gemini |
| Cleanup residue crosses lanes | Terra containers, network, scratch, and image tags must be verified absent before Gemini starts |
| Credential absence consumes authority | Both credentials are checked before any ledger consumption or work-cell start |
| Wrong Gemini service is substituted | Exact `gemini-3.5-flash` Developer API endpoint is frozen; no Vertex or older-model substitution |
| Product or patient data enters provider | Build context is an allowlist containing only authored-synthetic fixtures and launcher sources; no repository mount |

## Residual risk

The broker container has ordinary outbound network capability even though its
source permits one exact HTTPS destination. This is acceptable only for this
repository-local rehearsal and is not production network-policy evidence.
Provider-side retention and billing are governed by provider service controls;
the request disables storage where supported, but provider billing records
remain authoritative. No result establishes clinical correctness, production
privacy, reliability, or provider suitability.
