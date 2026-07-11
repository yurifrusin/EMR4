# Ariadne S4b Pure Allocator

Date: 2026-07-11

S4b is a deterministic, advisory-only allocator. It consumes only committed
S4a settings and caller-supplied `AvailabilityProbe` records. It makes no CLI,
network, provider, quota, filesystem-write, worktree, credential, sandbox, or
agent-launch call.

For each ranked required role, it selects the first resource that is both
declared capable and represented by a reachable, available probe, while
respecting its declared instance ceiling. If ordinary preference selection
cannot cover a role, the declared generalist may cover it. That fallback is
explicitly labelled `self_review` and `generalist_fallback_required`; it is not
reported as independent assurance. If no eligible resource exists, the role is
returned as an unfilled obligation.

The authored fixture replay exercises two situations: the normal three-resource
pool and a constrained one-resource generalist fallback. It proves that the
same inputs generate the same allocation and that the orchestrator-substitution
flag is always false. It does not yet produce a Conductor plan artifact,
calculate a settings fingerprint, evaluate user overrides, use real probes, or
dispatch workers. Those are separate future, explicitly approved slices.
