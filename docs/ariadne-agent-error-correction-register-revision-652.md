# Ariadne agent error and correction register — revision 652

Date: 2026-08-24

Timestamp: 2026-08-24T01:06:23.5988946+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 652
incident_count: 1138
new_incident_ids: AER-1137,AER-1138
open_incident_count: 0
-->

## AER-1137

The first traceability-envelope closeout intent used descriptive incident-stage
values where the register accepts only a closed vocabulary. After that
correction, the first semantic verifier invocation used system Python rather
than the profile's bound virtual-environment interpreter. Both gates rejected
before verification commands, preparation, publication or pointer movement.
The corrected closeout uses `deterministic_verification` and the bound
interpreter throughout.

## AER-1138

The first candidate precommit continuation intent listed implementation and
test paths in `active_evidence_paths`, whose closed schema admits only
documentation and orchestration evidence roots. Preflight rejected it before
runtime-state materialisation or repository mutation. The rejected intent is
preserved and a distinct corrected intent using only admitted roots passed.
