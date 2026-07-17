# DeepSeek Synthetic Noise Sol Recovery Review

**Date:** 2026-07-17
**Reviewer:** DeepSeek V4 Flash/high through Claude Code `--bare`
**Role:** Independent exact-candidate Silver reviewer

---

## Verification

| Check | Result |
|---|---|
| Source head | `0688818f3681da22a5586ce03f6a996eaa1f93e6` ✓ |
| Candidate file | `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl` ✓ |
| Canonical record hash | `sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf` ✓ |
| Record count | 192 ✓ |
| Central validator | `pass: 192 candidates` ✓ |
| Pytest | 10/10 passed ✓ |
| `git diff --check` | clean ✓ |

---

## Mechanical pass

All 192 candidates pass every mechanical gate defined in the Silver contract and
`validate_candidate_records` in `synthetic_noise_corpus.py`:

| Criterion | Status |
|---|---|
| 192 records, 2 per seed | pass |
| Exact source seed hashes | pass |
| Unique candidate IDs | pass |
| Unique dialogue payloads (canonical) | pass |
| Declared medium/high noise levels | pass |
| Minimum noise operation counts | pass |
| Allowlisted noise operations only | pass |
| Valid turn numbering and receptionist-only speaker | pass |
| Non-empty utterances (≤500 char) | pass |
| Evidence keys exactly match seed `required_evidence_keys` | pass |
| Evidence span coordinates exactly slice generated utterances | pass |
| `semantic_change=none` | pass |
| `provenance=silver`, `adjudication=pending` | pass |
| All authority fields `false` | pass |
| No contact detail, URL, phone, or long identifier | pass |
| `generator_identity` matches Sol recovery lane | pass |
| `candidate_id` prefix `sol_` | pass |
| One-shot: 1 turn; other forms: ≥2 turns | pass |

**Dialogue-form distribution** (24 candidates per form — exactly 12 seeds × 2):

- `one_shot`: 24
- `clarification`: 24
- `correction`: 24
- `reversal`: 24
- `ellipsis`: 24
- `anaphora`: 24
- `repeated`: 24
- `session_restart`: 24

**Action distribution** (32 candidates per action — 16 seeds × 2):

- `create`: 32
- `move`: 32
- `resize`: 32
- `cancel`: 32
- `status_change`: 32
- `explain_schedule`: 32

**Noise-operation frequency:**

- `filler`: 192 (all)
- `abbreviation`: 192 (all)
- `staff_shorthand`: 192 (all)
- `punctuation_case`: 96 (medium variant only)
- `speech_disfluency`: 96 (high variant only)
- `reordered_slots`: 96 (high variant only)
- `dictation_artifact`: 96 (high variant only)
- `correction`: 48 (12 correction seeds × 2 + 4 one-shot seeds × 2 with `entity_state: corrected`)
- `reversal`: 24 (12 reversal seeds × 2)
- `ellipsis`: 24 (12 ellipsis seeds × 2)
- `anaphora`: 24 (12 anaphora seeds × 2)

Medium variants have 4–6 operations (min 2 required); high variants have 6–8
operations (min 3 required).

---

## Semantic review

### 1. Intended action and action semantics

All 192 candidates preserve the frozen intended action (`create`, `move`,
`resize`, `cancel`, `status_change`, `explain_schedule`). Action semantics
remain `intended` throughout. No candidate changes the oracle meaning.

### 2. Patient/practitioner state

- **Exact** patient/practitioner seeds: all candidates include `Margaret
  Thompson` and/or `Dr Shera` in utterances, correctly captured in evidence
  spans.
- **Ambiguous** patient/practitioner seeds: candidates correctly use vague
  references (`someone`, `a doctor`) and do not include `patient` or
  `practitioner` in `required_evidence_keys`. No invented resolution of
  unresolved entities.
- **Omitted** patient seeds (seeds 081–096): candidates correctly omit patient
  references and have no `patient` in `required_evidence_keys`.
- **Corrected** practitioner seeds (correction form): Turn 1 uses `a doctor`,
  Turn 2 replaces it with `Dr Shera`. The correction is explicit and
  unambiguous.
- **Corrected** in one-shot seeds (017, 041, 065, 089): `entity_state:
  corrected` permits in-utterance correction; utterances convey the corrected
  entity directly. Acceptable per noise contract, though Sol may elect to
  quarantine if the correction surface is considered implicit.

### 3. Temporal meaning, duration, status

