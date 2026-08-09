# Ariadne agent-error register revision 165

Date: 2026-08-10

Revision 165 adds AER-0191 for the clean-checkout test defect found by the first
independent review of parent-recovery candidate `09436890`. The database repair,
generated body and inert SQL challenges passed, but the clean verifier worktree
ran only 319 of 320 tests because the new failure-034 diagnosis test
unconditionally read an intentionally untracked mutable evidence file.

The candidate remains rejected. The test now treats that mutable file as
optional, verifies its protected restoration hash when present, and continues
to require the committed immutable failure and diagnosis evidence in every
checkout. The full deterministic packet and a fresh exact-HEAD independent
veto remain mandatory before any disposable PostgreSQL run.
