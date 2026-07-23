# Ariadne Real-Isolation Rehearsal - Sol Acceptance

Date: 2026-07-23

Decision: `accepted`

Result: `ariadne_real_isolation_rehearsal_pass`

Reasoning level: High

## Authority finding

Yuri's fresh decision authorised the recorded disposable real-isolation
candidate. The implementation stayed within it: one local container, one
official digest-pinned base, one fixed allowlisted authored-synthetic workload,
no runtime network, no mounts, no secret and explicit scoped cleanup.

No model, provider, generated draft, product/database/event connection,
persistent mailbox, PII, protected/historical evidence, human action or command
was opened.

## Acceptance finding

Accept the result because:

1. plan, design and threat delta froze provenance, command, policy, evidence,
   collision and cleanup semantics before the real lifecycle;
2. registry and local inspection bound the official OCI index, exact
   `linux/amd64` manifest and source revision;
3. the temporary Docker context contained only 14 hash-bound synthetic files;
4. image and pre-start container inspection matched every frozen isolation and
   resource field;
5. the payload observed UID/GID 65532, loopback only and an `EROFS` write stop;
6. two in-container executions exactly reproduced the accepted 8-scenario,
   53-transition predecessor evidence;
7. the stopped container exited zero without OOM or engine error;
8. container, derived image, run-acquired base reference and temporary context
   were removed and read back absent; and
9. 28 focused and 177 combined tests, schema/semantic validation, Ruff,
   compilation, JSON and whitespace gates pass.

The protected-PR CodeQL no-effect comment on the structural protocol ellipsis
was repaired mechanically with `pass`; no lifecycle or authority semantics
changed.

## Claim boundary

This accepts one local effective-isolation rehearsal only. It is not evidence
of adaptive cognition, model safety, daemon or kernel invulnerability, live
authorization, persistence, product behaviour, production or autonomous
action. Possible Docker cache or unreferenced layer residue contains only the
official base and allowlisted authored-synthetic bundle; no daemon-wide prune
was authorised or performed.

## Next gate

Return the baton to Yuri. A bounded agent-admission design is the next smallest
candidate, but any generated draft, model selection/call/mount, provider
transport, networking, secret, writable/mounted input or adaptive container run
requires a new explicit decision.
