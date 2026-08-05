# Ariadne agent-error register revision 18

Date: 2026-08-05

Status: AER-0024 corrected before worker launch; no incident remains open

## AER-0024 C4 worker-dispatch runtime contract

The first C4 worker-dispatch runtime state used an intuitive but unsupported
DeepSeek adapter observation method and declared the assigned active worker
without its required workspace receipt. The deterministic receipt builder
returned `revision_required`, naming both
`adapter_probe_method_invalid:deepseek_via_claude_code_bare` and
`workspace_receipt_missing:model-required-bureau-c4-simulator-001`, and set
`worker_dispatch_permitted` false.

No DeepSeek/Claude Code transport, provider call, implementation edit, stage,
commit, push or ref movement followed that receipt. The exact worker worktree
remained clean at its source head.

The failed state and receipt remain preserved. A distinct runtime state chose
the exact allowed `synthetic_fixture` method from
`orchestration/harness_settings/transport_adapters.yaml` and supplied a complete
workspace receipt whose agent id matched the distinct assigned/active worker.
The corrected five-source receipt passed before launch.

AER-0024 is an orchestrator output-contract error, not a DeepSeek, Claude Code,
repository, harness or provider failure. The durable control is to copy adapter
methods from the transport settings and mechanically pair every assigned worker
with one complete workspace receipt before requesting dispatch.

Revision 18 contains 24 bounded incidents and no open incident.
