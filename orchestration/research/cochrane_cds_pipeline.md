# Cochrane / Evidence CDS Pipeline Research Note

Status: early research note, not an implementation commitment.

2026-06-20 update: Yuri has signed up with AWS and requested a private offer
for Wiley Agent Knowledge Base: Cochrane Library. Treat any vendor response as
input to licensing, data-flow, and architecture design; do not implement against
the product until use rights, privacy posture, data residency, and cost model are
clear.

## Bottom Line

Wiley now offers a dedicated AWS Marketplace product named **Wiley Agent
Knowledge Base: Cochrane Library**. It appears technically feasible to integrate
through an API/RAG-style clinical evidence assistant, but it is not a near-term
small-practice feature. Public pricing is private-offer/enterprise shaped, and
privacy, data residency, clinical safety, and licensing questions would need
formal answers before EMR4 sends any patient-context query to it.

For EMR4, the right near-term architectural move is to design an
evidence-provider abstraction with citation and audit support, not to bake Wiley
or Cochrane assumptions into the core workflow.

## Evidence-Provider Abstraction Target

The CDS layer should depend on a provider-neutral retrieval contract rather than
directly wiring the UI or model prompt to any single corpus.

Each evidence provider should expose the same internal shape:

- Request: clinician-controlled question, optional de-identified PICO/context,
  source preference, specialty/domain, and safety flags.
- Response: evidence items with title, source, date/version, citation, URL/DOI,
  evidence type, permitted snippet/excerpt, relevance score, and provider
  metadata.
- Policy metadata: PHI allowance, caching rights, snippet-storage rights, audit
  retention rights, region/data-residency status, rate limit, and licence scope.

This lets EMR4 start with cheaper/public or already-licensed Australian sources,
then add Cochrane/Wiley if the licence and cost model work, without rebuilding
the clinical reasoning layer.

## What Wiley/Cochrane Appears To Offer

- AWS Marketplace lists **Wiley Agent Knowledge Base: Cochrane Library** as an
  API-based knowledge base deployed on AWS.
- The listing describes Cochrane Library content as structured,
  machine-readable, metadata-rich, and compatible with AWS Bedrock-style AI/RAG
  use.
- The content is described as including Cochrane Database of Systematic Reviews
  and Cochrane Clinical Answers.
- The listing documents API-key authentication, `GET /articles?question=...`,
  and optional `GET /download/{uuid}` full-text HTML access when entitled.
- Pricing is not public in any practical sense. The AWS listing shows placeholder
  private-offer pricing and says to request a custom quote.

## Important Licensing Distinction

Australian human-reader access to the Cochrane Library does not imply permission
for commercial AI use, embedding, caching, redistribution, model training, or
tenant-wide SaaS reuse. EMR4 would need a commercial licence covering exactly the
intended use.

## Recommended EMR4 Architecture

Use RAG/retrieval, not training:

1. Convert clinical context into a de-identified clinical question/PICO where
   possible.
2. Query licensed evidence providers.
3. Feed only retrieved excerpts, metadata, review dates, DOI/source links, and
   evidence type into Gemini or another reasoning layer.
4. Display evidence assistance with citations, currency, evidence strength, and
   clinician override.
5. Store an audit trail: user, patient, prompt category, source ids, model
   version, response shown, and any final clinician action.
6. Assume patient-identifiable data must not leave Australia unless a contract,
   privacy assessment, and data-flow design explicitly support it.

## Questions For Wiley/Cochrane

- Corpus: exactly which Cochrane assets are included: CDSR, Clinical Answers,
  CENTRAL, protocols, tables, forest plots, full text?
- Licence: are RAG, generated summaries, local caching, embeddings, snippets,
  audit storage, and tenant/SaaS redistribution permitted?
- Pricing: startup/SaaS pricing, per-clinician/practice/API-call model, and
  whether open-source/self-hosted customers can use their own licence.
- Data handling: AWS region, PHI policy, query logging, no-training guarantees,
  subprocessors, deletion, audit rights, breach notification, and APP 8 support.
- API: sandbox, SLAs, rate limits, citation metadata, versioning, update cadence,
  Clinical Answer structure, and full-text entitlement rules.
- Clinical safety: intended-use wording, validation support, and TGA/CDSS
  regulatory posture.

## Australian Privacy And Safety Frame

- Health information is sensitive information under Australian privacy law.
- APP 8/cross-border disclosure is central if any query or log goes overseas.
- APP 11 security controls, auditability, access control, deletion, and breach
  processes must be designed before production use.
- Clinical decision support can enter TGA software-as-medical-device territory
  depending on intended purpose and how much the software drives diagnosis,
  prediction, treatment, or prognosis.
- EMR4 should position this as clinician-controlled evidence assistance, not a
  diagnostic replacement.

## Other Evidence Sources To Consider

Cochrane is excellent for systematic-review and intervention evidence, but it is
not a full differential diagnosis engine. For Australian GP support, consider an
evidence-provider layer that can later include:

- Therapeutic Guidelines
- RACGP Red Book, White Book, and HANDI
- Australian Immunisation Handbook
- PBS data, MBS Online, and TGA safety alerts
- AMH, HealthPathways, eviQ, RCH guidelines, Cancer Council guidelines
- Licensed DDx/reference products such as BMJ Best Practice, DynaMed, UpToDate,
  Isabel, or similar, with Australian guideline overlays

## Source Links

- AWS Marketplace - Wiley Agent Knowledge Base: Cochrane Library:
  https://aws.amazon.com/marketplace/pp/prodview-rxkns32my7r7m
- Cochrane Library data reuse:
  https://www.cochranelibrary.com/data
- OAIC Guide to health privacy:
  https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/health-service-providers/guide-to-health-privacy
- OAIC Australian Privacy Principles:
  https://www.oaic.gov.au/privacy/australian-privacy-principles
- OAIC APP 8 cross-border disclosure guidance:
  https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-8-app-8-cross-border-disclosure-of-personal-information
- TGA clinical decision support software guidance:
  https://www.tga.gov.au/resources/guidance/understanding-clinical-decision-support-system-software-regulation
- TGA software-based medical devices guidance:
  https://www.tga.gov.au/resources/guidance/understanding-how-we-regulate-software-based-medical-devices
- RACGP electronic clinical decision support position:
  https://www.racgp.org.au/advocacy/position-statements/view-all-position-statements/clinical-and-practice-management/electronic-clinical-decision-support
