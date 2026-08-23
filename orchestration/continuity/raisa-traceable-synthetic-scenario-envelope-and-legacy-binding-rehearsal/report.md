# Raisa traceable synthetic scenario envelope and legacy binding rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T01:06:23.5988946+10:00 (Australia/Brisbane)

Status: `candidate_pass`

Result: `raisa_traceable_synthetic_scenario_envelope_and_legacy_binding_pass`

## Lay summary

Raisa now has a small, mechanical label and binding layer for synthetic clinic
scenarios. It records where a scenario's supporting ideas came from, which
sources may decide a correct or safe outcome, who authored and reviewed the
oracle, what the scenario covers, and which existing files actually supply its
meaning and executable rehearsal.

This does not create another scenario system. The existing reception JSON
still owns meaning and expected behaviour; the existing YAML laboratory still
owns the stateful rehearsal. The new manifest only records their shared
scenario name, their complementary relationship, four exact file paths and
four SHA-256 readings. It contains no copied dialogue, Diary state, expected-
outcome payload or synthetic person names.

Private calibration is also unable to sneak in through a filename. Its
reference can only be a short opaque token: no path, URL, content hash,
resolvable pointer or claim that de-identification has already been achieved.
In this first version, only wholly authored synthetic evidence may have an
executable binding.

That is enough infrastructure to start the Diary privacy-feasibility gate. The
next tranche begins immediately with invented timestamped snapshots and builds
the field checks, adjacent-state differencer and linkage-risk measurements. It
will then define the exact path, file, byte, output and network controls for a
later real-archive reading. It does not open or enumerate the archive yet.

## Technical result

`orchestration_harness/synthetic_scenario_envelope.py` adds strict frozen
Pydantic records for eight source tokens across seven authority classes, six
derived oracle-eligibility values, four evidence labels, eight coverage kinds,
separated oracle bundles, four distinct roles, non-resolving calibration
references and exact execution bindings.

Authoritative truth and safety rules accept only an accepted EMR4 contract or
normative guidance whose scope has been explicitly reviewed. Vendor evidence
and fiction cannot bind authoritative oracles. A model may be represented as a
bounded extractor but cannot be the author, adjudicator or reviewer. Execution
results have no field or transition capable of promoting a source, evidence
label or oracle.

The legacy validator performs no discovery or replay. It admits only four
hard-coded non-protected paths, verifies both owning contract IDs, requires the
accepted-contract locators to equal those paths, checks all four byte digests,
loads semantic JSON through `ReceptionScenarioSpec`, loads YAML through
`load_scenario_yaml`, and requires both loaded identities to equal the envelope
identity. Its relationship is deliberately `complementary_shared_identity`,
not field equivalence.

The clean reviewed source is
`3ab338348001e5d136fafcccec84941d3860e259`. The combined provider-free reading
passes 124 tests: 43 new hostile cases and 81 unchanged semantic/loader cases.
Ruff, compilation, JSON parsing and whitespace checks pass.

## Contained process observations

The first test command included pytest's `-q` flag even though the provider-
free wrapper accepts paths only. Its argument parser rejected the call before
test execution or mutation; the corrected path-only command passed. The first
candidate receipt intent also placed implementation/test paths into a field
whose closed schema admits only documentation and orchestration evidence
roots. It failed before materialising a runtime state; a distinct corrected
intent passed. Both observations are retained for the error register.

## Parallelism and effects

DeepSeek had no safe independent lease and its occupied native harness remains
paused. Gemini was not called because the active latch forbade live provider
or model execution. Native subagents had negative leverage on one tightly
coupled invariant. GPT Sol performed the serial implementation and acceptance.

No historical Diary file was opened, listed, searched, sampled, hashed or
parsed. No protected evidence, patient/practice/clinical/product record,
provider, database, product source, runtime, ordinary-practice release,
deployment, Pages surface or protected ref changed.
