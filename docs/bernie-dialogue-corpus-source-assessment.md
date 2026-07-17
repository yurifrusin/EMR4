# Bernie Dialogue Corpus Source Assessment

Date: 2026-07-17

## Decision

The Healthcare Appointment Booking Calls dataset is worth a controlled next
look. It is unusually close to Bernie's receptionist domain and may expose
natural turn structure, repairs, hesitations, IVR transitions, ASR errors, and
booking vocabulary that synthetic authoring underrepresents. It is not yet
approved for download, import, training, Gold labelling, or evaluation.

The AI Doctor / MedInstruct dataset is not a receptionist corpus. Its canonical
lineage is synthetic medical instruction following, so it may inform a later
GP-assistant consultation research track but should not shape Bernie's booking
parser or be treated as clinical truth.

This assessment used public metadata and source cards only. No dataset content
was downloaded or opened, and holdouts V1-V10 remained sealed.

## Source comparison

### Healthcare Appointment Booking Calls (Kaggle)

- Public card: https://www.kaggle.com/datasets/ammarshafiq/healthcare-appointment-booking-calls-dataset
- Claimed content: 739 files of timestamped, speaker-labelled transcripts from
  calls to a generic medical clinic, with IVR events, word confidence, and PII
  redaction.
- Listed licence: ODC Public Domain Dedication and Licence (PDDL).
- Bernie relevance: high for receptionist language, multi-turn repair,
  cancellation/rescheduling patterns, spoken temporal forms, and ASR-shaped
  text.
- Unresolved provenance: the card does not identify the originating clinic,
  jurisdiction, collection dates, caller notice/consent, uploader authority,
  original audio rights, redaction method, residual-identifier audit, or
  whether every transcript is genuinely real rather than generated or mixed.
- Decision: `promising_but_quarantine_required`.

The PDDL label addresses database reuse; it does not prove that the uploader
held the rights or privacy authority needed to publish the underlying calls.
The statement that PII was redacted is useful but not sufficient for Australian
health-data handling without verification.

### AI Doctor / MedInstruct (Kaggle and canonical lineage)

- Kaggle card: https://www.kaggle.com/datasets/asadullahcreative/ai-doctor-fine-tuning-dataset
- Canonical source card: https://huggingface.co/datasets/xz97/MedInstruct
- Canonical lineage: MedInstruct-52K uses GPT-4-generated instructions and
  model-generated responses from an expert-curated seed set; its test set is
  clinician-authored with model reference answers.
- Canonical licence: CC BY-NC 4.0. The Kaggle title's “92K” shape requires
  separate provenance reconciliation before assuming it is the same work or
  that its licence is compatible.
- Bernie relevance: low. It targets medical knowledge and instruction
  following, not reception, appointment state, confirmation, or practice
  workflow.
- GP-assistant relevance: potentially useful for research taxonomy and failure
  ideation, but not for clinical truth, certification, or product fine-tuning
  without clinical governance, lineage reconciliation, and non-commercial
  licence review.
- Decision: `defer_from_bernie_consider_for_consult_research_only`.

### Complementary public dialogue sources

- Schema-Guided Dialogue / SGD-X provides more than 20,000 annotated,
  multi-domain task dialogues plus slot spans, canonical values, service calls,
  dialogue state, and linguistic schema variants. It was generated with a
  simulator and paid crowd-workers and is CC BY-SA 4.0. It is not medical, but
  is useful for testing dialogue-state and schema/projection methods without
  healthcare privacy exposure:
  https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
- MediTOD is an English medical-history-taking dialogue dataset with detailed
  medical annotations. It addresses consultation rather than reception and is
  therefore a possible future consult-role research source, not a Bernie
  booking corpus: https://aclanthology.org/2024.emnlp-main.936/

Neither source replaces Australian receptionist review. The best long-term
Gold source remains a consented, purpose-limited, locally governed corpus
authored or adjudicated by qualified GP reception staff and clinicians.

## Required quarantine gate

Before any appointment-call download or sample inspection, create a separately
authorized, local-only quarantine tranche that:

1. records the exact source URL, version, card, licence, hashes, uploader, and
   retrieval date;
2. seeks evidence of collection provenance, consent/notice, uploader rights,
   jurisdiction, and redaction process;
3. stores raw material outside runtime and protected-evaluation paths with no
   provider/model transmission;
4. scans for direct and quasi-identifiers, contact details, dates, rare
   conditions, free-text leakage, and recoverable job/account metadata;
5. manually audits a small bounded sample before broader processing;
6. labels real, synthetic, uncertain, ASR-derived, and IVR material separately;
7. deduplicates against every development corpus without opening sealed
   holdouts, and excludes source text from future certification authorship;
8. uses accepted material first for corpus-gap discovery and language-form
   taxonomy, not automatic Gold or parser tuning; and
9. preserves source spans and transformation provenance for every derived
   development probe.

## Pilot outcome and next decision

Yuri authorized the recommended metadata-to-quarantine pilot on 2026-07-17.
The preliminary provenance and licence-authority gate stopped before corpus
download or content inspection. The originating clinic/data controller,
jurisdiction, caller notice or consent/legal basis, uploader authority,
content-rights chain, redaction method, and residual-identifier audit remain
undocumented. No corpus content was downloaded, opened, transmitted, or
admitted.

The source remains promising but inadmissible. Reconsideration requires a
verifiable provenance/rights/privacy package and a new Yuri decision to pursue
external coordination or renew content inspection. See
`docs/bernie-appointment-call-quarantine-pilot-closeout.md`.
