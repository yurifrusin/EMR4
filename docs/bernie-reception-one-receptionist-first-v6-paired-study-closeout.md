# Reception One Receptionist-first v6 Paired Study Closeout

Status: closed — capability threshold failed safely
Recorded: 2026-07-30

## Result

The receptionist-first v6 paired development cohort is complete.

All twenty-four reused authored-synthetic cases ran through the exact
`gemini-2.5-flash` Sydney Vertex lane. Twenty-seven one-use calls were consumed:
twenty-four primaries and three proofreader-ticket replacements. Every ledger
is consumed, no call followed an admitted case, no fallback occurred, and final
container, network, image, process and temporary-credential residue is clear.

The exact-oracle result is 9/24. Twenty-three cases released an in-memory typed
value behind the human gate; one released nothing after an HTTP 200 response
failed the local JSON admission boundary. Fourteen of the twenty-three releases
were structurally valid and internally consistent but semantically wrong.

The result is therefore:

`reception_one_receptionist_first_v6_paired_development_fail_closed`

## What improved

The model produced a separately auditable, concise natural receptionist
response alongside the typed form. The broker never scraped that prose into
typed fields. On twenty-three parsed responses, the deterministic gate admitted
only natural/form pairs that agreed and made no completed-write claim.

The squeeze-in family passed 2/2; safe clarification passed 4/5; create passed
3/4, with the fourth case rejected before schema admission rather than released.

## What failed

Move, resize and cancel passed 0 cases; explicit status changes passed 0/2.
Across thirteen such requests, the model ignored the already grounded
`selected_appointment` binding and asked which appointment was intended. The
proofreader admitted those clarification forms because it checked structural
typing and prose/form agreement, not whether an explicit recognised intent cue
had been contradicted.

The converse occurred once: a noun-only list of appointment details was
converted into a create proposal despite no booking action being requested.

Three correction turns repaired only decision-note/form disagreement; the
replacement forms remained semantically over-cautious clarifications.

## Diagnosis

The main mismatch is not colloquial language recognition. The natural responses
show that the model understood words such as “reschedule,” “longer,” “call off”
and “completed.” It instead treated the form's request-local binding table as
mere possibilities rather than broker-grounded stamped facts, so it
re-litigated an appointment identity already supplied by
`binding:selected_appointment`.

The second mismatch is architectural: agreement between the receptionist's
speech and typed form is necessary but not sufficient. A confidently
self-consistent misunderstanding still needs an independent semantic veto.

## Bounded next repair

A separately versioned development repair should:

1. teach that binding-table entries are grounded facts and that a supplied
   selected-appointment binding resolves the target;
2. retain clarification for noun-only details without an action;
3. add a one-way proofreader assertion for explicit intent already recognised
   by the deterministic adapter, without making unknown novel language
   impossible; and
4. replay only the fifteen misses as development cases under a new contract.

This v6 record and its twenty-seven consumed calls remain immutable.

## Cost and usage

- prompt tokens: 69,776;
- visible candidate tokens: 9,368;
- thinking tokens: 16,699;
- total tokens: 95,843; and
- estimated application cost: USD 0.1017009 under the recorded public pricing
  formula.

No thought content or summary was requested or retained.

## Claim limit

This evidence proves the configured and observed
`australia-southeast1-aiplatform.googleapis.com` request path, keyless
impersonated Bernie ADC use, bounded dual-channel audit, no-write release and
complete cleanup. It does not prove Australian physical or sovereign
processing, independent holdout improvement, exhaustive language reliability,
production fitness, or safety for real, product-derived, patient, health,
clinical, protected or historical data.
