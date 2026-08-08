# Ariadne agent-error register revision 92

Date: 2026-08-08

Status: behavior/transaction planning correction controls accepted

Revision 92 adds AER-0111 and AER-0112 and brings the register to 112 bounded
incidents. No incident is open.

## Cross-worktree parent-hash correction

Candidate `1f21a3cca4b6a855fe8992f26023fee1750fd0df` correctly bound the
canonical inert SQL hash but applied no common newline rule to all six text
parents. Its focused hash test therefore failed after Git produced CRLF bytes
in fresh Windows worktree r73. Sol preserved the `revision_required` receipt,
computed raw and canonical hashes for all six parents, and found that the
function/trigger body contract was the sole divergent binding.

AER-0111 closes the defect by requiring canonical UTF-8/LF hashing across all
six text parents, rejecting lone carriage returns, rebinding the body contract
to canonical SHA-256
`634dbc5c1a5294c1ac2de6a913671cd968a9838aa763d4c2a4d229bbcd9c0271`
and rerunning the focused and inherited packet. This changes no parent file or
behavior scenario.

## Review test-accounting correction

The same r73 review found the valid hash defect but reported 118 total tests,
117 admitted and 116 passed. Exact per-file collection in the unchanged clean
worktree instead proves `27 + 9 + 12 + 7 + 36 + 4 + 7 + 22 = 124` admitted,
plus exactly one named baseline deselection. AER-0112 preserves the valid P2
finding while rejecting the inaccurate count narrative. It recurs with
AER-0110's exact-packet underreport signature.

The replacement review must use a distinct clean exact-HEAD worktree and print
the exact per-file collection and pass arithmetic before its terminal
decision.

## Authority boundary

These corrections are planning and workflow evidence only. They grant no
Docker/PostgreSQL behavior runtime, applied migration, application/API/Diary
wiring, operational source or database access, patient/product data, provider
call, command, deployment, Pages rebuild, release, production or protected-ref
movement.
