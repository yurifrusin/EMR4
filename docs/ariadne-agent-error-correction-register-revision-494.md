# Ariadne agent error and correction register — revision 494

Date: 2026-08-19

Timestamp: 2026-08-19T01:23:24.5466521+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0573 preserves a repeated-literal patch that changed the wrong recurrence
count. The parallelism count was changed from five to seven while the intended
population-fixture count remained five. Both blocks are now patched with their
own recurrence signatures as unique context and receive exact readback.

Revision 494 contains 573 bounded incidents. All are corrected or contained;
none is open. These observations do not score a model or provider and confer no
product, data, provider, deployment or protected-ref authority.

## Prevention

The typed reducer removes repeated manual count patches. Until it is adopted,
every repeated-field patch must include the owning recurrence signature and be
read back with a neighboring sentinel before validation.
