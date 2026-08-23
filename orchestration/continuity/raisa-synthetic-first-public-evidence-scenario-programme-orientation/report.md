# Raisa synthetic-first public-evidence scenario programme orientation — report

Date: 2026-08-23

Timestamp: 2026-08-23T23:56:40.7315990+10:00 (Australia/Brisbane)

Status: `candidate_pass`

Result: `raisa_synthetic_first_public_evidence_scenario_programme_orientation_pass`

## Lay summary

Raisa now has a practical route from broad public research to traceable
synthetic clinic scenarios. Australian safety and practice guidance can anchor
requirements; existing EMR4 contracts can anchor accepted product behaviour;
standards and synthetic-health methods can shape generation and coverage;
vendor documentation can reveal workflow edge cases; and fictional medical
practices can contribute human tensions such as interruptions, scarcity and
dual relationships. Vendor claims and fiction remain prompts only and cannot
decide what the safe or correct outcome should be.

The seven read-only research packages found enough material to support a first
corpus of roughly 350–700 executable synthetic cases across reception,
administrative and clinical-diagnostic families. That number is a planning
range, not proof of safety. Acceptance will depend on traceable requirements,
hazard and state coverage, counterfactual consistency, mutation rejection and
repeated-run reliability.

Yuri's further description of the historical Diary archive materially improves
its potential value. Scores of timestamped states per day over several months
should permit adjacent-state differencing and reconstruction of short-lived
corrections, races and queue changes. Each inferred change is nevertheless
known only to have occurred between two observations. The filenames therefore
provide `observed_after` and `observed_by` bounds, not an exact event time.

Near-real-practice synthetic scenarios derived from that archive are now a
reasonable future aim, subject to a separate local-only privacy feasibility
gate. Removing names alone would be unsafe because a high-frequency sequence
can fingerprint a person, practitioner, community event or exact practice day.
Yuri has rejected an aggregate-only presumption. The revised safe direction is
to test a near-lossless local de-identified projection first: random stand-ins
for names, removal of contact details, identifiers and revealing notes, and
preservation of the richest timing and lifecycle dynamics whose measured
linkage risk is very low in the restricted local setting. Aggregate-derived new
days remain the default for provider prompts or wider distribution, not a
mandatory replacement for controlled local analysis. No raw historical file
was opened, listed, parsed, hashed or transmitted in this orientation, and no
promise of perfectly irreversible de-identification is made.

## Technical synthesis

The orientation establishes seven closed source classes:
`normative_or_clinical_guidance`, `accepted_emr4_contract`,
`method_or_interoperability_standard`, `vendor_operational_documentation` or
`vendor_advertised_capability`, `fiction_prompt_only`,
`private_observed_calibration`, and `local_design_assumption`. Oracle authority
is fail-closed: vendor, fiction, model output and private observations cannot
become authoritative outcome oracles. Normative guidance remains jurisdiction-
and-scope dependent.

The research register includes Australian workflow and safety sources such as
[RACGP patient identification](https://www.racgp.org.au/running-a-practice/practice-standards/standards-5th-edition/standards-for-general-practices-5th-ed/core-standards/core-standard-6/criterion-c6-1-patient-identification),
[RACGP follow-up systems](https://www.racgp.org.au/running-a-practice/practice-standards/standards-5th-edition/standards-for-general-practices-5th-ed/general-practice-standards/gp-standard-2/criterion-gp2-2-follow-up-systems),
[the ACSQHC Primary and Community Healthcare Clinical Safety Standard](https://www.safetyandquality.gov.au/national-standards/primary-and-community-healthcare-standards/clinical-safety-standard)
and the [Queensland Primary Clinical Care Manual](https://www.health.qld.gov.au/clinical-practice/guidelines-procedures/clinical-resources/rural-and-remote-health-clinical-resources/primary-clinical-care-manual).
Method sources include [Synthea](https://github.com/synthetichealth/synthea),
[HL7 FHIR TestScript](https://hl7.org/fhir/R4/testscript.html),
[AU Core](https://hl7.org.au/fhir/core/),
[NIST combinatorial testing](https://csrc.nist.gov/pubs/sp/800/142/final),
[NIST differential-privacy evaluation guidance](https://csrc.nist.gov/pubs/sp/800/226/final),
the [OAIC de-identification guidance](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/de-identification-and-the-privacy-act)
and the [ABS Five Safes framework](https://www.abs.gov.au/statistics/understanding-statistics/data-confidentiality-guide/five-safes-framework).

Repository gap mapping found two strong existing contracts rather than an
empty field. `ReceptionScenarioSpec` already owns strict semantic truth,
temporal relations, source spans and expected reception outcomes. The Bernie
YAML loader/replay harness already owns executable turns, allowlisted state,
database/audit deltas, proposal/confirmation rules and provider-call denial.
The missing component is a small domain-neutral traceability envelope and
binding adapter, not a third scenario engine.

The next tranche is therefore
`raisa-traceable-synthetic-scenario-envelope-and-legacy-binding-rehearsal`. It
will bind the two existing non-protected matched reception pairs through typed
references, add source, oracle, coverage and role-separation controls, and keep
private calibration represented only by an opaque non-resolving reference.
It remains provider-free, unmounted and wholly synthetic.

The separate successor
`raisa-local-only-historical-diary-snapshot-privacy-feasibility-review` begins
with authored-synthetic snapshot fixtures. It must quantify equivalence-class
and trajectory uniqueness and run defined linkage attacks against the actual
field shape. If contextual re-identification risk is empirically very low, it
may admit a near-lossless de-identified projection for restricted provider-free
local development. Any opening of real snapshots still needs its own accepted
local-only gate, explicit field inventory, disclosure-subject model, attack
suite and output controls. Raw, locally de-identified observed and generated
synthetic data remain distinct evidence classes. Yuri has delegated launch
timing to GPT Sol; the gate follows immediately after the traceability envelope
when that dependency is satisfied.

## Parallelism and effects

Seven read-only packages completed through user-requested native research
workers. They made zero repository edits, accessed zero private or protected
data and made zero provider calls. DeepSeek had negative leverage because no
separable implementation package existed and its occupied native profile is
paused; Claude Code was not used as a fallback. Gemini is reserved for an
exact material candidate requiring independent veto. GPT Sol retains source-
authority reconciliation, privacy interpretation, architecture selection, Git
and acceptance.

No product source, route, API, client, database, feature flag, ordinary
check-in release, production runtime, deployment, release, Pages surface or
protected ref changed.
