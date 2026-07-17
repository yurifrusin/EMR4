# Bernie Fresh Certification Protocol

## Purpose and scope

This protocol captures the reusable evaluation discipline developed through
LC4V2-LC4V10. It certifies a frozen, explicitly bounded deterministic product
contract. It is not production release approval, provider approval, write
authority, or permission to reuse consumed holdout evidence.

## Non-negotiable roles

- The Conductor owns the contract, acceptance taxonomy, recovery, protected
  authorship, one-shot decision, integration, and protected refs.
- A bounded worker may implement only the empty content-blind framework.
- A fresh independent reviewer must veto the accepted framework before real
  corpus content exists.
- The corpus author cannot use a worker's self-certification as acceptance.
- No external worker receives protected content, integration authority, or
  permission to move the baton.

## Protocol

1. **Authorize a genuinely fresh version.** Record scope, dimensions,
   population shape, thresholds, failure taxonomy, access rules, and the
   exact user decision boundary before implementation.
2. **Build content-blind infrastructure.** The framework contains schemas,
   validators, hashing/sealing, one-shot state transitions, aggregate report
   structure, and fail-closed checks—but no actual cases, labels, utterances,
   or product-specific hints.
3. **Run the pre-content veto.** An independent fresh-context reviewer checks
   exact population rules, unknown-field rejection, binding integrity,
   one-shot consumption, aggregate-only output, runtime isolation, and
   evidence-invalidity precedence. Any material recovery requires a fresh
   veto; correction loops do not inherit acceptance.
4. **Close external sessions.** After the veto, only the protected author may
   create actual Gold content. Earlier protected versions remain inaccessible.
5. **Freeze acceptance before content.** Commit the thresholds and distinction
   between `certification_invalid` (the evidence procedure cannot support a
   conclusion), `certification_fail` (valid evidence misses product gates),
   and `certification_pass` (valid evidence meets every frozen gate).
6. **Author, validate, and bind.** Validate the fresh corpus locally, commit
   exact source blobs, create a manifest and seal bound to those blobs, and
   record a durable unconsumed marker before any protected evaluation read.
7. **Execute once.** The evaluator must atomically consume the authorized
   marker and seal. A crash, second attempt, drift, missing binding, or schema
   discrepancy fails closed; it never silently creates another attempt.
8. **Emit aggregate-only evidence.** The durable result may contain frozen
   counts, dimensions, generic groups, language-form totals, hashes, variance,
   and failure categories. It must not expose case text, Gold, identities,
   spans, diary state, or per-case results.
9. **Apply thresholds mechanically.** Evidence validity is decided before
   product performance. A product miss cannot be relabelled as evidence
   invalidity, and an evidence defect cannot be averaged away as performance.
10. **Seal permanently.** After consumption, the version cannot be opened,
    rerun, relabelled, repaired, or used as a development corpus. Planning may
    use only the explicitly accepted aggregate artifacts.
11. **Run preservation gates.** Execute the ordinary serial regression suite
    without loading protected evidence. Any historical equality deselection
    must be enumerated and justified as immutable-artifact preservation.
12. **Close out authority.** Record what passed, the exact bounded scope, what
    remains closed, the source/report hashes, incidents, worker provenance,
    and whether another version is authorized or a user decision is required.

## Required durable artifacts

- frozen contract and one-shot acceptance rule;
- content-blind framework acceptance and independent veto;
- source commit, manifest, seal, and consumed marker identities;
- aggregate report and its hash;
- Conductor acceptance and plain-language closeout;
- preservation-gate evidence and documented deselections;
- updated live handover and aligned protected refs.

## Anti-patterns

Do not inspect earlier cases to improve a fresh attempt, let the framework
author seed content hints, repair against a consumed version, rerun after a
poor score, expose per-case failures, allow a worker to certify itself, or
treat a perfect bounded result as authorization for providers, runtime wiring,
writes, deployment, or release.
