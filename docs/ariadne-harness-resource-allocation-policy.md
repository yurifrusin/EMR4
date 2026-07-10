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

## Worker Pool Contract

The harness needs a machine-readable worker pool, not a hard-coded list of
providers. A pool entry records how a resource is reached, how many concurrent
instances the user permits, its preferred sub-model and reasoning setting, and
its current availability. Subscription-backed and API-backed workers are both
first-class resources.

```json
{
  "schema_version": "ariadne.worker_pool.v1",
  "workers": [
    {
      "resource_id": "gpt-terra-primary",
      "provider": "openai",
      "access_mode": "subscription",
      "default_model": "gpt-terra",
      "default_reasoning": "high",
      "max_instances": 1,
      "availability": "available",
      "capabilities": ["orchestration", "implementation", "review", "testing"],
      "cost_tier": "already_subscribed"
    },
    {
      "resource_id": "claude-review",
      "provider": "anthropic",
      "access_mode": "subscription",
      "default_model": "opus",
      "default_reasoning": "medium",
      "max_instances": 1,
      "availability": "quota_limited",
      "capabilities": ["architecture_review", "implementation_review", "testing"],
      "cost_tier": "limited_subscription"
    },
    {
      "resource_id": "deepseek-flash-workers",
      "provider": "deepseek",
      "access_mode": "api_key",
      "default_model": "deepseek-4-flash",
      "default_reasoning": "medium",
      "max_instances": 3,
      "availability": "available",
      "capabilities": ["implementation", "test_design", "adversarial_review"],
      "cost_tier": "low_api_cost"
    }
  ]
}
```

`default_model` may be Fable, Opus, Sonnet, GPT Terra, DeepSeek Flash, DeepSeek
Pro, or another provider-specific sub-model. `default_reasoning` is the normal
starting setting, not a guarantee: a sprint packet can request a different
approved setting and must record the effective choice. `max_instances` is a
user-controlled ceiling, so an inexpensive API worker can be parallelised while
a scarce subscription can remain single-instance.

## Ranked Role Preferences

Roles are obligations; ranked preferences are a per-project staffing policy.
Each role lists preferred resources and fallbacks rather than permanently
assigning one model to one duty.

```json
{
  "schema_version": "ariadne.role_preferences.v1",
  "roles": {
    "orchestrator": {
      "required": true,
      "preferences": ["gpt-terra-primary", "deepseek-pro-fallback"]
    },
    "architecture_reviewer": {
      "required": true,
      "preferences": ["claude-review", "gpt-terra-primary", "deepseek-flash-workers"]
    },
    "implementer": {
      "required": true,
      "preferences": ["gpt-terra-primary", "deepseek-flash-workers", "claude-review"]
    },
    "test_engineer": {
      "required": true,
      "preferences": ["deepseek-flash-workers", "gpt-terra-primary", "claude-review"]
    },
    "product_or_adversarial_reviewer": {
      "required": false,
      "preferences": ["antigravity", "claude-review", "deepseek-flash-workers"]
    }
  }
}
```

The allocator selects the first available resource that satisfies the packet's
capability, independence, instance-count, and cost constraints. If it chooses a
fallback, it must record why: quota exhausted, user cost cap, unavailable
subscription, concurrency ceiling, or insufficient declared capability.

## Generalist Edge Case

Every worker pool must contain at least one `generalist` profile. It can cover
all required SSDLC obligations when only one agent is available:

```json
{
  "role": "generalist",
  "covers": [
    "orchestrator",
    "architect",
    "implementer",
    "test_engineer",
    "security_reviewer",
    "code_reviewer",
    "docs_handover_auditor"
  ],
  "independence": "self_review",
  "red_boundary_clearance": "never_without_explicit_user_approval"
}
```

This is not a weakened SSDLC. The harness records that reviews are self-review,
requires the available deterministic checks, and cannot represent the result as
independent assurance.

## Default Allocation And User Amendment

At sprint intake the orchestrator should propose a staffing plan by:

1. Listing the SSDLC obligations required by the sprint's boundary and risk.
2. Filtering the pool by availability, permitted instance count, capability,
   cost tier, and packet authority.
3. Applying each role's preference order while preserving independent review
   where resources permit.
4. Falling back to the generalist profile only when necessary and labelling the
   reduced independence.
5. Presenting the selected assignments, fallbacks, and unfilled obligations as
   a compact plan that the user may amend.

The user can override any assignment, model, reasoning level, instance ceiling,
or cost cap. The orchestrator may make sensible default allocations inside the
approved mandate, but it must not treat a preferred worker as authority to
expand scope or bypass a missing role obligation.
