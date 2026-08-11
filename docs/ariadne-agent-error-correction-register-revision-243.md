# Ariadne agent error and correction register — revision 243

Date: 2026-08-11

Revision 243 records and closes AER-0276. The register now contains 276 bounded
known incidents.

## AER-0276 — verifier timeout-value prose reconciled

The fresh Gemini 3.6 Flash/high implementation veto passed exact source
`a5b1107736ce64c0ee3861cb51b231d861b12764`. It ran all prescribed commands,
reported zero P0–P2 findings and performed zero Docker starts, database
operations, provider calls, product reads or external-network operations. Its
worktree remained clean and unchanged.

One review sentence nevertheless summarized the statement and idle transaction
timeouts as `5000ms`. Both the frozen contract and the reviewed participant
script set them to exactly `8000ms`. This is a bounded evidence misreport, not a
source, command, decision or runtime defect.

The immutable passing review remains preserved. Acceptance uses the exact
contract and source value of `8000ms`; the prose value carries no authority.
Future verifier summaries must have every numeric timeout, budget, count and
hash mechanically reconciled against the exact reviewed source before their
decision is admitted. No fresh review is required because the candidate and
review execution are unchanged and the discrepancy is independently decidable
from the exact allowlisted bytes.
