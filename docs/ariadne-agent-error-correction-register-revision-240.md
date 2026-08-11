# Ariadne agent error and correction register — revision 240

Date: 2026-08-11

Revision 240 records AER-0273 and AER-0274. The register now contains 274
bounded known incidents.

## AER-0273 — invalid CF-D2 verifier pre-dispatch metadata

The first CF-D2 planning pre-dispatch state used a non-allowlisted Antigravity
observation method and assigned a worker without a workspace receipt. Ariadne
correctly returned `revision_required` and forbade dispatch before any model
call or external operation.

Sol preserved that receipt, restored the accepted `agy_cli_observation` method,
left the pre-dispatch assignment set empty and generated a fresh passing
receipt with all five rehydration sources. AER-0273 is corrected.

## AER-0274 — planning formatter gate omitted before fresh veto

The first fresh Gemini 3.6 Flash/high planning veto at exact source
`a0797a17e99f4adfa65ce6bef96ffdcfcdf18c02` accepted the CF-D2 architecture,
hashes, storage topology, four-scenario population, no-guess classifier,
pending-anchor fence and claim boundary. It nevertheless returned
`revision_required` because the packet's required `ruff format --check` command
reported that the planning test needed formatting.

Sol had run the 40 semantic tests, Ruff lint and whitespace check but had not
run the formatter check named in the review packet. The candidate is therefore
not admitted. The exact rejected review remains preserved with zero Docker,
database, provider, product or external-network operations.

Only Ruff formatting has been applied to the planning test. All 40 tests, Ruff
lint and Ruff format now pass. AER-0274 remains contained pending a new commit
and genuinely fresh exact-head veto; no CF-D2 implementation or runtime is
opened by this revision.
