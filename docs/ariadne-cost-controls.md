# Ariadne Cost Controls

The harness retains optional monetary budget controls for future API-metered or
public deployments. They are inactive in the current EMR4 profile because
Claude is accessed through a subscription whose practical usage window is not
reliably represented by per-call dollar estimates.

Fable remains the default Conductor. Estimated monetary cost is advisory and
cannot stop a call. The orchestrator must not pass a locally selected
`--max-budget-usd` value. Opus becomes Conductor only after a provider-reported
Fable usage/window limit, model unavailability, or authenticated transport
failure after bounded retry. GPT Sol remains the third, distinct-subagent
fallback.

Monetary enforcement can be activated later only through an explicit user
override. The generic CLI capability remains available; profile policy decides
whether it may be used.
