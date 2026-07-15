# Bernie LC4V4D3 Option A Decision

Date: 2026-07-15

Decision owner: Yuri

Decision: approved Option A — strict separated semantics.

The approved contract is:

- explicit alternatives are returned losslessly as clarification choices;
- corrected identities are resolved again before availability or proposal;
- an omitted practitioner requires clarification and cannot produce a
  practitioner-less appointment;
- utterance entity semantics remain independent of diary state;
- diary duplicate/conflict evidence is represented through a separate state
  relation and cannot silently mutate an `exact` surface entity to
  `mismatched`; and
- an explicit confirmation-bypass demand is refused before diary/action tool
  selection.

The six incompatible D1 expectations are not to be forced green. They require
a versioned D3 policy contract: one omitted-practitioner case and five diary
state-join cases. Frozen D1/D2 fixtures, reports, hashes, acceptance history,
and protected holdouts remain unchanged.

This decision authorizes an ordinary development-only D3 implementation and
evidence tranche. It does not authorize product runtime wiring, confirmation
writes, routes/APIs, providers, T3 activation, holdout use, historical diary
access, database/UI work, deployment, or release.
