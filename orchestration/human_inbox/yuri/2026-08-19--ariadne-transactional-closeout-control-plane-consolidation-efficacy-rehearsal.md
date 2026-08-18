# Transactional closeout clock and DeepSeek broker coupling

Date: 2026-08-19

Timestamp: 2026-08-19T02:22:38.3870606+10:00 (Australia/Brisbane)

Status: accepted as a shadow candidate; no live control replaced

## Lay summary

The clockwork idea works in rehearsal. Ariadne can take one structured reading,
validate it before writing anything, derive its ledgers from that reading, and
hand the DeepSeek broker a sealed work order. The broker's events then continue
the same numbered, hash-linked clock instead of creating a second bureaucracy.

The candidate is smaller in the measured maintenance comparison and eliminates
the controlled reruns in the frozen sample. It is slower in milliseconds, so I
am not presenting speed as a benefit. Its value is consistency, traceability and
fail-closed publication.

The old closeout process then gave us unusually vivid evidence: fourteen further
contained clerical failures occurred while synchronizing duplicated fields such
as IDs, enum labels, counts, relationships and ordering. Nothing product-facing
was harmed, but these are exactly the avoidable reruns the clock is designed to
remove.

I have accepted the mechanism as a shadow candidate, not switched it on as the
live record keeper. The next development tranche returns to default-off check-in
admission-control architecture. No decision or action is required from you.

## Technical summary

Exact reviewed source is
`762cd8fd1a6493f4d4b82e24f97d851531b6f7f0`. The frozen comparison is 6 files /
1,002 lines versus 5 files / 981 changed-or-new lines; 72 manual constants versus
54 manifest leaves; 12 publication calls versus one atomic rename; and 7
controlled retries versus zero. Clean candidate timing is slower (985.012 ms
versus 321.402 ms) and is non-authoritative.

The journal validates contiguous sequence, stable identity, prior-event digest
and canonical event digest. WorkOrders bind source commit, authority/boundary
digests and exact tool posture. The broker verifies the WorkOrder digest before
listening and continues the journal chain. Eight injected write faults leave no
published generation.

The first Gemini pass was rejected because it overstated evidence deferral. The
replacement Gemini 3.7 Flash/high veto reproduced current-node rejection and
passed all nine commands at the unchanged clean reviewed HEAD. The complete
revision-509 register suite passes with 588 bounded incidents, all closed.

No live clockwork control was adopted or retired. No product route,
configuration, practice posture, patient/clinical data, occupied DeepSeek
session, deployment, Pages or protected ref changed. The continuing non-PHI
Pushover request is `2bc5eb1c-238a-437c-b9af-895bd89b837a`.
