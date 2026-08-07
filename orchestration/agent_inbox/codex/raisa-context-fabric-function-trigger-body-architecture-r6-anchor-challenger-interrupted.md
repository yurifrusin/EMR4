# R6 recovery-anchor challenger: preserved interrupted result

Date: 2026-08-07

Source HEAD: `2b3798f8884cb74a4454572e2f247131cd7a7fb5`

## Preserved challenger finding

The bounded read-only challenger reported the following material finding before
its requested terminal response failed to complete:

> R6B is not yet confirmed. The accepted parent requires KEY_ROTATION
> lifecycle.source_position IS NULL, so R6B cannot compare lifecycle position
> with checkpoint position; it must prove the NULL branch shape and prove
> checkpoint position did not change by comparison to the immediately
> preceding anchor.

Sol independently reproduced this against the immutable parent contract's
exact `context_durability_lifecycle` branch constraint. The worktree candidate
that generated contract
`sha256:49db11e74a46d1056e694614a970037cf021e174d71114f5262e950b9075b01f`
is therefore rejected without waiting for a terminal challenger response.

The challenger did not edit the repository or use any provider, database,
source, data, runtime, SQL/DDL, deployment or protected-ref surface. It was
interrupted after repeated requests for a bounded terminal result, and no
terminal acceptance decision is attributed to it.

## Sol reconciliation

The third exact-veto recovery now requires the rotation producer to store NULL
`source_position`, the anchor proof to validate that exact branch shape and to
prove unchanged checkpoint position from the preceding anchor. Sol also closes
the complete audit-packet claim by proving the current audit predecessor is the
latest earlier audit head, or the registration baseline when none exists,
including across intervening key rotations. A fresh exact-HEAD veto remains
mandatory after correction.

RESULT: preserved_nonterminal_revision_required_evidence
