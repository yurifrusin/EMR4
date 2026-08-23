# Raisa local-only historical Diary access boundary convergence — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T02:20:53+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-local-only-historical-diary-access-boundary-convergence`

## Assets

- the default denial for all historical data;
- the exact bounded local Diary privacy exception;
- the accepted non-executable real-access contract and its byte identity;
- denial of product, patient, appointment, clinical and protected data;
- the unopened historical Diary archive and any future ignored local binding;
- the live active-operation latch and clockwork generation lineage; and
- fixed protected Git refs and preserved untracked files.

## Threats and controls

### Broad exception hidden in prose

Threat: a model substitutes a plausible descriptive label for the intended
Diary exception, accidentally authorising a root, date range or data category
that was never reviewed.

Control: every boundary containing `historical` belongs to a closed immutable
set. Any unknown historical label fails before generation. The exception is one
exact token plus every exact scope member, not free-form prose.

### Partial scope publication

Threat: the clock publishes access while omitting a byte cap, path constraint,
cleanup rule, provider denial or downstream-use restriction.

Control: the bounded mode is admitted only when the complete set is present.
Removal or mutation of any member rejects the tick. Extra historical labels
also reject it.

### Contract drift

Threat: the boundary keeps its name after the referenced contract gains a real
path, becomes executable, permits network/model use or changes a limit.

Control: the exact SHA-256 of the accepted contract is part of the closed
vocabulary. A repository test independently reads the contract and verifies
its digest and semantic limits. Contract changes therefore fail until reviewed
code, tests and authority move together.

### Denial/exception contradiction

Threat: `no_historical_data_access` or the legacy compound denial coexists with
an exception, leaving downstream readers to choose whichever meaning they
prefer.

Control: historical modes are mutually exclusive. The exact exception rejects
both denial tokens, and the typed full denial rejects all exception members.

### Product-data denial weakened while separating history

Threat: extracting `historical` from the compound token inadvertently removes
the denial for current product, patient, appointment, clinical or protected
data.

Control: every new typed mode requires the independent exact token
`no_product_patient_appointment_clinical_or_protected_data`. The legacy compound
token remains a full-denial compatibility state only.

### Legacy state becomes an access escape

Threat: backward compatibility with already-published latches allows the old
compound token to be paired with a new access token.

Control: the legacy state admits no other historical vocabulary member and
cannot coexist with the bounded mode. It remains denial-only.

### Premature archive contact

Threat: validating the authority vocabulary discovers, lists or samples the
archive it is intended eventually to protect.

Control: this tranche reads only committed source, tests and the data-free
subgate contract. No archive path is bound, and archive open/list/search/
sample/hash/parse is outside authority.

### Downstream authority inflation

Threat: a successful bounded local privacy reading is interpreted as fixture,
model, provider, product or production approval.

Control: the exact mode fixes `locally_restricted_candidate` as the strongest
result and expressly denies fixture, memory, RAG, product runtime, route, API,
client, database and configuration use. Later promotion remains a new gate.

## Residual risk

Typed clockwork boundaries can prevent unreviewed authority descriptions, but
they cannot establish that a future parser correctly understands every legacy
Diary field or that a transformed trajectory is non-identifying. The following
bounded measured probe must still fail closed on unexpected schema, leakage,
poor utility or contextual linkability. Its strongest success remains ignored
local research retention only.
