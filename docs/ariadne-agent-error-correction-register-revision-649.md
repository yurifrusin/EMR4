# Ariadne agent error and correction register — revision 649

<!-- ariadne-agent-error-register-reading
revision: 649
incident_count: 1133
new_incident_ids: AER-1133
open_incident_count: 0
-->

## AER-1133

The first explicit-stage preparation typed
`orchestration/continuity/emr-compass.json` instead of the tracked
`orchestration/continuity/emr4-compass.json`. Exact-path existence validation
stopped the command before `git add`, so zero paths were staged and no file was
mutated. The corrected path was copied from the verified Git-status inventory;
the selected next rehearsal will replace manual transcription with a
machine-derived allowlisted stage manifest.
