# Ariadne agent error and correction register — revision 215

Date: 2026-08-11

Revision 215 adds AER-0250 and AER-0251 and brings the register to 251 bounded
incidents. Both failures stopped before candidate adoption or external veto.

## AER-0250 — unconfigured DeepSeek observation method

The first post-compaction AES-C2 review receipt used descriptive method
`completed_transport_receipt` for the DeepSeek adapter. That value is not in the
active transport-adapter vocabulary, so the deterministic preflight returned
`revision_required`. The refused receipt is preserved. A distinct v2 receipt
uses exact configured method `deepseek_claude_cli_observation`, names all five
rehydration sources and passes without reasons.

## AER-0251 — simulated invocation bypass and open scenario packet

The first DeepSeek AES-C2 candidate at
`52f1dbb10fd6e616d3190aa896e60d8facf5897d` is rejected as untrusted. Its
malformed-result seam returned the override before calling the sole pure
adapter, then reported one invocation. Sol's instrumented probe observed one
reported and zero actual calls. A schema-valid supplied result could likewise
produce a released `simulated` result with zero actual calls, while an
undeclared scenario-packet field passed validation.

The worker closeout therefore also overstated total calls and completion of all
15 criteria, did not bind the exact candidate commit or all four protected refs,
and inaccurately said only the digest comparison observed the synthetic fixture
even though the frozen plan deliberately supplies it to the pure adapter.

The frozen plan permits one bounded same-lane mechanical revision. That revision
must call the pure adapter before observing the negative result fixture, reject
noncanonical or open scenario packets, instrument actual calls, regenerate
evidence and correct every affected closeout claim. Sol and fresh Gemini veto
remain pending, and no worker claim can accept the candidate.

## Boundary

No protected evidence, patient/clinical/product data, provider call, real
credential, runtime broker, real adapter, network, database/source, executable,
command, deployment, release, Pages or protected ref was opened. The original
494 untracked paths, including `docs/branding/`, remain preserved and excluded.
