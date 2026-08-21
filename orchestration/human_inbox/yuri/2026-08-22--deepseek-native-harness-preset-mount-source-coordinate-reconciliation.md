# DeepSeek native Harness preset-mount source reconciliation — paired closeout

Date: 2026-08-22

Timestamp: 2026-08-22T04:50:32.7098461+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

We have now converted the Harness's “preset mount failed” result into a small
map of the only six internal places supported by the exact installed source.
This did not consume another Harness attempt: it was the equivalent of reading
the gearbox drawing and marking every remaining place where the gear train can
stop.

The useful finding is that both preset rows ask only for four services and the
host configuration declares all four. That does not prove they were visible at
runtime, but it removes a broad “the preset asks for something the Harness
never supplies” explanation. The exact stop remains deliberately unclaimed.

The next tranche builds a pure translator that can inspect the exception in
memory and emit only one safe code, discarding its path-bearing text. It will be
tested with synthetic errors in Node without starting the Harness.

## Technical summary

- Exact source: `2c0e24e6b59263129ec59e948f17a18203015b67`.
- Eight exact source/manifest SHA-256 bindings and four rc.7 versions pass.
- Eleven mount-state source anchors pass.
- Preset injections: `tools`, `fs`, `systemPrompt`, `subprocess`; all four are
  declared in the pinned host composition.
- Remaining source candidates: six, schema-closed.
- Native Harness/process downstream counters: all zero.
- Exact internal cause, raw error and repair: unobserved/absent/none.
- Nine focused and six immutable-evidence tests pass with static checks.

## Issue resolved

The first reader used the npm-cache location by analogy instead of the
accepted package-seed location. It failed closed before reading source or
writing evidence. AER-0879 binds the corrected `.cache` seed root.

## Deliberately closed and place in Raisa

No worker, model, provider, target, product/data, ordinary-practice,
production, deployment, release, Pages or protected-ref action opened. This is
another gear in the orchestrator-control chain: source layout is now a typed
input to the next safe runtime terminal rather than an informal debugging
guess. Work continues under standing authority; Yuri's attention is not
required.
