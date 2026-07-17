# Bernie Appointment-Call Corpus Provenance Inquiry Package

Date prepared: 2026-07-17

Status: `closed_unsent_product_misaligned`

Source: `ammarshafiq/healthcare-appointment-booking-calls-dataset`

Existing decision: `stop_before_content_download`

## Purpose and authority boundary

This package preserves a draft request for documentary provenance and rights
evidence from the uploader of the Kaggle Healthcare Appointment Booking Calls
Dataset. Yuri subsequently determined that patient-to-receptionist calls are
not the target distribution for Bernie's receptionist-to-assistant language
surface. The draft was never sent and is not currently planned for dispatch.
It does not reopen the quarantine pilot and does not authorize dataset
download, content inspection, external-model transmission, corpus admission,
training, Gold authorship, or certification use.

Yuri may send either message below personally. Preparation of this package is
not authority for an agent to send it. If a response arrives, assess the
response against the checklist before taking any dataset-specific technical
action.

When communicating, Yuri should describe the work accurately as an independent
open-source project. A University of Queensland student email address must not
be presented as university sponsorship, ethics approval, institutional
research authority, or legal review.

## Preferred private message

**Subject:** Provenance and reuse questions about the Healthcare Appointment
Booking Calls Dataset

> Hello Muhammad,
>
> I am an independent developer working on EMR4, an open-source Australian
> general-practice management system. I am assessing whether the Healthcare
> Appointment Booking Calls Dataset could be considered for a tightly
> controlled, local-only research and development review.
>
> I have not downloaded or inspected the dataset content. Before doing so, I
> need to establish the provenance, privacy basis, and scope of the listed ODC
> PDDL licence. Could you please provide or point me to documentary evidence
> covering the following?
>
> 1. The originating clinic or responsible data controller, together with a
>    verifiable official contact or controller-issued confirmation.
> 2. The country or jurisdiction, collection period, original purpose, and
>    circumstances in which the calls were recorded.
> 3. The caller notice, consent, or other documented legal basis for recording
>    the calls and making the recordings or transcripts available for reuse.
> 4. Your role in obtaining the material and your authority from the data
>    controller or relevant rights holder to upload and publish it.
> 5. The rights chain for both the original recordings and the transcripts,
>    including whether the PDDL dedication covers the database, its individual
>    transcript contents, or both.
> 6. The released data types and their lineage—for example, whether the files
>    contain audio, verbatim transcripts, ASR output, or annotations derived
>    from recordings.
> 7. The de-identification method: identifier categories addressed, treatment
>    of indirect or quasi-identifiers, timestamps and account/job metadata,
>    reviewer qualifications, quality assurance, and any residual-risk or
>    re-identification audit.
> 8. The permitted uses of the material and derived artifacts, including
>    research, model development, publication of non-verbatim synthetic
>    derivatives, commercial use, and redistribution.
>
> Please do not send recordings, transcripts, identifiers, or any other caller
> or patient content in your response. Supporting documents may redact
> irrelevant confidential details, but should retain the issuer, date, scope,
> and a way to verify their authenticity. If the originating organisation
> cannot be named publicly, direct confirmation from its data controller or
> rights officer would be helpful.
>
> Thank you for any clarification you can provide.
>
> Kind regards,
>
> Yuri
>
> EMR4 open-source project

## Short Kaggle discussion version

> Hello Muhammad. I am assessing this dataset for a local-only open-source
> healthcare software research project and have not downloaded its content.
> Before considering it, could you provide documentary provenance for the
> originating clinic/data controller, collection jurisdiction and purpose,
> caller notice/consent or other legal basis, your authority to publish the
> calls and transcripts, the rights covered by the PDDL declaration, and the
> de-identification and residual-risk audit? Please also clarify whether the
> release contains audio, transcripts, ASR output, or derived annotations and
> what uses and derived redistribution are authorized. Please do not post or
> send any recordings, transcripts, identifiers, or patient/caller content in
> response; provenance documents or a controller contact are sufficient.

## Response acceptance checklist

Every mandatory row must be `accepted` on verifiable evidence. `Unclear`,
`claimed`, `not supplied`, and an unsupported repetition of the dataset card
all count as unresolved.

