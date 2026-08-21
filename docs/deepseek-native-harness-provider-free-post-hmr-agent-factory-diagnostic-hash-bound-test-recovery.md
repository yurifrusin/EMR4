# DeepSeek native Harness agent-factory diagnostic hash-bound-test recovery

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

The first attempted AER-0871 correction changed the focused test to pass an
explicit npm cache root. That test is included in the diagnostic contract's
`implementation_bytes`, so the accepted source correctly rejected the next
deterministic run with `implementation_digest_mismatch`. No native process was
created and canonical state remained unchanged.

The focused test has been restored byte-for-byte. The mutable closeout command
manifest now runs the exact focused and immutable-evidence tests through
no-conftest pytest while retaining the host's accepted local cache-location
binding. This changes verification orchestration only; it does not alter the
implementation or any byte used by the consumed native attempt.
