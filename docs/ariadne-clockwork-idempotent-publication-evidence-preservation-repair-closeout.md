# Governance clockwork idempotent publication evidence preservation repair — closeout

Date: 2026-08-23

Timestamp: 2026-08-23T18:58:39.0105413+10:00 (Australia/Brisbane)

Status: `accepted_pending_semantic_publication`

Exact reviewed implementation source:
`0033e48b3c9bbd8e597dbb3fc9473dce60c1fb3b`

## Lay outcome

The clock can now take a second reading without replacing the first. The
accepted parent publication's evidence and human report kept exactly the same
hashes, while one generated JSON recorded that the repeat was only a readback.

No test command reran, no generation published, no lease advanced and no
canonical file changed.

## Technical outcome

- the CLI authenticates the existing publication pair before readback;
- missing, unreadable or mismatched evidence rejects before output;
- the original JSON and Markdown are never write targets in the readback path;
- one generated JSON is written atomically;
- ordinary and checkpoint names remain closed by intent schema;
- five focused tests, 54 clockwork-file tests, 120 full governance tests and
  Ruff pass; and
- the occupied proof retains lease 215, zero drift and the accepted generation.

One test-only correction derived the fixture successor from its isolated latch
instead of copying a historical current operation. It changed no production
behavior and reinforces the wider rule that moving readings belong behind the
clock face, not in permanent test constants.

## Ergonomic effect and next work

The repair adds zero operator fields, forms, reports, gates, ledgers or control
layers. Its sole new artifact is generated machine evidence.

Proceed under standing authority with
`ariadne-provider-free-governance-clockwork-typed-serial-continuation-state-projection-rehearsal`.
It will derive repeated runtime-state structure inside the existing preflight,
measured against the observed 14 files / 2,334 lines.

No Harness/provider, authority-allocation, product, data, runtime, deployment,
release, Pages, protected-evidence or protected-ref authority opens.
