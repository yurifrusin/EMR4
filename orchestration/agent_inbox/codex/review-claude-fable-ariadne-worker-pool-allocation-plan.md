# Claude Fable Worker-Pool Allocation Review

| Item | Value |
|---|---|
| Model evidence | Explicit `claude-fable-5` read-only consultation |
| Status | Consultant review preserved from local Claude plan artifact |
| Scope | Architecture only; no implementation, worker launch, or authority change |

## Verdict

Proceed, but do not build from the current illustrative pool directly. It
conflates transport, reachability, quota availability, capability, cost, and
authority, reproducing the assignment drift it is intended to solve.

## Required Corrections

- `transport` is a static trait (`cli_headless`, `bridge_subagent`,
  `filesystem_packet`, `manual`) with quirks; it is not availability.
- A timestamped `AvailabilityProbe` separately records reachability and quota
  state. Stale or unknown probes fail closed for allocation.
- Authority comes only from mandate plus worker packet, never a reachable CLI or
  bridge.
- Capability/role vocabulary must be a shared closed enum.
- Preferences are tiebreaks after capability, fresh probe, concurrency, cost,
  and independence filters. They need rationale and review dates to prevent
  provider stereotypes becoming policy.
- Independence is pairwise, computed from provider/account/resource, not a
  single worker label.
- User overrides require committed files with scope and expiry so they survive
  compaction.
- A fallback orchestrator requires a reduced autonomy profile, explicit
  substitution evidence, and a mandatory reversion checkpoint. It cannot widen
  its own authority.

## Proposed S4 Sequence

1. **S4a schemas and fixtures:** strict dataclasses for `WorkerResource`,
   `AvailabilityProbe`, `RolePreferencePolicy`, `AssignmentRecord`,
   `UserOverride`, and `GeneralistProfile`; files under
   `orchestration/harness_pool/`.
2. **S4b pure allocator and replay:** deterministic `allocate()` over supplied
   data. Replays include Claude quota exhaustion, Antigravity transport quirks,
   and DeepSeek Pro fallback-orchestrator reduced autonomy.
3. **S4c advisory CLI:** reads the data and proposes an allocation plan or
   `pause_required`; it does not launch or control workers.
4. **S4d manual EMR4 pilot:** use existing packet/submit workflow, compare the
   proposed allocation against actual staffing, and record drift metrics.

## Pilot Metrics And Gate

Track assignment match rate, fallback reasons, transport-misattribution count,
provider stereotype concentration, independence degradation, override survival,
probe staleness, and unfilled obligations. Go to adapter design only after at
least two pilots replay deterministically, honour overrides, label every
fallback/independence reduction, and report zero transport misattribution. Any
silent substitution, lost override, or non-deterministic replay is no-go.
