# Ariadne Secure SDLC Red/Blue/Purple Protocol

Date: 2026-07-17

This protocol turns EMR4's per-sprint security review into an executable
Ariadne gate. It supplements deterministic tests and scanners; it does not
replace them or grant a worker authority over protected integration.

## Review levels

Every material sprint supplies the structured security delta defined in
`orchestration/harness_settings/security_review_protocol.yaml`: assets/data,
trust boundaries, attacker inputs, dangerous capabilities, abuse cases,
controls, verification, and residual-risk ownership.

Materiality is itself an authority decision, not a worker-controlled boolean.
Even a non-material classification must be Sol-owned, justified, and free of
configured security triggers; otherwise the gate returns `revision_required`.

Routine material work receives that delta and deterministic checks. A sprint
with any configured security-sensitive trigger receives two independent lanes:

- **Blue** reviews defensive controls, implements/tests only its bounded packet,
  and tries nearby bypasses from the defender's perspective.
- **Red** receives a fresh context, the frozen candidate and threat inputs, but
  not the blue artifact or its acceptance framing. It attempts adversarial
  bypass and returns reproducible evidence.

Sol performs **purple** synthesis when four material sprints have elapsed since
the last synthesis, whenever a configured cross-layer/exposure trigger applies,
or before deployment/release. Purple synthesis reconciles disagreement,
reruns checks, owns residual-risk decisions, and is the only security acceptance
surface. A critical or high unresolved issue makes acceptance fail closed.

Every accepted review artifact is constrained to the repository, SHA-256
bound, and checked for the exact candidate head and decision. If a worker
self-passes a conceptually defective candidate, Sol may recover it only under
the Ariadne recovery lease: the original artifact and a bound recovery record
are preserved, and at least one fresh independent lane plus purple synthesis
must pass the final candidate exactly.

## Worker allocation

DeepSeek V4 Flash/high through Claude Code `--bare` is the preferred economical
blue lane for bounded controls and tests. Gemini 3.5 Flash through a fresh
Antigravity project is the preferred red lane. Roles are capabilities, not
model identities: substitutions must preserve fresh context, asymmetric
packets, bounded ownership, and separation from protected integration.

Neither lane may read the other's artifact, certify itself, alter scope,
integrate, commit `master`, push protected refs, dismiss a scanner finding, or
change an external security setting. Sol retains all adjudication and GitHub
authority.

## Gate use

Run the plan gate before dispatch:

```powershell
.\.venv\Scripts\python.exe scripts\ariadne_security_review_gate.py `
  --manifest <sprint-security-manifest.json> --phase plan
```

After review artifacts are integrated and the manifest records decisions, run
the acceptance gate:

```powershell
.\.venv\Scripts\python.exe scripts\ariadne_security_review_gate.py `
  --manifest <sprint-security-manifest.json> --phase acceptance
```

Both receipts are durable sprint evidence. Missing delta fields, unknown
triggers, missing/overlapping packets, stale red context, overdue purple
synthesis, absent artifacts, non-pass decisions, or unresolved critical/high
findings return `revision_required`.

## Packet asymmetry

Blue receives the expected invariants, preservation contract, candidate diff,
and defensive test surface. Red receives trust boundaries, attacker-controlled
inputs, candidate diff, and explicit malicious objectives. Red does not receive
blue conclusions, expected acceptance language, or instructions to confirm a
particular control. Purple receives both only after their decisions are frozen.

## Cadence and proportionality

This does not create ceremonial model calls for tiny edits. Non-material work
is classified as such; routine material work carries the security delta without
mandatory LLM review. Dual review is triggered by the configured security
surfaces, and purple review is tranche/cadence based. Human penetration testing
remains required before production or external patient exposure; model workers
are additional variance reduction, not a substitute.
