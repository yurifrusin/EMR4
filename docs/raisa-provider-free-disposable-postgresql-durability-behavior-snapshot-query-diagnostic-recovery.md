# Provider-free behavior rehearsal snapshot-query diagnostic recovery

Date: 2026-08-08

Status: diagnostic candidate; runtime closed pending fresh veto

Behavior attempt 009 passed the recovered parent, catalogue, fixture and
privilege gates. Before the first scenario could be recorded, a read-only query
returned psql exit code 3. The inherited generic catalogue helper retained only
that exit code, so the evidence could not distinguish the exact bounded query
site or safe SQLSTATE.

The snapshot path now uses the same fixed read-only file transport through a
behavior-local bounded helper. On failure it may release only:

- fixed query id `scenario_snapshot`;
- one syntactically valid SQLSTATE when exactly one is present; and
- a digest of that closed metadata object.

No stderr prose, SQL value, row, identifier from data, or caller-selected input
can enter evidence. The query text and success behavior are unchanged. Another
runtime attempt is permitted only after deterministic hostile tests and a fresh
exact-HEAD independent veto pass.
