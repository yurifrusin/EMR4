# Gemini Synthetic Noise Recovery Review Round 2

- **Worktree:** `C:\Users\sarashera\EMR4-worktrees\synthetic-noise-gemini-review-2`
- **Branch:** `codex/synthetic-noise-gemini-review-2`
- **Source Head:** `b1380f6aaf6eb21d9af763cfcc8db5130cba138d`
- **Candidate File Path:** `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- **Canonical Candidate Hash:** `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- **Model:** Gemini 3.5 Flash (Medium)
- **Role:** fresh independent exact-candidate Silver reviewer and veto
- **Acceptance/integration owner:** GPT Sol

---

## Executive Summary

We have performed an independent, comprehensive Round 2 review of all 192 candidate records generated from the 96 corrected semantic seeds. All candidates fully satisfy the semantic, structural, and mechanical requirements outlined in the Silver Corpus Contract.

No semantic contradictions, clinical data leakages, or authority breaches were identified. Crucially, all 18 records that erroneously declared a `correction` operation in Round 1 have been corrected, and no candidate has fallen below the required minimum count of operations for their noise level. Therefore, we pass the candidate set.

---

## Audit Methodology & Checks Performed

To ensure extreme rigor, we ran automated audits and manual verification on the entire candidate set:

1. **Mechanical Validation:** Verified using the official validator script (`scripts/bernie_synthetic_noise_candidates.py`) that all 192 candidate IDs, schema versions, generator details, and evidence spans are structurally valid and sequence-aligned.
2. **Turn Contract Integrity:** Checked that `one_shot` seeds have exactly 1 turn, and all other 7 dialogue forms (clarification, correction, reversal, ellipsis, anaphora, repeated request, session restart) have at least 2 receptionist turns.
3. **Semantic Consistency:** Audited all entity references (patients, practitioners, locations) and temporal variables (dates, times, durations) inside the generated receptionist utterances to ensure they perfectly match the `semantic_contract` specifications of the source seeds.
4. **Speaker & Authority Isolation:** Confirmed that all dialogue turns are authored exclusively by the `receptionist` speaker (no Bernie replies or oracle mutations) and that all `authority_grant` flags (`provider_write`, `diary_write`, `confirmation`, `override_authority`) are explicitly `false`.
5. **No Clinical or PII Leakage:** Checked dialogue utterances to ensure no clinical symptoms, diagnoses, medications, or real-world PII (e.g. phone numbers, email addresses, long identifiers) were introduced.
6. **Variant Distinction & Operations Counts:** Verified that for each seed, Variant 1 (`medium` noise, >= 2 operations) and Variant 2 (`high` noise, >= 3 operations) are distinct and represent different structural noise variations.
7. **Correction Operations Review:**
   - Audited the remaining 30 candidates declaring `correction` in `noise_operations` and confirmed that every single one exhibits an explicit `Correction—` or `—sorry,` surface in the receptionist turns.
   - Verified that the 18 records which had `correction` removed from their `noise_operations` list do not contain "Correction—" or "—sorry," surfaces in their dialogue.
   - Verified that removing the `correction` label from those 18 candidates did not cause them to drop below the minimum required count of operations (medium level candidates still have >= 2 operations, and high level candidates still have >= 3 operations).

---

## Summary of Accepted Patterns by Dialogue Form

Rather than listing all 192 accepted IDs, here is a summary of the recurring natural linguistic patterns observed:

### 1. One-Shot (`one_shot`)
- **Structure:** Exactly 1 turn.
- **Linguistic Style:** Direct, compact instructions from the receptionist to Bernie.
- **Example Patterns:**
  - *Medium:* "Quick one: book Margaret Thompson with Dr Shera tomorrow at 3pm; 15 mins appt, please."
  - *High:* "Quick one—right, book—book this one / tomorrow at 3pm / Margaret Thompson with Dr Shera / 15 mins appt." (utilizing disfluencies and slot-reordering).

### 2. Clarification (`clarification`)
- **Structure:** 2 turns.
- **Linguistic Style:** The receptionist notes that details may need clarifying in Turn 1, then provides the noisy instruction in Turn 2.
- **Example Patterns:**
  - *Turn 1:* "I have a diary request, but the details may need clarifying."
  - *Turn 2:* "Next diary job—someone, tomorrow at 3pm; book that 15 mins appt with a doctor."

### 3. Correction (`correction`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 specifies booking an appointment with a generic doctor, followed by a Turn 2 starting with "Correction—" correcting the practitioner to a specific entity (Dr Shera).
- **Example Patterns:**
  - *Turn 1:* "When you're ready; appt for Margaret Thompson: 15 mins, a doctor, tomorrow at 3pm—book it, please."
  - *Turn 2:* "Correction—When you're ready; appt for Margaret Thompson: 15 mins, Dr Shera, tomorrow at 3pm—book it, please."

### 4. Reversal (`reversal`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 presents the appointment instruction, and Turn 2 explicitly halts or cancels the operation, directing Bernie to leave the diary unchanged.
- **Example Patterns:**
  - *Turn 1:* "For the diary, please move Margaret Thompson's appt; Dr Shera, tomorrow between 2pm and 4pm."
  - *Turn 2:* "Actually, stop there—leave the diary unchanged."

### 5. Ellipsis (`ellipsis`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 contains the full details of the appointment request, and Turn 2 represents ellipsis, referring back to those exact details without repetition.
- **Example Patterns:**
  - *Turn 1:* "Small diary task: book Margaret Thompson with Dr Shera tomorrow 3pm or later; 15 mins appt, please."
  - *Turn 2:* "Same details—that one."

### 6. Anaphora (`anaphora`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 details the request, and Turn 2 uses pronominal reference to point back to the appointment.
- **Example Patterns:**
  - *Turn 1:* "This one next—shift Margaret Thompson's Dr Shera appt: tomorrow 3pm or later."
  - *Turn 2:* "Use that appointment for the request."

### 7. Repeated Request (`repeated`)
- **Structure:** 2 turns.
- **Linguistic Style:** The exact instruction is repeated across both turns with minor noise variants.
- **Example Patterns:**
  - *Turn 1 & Turn 2:* "While I'm here; appt for Margaret Thompson: 15 mins, Dr Shera, tomorrow by 5pm—book it, please."

### 8. Session Restart (`session_restart`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 contains the request, and Turn 2 starts with "Starting a fresh request—" and repeats the request.
- **Example Patterns:**
  - *Turn 1:* "Another diary item, please move Margaret Thompson's appt; Dr Shera, tomorrow by 5pm."
  - *Turn 2:* "Starting a fresh request—Another diary item, please move Margaret Thompson's appt; Dr Shera, tomorrow by 5pm."

---

## Quarantined & Rejected Candidates

- **Quarantined IDs:** None
- **Rejected IDs:** None

All 192 candidates are fully accepted.

---

DECISION: pass
SOURCE_HEAD: b1380f6aaf6eb21d9af763cfcc8db5130cba138d
CANDIDATE_SHA256: sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665
REVIEWED: 192
ACCEPT: 192
QUARANTINE: 0
REJECT: 0
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
