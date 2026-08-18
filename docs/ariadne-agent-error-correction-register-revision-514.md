# Ariadne agent error and correction register — revision 514

Date: 2026-08-19

Timestamp: 2026-08-19T04:21:58.9165592+10:00 (Australia/Brisbane)

Status: rejected before acceptance; superseded by revision 515

## New incidents

AER-0594 records recurrence of a generative acceptance command inside an exact
read-only review worktree. The kernel verifier manifest's C06 ran the evidence
generator, which rewrote only line endings in two committed evidence files.
The launcher rejected the review, the candidate HEAD and semantic content were
unchanged, both exact paths were restored from HEAD, and C06 is now a
non-writing Git postcondition.

AER-0595 records recurrence of incomplete Antigravity post-transport failure
persistence. The child process completed, but the dirty-worktree exception
occurred before structured-decision parsing and bypassed the configured
digest-only output. The launcher now writes one sanitized egress-failure
receipt for root, branch, HEAD or dirty-worktree postcondition failures before
raising. Focused launcher tests pass.

## Rejected register state

Draft revision 514 contained 595 bounded incidents but did not pass semantic
validation. It incorrectly linked AER-0594 and AER-0595 as peers under one
attempt identity even though their orchestrator and verifier roles differ.
The canonical validator rejected the draft before pattern generation,
acceptance, review retry or publication. Revision 515 preserves the two
incidents under distinct attempts and records the rejected draft as AER-0596.

## Prevention consequence

The proposed shared Ariadne/DeepSeek clock must classify every generated
command by side-effect capability. A read-only verifier tick may inspect
committed evidence but cannot run a generator. Every completed external
harness tick must also yield exactly one admitted result receipt or one
digest-only rejection receipt, including postcondition failures.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
