# Ariadne Agent Error and Correction Register — Revision 637

Date: 2026-08-23

Timestamp: 2026-08-23T08:34:31.0895778+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 637
incident_count: 1049
new_incident_ids: AER-1041,AER-1042,AER-1043,AER-1044,AER-1045,AER-1046,AER-1047,AER-1048,AER-1049
open_incident_count: 0
-->

## AER-1041 — Sequential Git-summary control not followed

The invalid PowerShell pattern from AER-1036 recurred when the orchestrator
again attempted to combine `git merge-base` and `$LASTEXITCODE` inside a
parenthesized assignment. Parsing failed before any Git reading or mutation.
The sequential form passed. For acceptance, this tranche now reuses the
existing preflight `git_refs_snapshot`; ad hoc composite summaries have no
acceptance authority and no new Git-summary layer was added.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1042 — Over-generalized expected validator error

The first focused packet expected every semantic mutation to return the generic
`contract semantics changed` error. A seven-character planning source correctly
failed earlier at the more specific `planning source changed` guard. The test
now expects that exact fail-closed reason.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1043 — Exact decomposition result token omitted from plan

The first focused packet found that the plan described the unchanged counts and
not-ready verdict but did not repeat exact token
`gap_decomposed_not_satisfied`. Adding the token changed no scope or meaning.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1044 — Markdown line wrap treated as semantic absence

The second focused packet searched for one exact phrase across a Markdown line
break without normalizing whitespace. The phrase was present semantically. The
test now normalizes whitespace before checking it.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1045 — Nonexistent surrounding-test path supplied

The first broader provider-free packet named a separate environment-
architecture plan test that does not exist. The wrapper rejected the path
before test collection. Repository file discovery then selected the exact
existing architecture test; the corrected 183-test packet passed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1046 — Windows-invalid wildcard supplied to ripgrep

A read-only search included an invalid PowerShell/Windows wildcard path after
two explicit valid settings paths. Ripgrep read the explicit paths but returned
an error for the wildcard. A directory-scoped search then produced the intended
continuation-event evidence. No file or workflow state changed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1047 — Next-operation boundary floor omitted

The first clockwork check rejected the closeout intent with
`tick_next_boundaries_floor`. The intent used a semantically broader
ordinary-practice restriction but omitted the exact code-owned required token
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
No canonical file was changed. The required token was added, the rejected check
was preserved, and the idempotent check was rerun.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1048 — Boundary-floor rejection misread as a count

The orchestrator interpreted `tick_next_boundaries_floor` as a minimum list
length and added a semantically correct external-choice boundary without first
reading the code-owned required set. The second check rejected the intent for
the same reason because the exact required ordinary-practice token was still
absent. The required set was then read directly, the exact token was added and
the second rejection was preserved. Future floor corrections must inspect the
code-owned set rather than infer meaning from the rejection label.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1049 — Register revision incremented per incident

While preserving AER-1047 and AER-1048, the orchestrator incorrectly advanced
the human register-summary revision once for each incident rather than once for
the tranche. That renamed revision 637 to 639 and left earlier observation
evidence paths pointing to a missing file. The third clockwork check rejected
the incident-register projection before canonical mutation. The summary was
restored to revision 637 with incident count 1,049 and all evidence paths were
rebound to that one tranche revision.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,049 corrected or contained incidents and
zero open incidents after clockwork publication. These nine rows concern local
orchestration commands, exact test expectations and documentation tokens only.
None caused a database/runtime rerun, secret or environment access, product
effect, provider call or protected-ref movement, and they make no comparative
model-quality claim.
