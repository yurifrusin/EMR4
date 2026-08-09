# Ariadne agent error and correction register revision 138

Date: 2026-08-09

Status: bounded register correction candidate

Revision 138 adds AER-0163 and brings the register to 163 bounded incidents
with zero open incidents.

## AER-0163 — clean-checkout mutable evidence dependency

The first fresh UUID-minimum behavior veto correctly rejected the candidate
after reproducing 483 passes and one `FileNotFoundError`. The diagnosis test
always required the deliberately untracked mutable behavior-evidence path,
which exists in the primary recovery worktree but cannot exist in a clean
committed verifier checkout.

The corrected test always verifies the tracked immutable attempt-025 bytes,
digest and bounded contents. It compares those bytes with the mutable current
evidence only when that optional untracked file exists. A fresh clean-worktree
deterministic packet and a genuinely fresh independent veto remain mandatory;
the rejected r136 decision cannot authorize behavior attempt 026.
