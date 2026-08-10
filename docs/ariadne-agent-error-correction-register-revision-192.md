# Ariadne Agent Error and Correction Register — Revision 192

Date: 2026-08-08

Revision 192 appends `AER-0221` through `AER-0223` without rewriting earlier
incidents.

- `AER-0221` records one PowerShell parse error in the first r170 worktree
  creation command. Git never ran. Separate path and branch checks then proved
  both targets absent and the corrected command created exactly r170 once.
- `AER-0222` records the fresh r170 verifier's clean-checkout discovery that
  the failure-042 diagnosis unconditionally required a deliberately untracked
  mutable behavior-evidence alias. Immutable evidence remains mandatory; the
  alias is now checked only when present, with positive absence and hostile
  wrong-present tests.
- `AER-0223` records the same review's Ruff format rejection of the touched
  register test that the orchestrator's hand-selected format list omitted. The
  exact changed Python set is now formatted and must pass before a fresh
  descendant review.

The rejected review remains immutable. It accepted every substantive
receipt-lock policy, parent, parse, scenario and authority-boundary challenge;
attempt 043 remains closed until a fresh exact-HEAD replacement veto passes.
