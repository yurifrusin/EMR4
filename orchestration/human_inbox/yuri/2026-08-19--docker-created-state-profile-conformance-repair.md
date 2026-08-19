# Docker Created-state profile conformance repair

Date: 2026-08-19

Timestamp: 2026-08-19T23:09:50.9051335+10:00 (Australia/Brisbane)

## Plain-language summary

The prerequisite worked. We created one never-started Docker container and its
private test network, read only the structural facts needed to understand the
earlier failure, and removed both cleanly. We learned that Docker's Created
state uses the network name as the map key, the network ID as its mode, and an
empty endpoint ID until attachment. The recovery harness now checks those exact
facts and no longer mistakes its ownership label for a leaked password.

No database was started and the failed database attempt was not repeated. The
next tranche can now freeze attempt 003 around the corrected harness.

## Technical summary

- Accepted unchanged candidate:
  `260eeda97a3204a39b0f639d216fd7a53c0d2014`
- Predicate-correction source:
  `02a1fbfaa517a0d2a2dff66f31fabe482653c430`
- Created-state executions/retries: 1 / 0
- Database executions: 0
- Network relation: exact sole captured-name key
- Network mode: exact captured network ID
- Created-state endpoint ID: empty
- Hostile contract mutations: 128/128 rejected
- Cleanup: container absent, network absent, labelled residue 0
- Gemini 3.7 Flash/high invocations/corrections: 2 / 1
- Manual canonical edits/drift: 0 / 0
- Protected refs: all four remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

The first independent review found no substantive defect; it failed closed on
one wrong field name in the review command I authored. The corrected field was
proved locally before a fresh review, which then passed all ten commands. The
clockwork also rejected an overlong checkpoint before publication, and fresh
successor rehydration found its rendered Compass omitted from the first explicit
closeout stage. These costs are retained explicitly: five authoring or packaging
correction cycles, one additional Gemini call, one redundant rejected publish
invocation and one bounded follow-up commit, but no repeated occupied run,
database action, hand-edited canonical field or canonical drift.

For attempt 003, every exact verifier assertion will be executed locally first,
clockwork check and publish will be separate commands, and explicit staging will
consume its exact ten-surface manifest. No ordinary practice,
product/API/config/client change, product/patient/clinical data, provider worker,
production, deployment, release, Pages or protected ref has opened.

Clockwork closeout is accepted at Continuity 336 / Compass 318, generation
`gen-4fd532706e6cfaccf0daf62c62b14727d2f8818e7f89248cc0660fa5ee3110b4`,
lease 20. The non-PHI continuing Pushover notification succeeded with request
`7029df75-70af-426c-83fd-3b8bfd402b70`.
