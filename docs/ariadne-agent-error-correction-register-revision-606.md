# Ariadne agent error and correction register — revision 606

Date: 2026-08-22

Status: **four corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 606
incident_count: 894
new_incident_ids: AER-0891,AER-0892,AER-0893,AER-0894
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

## AER-0894

The first closeout projection omitted the exact inherited boundary token
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`
while retaining a narrower descriptive successor boundary. The clockwork
published the internally valid projection, but the full current-baton
consistency suite rejected the missing exact vocabulary. The generation was
rolled back byte-exactly before any commit, and the source intent now carries
both the inherited token and the successor-specific constraint.

## Control reading

The first three observations share the same lesson: caller prose is not a source of
Git identity, repository path or schema shape. Git supplies identities, the
repository supplies paths and the schema supplies fields. The clockwork closeout
records the occurrences separately so recurrence and correction cost remain
measurable. AER-0894 adds the parallel rule for inherited policy vocabulary:
new restrictive wording supplements but never substitutes for a required exact
boundary token.
