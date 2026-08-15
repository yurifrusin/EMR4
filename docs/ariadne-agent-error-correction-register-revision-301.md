# Ariadne agent error and correction register — revision 301

Date: 2026-08-15

Timestamp: 2026-08-15T23:09:08+10:00 (Australia/Brisbane)

Revision 301 records AER-0340. The register now contains 340 bounded known
incidents, all corrected or contained by an explicit control.

AER-0340 preserves the failed first focused acceptance run for the AER-0335
through AER-0339 batch. Sol updated the main revision, ID range, aggregate
dictionaries and recurrence equality but left the standalone agent-origin
population at 230. The full focused suite rejected that fixture because the
register then contained 234 agent-behavior incidents.

No failed result was admitted. Adding this incident makes the final exact
agent-behavior population 235. Revision, total incident count, standalone
origin length, aggregate dictionaries and recurrence equality are reconciled
to a fresh report before the complete corrected rerun.

This is the third occurrence of
`orchestrator.agent_error_register_population_fixture_update_incomplete`, after
AER-0255 and AER-0318. The strengthened control requires a mechanical search of
the entire focused test for every population literal before the first full run,
followed by comparison against a freshly generated pattern report.
