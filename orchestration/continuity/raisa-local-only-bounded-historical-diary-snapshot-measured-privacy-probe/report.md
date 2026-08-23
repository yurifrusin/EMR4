# Raisa local-only bounded historical Diary snapshot measured privacy probe — report

Date: 2026-08-24

Timestamp: 2026-08-24T03:42:32.7376775+10:00 (Australia/Brisbane)

Result: `raisa_local_only_historical_diary_measured_privacy_revision_required`

Reviewed source: `a0887004298fbe3b3509f29c7844c228af16d4b3`

## Conclusion

The privacy gate was useful and worked. It bound one exact local day, opened
80 historical Diary snapshots read-only in one owned Word process, reduced all
1,120 occupied cell observations locally and emitted no source value. Cleanup
removed the private manifest and incomplete projection, retained no key or
mapping, and left the pre-existing user Word process untouched.

The empirical result is deliberately `revision_required`. The projection
preserved 40 stable structural records and recovered 118 adjacent changes, but
mapped none of the occupancy cells to a time row. That blocks downstream use:
the first cell parser captured motion but not yet the scheduling time axis.

## Privacy and linkability

- Source-value leakage detections: 0.
- Record uniqueness: 9 of 51 structural records.
- Trajectory uniqueness: 51 of 51.
- Cross-key structural differencing: 51 of 51.
- No universal probability of re-identification is claimed.
- The result grants ignored local research retention only; it does not grant
  fixture, memory, provider, model, product or publication use.

The high trajectory uniqueness is exactly why the private projection was not
promoted. A pseudonym is not anonymity when a rare trajectory remains stable.

## Verification and execution

- Phase A took seven metadata-only attempts. Six stopped before manifest or
  content access while the closed timestamp convention was derived from safe
  aggregate shapes; the seventh bound exactly 80 files.
- Phase B ran once, opened and parsed 80 of 80 snapshots, and performed no
  automatic content retry.
- Thirty-six new hostile tests and 86 unchanged privacy/H5/H15 controls pass
  through the provider-free runner; Ruff, compilation, PowerShell parsing and
  Git diff checks also pass.
- Five contained prepublication lapses are consolidated into one register
  incident in revision 655.
  None changed product, protected refs, raw output or the one-run decision.

## Next operation

Proceed to
`raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal`.
It must work synthetic-first, preserve the exact privacy and byte boundaries,
and may perform at most one newly bound local content run. Its task is narrow:
recover a trustworthy structural time axis. No downstream authority opens.
