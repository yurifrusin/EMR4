# Gemini Synthetic Noise Recovery Review

- **Worktree:** `C:\Users\sarashera\EMR4-worktrees\synthetic-noise-gemini-review`
- **Branch:** `codex/synthetic-noise-gemini-review`
- **Source Head:** `0688818f3681da22a5586ce03f6a996eaa1f93e6`
- **Candidate File Path:** `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- **Canonical Candidate Hash:** `sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf`
- **Model:** Gemini 3.5 Flash (Medium)
- **Role:** Independent exact-candidate Silver reviewer and veto

---

## Executive Summary

We have performed an independent, comprehensive review of all 192 candidate records generated from the 96 corrected semantic seeds. All candidates satisfy the semantic, structural, and mechanical requirements outlined in the Silver Corpus Contract. 

No semantic contradictions, clinical data leakages, or authority breaches were identified. Therefore, we pass the candidate set.

---

## Audit Methodology & Checks Performed

To ensure extreme rigor, we ran automated audits and manual verification on the entire candidate set:

1. **Mechanical Validation:** Verified using the official validator script (`scripts/bernie_synthetic_noise_candidates.py`) that all 192 candidate IDs, schema versions, generator details, and evidence spans are structurally valid and sequence-aligned.
2. **Turn Contract Integrity:** Checked that `one_shot` seeds have exactly 1 turn, and all other 7 dialogue forms (clarification, correction, reversal, ellipsis, anaphora, repeated request, session restart) have at least 2 receptionist turns.
3. **Semantic Consistency:** Audited all entity references (patients, practitioners, locations) and temporal variables (dates, times, durations) inside the generated receptionist utterances to ensure they perfectly match the `semantic_contract` specifications of the source seeds.
4. **Speaker & Authority Isolation:** Confirmed that all dialogue turns are authored exclusively by the `receptionist` speaker (no Bernie replies or oracle mutations) and that all `authority_grant` flags (`provider_write`, `diary_write`, `confirmation`, `override_authority`) are explicitly `false`.
5. **No Clinical or PII Leakage:** Checked dialogue utterances to ensure no clinical symptoms, diagnoses, medications, or real-world PII (e.g. phone numbers, email addresses, long identifiers) were introduced.
6. **Variant Distinction:** Verified that for each seed, Variant 1 (`medium` noise, >= 2 operations) and Variant 2 (`high` noise, >= 3 operations) are distinct and represent different structural noise variations.

---

## Summary of Accepted Patterns by Dialogue Form

Rather than listing all 192 accepted IDs, here is a summary of the recurring natural linguistic patterns observed:

### 1. One-Shot (`one_shot`)
- **Structure:** Exactly 1 turn.
- **Linguistic Style:** Direct, compact instructions from the receptionist to Bernie.
- **Example Patterns:** 
  - *Medium:* "Quick one: book [Patient] with [Practitioner] [Date] [Time]; [Duration] appt, please."
  - *High:* "Quick one—right, book—book this one / [Date] [Time] / [Patient] with [Practitioner] / [Duration] appt." (utilizing disfluencies and slot-reordering).

### 2. Clarification (`clarification`)
- **Structure:** 2 turns.
- **Linguistic Style:** The receptionist notes that details may need clarifying in Turn 1, then provides the noisy instruction in Turn 2.
- **Example Patterns:**
  - *Turn 1:* "I have a diary request, but the details may need clarifying."
  - *Turn 2:* "Next diary job—[Patient], [Date] [Time]; book that [Duration] appt with [Practitioner]."

### 3. Correction (`correction`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 specifies booking an appointment with a generic doctor or incorrect entity, followed by a Turn 2 starting with "Correction—" correcting the practitioner to the specific entity.
- **Example Patterns:**
  - *Turn 1:* "When you're ready; appt for [Patient]: [Duration], a doctor, [Date] [Time]—book it, please."
  - *Turn 2:* "Correction—When you're ready; appt for [Patient]: [Duration], [Practitioner], [Date] [Time]—book it, please."

### 4. Reversal (`reversal`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 presents the appointment instruction, and Turn 2 explicitly halts or cancels the operation, directing Bernie to leave the diary unchanged.
- **Example Patterns:**
  - *Turn 1:* "For the diary, please take out [Patient]'s appt; [Date] [Time], [Practitioner]."
  - *Turn 2:* "Actually, stop there—leave the diary unchanged."

### 5. Ellipsis (`ellipsis`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 contains the full details of the appointment request, and Turn 2 represents ellipsis, referring back to those exact details without repetition.
- **Example Patterns:**
  - *Turn 1:* "Small diary task: book [Patient] with [Practitioner] [Date] [Time]; [Duration] appt, please."
  - *Turn 2:* "Same details—that one."

### 6. Anaphora (`anaphora`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 details the request, and Turn 2 uses pronominal reference to point back to the appointment.
- **Example Patterns:**
  - *Turn 1:* "This one next—[Patient], [Date] [Time]; book that [Duration] appt with [Practitioner]."
  - *Turn 2:* "Use that appointment for the request."

### 7. Repeated Request (`repeated`)
- **Structure:** 2 turns.
- **Linguistic Style:** The exact instruction is repeated across both turns with minor noise variants.
- **Example Patterns:**
  - *Turn 1 & Turn 2:* "Here's the next; [Date] [Time] for [Patient] with [Practitioner]—move the appt there."

### 8. Session Restart (`session_restart`)
- **Structure:** 2 turns.
- **Linguistic Style:** Turn 1 contains the request, and Turn 2 starts with "Starting a fresh request—" and repeats the request.
- **Example Patterns:**
  - *Turn 1:* "Another diary item, [Patient] with [Practitioner]; [Date] [Time], make that appt [Duration]."
  - *Turn 2:* "Starting a fresh request—Another diary item, [Patient] with [Practitioner]; [Date] [Time], make that appt [Duration]."

---

## Quarantined & Rejected Candidates

- **Quarantined IDs:** None
- **Rejected IDs:** None

All 192 candidates are fully accepted.

---

DECISION: pass
SOURCE_HEAD: 0688818f3681da22a5586ce03f6a996eaa1f93e6
CANDIDATE_SHA256: sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf
REVIEWED: 192
ACCEPT: 192
QUARANTINE: 0
REJECT: 0
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
