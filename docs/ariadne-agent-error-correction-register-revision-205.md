# Ariadne agent error and correction register — revision 205

Date: 2026-08-11

Revision 205 adds AER-0239 and brings the register to 239 bounded incidents.

## AER-0239 — revision predispatch state omitted required observations

The first deterministic preflight for the bounded AES-C1 blue revision refused
dispatch because the newly authored runtime-state packet omitted four adapter
observations required by the active Ariadne settings. It reported exact missing
observations for `codex_subagent_spawn`, `antigravity_cli_print`,
`deepcode_cli`, and `claude_cli_print`, with
`worker_dispatch_permitted: false`. No second DeepSeek call had started and the
candidate worktree remained clean and unchanged.

The state was corrected to include each required adapter explicitly, using
`unknown` reachability and bounded evidence where it was unselected or not yet
eligible. The same deterministic preflight then passed with no reasons and
`worker_dispatch_permitted: true` before the bounded revision was launched.

The earlier host wrapper timeout ultimately produced a normal DeepSeek
transport receipt and non-transferable closeout from its one surviving call;
ordinary local inspection-command mistakes and the blue defect found during
expected code review fall under the register's explicit exclusions. They are
therefore not misclassified as transport or reasoning incidents.
