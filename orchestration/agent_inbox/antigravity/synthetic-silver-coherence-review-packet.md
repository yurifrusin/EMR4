# Synthetic Silver All-192 Coherence Audit — Independent Review Packet

Date: 2026-07-17

## Assignment

Review the exact Sol audit implementation and artifacts at source code head
`5649c9b1`. This is a fresh independent veto. Do not inherit Sol's acceptance
decision and do not modify the candidate implementation.

## Workspace and ownership

- worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-coherence-review`
- branch: `codex/review-synthetic-silver-coherence`
- source branch: `codex/synthetic-silver-coherence-audit`
- source code head under review: `5649c9b1`
- owned file:
  `orchestration/agent_inbox/antigravity/synthetic-silver-coherence-review.md`

Write and commit only the owned review file. Do not push any ref. You have no
integration, corpus-admission, acceptance, handoff, or protected-ref authority.

## Exact review surface

- `docs/bernie-synthetic-silver-coherence-audit-contract.md`
- `app/services/bernie/synthetic_noise_coherence.py`
- `scripts/bernie_synthetic_silver_coherence_audit.py`
- `tests/test_bernie_synthetic_silver_coherence_contract.py`
- `tests/test_bernie_synthetic_silver_coherence.py`
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`
- `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- `tests/fixtures/bernie_synthetic_noise/admission.json`
- `tests/fixtures/bernie_synthetic_noise/candidates_sol_coherent.jsonl`
- `tests/fixtures/bernie_synthetic_noise/admission_coherent.json`
- `docs/bernie-synthetic-silver-coherence-audit-pre-repair.json`
- `docs/bernie-synthetic-silver-coherence-audit-final.json`
- `docs/bernie-synthetic-silver-coherence-accepted-robustness.json`

The original candidate, seed, and admission files are ordinary-development
Silver evidence. Do not inspect any protected fixture, support module,
manifest, seal, receipt, per-case report, or path. Do not run broad discovery
commands that could enumerate protected paths.

## Required independent checks

1. Verify the three frozen Git blobs, original canonical candidate hash, and
   192-row original admission binding.
2. Decide independently whether the fail-closed classifications are justified:
   - a clarification tool with no clarification contract and with a success
     outcome or mutation delta is internally contradictory;
   - mutation tools without a corresponding outcome and delta are replay-
     contract contradictions;
   - `existing_booking_found` with a creation delta is contradictory; and
   - a dialogue that withdraws the whole action is incompatible with an oracle
     that still expects that action to execute.
3. Confirm the pre-repair audit covers 192/192 without product-parser output
   influencing admission decisions.
4. Confirm Sol changes exactly the candidate-text defects it claims: eight
   resize surfaces receive an explicit resize statement and four schedule-
   anaphora surfaces replace an appointment referent with a diary-request
   referent. IDs, seed hashes, evidence coordinates, provenance, authority,
   and every frozen semantic oracle remain unchanged.
5. Reproduce the final counts: accept 90, quarantine 102, reject 0; confirm
   every accepted row has decision `accept_coherent` and every other row is
   explicitly bound in the quarantine admission.
6. Reproduce exact hashes:
   - pre report:
     `sha256:616f6180108776991096f4e90d5454a99aa313471fe97591d6d527175b17c79a`;
   - final report:
     `sha256:4e2f3a5dd3632a8d5f927a2d42a203a909673d89d6406ded886eb37bbbfabd80`;
   - repaired candidate:
     `sha256:4ac2b4705a49b9f394351ce523808e9c6b06c8cabd9cc2f4b1f6db6b5fe116f8`;
   - admission:
     `sha256:55b5c968fa066fc0830e9c80781b0ded1e13520b6f206a41fee9dd0e027687cd`;
   - accepted-population robustness:
     `sha256:040a661d0b2f14ee1d8e4b15dd151aa9af09fa09960e1984164106a6f6ba58c2`.
7. Reproduce accepted-population evaluation: 90 candidates, 180 observations,
   4/90 complete, safety 180/180, and zero variance.
8. Run serially with the integration virtual environment:
   `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_coherence_audit.py --check`
   and
   `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_synthetic_silver_coherence.py tests\test_bernie_synthetic_silver_coherence_contract.py tests\test_bernie_synthetic_noise_corpus.py tests\test_bernie_synthetic_noise_sol_recovery.py`.
9. Verify `git diff --check`, no product parser/policy/replay/scorer change, and
   `PROTECTED_ACCESS: false`.

## Durable decision format

End the review with exactly these lines:

```text
DECISION: pass|revision_required
SOURCE_HEAD: 5649c9b1
PRE_ACCEPT: <n>/192
FINAL_ACCEPT: <n>/192
FINAL_QUARANTINE: <n>/192
ACCEPTED_ROBUSTNESS_COMPLETE: <n>/<n>
SAFETY_PASS: <n>/<n>
VARIANCE: <n>
PROTECTED_ACCESS: false
```

If `revision_required`, state each exact conceptual or mechanical blocker above
the decision block. Do not repair it.

