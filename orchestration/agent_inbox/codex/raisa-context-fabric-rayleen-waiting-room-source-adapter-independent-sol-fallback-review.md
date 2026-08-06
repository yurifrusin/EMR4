# Independent fallback veto: Rayleen waiting-room source adapter

Date: 2026-08-06

Reviewer: fresh independent GPT Sol coding-agent context

Role: read-only veto review only; no implementation, acceptance, integration or
protected-ref authority

Candidate: `3edbe828fa1f261e59b8478db79d80e4c291cbbc`

Fallback basis: the bounded fresh Gemini 3.6 Flash/high Antigravity retry timed
out at expired OAuth before model admission. Repository policy explicitly
permits authentication/transport fallback. No reviewer decision was inferred
from the failed transport.

Decision: `revision_required`

## Material finding

The required closed adapter-result contract was absent. The file named
`adapter-result.schema.json` described the acceptance-evidence summary, and
both the generator and focused test validated that summary instead of the
`WaitingRoomSourceAdapterResult` and its nested source envelope, payload entries
and trace.

An in-memory adversarial probe added a patient-token-shaped property to the
source envelope and resealed the envelope/result. The unchanged parent
assembler and same-packet proofreader returned `RELEASE`; the projector merely
discarded the unknown field. A narrow grant also left fields in the
pre-projection source envelope that the final projector omitted. Thus the
candidate did not prove recursive output closure or a validated minimal
adapter-to-assembler handoff.

## Evidence reproduced

- Required HEAD before/after:
  `3edbe828fa1f261e59b8478db79d80e4c291cbbc`.
- Review worktree tracked-clean before/after.
- Focused adapter tests: 14/14 passed.
- Exact reconstructed nine-file A4/Context Fabric suite: 173/173 passed.
- Internal acceptance cases: 13/13 passed.
- Ruff and diff checks passed.
- Parent Current-weave artifacts remained byte-identical and hash-matched.
- Authority, expiry, aliases, missing-arrival handling and zero mounted
  route/watcher/provider/database/write surfaces otherwise held.
- Protected local/origin `master` and `handoff/current` remained
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The repair must add a true recursively closed adapter-result schema, validate
the full sealed result at the handoff, reject resealed nested additions before
assembly, separate the evidence-summary schema, and prove narrow-grant source
minimisation. A fresh exact-head independent review is required after repair.

`DECISION: revision_required`
