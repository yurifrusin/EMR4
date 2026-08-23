# Governance clockwork idempotent publication evidence preservation repair

Date: 2026-08-23

Timestamp: 2026-08-23T19:17:37.6365055+10:00 (Australia/Brisbane)

Result: `publication_evidence_preservation_pass`

## Lay result

The clock can now be read twice without erasing what happened the first time.
When the same accepted intent is published again, the original publication
evidence and report remain untouched. One separate machine JSON records that
the second action was only a readback.

The occupied proof preserved both publication hashes exactly and left the
clock at the same generation and lease. No verification command reran and no
canonical file moved.

## Technical result

- the already-published branch validates the existing publication JSON and
  report against operation, source, generation and publication disposition;
- missing, unreadable or mismatched evidence rejects before a readback write;
- one same-directory temporary file and atomic replace writes only the
  generated `clockwork-tick-idempotent-readback.json`;
- the ordinary/checkpoint prefix remains derived from the closed intent schema;
- the occupied parent evidence SHA-256 remained
  `e2b8fbf6c1beacecd086f210207fe97f0105cc2d7632001f638ddfa37e73641f`;
- the occupied parent report SHA-256 remained
  `f0c27dc2df8a81c265f6648ae2ab155994a4db23d510cd54b71902ef5f3c6131`;
- pointer, transaction, generation-manifest and latch hashes were unchanged;
- the generated readback records zero commands, zero publications, zero lease
  advance, lease 215 and the accepted generation; and
- five focused cases, all 54 clockwork-file tests, all 120 governance tests and
  Ruff pass.

One broader-test correction round was required. The semantic fixture still
copied a historical next-operation reading, which became already recorded when
the clock advanced. It now derives a non-published test-only successor from its
isolated latch. That is the same ergonomic lesson found in the matched review:
tests should assert invariant relations rather than freeze current readings.

## Ergonomic effect

The repair adds no operator field, document, decision, gate, ledger or control
layer. It adds exactly one generated JSON only when an operator asks for an
idempotent publish readback. The existing publication report remains the human
reading; the new JSON is machine evidence, not a second form to fill in.

## Next target

The next high-yield repair is a typed serial-continuation projection inside the
existing orchestrator preflight. It should derive the active latch, adapter
inventory, worker slots, five-source context and default declined-lane shapes
from a small intent, replacing repeated runtime-state paperwork rather than
adding another receipt layer.

## Boundaries

No DeepSeek, Gemini or native subagent ran. No provider, product source, data,
database, credential, environment, runtime, deployment, release, Pages,
protected evidence or protected ref was opened. Historical lost digests remain
lost and were not reconstructed.
