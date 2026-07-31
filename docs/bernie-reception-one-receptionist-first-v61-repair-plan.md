# Reception One Receptionist-first v6.1 Targeted Repair

Status: provider-blocked gates passed; occupied gate pending
Recorded: 2026-07-30

## Purpose

v6.1 is a separately versioned, targeted development descendant of the closed
v6 paired study. It tests only the fifteen v6 misses. It neither edits nor
rescores v6 and is not an independent holdout.

The model remains a medical receptionist. JSON is the API transport for one
paper-like bureau packet containing:

- a natural receptionist response;
- one bounded decision note;
- evidence-utterance indices; and
- a typed form.

The natural response is retained beside the typed form for bounded audit and
troubleshooting, but is never parsed into form fields and has no command
authority.

## Repair hypothesis

The closed v6 evidence showed that Gemini usually understood the colloquial
request but treated the grounded binding table as optional and asked again for
an appointment already supplied as `binding:selected_appointment`. Fourteen
schema-valid, internally consistent but semantically wrong forms were
therefore admitted. A fifteenth case was rejected before schema admission.

v6.1 changes only:

1. the desk instruction, which calls binding-table rows broker-grounded
   stamped facts and requires the selected appointment to be used;
2. explicit mapping guidance for move, resize, cancel and status language;
3. a one-way proofreader assertion when the existing deterministic adapter
   already recognizes a supported explicit intent; and
4. a noun-fragment veto for grounded appointment details without an action.

The assertion does not require every model form to match the deterministic
adapter. If the adapter does not recognize a novel action and the utterance is
not a grounded noun fragment, the candidate continues through the unchanged
typed compiler and proofreader. The proofreader never chooses or writes a
replacement form.

## Frozen occupied boundary

- provider/model: Google Cloud Vertex AI `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: keyless impersonated ADC only;
- location/hostname: `australia-southeast1` /
  `australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- cases: exactly the fifteen recorded v6 misses;
- maximum: fifteen primary calls and at most one closed correction per case;
- absolute v6.1 call ceiling: 30;
- incremental application-cost ceiling: USD 1;
- temperature: 0;
- thinking budget: 1024; hidden thought content excluded;
- no API key, service-account key, global endpoint or fallback;
- no tools, grounding, retrieval, cache creation, database/product access,
  write, confirmation, delivery, deployment or release.

Each call uses a distinct one-use ledger. Each case stops after its first
admitted result or terminal second turn. Prompt, schema, generation settings
and proofreader remain frozen during the occupied cohort.

## Acceptance

Before the occupied cohort:

1. all fifteen deterministic reference forms admit;
2. the fourteen reconstructable wrong v6 forms fail the new assertion;
3. the historical pre-schema failure remains only a bounded classification;
4. an unknown novel typed composition is not closed merely because the
   deterministic adapter lacks its verb;
5. a two-turn real-isolation rehearsal passes with non-root, read-only,
   network-none, credential-free cells and no residue;
6. focused, repository-only, API Spine, schema and static checks pass;
7. Continuity and Compass advance together, and the rendered Compass validates;
8. the exact existing Bernie ADC and control posture pass read-only preflight;
   and
9. independent process, container, network, image and credential residue is
   clear.

The targeted occupied result passes only if all fifteen final dispositions
equal their deterministic reference outcomes and all cleanup/ledger gates
pass. Otherwise it fails closed and preserves the complete evidence.

## Claim limit

This tranche can show whether the narrow prompt and proofreader repair improves
the fifteen known authored-synthetic v6 misses through the configured and
observed Sydney locational request path. It cannot prove holdout
generalisation, production fitness, Australian physical or sovereign
processing, or safety for real, product-derived, patient, health, clinical,
protected or historical data.
