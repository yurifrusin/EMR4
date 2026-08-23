# Ariadne agent error and correction register — revision 645

<!-- ariadne-agent-error-register-reading
revision: 645
incident_count: 1120
new_incident_ids: AER-1116,AER-1117,AER-1118,AER-1119,AER-1120
open_incident_count: 0
-->

## AER-1116

One direct-path latch invocation failed because the repository module must be
run with `python -m`. The module form was used on the fresh attempt and passed.

## AER-1117

One post-restart receipt draft repeated a protected Git object in prose. The
preflight rejected it before acceptance; the corrected receipt uses only the
machine-owned Git snapshot.

## AER-1118

One packet draft copied the wrong admission schema vocabulary. The canonical
call returned `snapshot_invalid`; the exact product vocabulary was read from
source, corrected and all focused and surrounding tests passed.

## AER-1119

One surrounding-suite command guessed a nonexistent test filename. Repository
search resolved the exact existing test path and the complete suite passed.

## AER-1120

One closeout intent used the descriptive Continuity node kind `rehearsal`,
which is outside the graph's closed vocabulary. The first clockwork check
failed before publication or pointer movement; the corrected intent selects
the admitted `integration` kind.
