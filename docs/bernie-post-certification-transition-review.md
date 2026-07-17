# Bernie Post-Certification Transition Review

Date: 2026-07-17

## Executive conclusion

LC4V10 is a strong and valid result: the bounded deterministic language,
policy, interpretation, replay, and safety contract passed every frozen gate
over 576 repeat observations with zero variance. The result closes the
successive fresh-holdout cycle. It does not certify the whole EMR4 product,
clinical safety, production security, live models, provider adapters, or write
authority.

The most important outcome is larger than the perfect score. The programme
developed a reusable way to separate evidence validity from product validity,
prevent evaluation leakage, classify failures at the correct layer, remediate
only with development evidence, and preserve consumed certification evidence.
That process is now captured in
`docs/bernie-fresh-certification-protocol.md`.

## What the sequence established

- Deterministic semantics can cover varied receptionist phrasing without
  repeat variance across the certified contract.
- Entity extraction, temporal relations, correction/negation, policy
  projection, clarification, composition, replay, and safety need distinct
  observability; a single “intent accuracy” number would have hidden the real
  causes of earlier failures.
- Fresh holdouts are useful only when authoring, sealing, consumption, and
  aggregate reporting are themselves fail-closed.
- Corpus engineering and parser repair are different activities. Contradictory
  Gold must be quarantined; independently supported parser gaps may be fixed
  in ordinary development; consumed holdouts may not become repair fixtures.
- External economical models remain valuable for bounded implementation and
  independent vetoes, while taxonomy, acceptance, protected authorship, and
  integration remain Conductor work.

## Transition state

Holdouts V1-V10 remain sealed. T3.1-T3.4 remain blocked by default, and T3.5,
live provider calls, raw-response persistence, provider tools, runtime wiring,
product writes, deployment, and release remain at their existing decision
boundaries. No V11 is authorized or needed under the completed cycle.

The next phase should not be another certification run. The recommended
sequence is:

1. complete the current security/CI maintenance and retain its evidence;
2. triage the open high-severity CodeQL findings for reachability and validity;
3. decide whether to enforce protected-master and secret push-protection
   controls in GitHub;
4. execute the highest-priority Secure SDLC structural tranche; and
5. only then plan the next product track, with a fresh threat-model delta and
   the existing provider/write gates still closed.

## Deliverables

- reusable fresh certification protocol;
- dependency/security maintenance record;
- Secure SDLC lifecycle review;
- evidence-bound security-hardening proposal for the delivery control plane;
- refreshed live baton after verification and GitHub closeout.
