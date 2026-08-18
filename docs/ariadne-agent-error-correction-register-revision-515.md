# Ariadne agent error and correction register — revision 515

Date: 2026-08-19

Timestamp: 2026-08-19T04:21:58.9165592+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

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

AER-0596 preserves rejected draft revision 514. The draft falsely linked the
orchestrator and verifier incidents as peers under one attempt despite their
different roles. The canonical validator rejected that split identity before
pattern generation. Revision 515 assigns distinct attempts, removes false peer
links and retains the relationship only in prose.

## Register state

Revision 515 contains 596 bounded incidents. All are corrected or contained;
none is open. The recurrence projection explicitly binds AER-0040 with
AER-0594 and AER-0424 with AER-0595. These are workflow-control signals only
and make no comparative model-quality claim.

## Clockwork consequence

The proposed shared Ariadne/DeepSeek clock must classify every command by
side-effect capability and derive attempt identity plus peer eligibility from
one typed event. A read-only verifier tick cannot run a generator, and every
completed external harness tick must yield exactly one admitted result receipt
or one digest-only rejection receipt, including postcondition failures.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
