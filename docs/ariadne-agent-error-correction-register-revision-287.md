# Ariadne agent error and correction register — revision 287

Date: 2026-08-15

Timestamp: 2026-08-15T13:46:00+10:00 (Australia/Brisbane)

Revision 287 records AER-0326. The register now contains 326 bounded known
incidents, all corrected or contained by an explicit control.

AER-0326 records a DeepSeek transport timeout during the bounded delete-confirm
physical-representability inventory. The exact launcher exceeded its 124-second
outer observation bound without a terminal result. Exact readback found no
result file, no owned inventory, no tracked change and the disposable worker
still at frozen source `a02e424eac89c12d42ff2c25cfafcc80f3fef077`.

This is transport evidence, not a model-capability finding. No source or review
claim is admitted. Because the same no-terminal signature is already preserved
at AER-0036 and AER-0038, the lane receives no same-packet retry: the inventory
and synthesis transfer directly to Sol while the worker branch remains
unchanged and quarantined pending ordinary cleanup.

Future bounded external inventory lanes must retain an exact result path, owned
path, HEAD and worktree readback. Recurrence of a no-terminal transport closes
the lane for that tranche unless a distinct recovery has positive leverage and
new authority.
