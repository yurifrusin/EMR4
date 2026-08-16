# Delete-confirm behavior/transaction final-attempt stop

Date: 2026-08-16

Timestamp: 2026-08-16T13:47:28.7257954+10:00 (Australia/Brisbane)

Status: `blocked_after_consumed_attempt_budget`

## Lay summary

The authority-counter repair worked: the single final rehearsal moved beyond
the earlier TX-S06 failure and reached the ninth transaction family. It then
stopped safely on a different bookkeeping error in the rehearsal itself. The
test harness had constructed candidate response bytes inside a transaction and
mistook those local bytes for a response released to a caller after the
transaction correctly rejected and rolled back an incomplete write set.

Nothing escaped. The transaction rolled back, the relay stopped, the disposable
PostgreSQL container and internal network were removed, and no product data,
route or provider was opened. The tranche is not accepted and Gemini was not
called. The one attempt Yuri authorized has been consumed, so work is paused for
his decision rather than quietly creating another retry.

## Technical summary

- Exact preexecution source: `31fcedf48e81bc896cc5ea9ab5ab7312a77f4768`.
- Deterministic admission before runtime: 37 focused passes, one intentional
  runtime skip, Ruff, no-write compilation, schema/whitespace gates and the
  canonical 196-test profile.
- Occupied result: `rehearsal_failed` at
  `transaction/TX-S09_disclosed_bytes` with the empty-detail SHA-256.
- AER-0353's semantic authority-call counter is verified by progression beyond
  TX-S06. AER-0355 records the distinct candidate-versus-release accounting
  defect. AER-0354 separately preserves the corrected preexecution Git-hash
  metadata defect.
- Cleanup evidence and a fresh label-filtered Docker inspection both prove no
  owned container or network remains.
- No Gemini review ran because occupied evidence did not pass.

## Deliberately closed surfaces

No further repair or database attempt, mounted route, public API/GraphQL/UI,
product/patient/clinical data, provider/ADC/credential/IAM, external network,
deployment, production, release, Pages or protected-ref movement is authorized.
All unrelated untracked files, including `docs/branding/`, remain preserved.

## Decision required

Yuri's attention is required only to decide whether to authorize a new narrow
recovery that separates candidate bytes from externally released bytes, adds
focused rollback/abort release tests and defines one fresh occupied-attempt
budget, or to leave this rehearsal stopped.
