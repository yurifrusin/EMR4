# Ariadne Agent Error and Correction Register — Revision 640

Date: 2026-08-23

Timestamp: 2026-08-23T11:20:38.5755231+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 640
incident_count: 1087
new_incident_ids: AER-1083,AER-1084,AER-1085,AER-1086,AER-1087
open_incident_count: 0
-->

## AER-1083 — Preplanning narrative duplicated machine-owned Git bindings

The first typed-input runtime-state draft repeated four full Git object IDs in
the Git-ref narrative. The orchestrator preflight rejected the draft before it
could become an accepted receipt. Removing the manual values and relying only
on the machine snapshot passed with zero manually supplied objects.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1084 — Active acceptance draft named descriptive rather than retained paths

The first draft named three plausible descriptive paths for the accepted
environment-manifest architecture instead of its exact retained default-off
manifest-secret-posture paths. Exact reads exposed the mismatch before
implementation; the existing document, contract and schema paths replaced the
draft and the receipt was regenerated.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1085 — Typed-input capability guard matched an ordinary word fragment

The first source guard searched for `environ`, which appears inside the required
`environment_identifier` field. The focused suite rejected its own false
positive. Matching only the actual `os.environ` API restored the intended
capability check.

Origin: repository. Severity: low. Status: corrected and contained.

## AER-1086 — Historical descendant tripwire could not see the precommit candidate

The first updated gap-decomposition tripwire compared the planning source only
with committed `HEAD`, so it could not see the newly staged unmounted module
during precommit verification. Comparing the planning source directly with the
working/index view preserved the exact allowlist and made the authorized
candidate visible before commit.

Origin: repository. Severity: moderate. Status: corrected and contained.

## AER-1087 — Unhashable categorical input could escape closed denial

Sol source review found that a list supplied to a frozenset-backed categorical
field could raise before returning `evidence_shape_invalid`. Every category now
requires exact string type before membership, with hostile list regressions for
role, credential-slot and break-glass fields.

Origin: repository. Severity: moderate. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,087 corrected or contained incidents and
zero open incidents after clockwork publication. The preplanning machine gate
prevented manual Git evidence from becoming authoritative, and the remaining
four observations were corrected before source acceptance. No correction
opened a provider, Harness session, external evidence, secret, database, route,
ordinary-practice admission, deployment, Pages action or protected ref.
