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

The clockwork now derives AER-0657 and all aggregate updates from a semantic
observation in the closeout intent. The register contains 657 incidents, all
corrected or contained and none open.

## Prevention

Every review packet with an exact test-count claim must bind the mechanical
collection of its exact command before dispatch. A qualifying closeout incident
enters through clockwork intent v2; callers cannot author the AER ID, revision,
origin, peer links, status, counts or pattern report.
