# Status-confirm preflight idempotency expectation repair plan

Date: 2026-08-12

Status: frozen

Source HEAD: `97108ced05e5e7c31587cc24e325d55c566ba712`

## Scope

Correct only the stale assertions in
`tests/test_api_spine_status_confirm_idempotency_preflight.py` that still claim
the accepted update-confirm and delete-confirm routes lack `Idempotency-Key`.
Bind those assertions to the current route source, where create, update, status
and delete confirmation routes all use the accepted header and durable command
idempotency service.

The historical Sprint-136 preflight document remains unchanged as historical
evidence. No application, schema, migration or public contract may change.

## Acceptance

- the formerly failing test passes;
- the exact 125-check status-confirm lineage passes serially;
- the canonical 191-test profile and static checks remain green; and
- the diff contains only the test expectation, this plan and closeout evidence.

## Boundary

No route edit/call, database or product data, provider, credential, command,
deployment, release, Pages or protected-ref action is authorised. Preserve
`docs/branding/` and every unrelated untracked file.
