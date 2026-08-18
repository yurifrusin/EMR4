# Ariadne agent-error and correction register — revision 552

Date: 2026-08-19
Timestamp: 2026-08-19T09:24:59.5481840+10:00 (Australia/Brisbane)

## Revision scope

Revision 552 preserves AER-0640. The first exact staging attempt failed closed before commit because eight register notes plus the repair plan and threat delta contained Markdown two-space hard breaks reported by `git diff --cached --check` as trailing whitespace.

The exact files now use ordinary line breaks. The register contains 640 incidents, all corrected or contained and none open. This is construction rerun eleven, separate from the zero-rerun steady-state replay.

Repair-only break-even remains two future closeouts at the measured nine-rerun avoidance rate. Cumulative break-even remains three closeouts.

## Prevention

New Markdown uses ordinary line breaks, and every exact staged candidate must pass `git diff --cached --check` before commit.
