# Reception One Receptionist-first v6.3 Form Toolkit Repair Plan

Status: authorised; provider-free implementation pending
Recorded: 2026-07-30

## Purpose

v6.3 is a new descendant of the immutable v6.2 result. It addresses only the
three terminal v6.2 failure classes and then reruns all twenty-four original
authored-synthetic requests to detect regression.

It does not rescore or alter v6.2 evidence.

## Repairs

1. Raise `maxOutputTokens` from 2048 to 3072 while retaining temperature 0,
   the 1024-token thinking budget, hidden-thought exclusion and USD 1 ceiling.
   This accommodates the closed form after the thinking budget and targets the
   repeated `MAX_TOKENS` result.
2. Explain the existing typed source discipline as part of the receptionist's
   form toolkit: a mention binding is not a resolved entity; it must pass
   through its resolver before its typed output feeds later operators.
3. Explain the common selected-appointment move sequence without preselecting
   the request's goal: resolve the mentioned patient, read the stamped selected
   appointment, search with typed practitioner/date/time/duration sources, and
   prepare the move proposal.
4. Require clarification when a requested status has no stamped
   `binding:status`. v6.3 does not add a `no-show` to `dna` alias and does not
   decide that product semantic question.

The output schema, operator table, binding table, deterministic proofreader,
desk-context schema and proposal-only release contract are unchanged.

## Evaluation

Provider-free gates cover all twenty-four deterministic reference forms,
explicitly reproduce the three v6.2 failures, verify the higher ceiling and
new source instructions, and rerun real isolation.

If those gates pass, the complete twenty-four-case cohort may run through the
same exact Sydney Vertex lane. Each case receives one primary and at most one
terminal second call; the absolute ceiling is forty-eight calls and USD 1.
There is no call after an exact admission, no third call, and no prompt/schema
change during the occupied cohort.

## Frozen boundary

- Google Vertex AI `gemini-2.5-flash`;
- project `bernie-emr4-dev`;
- exact Bernie service account through existing keyless impersonated ADC;
- `australia-southeast1` and
  `australia-southeast1-aiplatform.googleapis.com`;
- authored-synthetic data only;
- no API key, service-account key, global endpoint or fallback;
- no tools, grounding, retrieval, cache creation, database/product access,
  confirmation, write, delivery, production or deployment.

This can establish only the configured and observed Sydney locational request
path, not Australian physical or sovereign processing.
