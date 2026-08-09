# Ariadne agent error and correction register revision 129

Date: 2026-08-09

Status: bounded register correction candidate

Revision 129 adds AER-0154 and brings the register to 154 bounded incidents
with zero open incidents.

## AER-0154 — wrong observation method for the native-subagent adapter

The first postcompaction runtime state correctly identified the separately
authorised read-only codebase-health researcher, but labelled the
`codex_subagent_spawn` observation with `codex_session_observation`. That
method belongs only to the primary-session adapter. The deterministic Ariadne
preflight returned `revision_required` with
`adapter_probe_method_invalid:codex_subagent_spawn`, set
`worker_dispatch_permitted` false and preceded any diagnosis or database
runtime.

The failed state and receipt remain immutable. A distinct corrected state uses
the exact `codex_subagent_observation` method copied from
`transport_adapters.yaml`, preserves all five rehydration sources and leaves
the research consultation outside Sol's serial database authority. This is a
recurrence of the worker-dispatch runtime-contract family, not a subagent or
model failure.
