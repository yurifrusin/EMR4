# Durability typed-body admission-lock policy parent rebind

Date: 2026-08-08

Status: deterministic parent rebind complete; body semantics unchanged.

The typed function/trigger body contract now binds repaired structural parent
`sha256:80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac`
from exact structural commit
`3a19167e13ac01996180e1b5ada2a6e2ae7e135f`.

No typed body program, node, predicate, failure mapping, call edge, effect,
entry point or trigger changes. The contract reseal is solely the deterministic
consequence of its structural parent binding and is now
`sha256:8124957e32657076c3befc96a7b5e8770dcd37fcb5b91e33c136f01cbf2dd5ea`.

This architecture remains unmounted and non-executable. Inert DDL regeneration,
parse/catalogue reproduction, behavior-parent rebind, independent veto and any
further disposable behavior attempt remain separate closed descendants.
