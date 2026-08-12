# Ariadne agent error and correction register — revision 256

Date: 2026-08-12

Revision 256 records and corrects AER-0289. The register now contains 289
bounded known incidents with none open.

AER-0289 is a recurrence of the exact-source-binding lapse previously recorded
under `orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id`.
While drafting the conditional-command admission rehearsal closeout, Sol
expanded displayed short HEAD `f465d6a6` into a nonexistent forty-character
value instead of first capturing the full commit identity. The discrepancy was
caught before acceptance, staging, commit, publication or any external/runtime
action. Literal `git rev-parse HEAD` returned
`f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c`; that object was independently
verified as a commit and all three uncommitted draft occurrences were replaced.

The prevention rule remains unchanged: an abbreviated Git display is never a
completion task. Capture the full identity mechanically before drafting any
source-bound evidence, and copy only that captured value.
