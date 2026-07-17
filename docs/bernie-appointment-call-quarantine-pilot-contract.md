# Bernie Appointment-Call Corpus Quarantine Pilot Contract

Date: 2026-07-17

## Authority and purpose

Yuri authorized the recommended appointment-call corpus quarantine pilot on
2026-07-17. This tranche may perform a local-only, non-provider, non-training
diagnostic review of version 1 of the Kaggle Healthcare Appointment Booking
Calls dataset. It grants no authority to admit source text to development
evidence, author Gold, tune the parser, create a certification corpus, open a
runtime surface, or access protected holdouts V1-V10.

Source:
`https://www.kaggle.com/datasets/ammarshafiq/healthcare-appointment-booking-calls-dataset`.

## Ordered fail-closed gate

The pilot runs in this order:

1. Freeze public source-card identity, version, uploader, licence label,
   retrieval time, and metadata hashes.
2. Seek documentary evidence for the originating clinic/data controller,
   collection jurisdiction and period, caller notice or consent/legal basis,
   uploader authority, transcript/audio rights, redaction method, and residual
   identifier audit.
3. Stop before corpus download if any provenance, authority, consent/legal
   basis, or licence-scope requirement remains materially unresolved.
4. Only after stage 3 passes, create an ignored local quarantine root at
   `local_data/appointment-call-quarantine/` and download at most five
   deterministically selected transcript files from the frozen version.
5. Scan and manually audit only those files for direct identifiers,
   quasi-identifiers, contact details, dates, rare conditions, free-text
   leakage, and job/account metadata. Do not extract or quote source dialogue
   into committed evidence.
6. Label real, synthetic, uncertain, ASR-derived, and IVR material separately.
   Stop if the origin cannot be established or residual privacy risk is not
   acceptably low.
7. Only after privacy acceptance, deduplicate against ordinary development
   corpora without opening or enumerating any protected holdout. Source text is
   permanently excluded from future certification authorship.
8. Accepted material may initially support corpus-gap discovery and
   language-form taxonomy only. Every derived development probe requires
   source-span and transformation provenance plus a separate promotion gate.

## Data controls

- Raw and sampled material remains ignored, local, and outside runtime,
  product, evaluation, and provider paths.
- No transcript, span, identifier, derived text, prompt, or summary may be
  transmitted to DeepSeek, Gemini, Claude, Codex subagents, or any other
  external model/provider.
- Committed artifacts may contain public metadata, aggregate counts, gate
  outcomes, and hashes only; they may not contain corpus dialogue.
- A failed preliminary gate is a valid pilot result and forbids later stages.

## Decision values

- `provenance_pass_sample_audit_authorized`
- `stop_before_content_download`
- `sample_audit_reject_destroy_local_sample`
- `sample_audit_pass_taxonomy_only`
