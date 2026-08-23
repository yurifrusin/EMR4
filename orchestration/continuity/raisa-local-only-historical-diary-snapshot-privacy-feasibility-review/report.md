# Raisa local-only historical Diary snapshot privacy feasibility review — report

Result: `raisa_local_only_historical_diary_snapshot_privacy_gate_mechanics_pass`

Reviewed source: `1746cbf7a78d7d98597e6458f00953bd1ab193aa`

## Conclusion

The privacy gate is useful now and its synthetic mechanics pass. It can preserve
stable nonsemantic linkage, relative observation windows and exact scheduling
changes while replacing identity-bearing values, dropping contact details and
reducing notes to closed buckets. All 14 invented changes across four irregular
poll observations were recovered without source values or key material in the
projection.

The result is intentionally not a finding that the real archive is anonymous
or de-identified. The synthetic risk exercise found one unique record and one
unique trajectory in a population of seven. Its record and trajectory linkage
attacks each succeeded once in two defined trials. Independent key rotation
still left the rare trajectory distinguishable once in seven records. These
are synthetic conditional readings, but they prove the gate exposes residual
linkability instead of treating pseudonymisation as sufficient.

## Frozen next boundary

The committed real-access subgate is non-executable and contains no path. A
later accepted operation may bind only one explicit leaf root, one dense day,
at most 80 non-recursively inventoried files, 128 MiB total and 8 MiB per file.
It must remain local, provider-free and network-closed, use an ephemeral key,
write only to a new ignored output root, clean up on failure and commit no raw
or extracted text, original identity, filename, timestamp or mapping.

Its strongest decision is `locally_restricted_candidate`: permission to retain
one ignored local research projection for review. It cannot authorise fixture
promotion, model/provider use, memory, product runtime or publication.

## Verification

- 46 new hostile privacy-gate tests passed.
- 40 unchanged H5/H15, output-safety, leakage-lint and timeline tests passed.
- All 86 tests passed through the provider-free wrapper.
- Ruff, compileall, canonical contract rendering and Git diff checks passed.
- Existing H5/H15 source and approval artifacts were not changed.
- No historical Diary file or private calibration reference was opened,
  listed, searched, sampled, hashed or parsed.
- No provider, model, network, product, database, deployment, Pages or
  protected-ref effect occurred.

## Next operation

Launch `raisa-local-only-historical-diary-access-boundary-convergence`. The
clockwork mandatory floor still forbids all historical data, so a direct
handoff to the measured probe would be contradictory. The successor must make
only the exact bounded local Diary subgate representable while preserving all
product, patient, appointment, clinical and protected-data denial. It will not
read the archive; the 80-file measurement remains the following tranche.
