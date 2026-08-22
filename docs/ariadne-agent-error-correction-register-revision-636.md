# Ariadne Agent Error and Correction Register — Revision 636

Date: 2026-08-23

Timestamp: 2026-08-23T07:53:10.3671912+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 636
incident_count: 1040
new_incident_ids: AER-1036,AER-1037,AER-1038,AER-1039,AER-1040
open_incident_count: 0
-->

## AER-1036 — Invalid PowerShell grouping in read-only Git summary

The first rehydration Git-summary command placed a native command and
`$LASTEXITCODE` assignment inside a parenthesized expression that PowerShell
could not parse. It changed nothing. A simpler sequential command performed the
same read-only checks successfully.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1037 — Manual Git IDs in machine-snapshot receipt prose

The first fresh preplanning runtime state repeated three Git object IDs in its
human source-evidence sentence. The receipt correctly rejected caller-authored
Git bindings because its machine snapshot owns those readings. The rejected
receipt was preserved; prose without manual IDs produced a passing receipt
with `manually_supplied_object_id_count` zero.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1038 — Exact verdict token omitted from threat delta

The first focused candidate run found that the threat delta described the
unchanged not-ready verdict only in prose. The deterministic plan test required
the exact closed-vocabulary token. Adding the token changed no acceptance
meaning and the next run advanced to the following assertion.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1039 — Exact remaining-gap token omitted from threat delta

The second focused candidate run found the analogous omission for the sole
remaining environment/secret-posture dimension. Adding the exact dimension ID
made the threat delta mechanically traceable; the third focused run passed all
twenty tests.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1040 — Descriptive closeout label outside the indexed vocabulary

The first clockwork check used a new descriptive Baton acceptance label rather
than selecting the existing rolling label from the hash-bound compaction
manifest. The clockwork rejected `tick_baton_compaction_unindexed` before
generation construction or canonical mutation. The rejected check is preserved
and the corrected intent uses `Current DeepSeek native Harness acceptance`.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,040 corrected or contained incidents and
zero open incidents after this clockwork publication. These five rows describe
workflow behavior only. None caused a database/runtime rerun, product effect,
provider call or protected-ref movement, and they make no comparative model-
quality claim.
