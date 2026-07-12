# Ariadne Cost Controls

The harness retains optional monetary budget controls for future API-metered or
public deployments. They are inactive in the current EMR4 profile because
Claude is accessed through a subscription whose practical usage window is not
reliably represented by per-call dollar estimates.

Fable remains the default Conductor. Estimated monetary cost is advisory and
cannot stop a call. The orchestrator must not pass a locally selected
`--max-budget-usd` value. Opus follows a provider-reported Fable limit. If the
Claude subscription cannot supply either model, DeepSeek 4 Pro runs through
Deep Code as temporary Conductor until Claude refills; a distinct GPT Sol
subagent remains fourth. None of these fallbacks receives integration authority.

Monetary enforcement can be activated later only through an explicit user
override. The generic CLI capability remains available; profile policy decides
whether it may be used.
