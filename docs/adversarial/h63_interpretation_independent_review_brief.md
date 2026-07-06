# H63 Bernie Interpretation Harness Independent Review Brief

## Purpose

This brief is the handoff point for a bounded independent review of the
provider-free Bernie Interpretation Harness readiness/gate stack.

The recent H40-H62 work is substantial enough to deserve non-Ariadne scrutiny
before any later sprint proposes runtime route wiring, provider prompt/dry-run
wiring, memory/RAG/GraphRAG use, H15/H-series runtime imports, or historical
diary material access.

## Required Preflight

Run this command first:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

Expected current values:

- `runtime_or_provider_wiring_ready: false`
- `raw_trove_access_ready: false`
- `runtime_gate_decision: blocked`
- `sprint_engine_state: continuing`

If the command fails or any expected value changes, pause the sprint engine for explicit review before continuing.

## In Scope

- Review `app/services/bernie/interpretation_harness.py`.
- Review `scripts/bernie_interpretation_harness_report.py`.
- Review `scripts/bernie_interpretation_runtime_gate_check.py`.
- Review `scripts/bernie_interpretation_readiness_check.py`.
- Review the interpretation harness fixtures under
  `tests/fixtures/bernie_interpretation_harness/`.
- Review the readiness snapshot under
  `tests/fixtures/bernie_interpretation_readiness/`.
- Review the interpretation harness tests and protocol/release-gate docs.
- Produce a review artifact with findings, residual risks, and recommended
  follow-up tests or guardrails.

## Out of Scope

- Runtime route wiring.
- Frontend or taskpane changes.
- Provider prompts, provider dry-runs, live provider calls, or model selection.
- Database reads, database writes, migrations, or live patient matching.
- Memory, RAG, GraphRAG, or Access-AI wiring.
- H15/H-series runtime imports or profile consumption.
- Historical diary trove processing, raw diary reads, ignored local-data reads,
  filename inspection, timestamp inspection, or document text inspection.
- Any code change beyond a review artifact, unless Ariadne/Yuri explicitly
  opens a follow-up implementation sprint.

## Review Questions

1. Can any current report, readiness output, gate status, fixture, or document be
   mistaken for approval to wire runtime routes or providers?
2. Could production `app/` runtime code import or depend on interpretation
   harness tooling, fixtures, H15/H-series material, or ignored local payloads?
3. Are the projected-frame contracts strong enough to prevent confirmation
   bypass, invented live availability, route escalation, or payload leakage?
4. Are the release-gate and protocol-alert pause triggers sufficient before any
   future runtime/provider/trove proposal?
5. What additional tests should exist before a later sprint even drafts runtime
   or provider integration?

## Required Output

The reviewer should submit a source-safe review artifact only. It must not
include utterance text beyond already committed synthetic fixtures, raw diary
content, local paths under `local_data`, PHI, endpoint payloads, provider
prompts, or runtime wiring instructions.

Any recommendation to change `runtime_or_provider_wiring_ready`,
`raw_trove_access_ready`, or `runtime_gate_decision` requires Yuri approval and a
paused sprint engine.
