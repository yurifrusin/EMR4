# Bernie LC4V4D1 Authoring-Defect Incident

Date: 2026-07-15

Status: confirmed development-evidence defect; protected evidence unaffected.

## Summary

The LC4V4D2 semantic-remediation audit found three contradictions in the
ordinary, inspectable LC4V4D1 development oracle. The frozen D1 fixture and
report remain unchanged for provenance, but the original D1 acceptance and
closeout counts are superseded for interpretation and remediation decisions.

The corrected D1 adjudication is:

| Classification | Frozen raw report | Audited interpretation |
|---|---:|---:|
| `authoring_invalid` | 0 | 3 |
| `parser_gap` | 23 | 20 |
| `policy_contract_gap` | 12 | 12 |
| `scorer_gap` | 0 | 0 |
| `planned_unavailable` | 0 | 0 |
| `supported_pass` | 25 | 25 |

The exact valid 20-case parser selection hash is
`sha256:0badec28ad533b630786d245e5ab47dee5655b83239869f7d0a2d12a8935d105`.

## Contradictory rows

1. `lc4v4d1_entity_duration_corrected_28` surfaces a correction to 45 minutes
   in turn 1, while its frozen normalized duration remains 30 minutes.
2. `lc4v4d1_entity_duration_negated_29` explicitly negates the 30-minute
   duration, while its frozen normalized duration retains 30 minutes.
3. `lc4v4d1_dialogue_ellipsis_multi_08` explicitly supplies 30 minutes in the
   second turn, while its frozen duration semantics say `omitted`.

These contradictions are proved from the authored utterances, source spans,
semantic labels, and normalized values. They are not inferred from current
parser output. They therefore cannot be used as parser-remediation targets.

## Cause and detection gap

D1 validated span coordinates and broad structural constraints but did not
enforce all cross-field semantic invariants for corrected, negated, and
explicitly supplied durations. Sol's original acceptance and Gemini's
independent review reproduced the frozen report and its existing validators;
neither performed the additional cross-field oracle audit that D2 exposed.

This is a bounded evidence-authoring failure, not evidence of general parser
regression or poor overall progress. It changes three cells in an ordinary
development diagnostic. It does not affect any protected holdout, live
provider, patient data, route, database, or write surface.

## Containment and prevention

- Preserve the frozen D1 fixture, report, hashes, and historical review as
  immutable provenance.
- Mark the old `diagnostic_valid` acceptance as superseded by an explicit
  acceptance amendment.
- Quarantine exactly these three rows from parser-remediation scoring.
- Fail closed when a corrected duration is not normalized to the final surfaced
  value, a negated duration retains a normalized value, an ambiguous duration
  collapses to one value, or an `omitted` duration has an explicit duration
  source span.
- Recompute and bind both the historical 23-case hash and the audited 20-case
  hash in D2 evidence.
- Require the independent D2 reviewer to audit this incident and the new
  cross-field validation, not merely reproduce aggregate counts.

No fixture repair is authorized in place. Any future corrected development
corpus version must be separately versioned and reviewed.
