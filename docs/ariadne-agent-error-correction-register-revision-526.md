# Ariadne agent error and correction register — revision 526

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 525

AER-0607 preserves one read-only closeout-template path error. A chained
PowerShell read correctly opened the tracked kernel updater and continuity test
but guessed a shorter Yuri-summary filename that does not exist. The updater
already contained the exact retained mailbox path. No file changed.

The correction uses the inventory-resolved path and returns to one executable
per process for subsequent reads.

## Register state

Revision 526 contains 607 bounded incidents. All are corrected or contained;
none is open. AER-0607 is the third occurrence of
`operator.explicit_repository_path_operand_not_inventory_resolved`.

## Clockwork consequence

The future command gear must bind every path operand from a typed inventory
before process launch. It should be impossible for one guessed path to enter a
command or to obscure the outcomes of otherwise valid reads in the same shell
process.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
