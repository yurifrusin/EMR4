# Inert durability DDL rehearsal plan recovery

Date: 2026-08-07

Status: Sol recovery accepted after replacement independent challenge

## Reason for recovery

The first independent challenge returned `pass`, but its narrative did not
match the immutable body contract. It reported 21 declared instruction opcodes
and 33 expression opcodes; the contract declares 22 and 34 respectively. It
also asserted that unique-race mismatch would raise `42000`/`P0001`, although
neither value is a registered durability failure. The review is preserved but
is not admitted.

Sol's exact read-only reconciliation found 21 observed instruction opcodes,
with only declared `DERIVE_BINDING` absent, and all 34 expression opcodes
observed. The same review exposed a genuine plan ambiguity: implicit exact
cardinality and unique-winner reload failures had not been explicitly mapped to
the existing failure registry, so an implementation worker could have invented
that security-relevant behavior.

## Recovered exact rules

1. The lowering contract records 22 declared/21 observed instruction opcodes,
   names `DERIVE_BINDING` as the sole unobserved form, and records 34 declared/34
   observed expression opcodes. The renderer lowers only the immutable
   observed population; seeing an unobserved or new form fails.
2. Every implicit `EXACTLY_ONE` zero/non-unique outcome maps to registered
   `F_CARDINALITY`, SQLSTATE `CF004`, reason
   `required_row_missing_or_ambiguous`, without values.
3. `INSERT_OR_RELOAD_COMPARE` derives exactly one named unique constraint whose
   ordered key equals `conflict_key_columns`. Its exception block handles only
   SQLSTATE `23505` with that exact `CONSTRAINT_NAME`; all other violations are
   rethrown unchanged. Winner reload uses the conflict key plus the accepted
   `winner_predicate`; missing/mismatch maps only to `F_CARDINALITY`/`CF004`.
4. The structural omission flags and body `renderer_present:false` evidence
   remain immutable history. This descendant activates only fixed-path inert
   rendering after both parent hashes and all 22 programs reconcile. It does
   not activate execution, migration, runtime or product authority.
5. PostgreSQL 16 official documentation confirms core `sha256(bytea)`,
   `convert_to(text,name)`, `encode(bytea,text)` and `octet_length(text)`
   primitives. Server parsing and catalogue equivalence remain deliberately
   deferred.

## Disposition

The original plan commit remains preserved evidence. The plan, design, threat
delta and tests carry this recovery at a new descendant HEAD. One fresh
independent exact-HEAD challenge verified the corrected populations, failure
mapping, expected-constraint fence and activation delta with no P0-P3 finding.
The bounded implementation worker may now be dispatched under the plan's
existing closed authority; SQL execution, database contact and every later gate
remain closed.
