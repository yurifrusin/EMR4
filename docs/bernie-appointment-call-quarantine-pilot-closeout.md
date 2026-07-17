# Bernie Appointment-Call Corpus Quarantine Pilot Closeout

Date: 2026-07-17

Decision: `stop_before_content_download`

## Outcome

The authorized local-only pilot completed its preliminary provenance and
licence-authority gate and failed closed before transcript download or content
inspection. No corpus archive or transcript was persisted, no quarantine data
directory was created, and no source text was sent to a provider, model,
subagent, runtime, product path, development corpus, or protected evaluation
surface.

The frozen public metadata identifies Kaggle dataset
`ammarshafiq/healthcare-appointment-booking-calls-dataset`, dataset ID 6376623,
version 1, created 2024-12-26, owned and uploaded under the display name
Muhammad Ammar. The card reports 739 files and 154,124,772 bytes and labels the
dataset ODC PDDL. Exact retrieval metadata and in-memory capture hashes are in
`docs/bernie-appointment-call-quarantine-pilot-evidence.json`.

## Why the gate stopped

The public card says the material is verbatim transcript data from a generic
medical clinic and that PII was redacted. It also says files include detailed
timestamps, speaker turns, word confidence, and job/account metadata. No public
evidence found in the card or its zero-comment discussion surface identifies:

- the originating clinic or data controller;
- jurisdiction, complete collection period, or collection purpose;
- caller notice, consent, or another documented legal basis;
- the uploader's authority over the calls, transcripts, and original audio;
- the redaction method or residual-identifier audit; or
- whether the PDDL declaration covers both database rights and transcript
  content rights held by the declaring party.

The official PDDL text warns that a rightsholder can license only what they own
and must clearly state whether the dedication covers the database, its
contents, or both. A Kaggle licence label therefore does not cure the missing
rights chain. Australian de-identification guidance also treats removal of
direct identifiers as only the first step: quasi-identifiers and the access
context must leave a very low re-identification risk. The card's unsupported
redaction statement cannot establish that standard.

Sources:

- Kaggle source card:
  https://www.kaggle.com/datasets/ammarshafiq/healthcare-appointment-booking-calls-dataset
- Open Data Commons PDDL 1.0:
  https://opendatacommons.org/licenses/pddl/1-0/index.html
- OAIC, De-identification and the Privacy Act:
  https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/de-identification-and-the-privacy-act

## Disposition

The corpus remains `promising_but_not_admissible`. Do not download, inspect,
train on, tune against, label as Gold, deduplicate, or use it for parser or
certification authorship. The unexecuted sample-scan and taxonomy stages are
not failures; the ordered contract forbids reaching them after a preliminary
provenance stop.

Reconsideration requires a verifiable provenance package from the responsible
data controller or rights holder covering clinic identity, jurisdiction,
collection basis, uploader authority, content rights, and the redaction and
residual-risk audit. Seeking that package from an external party is a new
coordination decision for Yuri.

Holdouts V1-V10, T3.1-T3.5, provider calls, historical data, runtime/product
wiring, API/write authority, database, deployment, and release remain closed.
