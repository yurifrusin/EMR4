# Ariadne Agent Error and Correction Register — Revision 641

Date: 2026-08-23

Timestamp: 2026-08-23T12:01:25.0104668+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 641
incident_count: 1096
new_incident_ids: AER-1088,AER-1089,AER-1090,AER-1091,AER-1092,AER-1093,AER-1094,AER-1095,AER-1096
open_incident_count: 0
-->

## AER-1088 — Closeout check ran before the prospective register reading existed

The typed-input closeout check correctly rejected an intent whose prospective
revision document had not yet been written. Canonical state remained unchanged;
the exact prospective reading was created before the next attempt.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1089 — New Baton label had not been admitted to the compact index

The second typed-input closeout check proposed a descriptive active acceptance
label absent from the compact Baton index. The check rejected it before
publication. Reusing the existing indexed native-Harness acceptance slot while
retaining predecessor evidence restored the bounded active row.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1090 — Active acceptance carried two incident-register revisions

The third typed-input closeout check found both the predecessor and prospective
register documents in one active acceptance row. The current register path is
singular by design. Removing only the superseded revision from the active row
passed; its historical lookup remains in the immutable index.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1091 — Capability-free assertion used an unguarded attribute lookup

The first evaluator test called `getattr` without a default while proving that
the result exposes no `admit` or `execute` method. The expected absence raised
inside the test rather than producing the intended assertion. A `None` default
made absence itself the checked condition.

Origin: repository. Severity: low. Status: corrected and contained.

## AER-1092 — Issued-boundary test expected the wrong evidence stage

At the manifest's exact issued boundary the role evidence was current, but the
first rotation observation was still in the future. The initial test expected
`role_evidence_invalid`; the evaluator correctly returned
`rotation_evidence_invalid`. The expectation now follows the frozen evaluation
order and exact timestamps.

Origin: repository. Severity: low. Status: corrected and contained.

## AER-1093 — Commit-relative tripwire was run before the new path was staged

The first surrounding-suite run asked Git for a plan-source-to-working/index
diff while the new evaluator file was still untracked. Git intentionally omits
untracked files, so the exact-path tripwire could not see it. Explicitly staging
only the three authorized implementation paths before the rerun made the
precommit candidate visible without touching unrelated untracked files.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1094 — Validation hardening edit omitted one Boolean connector

While extending direct source review controls, one new secret-field condition
was followed by the next condition without `or`. Python compilation rejected
the edit immediately. Adding the connector restored the expression before any
test or commit.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1095 — Initial evaluator did not contain hostile timezone exceptions

Direct review found that an exact `datetime` may still carry a caller-defined
`tzinfo` whose `utcoffset` raises. The initial candidate caught ordinary date
errors only. The public boundary now catches hostile object exceptions and
returns `manifest_invalid`; a dedicated exploding-timezone regression passes.

Origin: repository. Severity: moderate. Status: corrected and contained.

## AER-1096 — Active acceptance exceeded the compact Baton byte budget

The first evaluator closeout check appended every predecessor and current
artifact to a Baton already close to its fixed byte ceiling. The clockwork
rejected the projection before publication. The active row was reduced to the
primary accepted artifacts for each of the three current layers; full
historical lookup remains in the immutable acceptance index.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,096 corrected or contained incidents and
zero open incidents after clockwork publication. Three observations were
carried from the prior tick's rejected dry runs and six arose during evaluator
implementation and review. All failed closed before publication; no provider,
external evidence, secret, database, route, admission, deployment, Pages action
or protected ref was opened.
