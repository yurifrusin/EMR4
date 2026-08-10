# Durability inert DDL admission-lock RLS rebind

Date: 2026-08-08

Status: deterministic descendant rebind and regeneration complete.

The inert renderer now binds structural parent
`sha256:80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac`
at exact source `3a19167e13ac01996180e1b5ada2a6e2ae7e135f` and semantically unchanged
typed-body parent
`sha256:8124957e32657076c3befc96a7b5e8770dcd37fcb5b91e33c136f01cbf2dd5ea`
at exact source `f42558c14c59c2d37a5b96d4a880941f26038d26`.

The sole semantic addition is rendered PUBLIC UPDATE policy
`pol_cf_04_update_lock`. Its exact COORDINATOR `USING` predicate permits the
required admission row lock, while its identical `WITH CHECK` ends in
`AND FALSE`. No typed body node, direct DML grant, admission immutability,
entry-point grant or external authority changes.

The regenerated artifact remains inert, repository-local and forbidden to
execute or apply. A fresh parse/catalogue reproduction and behavior-parent
rebind remain required before another disposable behavior attempt.

The canonical LF artifact contains 1,436,426 bytes and 423 statements at
SHA-256 `1ab976d0555021aa6ec41778b2c3de6ef27105f17f8d1d941b714006da93b1d5`;
the render manifest SHA-256 is
`6adab0a48917c518df81035befe0991f15cba56950713f7329a08054a35f5dd7`.