Every normalized date (`2026-07-15`), time (3pm, 2pm, 4pm, 5pm), duration
(15 mins), and temporal relation (exact, not_before, not_after, interval,
approximate, unspecified) is correctly preserved in the generated utterances
and captured in evidence spans. No temporal corruption detected.

### 4. Dialogue form

Each candidate faithfully implements its seed's `dialogue_form`:

- **one_shot**: Single-turn instruction with all required slots.
- **clarification**: Turn 1 signals ambiguity/need for clarification; Turn 2
  restates the request with vague or ambiguous entities.
- **correction**: Turn 1 with generic practitioner (`a doctor`); Turn 2
  explicitly corrects to `Dr Shera`. Correction noise operation declared.
- **reversal**: Turn 1 states a request; Turn 2 reverses/withdraws it
  (`"Actually, stop there—leave the diary unchanged."`). Reversal noise
  operation declared.
- **ellipsis**: Turn 1 provides full details; Turn 2 uses an elliptical
  reference (`"Same details—that one."`). Ellipsis noise operation declared.
- **anaphora**: Turn 1 provides full details; Turn 2 uses a pronoun/phrase
  (`"Use that appointment for the request."`). Anaphora noise operation
  declared.
- **repeated**: Both turns contain substantively identical utterances.
- **session_restart**: Turn 1 starts the request; Turn 2 restates it with a
  fresh-start marker (`"Starting a fresh request—..."`).

### 5. Receptionist-to-Bernie staff instruction

Every utterance is a natural staff instruction to an assistant. No candidate
contains patient dialogue, Bernie reply, clinical triage, or counselling
language. No `"got it"`, `"sure"`, `"will do"`, or similar Bernie-response
wording present.

### 6. Noise plausibility

All noise operations produce plausible receptionist language variation:

- `filler`: "Quick one:", "Before I forget:", "Next item," etc.
- `abbreviation`: "mins", "appt", "Dr"
- `staff_shorthand`: "book that", "move this", "diary job", "rundown"
- `speech_disfluency`: "book—book this", "sorry, book—booking"
- `reordered_slots`: Slots appear in varied orders across high variants
- `dictation_artifact`: Slash-separated fragments ("/ Margaret Thompson / Dr Shera / tomorrow")
- `correction`/`reversal`/`ellipsis`/`anaphora`: Appropriately used per dialogue form

No candidate exhibits semantic corruption from excessive noise.

### 7. Evidence span integrity

All evidence spans are verified to exactly slice the generated utterance text
at the stated coordinates. No evidence span references a turn or character
range outside the utterance. The `evidence_spans` dictionary keys exactly match
the seed's `required_evidence_keys`.

### 8. Error-free handling of ambiguous/omitted slots

When the seed omits a slot (e.g., `patient_semantics: omitted`, `latest_time:
null`), the candidate does not invent a value. The `required_evidence_keys`
omits that key, and the utterance avoids the omitted detail. No hallucinated
resolution occurs.

### 9. Variant distinction

Medium (variant 1) and high (variant 2) candidates for the same seed are
always distinguishable. High variants consistently add `speech_disfluency`,
`reordered_slots`, and `dictation_artifact` with a higher total operation
count (6–8 vs. 4–6). No pair of variants has identical dialogue payloads.

### 10. Prohibitions

| Prohibition | Status |
|---|---|
| No Bernie reply or oracle mutation | pass |
| No `provider_write`, `diary_write`, `confirmation`, `override_authority` | pass |
| No access to protected holdouts, historical data, or external corpora | pass |
| No clinical data, identifiers, or contact details | pass |
| No Gold/adjudicated/accepted/certified claims | pass |
| No real-world provenance claims | pass |

---

## Minor observation (not a rejection)

One-shot candidates for seeds **017**, **041**, **065**, and **089** (8
candidates: both variants) declare `correction` as a noise operation even
though the dialogue form is `one_shot`. This is permitted by the contract — the
seed `entity_state` is `"corrected"`, allowing in-utterance correction — but
the correction surface is implicit (the utterance presents the corrected entity
directly rather than showing the before-and-after). Sol may wish to quarantine
these 8 candidates for verification that the correction is linguistically
manifest, or accept them as valid bounded one-shot corrections.

---

## Final classification

All 192 candidates are classified as **accept**. No candidate requires
quarantine or rejection. The 8 one-shot candidates with implicit `correction`
noise are structurally and semantically valid per the contract; Sol may
disposition them as part of the acceptance decision.

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
