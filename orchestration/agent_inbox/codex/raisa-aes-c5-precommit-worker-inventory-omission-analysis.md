# AES-C5 precommit worker-inventory omission analysis

Date: 2026-08-11

The first Sol-recovery precommit runtime state supplied the complete five-source
rehydration and correctly stated that the DeepSeek implementation worker had
finished, but represented `worker_slots` as an empty list. The current Ariadne
settings require an explicit inventory row for `deepseek-flash-workers`, even
when it has zero active and zero stale instances. The orchestrator receipt
returned `revision_required` with
`worker_slot_inventory_missing:deepseek-flash-workers`.

The rejected receipt supplies no commit authority. No database, product route,
credential, cloud or provider action occurred. The corrected v2 state repeats
all five sources and adds the exact empty worker inventory before a fresh
receipt.
