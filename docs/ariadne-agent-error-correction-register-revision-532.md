# Ariadne agent error and correction register — revision 532

Date: 2026-08-19

Timestamp: 2026-08-19T07:18:30.9672439+10:00 (Australia/Brisbane)

Status: rejected draft preserved; superseded by revision 533

## Change from revision 531

AER-0616 preserves the first engine test failure. The private publisher's
generic readback helper required every JSON file to be an object even though
the declared clockwork journal is an array. The exception path removed all
staging state and published nothing. Shape-neutral JSON readback now follows
the typed generator's own shape validation.

AER-0617 preserves the first complete but rejected private generation. It
derived one candidate rerun but displayed a hard-coded 100 percent reduction,
and its authoritative generation digest omitted the whole efficacy projection
instead of excluding timing alone. The complete rejected directory remains
immutable. The reducer now calculates 85.714 percent from fourteen comparator
reruns and two candidate reruns; the manifest binds every non-timing efficacy
field, with a test proving timing independence and efficacy sensitivity.

## Register state

Revision 532 contains 617 bounded incidents. All are corrected or contained;
none is open. The new recurrence signatures are
`repository.generic_json_readback_rejected_declared_array` and
`repository.derived_efficacy_percentage_and_digest_scope_diverged`.

## Clockwork consequence

The rehearsal does not erase its own construction cost. Its candidate reading
is two failure-induced reruns, an 85.714 percent reduction against the frozen
fourteen-rerun comparator. Both failures were detected before exact-candidate
admission; the second complete generation is the only candidate result.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.

## Rejection

The deterministic register validator rejected this draft before pattern-report
publication because AER-0617 combined repository origin with the
`evidence_misreport` category, whose controlled origin is agent behaviour.
Revision 533 preserves and corrects that exact failure.
