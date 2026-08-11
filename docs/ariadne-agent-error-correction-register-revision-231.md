# Ariadne agent error and correction register — revision 231

Date: 2026-08-11

Revision 231 adds AER-0266. The register now contains 266 bounded known
incidents.

## AER-0266 — completed worker omitted from explicit precommit inventory

The first AES-C5 Sol-recovery precommit runtime state used an empty
`worker_slots` list after the DeepSeek lease completed. Ariadne requires the
`deepseek-flash-workers` resource to remain explicitly inventoried with empty
active and stale instance lists. The receipt failed closed before staging.

The rejected state and receipt are preserved. The v2 attempt repeats the full
five-source rehydration and adds the exact empty inventory. No database,
product, credential, cloud or provider action occurred.
