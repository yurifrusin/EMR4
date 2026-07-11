DECISION: pass

## D2 Final Contradiction Correction

### Change Made

Removed the contradictory exception in the Forced Cleanup Constraint section of
`docs/ariadne-deepcode-adapter-authority.md`.

### Before

The section declared that forced cleanup requires **both** a valid artifact
**and** a completed-turn signal (lines 94-102), then immediately introduced an
exception (lines 104-107) permitting forced cleanup when only an artifact exists
but the turn has not completed.

### After

The exception paragraph was replaced with a clean no-exception statement:

> There is no exception: forced cleanup is permitted only when both conditions
> are satisfied. If either condition is absent, the orchestrator must investigate
> before cleanup.

The summary table row was already correct (| Forced cleanup condition | Valid
artifact exists AND turn reports completion |) and required no change.

### Scope

- Only the Forced Cleanup Constraint section body was edited.
- No other sections, files, commands, commits, pushes, or dispatches were
  performed.

### Verification

- The contradictory exception paragraph is removed.
- The rule now has no exception: forced cleanup requires **both** a valid
  durable artifact **and** a completed-turn signal.
- All other corrected facts in the document are preserved.
