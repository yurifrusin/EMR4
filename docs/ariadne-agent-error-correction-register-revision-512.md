# Ariadne agent error and correction register — revision 512

Date: 2026-08-19

Timestamp: 2026-08-19T03:37:41.2756177+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0591 records a read-only pre-commit Git probe that placed five revision
operands behind `git rev-parse --verify`. Git rejected the command because
`--verify` accepts one revision. No ref or file changed. Five separate scalar
reads then proved task HEAD exactly and all four protected refs still at the
required full object ID.

Revision 512 contains 591 bounded incidents. All are corrected or contained;
none is open.

## Prevention

The causal clock should own a typed `VerifyRef` operation that emits one valid
Git invocation and one full-object reading per tick. Until adoption, never
batch revision operands behind `git rev-parse --verify`.
