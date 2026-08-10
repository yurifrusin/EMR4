# Durability inert DDL anchor-lock RLS rebind

Date: 2026-08-08

Status: deterministic descendant rebind and regeneration complete.

The inert renderer now binds structural parent
`sha256:6802a7355e62d9d29f735a4c0703e90f2c9bcfaa4606d694070fa62380dc741c`
at source `35c4ded8163a7d04667d1e53ccd3c6f41f059e59` and byte-unchanged typed-body
parent `sha256:b54b2e6800b4484f84b2c7ba57566ecfe8c04b9a8c8e91ac6bd67be8f22b5840`
at source `f94d4c610dbff3ddb448eb4ac8677ca230a298e3`.

The sole semantic addition is one rendered PUBLIC UPDATE policy,
`pol_cf_08_update_lock`, whose exact COORDINATOR/LIFECYCLE `USING` predicate
permits required `FOR SHARE` visibility and whose identical `WITH CHECK` ends
in `AND FALSE`. No body node, direct DML grant, append-only invariant or
external authority changes.

The regenerated artifact remains inert, repository-local and forbidden to
execute or apply. A fresh parse/catalogue reproduction and behavior-parent
rebind remain required before another disposable behavior attempt.

The canonical LF artifact contains 1,435,884 bytes and 422 statements at
SHA-256 `550336e145eac6ac004447d05ea3e72d970f6d8283d3af2689aed62cfff92bc6`;
the render manifest is
`95a5c0a613329bd8e6f103130b217a73d597e4e065ca547f658f96db72e8c205`.