| Gate | Mandatory evidence | Examples of potentially adequate evidence | Insufficient by itself |
|---|---|---|---|
| Controller identity | Legal identity of the originating clinic or data controller and a verifiable official contact | Controller-issued letter or confirmation from an organisational domain | Uploader display name; “generic medical clinic” |
| Jurisdiction and collection | Country/jurisdiction, complete collection period, purpose, and recording context | Collection protocol, project record, or controller attestation | Accent, file metadata, or an inferred country |
| Recording and disclosure basis | Documented basis for recording and for subsequent disclosure/reuse | Contemporaneous notice/consent form, ethics approval plus applicable consent, statute, or controller legal-basis statement | “Calls were for training”; availability on Kaggle |
| Uploader authority | Verifiable authority connecting the uploader to the controller or rights holder | Contract, delegation, permission letter, or direct controller confirmation | Uploader self-assertion with no verifiable chain |
| Recording rights | Party holding rights in any original audio and authority for the present use | Rights-holder declaration or licence grant identifying recordings | Rights in the database structure only |
| Transcript/content rights | Party holding rights in transcripts/annotations and authority for the present use | Rights-holder declaration identifying transcript content and annotations | PDDL badge without a statement of owned rights |
| Licence scope | Clear statement whether PDDL applies to the database, individual contents, or both, plus any exclusions | Controller/rightsholder licence statement matching the released version | Kaggle's licence label alone |
| Data lineage | Inventory of released formats and how each was created | Versioned data dictionary and derivation record | File extensions or card prose alone |
| De-identification method | Identifier taxonomy, transformations, handling of free text and quasi-identifiers, responsible reviewers, and QA | Redaction SOP, implementation record, reviewer/audit report | “PII redacted” |
| Residual-risk assessment | Context-specific evaluation showing very low reasonable re-identification risk | Documented risk assessment addressing dataset detail and release environment | Direct-identifier scan alone |
| Permitted downstream use | Explicit position on research, development, synthetic derivatives, commercial use, and redistribution | Rights-holder/controller statement or governing licence terms | Assumption that all derived uses follow from public access |

### Evidence verification rules

- Record the sender, channel, date, exact response, and any public URL.
- Preserve provenance documents locally without committing confidential or
  personal information. Commit only hashes, public references, and gate
  outcomes.
- Verify organisational issuers through independently obtained official contact
  details. Do not rely solely on contact information supplied in the response.
- A statement from the uploader is controller evidence only if the uploader's
  controller role or delegated authority is independently verifiable.
- Redacted documents must retain enough issuer, date, scope, dataset identity,
  and authority information to be verified.
- Do not accept patient records, caller details, source recordings, transcript
  excerpts, or screenshots containing sensitive content as provenance proof.
- Do not upload the response or attachments to an external model if they are
  confidential or contain personal information.

## Decision rule after a response

Use exactly one preliminary disposition:

- `no_response_keep_rejected`: no substantive response; existing rejection
  remains unchanged.
- `response_inadequate_keep_rejected`: one or more mandatory gates remain
  unresolved.
- `response_plausible_request_specific_evidence`: the response identifies a
  potentially verifiable chain but a small, precisely named document or
  confirmation is missing. At most one focused follow-up should be considered.
- `provenance_package_complete_pending_fresh_authorization`: every mandatory
  gate has credible, verifiable evidence. This does not authorize download; it
  returns the matter to Yuri for a fresh decision.
- `evidence_contradictory_or_sensitive_stop`: provenance conflicts, improperly
  disclosed sensitive data, or another material concern requires immediate
  stop and local containment.

Silence, inconvenience, public availability, or the apparent usefulness of the
corpus must never be used to lower a mandatory gate.

## Conditional clean-room outline

This section is dormant unless the disposition is
`provenance_package_complete_pending_fresh_authorization` and Yuri then gives
fresh, explicit authority for a new sample-audit stage.

1. Amend or replace the quarantine contract with the accepted evidence hashes,
   exact authorized version, allowed purposes, retention limits, and deletion
   obligations.
2. Create the ignored local quarantine root already specified by the pilot.
   Confirm that it is excluded from source control, backup/sync, runtime,
   provider, and indexing paths.
3. Retrieve only the frozen version and only the maximum five-file sample
   allowed by the existing pilot. Record retrieval and file hashes without
   committing content.
4. Keep all processing local and offline. Do not expose source content to
   Codex, DeepSeek, Gemini, Claude, subagents, hosted APIs, telemetry, or cloud
   storage.
5. Inventory formats and fields before reading dialogue. Reject unexpected
   audio, identifiers, source-system payloads, or scope expansion.
6. Audit direct identifiers, quasi-identifiers, dates, locations, rare events,
   free-text details, account/job metadata, voice or acoustic identity, and
   linkability with public information.
7. Treat removal of direct identifiers as necessary but not sufficient.
   Generalize, suppress, or reject details until the residual risk is very low
   in the intended access environment; reject the sample if this cannot be
   demonstrated without destroying its utility.
8. Prefer derived dialogue-act taxonomies and newly authored fictional probes
   over retained or lightly paraphrased transcript text. Do not publish source
   dialogue or near-verbatim derivatives.
9. Require a separate recorded privacy decision before taxonomy work and a
   separate promotion decision before any development probe. The source must
   never author a protected certification holdout.
10. Apply the contract's destruction outcome immediately if the sample fails.

## Send and follow-up record

Complete only when Yuri actually sends a message:

- Channel: `not_sent`
- Sent at: `not_sent`
- Sender identity used: `not_sent`
- Public discussion URL or private-message reference: `not_sent`
- Response deadline or review date: `not_set`
- Follow-up sent: `false`
- Response received: `false`
- Current disposition: `closed_unsent_product_misaligned`
