# Provider-free governance clockwork prospective evidence and transaction-fact repair — closeout

Date: 2026-08-23

Timestamp: 2026-08-23T16:46:31.8267653+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed implementation source:
`86dc6652d154eaa6adc9ca97e7fa2b7e66d7323c`

## Lay outcome

The first ergonomic repair passes. Before the clock moves, it now reads every
prospective plan, closeout and acceptance header and returns all detectable
problems together in one typed response. A malformed packet cannot move the
pointer or change a governance record.

The CLI also takes its own transaction reading. It reports what this command
actually prepared, published, read back or rolled back, which lease it saw and
which generation it selected. We no longer ask the operator to remember or
reconstruct these facts, and the clock does not invent history it cannot know.

## Technical result

- three human-evidence categories are validated before projection and before
  canonical writes;
- path type, uniqueness, repository containment, Markdown shape, existence,
  Date, ISO Timestamp, Brisbane name/offset and calendar parity are checked;
- one hostile fixture returns ten ordered errors at once;
- a two-file build fixture returns four header defects in one rejection and
  proves canonical, metadata and pointer bytes unchanged;
- prospective rejection is typed `revision_required` JSON with zero
  publication and lease movement;
- dry preparation, rejected preparation, publication, idempotent readback and
  rollback have exact output-owned transaction facts;
- the current-Baton test reuses the production timestamp rule;
- an actual idempotent readback reported no new preparation, publication,
  rollback or lease advance at lease 212 with zero drift; and
- Ruff, byte compilation and all 108 governance tests pass.

The first full run exposed six test-only historical replay compatibility
defects. Their new acceptance fixture path did not satisfy the graph's existing
canonical acceptance-reference rule. The fixtures were corrected without
changing the production invariant; all six tests and the full suite pass.
One attempted six-test diagnosis used node selectors with the whole-file
provider-free runner, which correctly rejected that command shape. Direct
serial pytest supplied the diagnosis and the canonical whole-file run supplied
acceptance. No product or provider run was repeated.

After the Codex restart, the first restored-session receipt draft repeated two
Git objects in narrative evidence. The preflight rejected it before any
canonical change; the corrected receipt delegates all exact identities to the
machine snapshot and passes. AER-1128 preserves the recurrence. This lies
outside the first repair's prospective-header and transaction-fact target and
directly strengthens the next typed-builder priority.

## Matched ergonomics reading

The preceding packet's three rollback shapes are now controlled earlier or
owned by output: two missing-timestamp shapes become one prepublication error
set, and the publication counter is emitted by the CLI. This adds zero intent
field, operator input, approval, gate, ledger, required closeout document or
parallel control layer.

This closeout intentionally does not pre-author its own publication total. The
repaired clockwork tick evidence will be the authority for publication,
generation, lease and rollback facts after the pointer moves.

## Parallelism and Harness posture

DeepSeek was declined because the native profile remains paused, Claude Code is
not a fallback and the single-writer state is serial. Gemini was declined
because this is a provider-free exact deterministic control repair. Native
subagents were declined under developer policy. GPT Sol owned the candidate and
acceptance.

The three useful Harness/clock boundaries remain `prepared`, `terminal` and
`accepted_or_recovered`. This repair neither launches nor qualifies a worker
transport.

## Next tranche

Proceed under standing authority with
`ariadne-provider-free-governance-clockwork-typed-semantic-closeout-builder-and-command-registry-rehearsal`.
It will target the highest-yield remaining free-form command shapes, closed
labels, repository test paths and repeated human-evidence headers inside the
existing tick. It must show fewer required operator leaves without adding a
gate, document, approval or second control layer.

No Harness/provider, authority-allocation, product, check-in choice, data,
runtime, deployment, Pages or protected-ref authority opens.
