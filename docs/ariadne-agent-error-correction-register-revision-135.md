# Ariadne agent error and correction register revision 135

Date: 2026-08-09

Status: bounded dispatch-control correction candidate

Revision 135 adds AER-0160 and brings the register to 160 bounded incidents
with zero open incidents.

## AER-0160 — Antigravity launch after rejected dispatch receipt

The first interval-construction veto state incorrectly declared an external
Gemini verifier as an active assigned native worker without the corresponding
closed workspace receipt. Ariadne therefore returned `revision_required` with
`worker_dispatch_permitted: false`. Sol launched the verifier before reading
and enforcing that terminal status. The verifier made no edits, ran no Docker
or product surface and returned a technically clean pass, but that result is
inadmissible and grants no behavior execution.

This is a material recurrence of the worker-dispatch runtime-contract family,
related to AER-0153. The corrected v2 state keeps external verifier worktree
evidence separate, leaves native worker assignment empty, and must pass before
a fresh project/worktree review. More importantly, the Antigravity launcher now
requires an exact orchestrator-receipt path and rejects any receipt that lacks
the five rehydration sources, `status: passed`, or
`worker_dispatch_permitted: true` before it can invoke `agy`. The admitted
receipt SHA-256 is copied into the worker receipt.
