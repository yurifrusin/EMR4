# Threat-model delta — unmounted status-confirm kernel adapter contract

Date: 2026-08-12

This tranche adds no runtime attack surface. Its threats are confused-deputy
client authority, cross-practice/actor evidence replay, missing session binding,
status/waiting-area union confusion, warning-acknowledgement smuggling, stale
state, terminal re-transition, digest ambiguity, success reconstruction and
duplicate delivery after an unknown client response.

Controls are server-owned authority/state inputs, exact signed-evidence binding,
closed status-only discrimination, exact warning sets, canonical JSON digesting,
effect-free terminal deferral, stored-receipt-only success/replay and hostile
mutation rejection. AER-0291 additionally requires exact non-protected search
allowlists. No cryptography, database, route, provider, network or command is
executed here.
