# Ariadne agent error and correction register revision 133

Date: 2026-08-09

Status: bounded register correction candidate

Revision 133 adds AER-0158 and brings the register to 158 bounded incidents
with zero open incidents.

## AER-0158 — undefined-symbol diagnostic parser undercoverage

The first failure-024 diagnostic replayed the exact synthetic BTR-E01/E02 path
through the normal owned-container cleanup, but its narrow PostgreSQL error-line
regular expression did not recognize one allowlisted symbol. It raised
`single_allowlisted_undefined_symbol_missing` before emitting a durable
minimized receipt. No raw PostgreSQL error text or diagnosis was released, and
the failure grants no behavior retry.

The corrected diagnostic no longer depends on prose formatting for its primary
classification. It runs a fixed read-only catalogue-resolution probe for six
exact candidate functions/operators immediately before BTR-E02, releases only
booleans and missing symbol identifiers, and retains the raw-message parser as
optional corroboration. A distinct execution receipt is required before its
newly owned diagnostic run.
