# Ariadne agent error and correction register — revision 227

Date: 2026-08-11

Revision 227 adds and closes AER-0261. The register now contains 261 bounded
known incidents.

## AER-0261 — AES-C4 non-existent source binding

The first AES-C4 factual-rebind zero-call evidence and ledger used the
non-existent source string `ec6a04345fb8a5ec65da112fbacbc98bfb040030`
copied from restored summary state. Mandatory post-compaction Git verification
found the mismatch against actual committed HEAD
`ec6a043410661d563c53d205cd4958d100732e97` before independent review, cloud
preflight, occupied-ledger opening or provider inference. The invalid pair made
zero calls and is preserved under explicit `invalid-source` filenames; it
supplies no evidence.

Sol then captured the complete HEAD using `git rev-parse`, verified it as a
commit with `git cat-file`, and passed that same captured value directly to the
provider-free harness. The corrected evidence and consumed zero-call ledger are
bound to the exact existing source. A fresh exact-head independent veto remains
required before any cloud or provider execution gate.
