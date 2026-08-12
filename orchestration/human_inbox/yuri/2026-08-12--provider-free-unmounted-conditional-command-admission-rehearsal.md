# Provider-free unmounted conditional-command admission rehearsal

Date: 2026-08-12

## Lay summary

The new referee's rulebook has now been rehearsed without touching a real game.
Thirty-seven synthetic cases prove that malformed tickets are stopped at the
gate, while valid tickets receive exactly one clear result: win, harmless
replay, stale view, schedule conflict, revoked authority, missing confirmation,
invalid action or reused retry key.

Only a winner is even described as planning a database change. The rehearsal
never performs that change. It also proves the important privacy ordering: a
person whose authority has been revoked is rejected before the system reveals
an old receipt, and an event cannot masquerade as either current truth or proof
that a command succeeded.

The next step is to draw the common backend doorway through which the four old
appointment routes and the newer proposal/confirm routes will eventually pass.
That remains a design exercise; no route is changing yet.

## Technical summary

- Accepted result:
  `raisa_provider_free_unmounted_conditional_command_admission_rehearsal_pass`.
- Exact source: `f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c`.
- 37 canonical cases; 19 structural admission rejections; all four operations
  and all eight outcomes represented.
- 32 hostile mutations fail closed.
- Create requires its schedule-domain fence; update/status/delete retain exact
  target and projected canonical-lock requirements.
- Current authority precedes replay disclosure; confirmation, replay,
  freshness, conflict and validation have a deterministic order.
- Only `committed` has `planned_mutation: true`; every case has
  `effect_performed: false`.
- 191 canonical repository tests, Ruff, 202-source compilation, Diary
  JavaScript syntax and Git whitespace pass.
- No model review was risk-triggered because no accepted architecture meaning
  changed and deterministic evidence was complete.
- No route, database/source, event, watcher, provider, patient/product data,
  command, deployment, Pages or protected ref was opened.
- Next: provider-free unmounted legacy-route convergence and common
  conditional-command kernel-interface design. Yuri's attention is not
  required.
