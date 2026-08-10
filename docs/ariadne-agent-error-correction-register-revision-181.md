# Ariadne agent error and correction register — revision 181

Date: 2026-08-08

Revision 181 records AER-0209 and raises the bounded incident population to
209. The admission-lock structural precommit receipt named the correct scope
but misstated its exact path count as eight; the explicit stage and resulting
commit contained nine intended files because two test files had been counted
as one.

The commit summary exposed the mismatch before any descendant rebind or runtime
action. The preserved receipt now says nine. No path outside the named repair
scope was staged, the structural candidate is unchanged, and no incident
remains open. Future receipts will derive counts from the staged index or omit
the numeric count when they necessarily precede staging.
