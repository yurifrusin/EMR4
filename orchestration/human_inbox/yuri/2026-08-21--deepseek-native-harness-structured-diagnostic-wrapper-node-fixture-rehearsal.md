# DeepSeek Harness structured diagnostic wrapper Node rehearsal

Date: 2026-08-21

Timestamp: 2026-08-21T09:19:00.3227540+10:00 (Australia/Brisbane)

## Lay summary

The new diagnostic gear has now worked in the real Node runtime, not merely in
source inspection. Four deliberately failing local examples all preserved the
original failure. Three produced the exact small safe diagnostic we expected;
the fourth proved that an existing diagnostic file cannot be overwritten or
hide the original error. Nothing contacted DeepSeek or any provider, and all
temporary files were removed.

The first run usefully found a formatting mismatch: JavaScript wrote safe JSON
keys in construction order while our reader requires a canonical sorted order.
The narrowly allowed serializer correction fixed that, and the second run
passed. The first run remains preserved rather than rewritten.

This makes the harness work materially more promising: we now have evidence
that its early-failure diagnostic mechanism behaves correctly under Node. It
does not yet prove that the mechanism works around an actual native Harness
boot or that a DeepSeek worker can complete development reliably.

## Technical summary

- corrected source: `32dbd5233d114692d1913163ba62fc25e44a013f`;
- evidence binding: `3ed856dac63bf0e51312e2b3dee14bdc2c934daf`;
- attempt 002: 4/4 identical rejections, 3/3 canonical safe sidecars, one
  unchanged pre-existing sidecar, zero stdout/stderr bytes and complete cleanup;
- Node/Harness/broker/worker/model/provider counts: `4/0/0/0/0/0`;
- 116 focused tests plus Ruff, compilation and whitespace validation pass; and
- five bounded workflow/implementation observations are corrected and closed.

## Deliberately closed

No DSH import, native Harness process, worker session, model/provider request,
occupied retry, product or practice change, patient/clinical data, production
runtime, deployment, release, Pages or protected-ref movement occurred.

## Place in the wider work

The clockwork now has a tested safe gear for converting an otherwise opaque
early JavaScript failure into a canonical diagnostic reading. The next narrow
step is to connect that gear around exactly one provider-free pinned native
Harness boot, still before any worker, prompt, tool or provider activity.

Yuri's attention is not required; this is the dependency-satisfied course under
the standing uninterrupted-development authority.
