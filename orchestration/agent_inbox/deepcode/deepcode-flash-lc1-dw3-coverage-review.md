# Task Packet: LC1 DW3 — Independent Review + Coverage Sweep

Role: DeepSeek Flash Worker (independent review/veto)
Model: `deepseek-v4-flash` / high
Branch: `codex/lc1-dw3-coverage-review`
Source Plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation-v2.md`
Depends On: DW1 (`codex/lc1-dw1-temporal-foundation`), DW2 (`codex/lc1-dw2-scenario-contract`)

## Mission

Perform an independent verification sweep over the integrated DW1 and DW2
artifacts. Run every deterministic acceptance check. Report pass/fail with
specific failure evidence. Produce a review artifact. This is a read-only
review lane — do not modify any project code.

## Boundary

- Do NOT touch any `app/` code, scenario fixtures, temporal module,
  routes, schemas, or migrations.
- Only file created: the review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-lc1-dw3-coverage-review.md`.
- This is veto/adversarial evidence, not corpus authority.

## Procedure

### 1. Environment Setup

Check out this branch in a disposable worktree from the integrated DW1+DW2
baseline. Verify Python and test tooling are available:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe --version
C:\Program Files\nodejs\node.exe --version
```

### 2. Run DW1 Acceptance Checks

Execute every check in the DW1 acceptance section of the V2 plan:

```powershell
# DW1-2: `at` operator sets both earliest and latest + temporal_relation
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3pm duration 15" \
  --provider fake \
  --reference-date 2026-07-14 \
  --json

# DW1-3: Time-form variants
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3 pm duration 15" \
  --provider fake --reference-date 2026-07-14 --json

C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3.00pm duration 15" \
  --provider fake --reference-date 2026-07-14 --json

C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 15:00 duration 15" \
  --provider fake --reference-date 2026-07-14 --json

# DW1-4: Existing operators still work
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" \
  --provider fake --reference-date 2026-07-14 --json

# DW1-5: Approximate operator
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow around 3pm duration 15" \
  --provider fake --reference-date 2026-07-14 --json

# DW1-6: Unspecified
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow 3pm duration 15" \
  --provider fake --reference-date 2026-07-14 --json

# DW1-7: All temporal tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_temporal_policy.py -q

# DW1-8: All existing smoke tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py -q
```

### 3. Run DW2 Acceptance Checks

```powershell
# DW2-9: Scenario spec contract validates
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q

# DW2-10: Adapted T1/T2 seeds pass contract validation
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "seed"

# DW2-11: Normalizer preserves original utterance
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "normalize"

# DW2-12: Coverage lattice emits valid JSON with explicit empty cells
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_coverage_lattice.py

# DW2-13: Coverage report tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_coverage_lattice.py -q
```

### 4. Run T3 Preservation Checks

```powershell
# T3.1-T3.4 infrastructure unchanged
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_shadow_eval_contract.py tests\test_bernie_shadow_corpus.py tests\test_bernie_shadow_runner.py tests\test_bernie_shadow_live_gate.py -q
```

### 5. Run Readiness Gate Check

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
# Expected: runtime_or_provider_wiring_ready=false, raw_trove_access_ready=false, runtime_gate_decision=blocked
```

### 6. Verify Specific Claims

For each claim below, record pass/fail with the exact command output as evidence:

| # | Claim | How to verify |
|---|---|---|
| C1 | `at 3pm` produces `earliest_time=15:00`, NOT `None` | Smoke script output |
| C2 | `at 3pm` produces `temporal_relation=exact` | Smoke script JSON output |
| C3 | `at 3pm` NO LONGER produces `earliest_time=null, latest_time=null` | Smoke script output |
| C4 | `TemporalRelationKind` has all six values: `exact`, `not_before`, `not_after`, `interval`, `approximate`, `unspecified` | Read the literal definition in `app/services/diary/temporal.py` |
| C5 | `SlotSearchCommandIn` has `temporal_relation: Optional[str]` | Inspect schemas |
| C6 | `SlotSearchProposalIn` has `temporal_relation: Optional[str]` | Inspect schemas |
| C7 | `approximate` does NOT grant duplicate authority | Read the duplicate classifier gating |
| C8 | `unspecified` does NOT grant duplicate authority | Read the duplicate classifier gating |
| C9 | Existing `after`/`before`/`between` operators are unchanged | Smoke script output |
| C10 | Coverage report explicitly shows empty cells | Coverage lattice JSON output |
| C11 | Three adapted seed fixtures exist at `tests/fixtures/bernie_scenario_spec/` | `ls` the directory |
| C12 | Seed fixtures reference known T1/T2 scenario IDs | Read fixture JSON files |
| C13 | `language_normalization.py` preserves operator words | Run normalization tests |
| C14 | `scenario_spec.py` does NOT overwrite `app/services/bernie/normalizer.py` | Verify `normalizer.py` is unchanged from git baseline |
| C15 | T3 tests (`test_bernie_shadow_eval_contract.py`, `test_bernie_shadow_corpus.py`, `test_bernie_shadow_runner.py`, `test_bernie_shadow_live_gate.py`) pass unchanged | Pytest output |
| C16 | Readiness gate still `blocked` | Readiness check output |

### 7. Produce Review Artifact

Write `orchestration/agent_inbox/codex/review-deepseek-lc1-dw3-coverage-review.md`
with:

1. **Header:** Review role, date, model, source plan reference, DW1/DW2 branch
   baselines reviewed.
2. **Test Results Table:** Every check from steps 2-5, with pass/fail and the
   exact command output or error message. For failing checks, include the
   specific failure evidence.
3. **Claims Table:** All 16 claims (C1-C16) with pass/fail and verification
   evidence.
4. **Verdict:** One of:
   - `DECISION: pass` — all checks pass, all claims verified
   - `DECISION: revision_required` — one or more checks/claims fail, with
     specific blocking defects listed
5. **Blocking Defects (if any):** Each defect with: the failed check/claim,
   reproduction command, expected vs actual, and the minimum fix needed.
6. **Non-Blocking Observations:** Any code quality, test coverage, or
   documentation observations that do not block integration.

### 8. Submit

If verdict is `pass`:
```powershell
python scripts\agent_worktrees.py submit --agent deepcode --commit-message "LC1 DW3: independent review — all checks pass" --message "Independent review of DW1+DW2 artifacts. All deterministic acceptance checks pass. All 16 claims verified. Verdict: pass."
```

If verdict is `revision_required`:
```powershell
python scripts\agent_worktrees.py submit --agent deepcode --commit-message "LC1 DW3: independent review — revision required" --message "Independent review of DW1+DW2 artifacts. Verdict: revision_required. See review artifact for blocking defects."
```

## Out of Scope

- Modifying any project code, fixtures, schemas, or routes.
- Fixing issues found (report only).
- Provider calls, DB writes, confirmation authority.
- Any file other than the review artifact.

## Acceptance (by Sol)

Sol reads the review artifact and verifies:
- All checks were actually run (not claimed without output evidence)
- Findings are bounded and substantiated
- Pass/fail verdict is consistent with the evidence presented
- If `revision_required`, blocking defects are specific and actionable
