# Claude Fable Ariadne Worker Pool Allocation Review

Status: consultant review requested. Read-only; no implementation or live-agent
launch authority.

Review the Ariadne worker-pool and ranked-role proposal in:

- `docs/ariadne-harness-resource-allocation-policy.md`
- `docs/ariadne-multi-agent-ssdlc-harness-blueprint.md`
- `AGENTS.md`

The operating reality is deliberately heterogeneous: GPT Terra is normally the
orchestrator under an OpenAI subscription; Claude and Antigravity are available
through their CLIs but quota-limited; DeepSeek Flash/API workers are economical
and bridged locally; DeepSeek Pro may temporarily replace the orchestrator when
OpenAI capacity is unavailable. Transport differences have previously been
misread as capability or availability differences, causing assignment drift.

Provide an implementation plan for a portable, advisory-first worker-pool and
role allocator. Address:

1. Separate reachability/transport, availability/quota, capability, authority,
   cost, and independence as distinct observable fields.
2. Define the minimal schemas for worker pool, role preferences, assignment
   record, availability probe, and generalist fallback.
3. Specify deterministic allocation and failover rules that preserve user
   overrides and never infer authority from a reachable CLI or bridge.
4. Recommend a real EMR4 pilot using manual structured packets before any live
   harness adapter, including useful metrics for detecting allocation drift.
5. Identify flaws in the current proposal, especially the risk that role
   ranking hard-codes provider stereotypes or that a fallback orchestrator
   silently degrades assurance.

Hard boundaries: no live agent launch, harness git mutation, runtime wiring,
provider calls, database access, deployment, GUI, or automatic enforcement.
Do not assume Fable is a default worker; it is being used only for this
exceptional architecture checkpoint.
