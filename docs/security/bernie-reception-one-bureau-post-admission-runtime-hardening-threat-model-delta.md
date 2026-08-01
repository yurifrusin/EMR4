# Reception One Bureau post-admission runtime hardening threat-model delta

Status: frozen provider-free delta
Recorded: 2026-07-31

## New risks

- A response from a different planner could be displayed under the user's
  current planner selection.
- A nominal `proposal_ready` response could display despite a non-admitted
  proofreader disposition.
- An impossible provider-call count or malformed audit reference could be
  presented as trusted provenance.
- Changing planner mode could leave the previous planner's proposal or
  provenance visible and encourage mistaken attribution.
- A fixture could be misrepresented as a fresh live provider result.

## Controls

- Bind every displayed proposal to the exact requested and returned planner.
- Require exact proofreader admission before binding identities or rendering
  proposal fields.
- Require zero calls for Standard and one call plus a bounded opaque audit
  reference for Isolated model.
- On planner change, discard the planner-scoped projection, proposal result and
  provenance before announcing the new selection.
- Preserve no raw prompt, provider response, hidden reasoning, credential,
  database identifier or unverified draft in client state or evidence.
- Label all new browser evidence `route_intercepted_browser`; retain earlier
  live-local and occupied evidence only by reference.

## Invariants

The deterministic proofreader and backend proposal adapter remain the sole
release boundary. The browser has no confirmation or write command. Standard
remains default, Isolated model remains explicit/default-off, and no fallback
or provider call is permitted in this tranche.
