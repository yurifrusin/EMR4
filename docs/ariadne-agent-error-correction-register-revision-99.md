# Ariadne agent error and correction register revision 99

Date: 2026-08-08

Status: accepted register correction

Revision 99 adds AER-0120 and AER-0121, bringing the register to 121 bounded
incidents.

## AER-0120 — verifier misnamed the reviewed bootstrap symbol

The coordinate-review receipt referred to `_bootstrap_sql()`, which does not
exist. The reviewed renderer is `render_bootstrap_sql()`. The allowlist was
reconciled directly against that exact symbol and remains valid; the erroneous
symbol-name claim receives no acceptance weight.

## AER-0121 — coordinate rejection branch was not observable

Failure evidence 005 retained `23502` but no relation or column. The parser
previously returned that same safe shape for missing verbose fields, ambiguous
fields, an unlisted relation and an unlisted column, so the next bounded repair
could not be selected without guessing.

The evidence now adds one closed `coordinate_status` enum: `missing`,
`ambiguous`, `unlisted_relation`, `unlisted_column` or `released`. Rejected
identifiers remain sealed. No further run is eligible until deterministic
checks and a fresh exact-HEAD independent veto accept this branch signal.
