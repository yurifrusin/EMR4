# Ariadne agent error and correction register — revision 491

Date: 2026-08-19

Timestamp: 2026-08-19T01:09:20.7083994+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0569 preserves the orchestrator's use of a two-process shell pipeline while
discovering the current-baton consistency test. The exact path was recovered,
and every successor command returned to the one-executable-per-invocation
discipline.

AER-0570 preserves the follow-up lookup's nonexistent companion-script operand.
The scripts inventory was then resolved with one `rg --files` invocation and
only the existing agent-error-register validator was used.

Revision 491 contains 570 bounded incidents. All are corrected or contained;
none is open. These observations do not score a model or provider and confer no
product, data, provider, deployment or protected-ref authority.

## Prevention

These incidents reinforce the clockwork boundary rather than adding another
prose reminder: a later typed command-manifest executor should resolve each path
before dispatch and admit exactly one executable plus argument vector at each
causal tick. Until that mechanical admission exists, exact inventory resolution
and one-executable invocations remain the controlling discipline.
