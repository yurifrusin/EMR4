# Durability inert DDL alias-lock policy rebind

Date: 2026-08-09

Status: deterministic inert-artifact regeneration candidate; execution closed

The inert renderer now binds body contract
`sha256:9b57d9d28f216e494da91715fcf7dfc7f49c80bbbe836fe0c685cd1dd4929268`.
That body differs from its predecessor only by the structural parent digest;
all body programs are unchanged.

The regenerated inert SQL adds exactly one structural statement:
`pol_cf_02_update_lock`, whose `USING` is the exact producer binding and whose
`WITH CHECK` is that binding conjoined with literal `FALSE`. The artifact is
still unmounted, inert evidence only. No migration, database, product/patient,
provider, application/API/Diary, command, deployment, release or protected-ref
surface is opened.
