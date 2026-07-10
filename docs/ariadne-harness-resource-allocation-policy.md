# Ariadne Harness Resource Allocation Policy

Date: 2026-07-10

The harness controls authority and evidence, not a fixed hierarchy of model
brands. It must work when the user has abundant access to one provider, small
and intermittent access to others, and inexpensive API workers.

## Operating Rule

Assign the cheapest currently available resource that can meet the task packet's
required capability, evidence, and independence level. Record the assignment
and any reduced independence in closeout evidence.

| Need | Normal allocation | Fallback |
|---|---|---|
| Orchestration and integration | GPT Terra | DeepSeek 4 Pro after context rehydration |
| Ordinary design or code review | Claude Opus at medium reasoning, or Sonnet | GPT/DeepSeek review with reduced-independence label |
| Exceptional architecture checkpoint | Claude Fable | Explicitly justified alternative review mix |
| Parallel bounded implementation or tests | GPT worker, Antigravity, or DeepSeek 4 Flash | Any available bounded worker |
| Product, UX, adversarial, or domain review | Antigravity, Claude, GPT, or DeepSeek according to packet | Any available reviewer with the limitation recorded |

The table is illustrative, not a permanent routing rule. Antigravity is not a
UX-only agent. DeepSeek is not globally retired. The earlier removal of an
unused local DeepSeek worker configuration applies only to that obsolete local
setup; it does not prevent a new explicitly enabled DeepSeek packet.

## Non-Negotiable Controls

- The orchestrator must rehydrate from the committed mandate, checkpoint,
  evidence ledger, and git state after a model or session change.
- The mandate and deterministic boundary policy remain authoritative regardless
  of which model fills the orchestrator role.
- A worker packet states role, scope, authority, forbidden actions, required
  output, and verification evidence.
- Resource scarcity may reduce independence; it may not erase an SSDLC duty or
  self-authorize a boundary crossing.
- Fable use requires a leverage reason. It is not the default cost of running a
  sprint.

This policy is advisory documentation only. It does not activate a live worker
adapter or grant any worker git, runtime, provider, database, deployment, or
release authority.
