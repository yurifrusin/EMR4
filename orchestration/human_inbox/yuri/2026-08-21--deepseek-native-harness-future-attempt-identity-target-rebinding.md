# DeepSeek native Harness future-attempt identity and target rebinding — paired closeout

Date: 2026-08-21

Timestamp: 2026-08-21T23:08:25.7482343+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The future DeepSeek Harness package no longer carries the identity and file
address of a consumed failed attempt. The orchestrator can now issue it a new
machine-bound attempt identity and one harmless synthetic relative target, then
check that the runner, diagnostic helper, bundle and terminal all agree before
anything is allowed to start.

This is a small but significant control gain. A future DeepSeek process will
not be asked to remember which attempt it belongs to or which file is in scope;
those facts are now fixed by deterministic code, hashes and schemas. If any one
of them is abbreviated, partially replaced, freely renamed or made executable,
the preparation rejects before the worker exists.

## Technical summary

- Accepted task-branch source:
  `5f30c69d8cd0ad6f4c01f33b465fe7b541ef1f47`.
- Full frozen identity source:
  `deaf0b3ccc23adb2f2f17b275a6a7faa4d2ae2ac`.
- Exact inert target:
  `workspace/authored_synthetic_control_probe.py`.
- Rebound runner/helper hashes:
  `d025d1929f20589e86cbd66e983bda17435c1a21e937468532c38bb4895efb1a` /
  `7ff2630b1523c66bb9e0cb5d649879cfa97d0340b791a85255c7dc5ad1fb66fd`.
- Bundle and terminal identity, target and source bindings converge exactly.
- Completed verification: 53 focused, 187 accepted-chain and 548 governance
  tests; generator, Ruff, compilation, schemas and diff checks pass.

## Issue exposed and resolved

The first fresh receipt repeated a familiar clerical lapse by placing a Git
object value in prose that is reserved for the machine snapshot. The clockwork
rejected it before planning; the failed receipt was preserved and a distinct
corrected receipt passed. No implementation, provider or protected state was
affected.

I also advanced an intermediate checkpoint directly in the canonical latch,
even though the new clockwork is now its sole writer. The pre-closeout
comparison caught this before publication. The previous latch bytes were
restored, but the clockwork correctly required that restoration to exist in
the exact source commit rather than only the working tree. The closeout-paper
recovery commit now carries those prior bytes, while the candidate receipts
retain the progress reading; the clockwork will publish the accepted result
and next tranche atomically.

Finally, the first closeout intent used a remembered descriptive schema name
rather than the clockwork's exact current name. The read-only check rejected it
before running commands or writing canonical state. The failed intent is
preserved and a distinct corrected intent copies the live schema exactly.

That corrected content was initially offered under a versioned filename, while
the clockwork accepts only its exact canonical filename. It rejected this too
before reading content. The failed copy is preserved and the corrected intent
now occupies the one closed path.

The next read-only check exposed one further clockwork input dependency: the
intent named the prospective error-register revision, but I had expected the
clockwork to write its human revision note. It correctly rejected the missing
document before commands or canonical state. The exact prospective note is now
an explicit pre-check input, including the revision, total count and ordered
new incident identifiers.

## Deliberately closed

No Node, native Harness, broker, DeepSeek worker, model or provider ran. No
target file, occupied attempt, retry, fallback, product/configuration/API/
database change, ordinary-practice enablement, patient/appointment/clinical
data, production, deployment, release, Pages or protected-ref movement occurred.

## Place in Raisa and next tranche

The deterministic casing now owns both the future worker's identity and its
one-file boundary. The next tranche will exercise one provider-free native
stock-headless/HMR boot against this rebound package and require a typed
pre-request terminal plus independent broker-zero reading. Only after that
passes can we responsibly freeze a new occupied DeepSeek development attempt.
