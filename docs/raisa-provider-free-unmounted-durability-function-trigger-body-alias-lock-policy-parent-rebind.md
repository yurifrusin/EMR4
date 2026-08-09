# Durability function/trigger body alias-lock policy parent rebind

Date: 2026-08-09

Status: deterministic parent rebind; body programs unchanged

The function/trigger body contract now binds structural parent
`sha256:00a4102ff0e884038e4a25f814dab84f5500b5e597058e30012b3a6d0be6514b`.
The only parent delta is `pol_cf_02_update_lock`: producer-scoped alias row-lock
visibility with a permanently false write check.

All typed body programs, predicates, failure identities, lock nodes, lock
ordinals, trigger programs, effect summaries, call graph and renderer order are
unchanged. In particular,
`project_update_confirm_reschedule_v1.p15` remains the exact alias
`LOCK_EXACT` node in `FOR_KEY_SHARE` mode. This rebind grants no renderer
invention, body-program change, direct DML, runtime, product/patient, provider,
command, deployment, release or protected-ref authority.
