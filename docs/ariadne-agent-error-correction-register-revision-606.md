# Ariadne agent error and correction register — revision 606

Date: 2026-08-22

Status: **three corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 606
incident_count: 893
new_incident_ids: AER-0891,AER-0892,AER-0893
open_incident_count: 0
-->

## AER-0891

The orchestrator drafted a guessed 40-character candidate identity before
machine resolution. The draft was corrected before receipt generation and the
measurement field was changed to require the machine snapshot rather than a
caller-authored identity. No false identity reached a receipt or publication.

## AER-0892

A read-only verification command guessed the sanitizer and wrapper paths from
memory. The missing-path failure occurred before any executable process; both
paths were then resolved from repository-owned names and their exact hashes
passed. The one permitted Node execution remained unconsumed.

## AER-0893

The first post-execution summary query guessed evidence field names and returned
null readings. The evidence and process-envelope schemas were read directly,
after which the typed fields passed. The query changed no artifact and caused
no process rerun.

## Control reading

All three observations share the same lesson: caller prose is not a source of
Git identity, repository path or schema shape. Git supplies identities, the
repository supplies paths and the schema supplies fields. The clockwork closeout
records the occurrences separately so recurrence and correction cost remain
measurable.
