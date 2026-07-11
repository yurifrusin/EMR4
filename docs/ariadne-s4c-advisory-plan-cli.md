# Ariadne S4c Advisory Plan CLI

Date: 2026-07-11

`scripts/ariadne_allocation_plan.py` converts committed S4 settings and an
explicit local JSON probe file into a deterministic allocation-plan report.

```powershell
.\.venv\Scripts\python.exe scripts\ariadne_allocation_plan.py `
  --sprint-id s4d-pilot `
  --probes tests\fixtures\ariadne_harness\s4c_normal_probes.json
```

The CLI does not discover availability, call an LLM or provider, launch an
agent, alter a worktree, inspect credentials, integrate, commit, or push. It
prints its JSON report by default; `--output <path>` writes only that requested
report artifact. The report carries the exact settings fingerprint, an advisory
Conductor plan if roles can be assigned, unfilled obligations, and the worker
mix constraints that a later Conductor plan must satisfy.

It is not a DeepSeek verifier result. `verifier_decision` is intentionally
`null`; S4d uses a human-invoked DeepSeek Flash review of the plan against the
same committed settings before any workers receive packets.

## Transport Evidence

`transport_adapters.yaml` declares how a resource is reached separately from
whether it is presently available. In the active EMR4 profile, DeepSeek Flash
is reached through the Deep Code interactive CLI. A real S4d probe must use
`method: deepcode_cli_observation` and record the observed result. The CLI
rejects a probe method not declared for that resource's transport adapter.
