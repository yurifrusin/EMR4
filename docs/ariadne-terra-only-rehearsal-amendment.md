# Ariadne Terra-only Work-Cell Rehearsal Amendment

Date: 2026-07-24
Owner: GPT Sol
Authority: Yuri's instruction, “Just run the Terra rehearsal for now”
Status: superseded before consumption by Yuri's restored two-lane instruction

## Effect

This amendment narrows
`docs/ariadne-terra-gemini-comparative-rehearsal-plan.md` to the Terra lane
for the present tranche. It overrides only the earlier requirement that both
provider credentials be present before Terra authority is consumed.

All shared-task, isolation, provider, budget, output, proofreader, evidence,
failure, cleanup, no-retry, no-fallback, and closed-surface rules remain
unchanged.

No authority was consumed while this amendment was active. Yuri restored the
original sequential Terra-then-Gemini plan on 2026-07-24; this document remains
only as an immutable decision-history record.

## Exact live authority

- Read the machine, user, or process `OPENAI_API_KEY` without printing,
  hashing, persisting, or placing it in a command line or container
  environment.
- Start the prepared Terra broker and provider-neutral work cell.
- Consume `terra-single-use-ledger.json` immediately before the work cell
  starts.
- Permit at most one provider-generating request to
  `POST https://api.openai.com/v1/responses` using exactly
  `gpt-5.6-terra`, medium reasoning, no tools, `store: false`, strict
  structured output, and the 2,048-output-token cap.
- Apply the common provider schema, unchanged full schema, and unchanged
  deterministic proofreader.
- Persist only sanitised hashes, sizes, numeric usage/cost estimate, fixed
  verdicts, effective container policy, and cleanup evidence.
- Remove and verify absence of the Terra cell, broker, private network,
  temporary secret files, and Terra-specific image tags.

## Gemini exclusion

No Gemini credential check, broker start, work-cell start, prompt
transmission, provider call, ledger consumption, verdict, comparison, fallback,
or substitution is authorised in this tranche. The Gemini ledger must remain
`available`. Its prepared credential-free image tags may remain for a future
fresh instruction.

## Result rule

The exact pass result is `ariadne_terra_only_rehearsal_pass` and requires:

- exactly one Terra provider call;
- successful common and full schema validation;
- deterministic proofreader pass with five verified output dispositions;
- no raw prompt, raw provider response, draft payload, or credential in
  persisted evidence;
- complete Terra cleanup; and
- Gemini authority still available with zero Gemini calls.

Any occupied-process failure is
`ariadne_terra_only_rehearsal_revision_required`, consumes Terra authority,
and grants no retry. A failure before ledger consumption is a closed preattempt
gate and does not consume Terra authority.
