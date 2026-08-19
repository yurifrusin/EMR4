# Ariadne agent-error and correction register — revision 567

Date: 2026-08-20

Timestamp: 2026-08-20T07:22:35.5977084+10:00 (Australia/Brisbane)

## Revision scope

Revision 567 adds AER-0657 for the orchestrator's rejected preterminal
observability review packet. The packet said that C03 contained 137 tests while
its exact seven-module command contained 85. Gemini returned `pass` without
challenging the false count, so Sol rejected the receipt as
`revision_required`; neither the receipt nor that statement is acceptance
evidence.

The corrected packet mechanically bound the exact 85 count and seven component
counts. After human-restored authentication, a fresh review passed all ten
commands against the unchanged candidate. The original evidence conflict is
attributed to orchestrator packet construction, not Gemini reasoning or the
Antigravity transport.

The first incident-intake publication then exposed AER-0658: one historical
register test still required the literal source cutoff `2026-08-19`, although
the new incident correctly advanced the canonical cutoff to `2026-08-20`.
The entire generation was rolled back byte-exactly. The corrected test now
derives the cutoff from the maximum validated incident date.

Before corrected publication, AER-0659 records one further orchestrator error:
the short commit `835ee7af` was manually expanded incorrectly in commentary.
The repository and dry run already held the correct machine-resolved full ID,
the user-facing correction was immediate, and no canonical artifact contained
the false value.

The second incident-intake publication then exposed AER-0660: two more
historical tests encoded current revision and agent-origin population as fixed
arithmetic formulas. That generation was also rolled back byte-exactly. The
tests now validate the canonical current revision document and direct
population properties without forecasting the next update.

The third incident-intake publication exposed AER-0661: the full historical
recurring-pattern literal list still rejected the newly derived post-baseline
peer group. That generation was rolled back byte-exactly. The literal list is
now frozen through AER-0656, while later patterns and counts are recomputed from
the validated current population.

The clockwork now derives AER-0657 through AER-0661 and all aggregate updates
from semantic observations in the closeout intent. The register contains 661
incidents, all corrected or contained and none open.

## Prevention

Every review packet with an exact test-count claim must bind the mechanical
collection of its exact command before dispatch. A qualifying closeout incident
enters through clockwork intent v2; callers cannot author the AER ID, revision,
origin, peer links, status, counts or pattern report. Current register tests
derive moving revision/count/cutoff/aggregate readings from the validated
population rather than retaining next-update literals.
Historical recurring-pattern fixtures have an immutable cutoff; post-baseline
patterns are current readings, not manually extended lists.
Full Git object IDs in commentary and reports are copied only from current
machine output or a persisted receipt; abbreviations are never manually
expanded.
