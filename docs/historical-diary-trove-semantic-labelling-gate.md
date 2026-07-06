# Historical Diary Trove Semantic Labelling Gate

Date: 2026-07-06
Sprint: H15 de-identification review gate
Scope: precondition for any semantic appointment labelling from the historical
diary trove
Privacy posture: synthetic tests and policy template only; no raw diary files,
filenames, document text, exact source document timestamps, patient labels,
staff labels, or visible diary content committed.

## Rule

Semantic labelling of historical diary deltas is blocked unless a gate payload
passes:

```text
scripts/historical_diary_deidentification_gate.py
```

The default committed template is intentionally blocked:

```text
docs/historical-diary-trove-semantic-gate-template.json
```

This means future sprints may continue neutral structural work, but must not
create committed semantic fixtures from the trove until the gate is explicitly
reviewed and changed.

## What The Gate Enforces

The validator requires:

- raw processing remains local only;
- raw data is not sent to external providers;
- raw or extracted text is not committed;
- identifying labels are not committed;
- date policy is explicit;
- resource labels are synthetic;
- text policy is either no text export or bucket flags only;
- committed fields come from a safe structural allowlist;
- forbidden categories include names, phone numbers, Medicare numbers,
  addresses, notes, staff labels, original filenames, exact source timestamps,
  and external raw uploads.

If semantic fixture promotion is approved later, the gate also requires:

- a safe reviewer identifier;
- explicit semantic-labelling acknowledgement;
- all forbidden categories still present;
- all privacy booleans still restrictive.

## Allowed While Blocked

Allowed work while the gate decision is `blocked`:

- neutral count/range reporting;
- ordered neutral snapshots;
- neutral transition summaries;
- neutral large-delta triage;
- neutral transition-neighborhood reporting;
- runtime and guardrail checks.

Blocked work while the gate decision is `blocked`:

- committed appointment create/move/delete/status labels derived from raw
  historical content;
- committed redacted diary fixtures;
- LLM/Gemini interpretation over raw diary files or extracted raw text;
- committed examples containing original labels, notes, filenames, or exact
  source timestamps.

## Recommendation

Next historical-trove sprint should either keep broadening neutral-only samples
under H10 guardrails, or prepare a concrete gate-review packet for Yuri before
semantic fixture promotion begins.
