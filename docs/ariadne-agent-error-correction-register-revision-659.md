# Ariadne agent error and correction register — revision 659

Date: 2026-08-24

Timestamp: 2026-08-24T09:01:37.5638009+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 659
incident_count: 1149
new_incident_ids: AER-1148,AER-1149
open_incident_count: 0
-->

## AER-1148

The complete pre-access historical-Diary regression gate found one older
attempt-specific test still asserting that the v2 ignored root was the active
root. That made immutable prior evidence claim mutable current ownership.

The old assertion was removed and the current v3 test remains the sole owner of
the active-root check. All 222 controls passed before metadata bind or private
content access. The correction caused one deterministic suite rerun and zero
historical content reruns.

## AER-1149

Closeout assembly incurred a compound series of typed-form and dependency
ordering lapses. Drafts used an unregistered incident stage, a coined category,
custom historical boundary labels and then omitted the required exact denial
mode. The corrected semantic validator passed, but its reporting wrapper
assumed one absent top-level key. Finally, the first admitted driver tick and a
direct diagnostic tick found that both incident rows referenced this human
register reading before the file existed.

All checks failed closed before publication or staging. The accepted form reads
incident values and historical modes from executable constants, uses ordinary
private-archive denials alongside `no_historical_data_access`, reports only
keys present in the admitted object, and includes this bounded human reading
before tick projection. The ergonomic cost is preserved in the tranche
efficacy reading rather than treated as product or privacy failure.
