# Secure SDLC and Diary Hardening — Sol Recovery

Date: 2026-07-17

Original candidate: `604b3452787d45ad99d9f08e70101bfd87516671`

Recovered final candidate: `4efe9ff3363c3f563a03a1f5bd0978998ca55d07`

## Recovery authority

DeepSeek's blue lane self-passed the original candidate but missed a conceptual
fail-open: a manifest could mark itself non-material without Sol-owned
classification, and its acceptance evidence was neither hash-bound nor
candidate-bound. Under the Flash complexity rule, no correction loop was
opened. Sol preserved the review, rejected its acceptance conclusion, and
recovered under `docs/ariadne-orchestrator-recovery-lease.md`.

Gemini's independent red lane then returned `revision_required` on the same
original candidate. The following instance-preserving dispositions were used:

- SEC-RED-01: partially valid boundary ambiguity, overstated as critical.
  Empty host now enables the harness only for the `file:` protocol; `data:` and
  `blob:` cannot satisfy the gate. File-based local mock QA remains intentional.
- SEC-RED-02: pre-existing and impact-overstated because an attacker-origin
  copy has no canonical-origin token, but the weak ngrok substring was still
  hardened to approved domain suffixes.
- SEC-RED-03: valid; packet paths are repository-resolved before comparison.
- SEC-RED-04: valid; red and blue acceptance artifacts must resolve to distinct
  repository files.
- SEC-RED-05: valid; malformed unresolved-finding entries now fail closed.
- SEC-RED-06: valid; severity is validated canonically and case variants still
  block critical/high acceptance.
- SEC-RED-07: valid; cadence now derives from a hash-bound repository JSONL
  ledger rather than an unverified manifest integer.
- SEC-RED-08: intended behavior, not a defect. Remote ngrok smoke/dev controls
  are disabled by the explicitly authorized local-only capability policy.

Sol additionally constrained all review/recovery artifacts to the repository,
bound them by SHA-256, candidate head, and stated decision, required a
Sol-owned rationale for non-material classification, and required at least one
fresh independent exact-final-candidate pass whenever a prior lane is recovered.

The recovered candidate passes the executable plan gate, 44 focused Python
tests, Node syntax, and diff whitespace checks. It still requires a fresh
Gemini exact-candidate red veto and Sol purple synthesis before integration.
