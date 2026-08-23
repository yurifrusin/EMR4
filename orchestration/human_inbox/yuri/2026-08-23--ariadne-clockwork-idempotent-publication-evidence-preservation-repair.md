# Yuri closeout — clockwork publication evidence preservation

Date: 2026-08-23

Timestamp: 2026-08-23T18:58:39.0105413+10:00 (Australia/Brisbane)

## Lay summary

The specific traceability defect is fixed. Taking the same publication reading
again no longer replaces the first evidence. The original evidence and report
kept exactly the same hashes, and one separate machine JSON recorded the
readback.

The clock itself did not move: no verification reran, no generation published,
no lease advanced and no canonical file changed.

## Technical summary

The CLI now verifies operation, source, generation and publication disposition
in both existing files before it writes a readback. Missing or mismatched
evidence rejects. The readback is one atomic generated JSON, not another form or
human report.

Five focused cases, all 54 clockwork-file tests, all 120 governance tests and
Ruff pass. One test-only correction removed another copied historical
next-operation constant and derived it from the isolated latch instead.

## Direction and boundaries

This clears the prerequisite for the largest measured ergonomic target: the
14 repeated continuation state/receipt files totalling 2,334 lines. The next
tranche will add a small typed input to the existing preflight and derive its
repository-known structure, replacing form filling rather than adding a layer.

No DeepSeek/Gemini/native worker, provider, product, data, deployment, release,
Pages or protected ref was used. Yuri's attention is not required.
