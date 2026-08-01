# Reception One Receptionist-first v6.6 De-identified Note Plan

Status: active bounded repair plan
Recorded: 2026-07-30

## Purpose

Repair the sole v6.5 no-release terminal without revising any historical node.
The typed squeeze-in form, its goal, evidence bindings and proposal were exact
on both v6.5 turns. The deterministic proofreader rejected only because the
model repeated a patient or practitioner identifier in its internal
`decision_note`, including after the bounded correction code.

The complete original twenty-four-request authored-synthetic cohort will be
rerun, including every earlier pass. v6.5 remains immutable and no v6.5 ledger
may be reopened.

## Exact repair

The system instruction will define `decision_note` as a de-identified internal
control line:

- it may name the typed intent and a generic policy rationale;
- it must not contain a patient or practitioner display name, alias, raw
  reference or identifier;
- it must not copy a person-identifying fragment from the staff utterance or
  desk context; and
- after `decision_note_identifier`, the model must replace the complete note
  with a generic line that contains no person identifier.

An acceptable pattern is:
`Intent squeeze_in_assessment: assess squeeze-in under frozen policy.`

The deterministic proofreader remains unchanged. It will not redact, repair or
reinterpret a person-identifying note. The output schema, typed operator
catalogue, semantic-role constraint gate, desk context, 3072-token response
ceiling, temperature zero and 1024-token thinking budget remain unchanged.

## Frozen boundaries

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- identity:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: existing keyless impersonated service-account ADC;
- location: `australia-southeast1`;
- endpoint: `australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- 24 primaries and at most one terminal second call per case;
- absolute 48-call and USD 1 ceiling;
- no API key, static key, global endpoint, fallback, provider tool, grounding,
  retrieval, cache creation, product/database access, appointment write,
  product delivery, production, deployment or release; and
- raw prompts, raw provider responses, credentials, API-key information and
  hidden chain-of-thought are not retained.

The no-show-to-`dna` alias remains closed.

## Deterministic gates

Before an occupied call:

1. a person-identifying `decision_note` rejects with
   `decision_note_identifier`;
2. its correction ticket retains only the bounded field/code/path contract and
   no rejected prose;
3. a generic de-identified replacement note with the same exact typed form
   admits;
4. the system instruction explicitly teaches the field rule and correction
   action;
5. all twenty-four reference forms and all historical wrong forms retain their
   existing deterministic dispositions;
6. provider-blocked, real-isolation, focused, API Spine, Continuity, Compass,
   JSON, compilation, Ruff and whitespace gates pass;
7. the exact read-only Bernie/Sydney cloud-control preflight passes;
8. pre-run residue is zero; and
9. Continuity and rendered Compass revisions bind the frozen candidate.

Once occupied execution starts, no prompt, schema, proofreader, desk-context or
generation-setting change is permitted.

## Acceptance

Capability acceptance requires all twenty-four terminal outcomes to match
their frozen oracle, all ledgers and audit chains to close, no call after the
terminal result and zero task residue. Any mismatch closes v6.6 candidly and
releases no product capability.

The evidence remains a reused development cohort, not an independent holdout.
The Sydney locational path does not prove Australian physical or sovereign
processing.
