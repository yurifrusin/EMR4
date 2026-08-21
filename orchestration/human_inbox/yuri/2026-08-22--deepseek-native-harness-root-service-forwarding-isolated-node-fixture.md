# DeepSeek native Harness root-service isolated Node fixture

Date: 2026-08-22

Timestamp: 2026-08-22T09:52:21.2973747+10:00 (Australia/Brisbane)

## Lay summary

The corrected connection has now worked in real JavaScript, but inside the
smallest possible test box. One Node process called the synthetic preset
service exactly once with the right receiver and arguments. When the service
or its mount function was missing, both failures became the same small typed
terminal instead of leaking an opaque error.

The temporary JavaScript box was deleted before the result was accepted. No
DeepSeek worker, model, provider or native Harness ran.

## Technical summary

Exact implementation source
`4a99a8b5f9ee45210a635e8b18281ca5cf143695` produced
`isolated_node_fixture_pass`. The process envelope was written before stream
interpretation, with exit zero, 526 stdout bytes represented only by a digest,
zero stderr, a five-key value-free environment projection, one Node process
and complete root cleanup. The 24 focused tests and exact 126-test broader
collection passed.

Three local workflow incidents were corrected: a manually
expanded short Git identity was rejected before push, and one test incorrectly
forbade the sanitizer's legitimate content-free terminal constructor. A
manually composed closeout timestamp was also replaced by the exact clock
reading before validation. None wasted the single Node attempt or any
worker/provider resource.

## Place in Raisa and next work

This is a small but material control gain: the orchestrator has moved from a
static wiring proposal to an exact, reproducible behavioral reading while
keeping the native DeepSeek process closed.

Next is a package-unloaded guard–bridge–sanitizer module graph with authored
local stubs. It will test the next surrounding gear without yet loading the
runner, installed package, native Harness, worker, model or provider. Yuri's
attention is not required.
