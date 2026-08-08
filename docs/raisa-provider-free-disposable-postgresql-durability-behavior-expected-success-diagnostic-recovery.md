# Provider-free behavior expected-success diagnostic recovery

Date: 2026-08-08

Status: deterministic repair candidate; runtime closed pending fresh veto

Attempt 011 established that the repaired scenario snapshot succeeds. The
first expected-success transaction was then rejected before any scenario was
admitted, and the run proved complete exact-container cleanup. The previous
failure branch did not retain the fixed scenario identifier or one safe
SQLSTATE.

The bounded failure path now emits only the current contract-defined scenario
id, one unambiguous valid SQLSTATE when available and a digest of that closed
metadata. The evidence schema enumerates the exact twenty scenario ids. No
stderr prose, SQL text, query values or database rows can be released. This
change grants authority only for a newly reviewed single diagnostic rehearsal.
