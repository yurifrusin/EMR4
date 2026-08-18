# Ariadne agent error and correction register — revision 397

Date: 2026-08-18

Status: accepted correction

## Revision

Revision 397 carries forward AER-0454 and AER-0455 and adds AER-0456 through
AER-0458.

AER-0456 records that the first actual sparse-worker provider-free container
used `DSH_TOOLS_MODE=local`, while pinned rc.7 admits only `native`, `code` or
`both`. Plugin validation stopped before credential resolution, broker or
provider traffic, model execution or candidate change. The already-preserved
passing container supplied exact `native`; the plan's one allowed fresh
provider-free corrected boot used that value and reached exact
`MISSING_CREDENTIAL`. The sparse worktree remained unchanged apart from its
pre-existing disposable worker packet.

AER-0457 preserves the first rejected worker pre-dispatch receipt. It used the
unrecognised lane disposition `selected` and predeclared the not-yet-started
worker as assigned without a handoff-current workspace receipt. The corrected
runtime uses exact disposition `planned` and leaves assignment and active-slot
state empty until process start.

AER-0458 records that the orchestrator reused output-limiting PowerShell
pipelines after AER-0455's one-command-per-process correction. The readbacks
were non-mutating, but a downstream pipeline command can mask the first
command's exit. All remaining shell calls use one executable command and no
pipe, semicolon or newline-composed successor.

## Population

- incidents: 458;
- corrected or explicitly contained: 458;
- open: 0;
- latest id: `AER-0458`.
