# Ariadne agent-error register revision 166

Date: 2026-08-10

Revision 166 adds AER-0192. Sol used the correct short parent commit label
`c8ab7602` but wrote a fabricated forty-character expansion into the parse
contract instead of resolving it with `git rev-parse`. The recorded value was
not a Git object; the actual accepted parent is
`c8ab7602e16e24453dbf909597b4f702a2388416`.

No Docker or PostgreSQL run occurred. The contract, ledger and plan test now
bind the actual full object ID, and the resulting non-accepting characterization
contract SHA-256 is
`a34fb46701396f9626a11f94024e233637e381f15e50d10bbec3cba6f1c4a0fa`.
Exact Git identities must henceforth be obtained from Git output, never inferred
or expanded from a short label.
