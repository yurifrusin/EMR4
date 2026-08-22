# Ariadne Agent Error and Correction Register — Revision 638

Date: 2026-08-23

Timestamp: 2026-08-23T09:22:37.2550535+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 638
incident_count: 1059
new_incident_ids: AER-1050,AER-1051,AER-1052,AER-1053,AER-1054,AER-1055,AER-1056,AER-1057,AER-1058,AER-1059
open_incident_count: 0
-->

## AER-1050 — Pipeline placed directly after PowerShell foreach

The first closeout-inventory summary placed a pipeline directly after a
`foreach` statement block and PowerShell rejected the empty pipe element before
the summary ran. Assigning the loop results to an array and piping that array
produced the intended read-only summary.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1051 — Windows-invalid wildcard in retained-evidence search

A read-only ripgrep command supplied a wildcard as part of a Windows path.
Ripgrep rejected that target. A valid directory-scoped search supplied the
required retained evidence and changed no file.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1052 — Unmatched parenthesis in tool-call composer

The first JavaScript composer for a PowerShell file-size inventory contained an
unmatched parenthesis. The tool wrapper rejected it before PowerShell started.
The command was rebuilt from an explicit quoted path array.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1053 — PowerShell backtick not escaped in JavaScript template

The rebuilt file-size composer embedded PowerShell's tab escape inside a
JavaScript template literal, causing a second wrapper syntax rejection before
PowerShell invocation. Replacing it with `[char]9` produced the intended
read-only inventory.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1054 — Nonexistent Continuity graph directory searched

A read-only search named `orchestration/continuity/ariadne-continuity-graph` as
a directory although the graph is the file `emr4-continuity-graph.json` in the
Continuity root. Listing the root located the canonical file before the node
inventory was recomputed.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1055 — DateTime used as string-concatenation accumulator

A PowerShell formatter attempted to concatenate the parsed `created_at`
DateTime directly with a tab and status string. PowerShell tried to coerce the
status to a `TimeSpan` and rejected all twelve display rows. Casting every
field to string produced the intended read-only chronology.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1056 — Windows wildcard search pattern recurred

The invalid wildcard-path form from AER-1051 recurred once during the API-
manifest source pass. The search returned useful explicit-path results but a
nonzero target error. Subsequent searches use explicit files or valid directory
roots only.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1057 — Closeout subdirectory omitted from read path

A read-only lookup asked for the predecessor `closeout-intent.json` at the
operation root although the accepted layout places it under `closeout/`.
Listing the exact operation directory located and read the intended artifact.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1058 — Transactional node given three parents

The first idempotent clockwork check rejected the closeout intent because its
Continuity node listed the active predecessor and two historical Harness
evidence nodes as three `builds_on` relationships. The transaction schema
requires exactly one active predecessor. The two historical nodes remain
decision evidence, while the node retains only the active predecessor.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1059 — Descriptive incident stages used outside closed vocabulary

The second idempotent clockwork check rejected the corrected closeout intent
because its nine incident rows used five descriptive stage labels rather than
one of the clockwork's seven enumerated stages. All nine review and closeout
assembly rows now select the admitted `closeout` value. The rejected intent
hash is retained and the check changed no canonical surface.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,059 corrected or contained incidents and
zero open incidents after clockwork publication. These ten rows concern
local evidence inventory, command composition, path selection and one rejected
closeout relationship shape only. None
started a Harness, worker, provider, database or runtime, changed candidate or
product bytes, or moved a protected ref. They reinforce the adoption plan's
decision to keep clockwork interaction to sparse pre-dispatch and terminal
readings rather than add another procedural layer.
