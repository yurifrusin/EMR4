# Threat-model delta — exact-digest historical-derived check-in adapter-test consumption

Date: 2026-08-24

Timestamp: 2026-08-24T13:42:27.9853208+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_before_fixture_read`

## New trust edge

One ignored, previously admitted local minimised structural fixture may cross
into one provider-free in-memory test of the unmounted check-in adapter. It may
cross no provider, network, archive, product, database, route, client, runtime,
configuration or ordinary-practice boundary.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| wrong or altered fixture | atomically consume the one-read lease, hash the same bytes before parsing, and require SHA-256 `2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe` |
| accidental repeated private read | prepare/consuming/complete local control; consuming is durable before open; no retry after consuming; recurring tests cannot receive the real path |
| archive fallback after fixture failure | archive paths and archive reads are absent from the executable interface; failure is terminal |
| source or adapter drift | require full 40-character ancestor bindings, exact candidate-gate blob `fe05df...f7f7`, exact current adapter blob `6955de...715b`, and all four protected refs at `2e34bd...d602` |
| derived identifiers become re-identification mappings | use one-way namespaced synthetic derivation only; never persist structural slot values, derived identifiers, keys or mappings |
| scenario context becomes command authority | independently require authenticated synthetic Receptionist/practice scope, idempotency claim, confirmation, signed evidence, freshness, current-state lock, reauthorisation, audit, event, commit and readback |
| waiting-area semantics broaden | use no waiting-area target and require before/after `null`; no area lookup occurs |
| event becomes command authority | invoke only the REST-command adapter; the patient-free committed event is an observed result after the effect/audit plan, never an actuator |
| private structure leaks into evidence | commit only accepted digests, aggregate counts, closed labels and test assertions; reject fixture rows, slot values, source text, paths, times, identifiers and mappings |
| external reviewer receives local material | no external worker dispatch; deterministic source, schema, state-machine and output checks own acceptance |
| crash creates ambiguous permission to rerun | `consuming` is terminal for retry purposes even when the fixture may not have been opened; ambiguity resolves to no retry |

## Residual risk and claim ceiling

This proves only that one exact, already minimised structural scenario can
exercise one existing local adapter composition while all command-authority
checks remain independent. It does not prove de-identification of the wider
trove, real-practice representativeness, route/database/runtime behaviour,
ordinary-practice readiness, clinical validity, production suitability or
safe future reuse. Authority is non-transitive.
