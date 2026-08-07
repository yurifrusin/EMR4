# Ariadne agent-error register revision 77

Date: 2026-08-08

Status: fourth durability-body exact-veto omission contained

Revision 77 adds AER-0079. Fresh exact-HEAD review rejected committed candidate
`0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d` because the key-rotation body
locked the correct current recovery anchor but did not independently compare
its four checkpoint fields and seven controlling generation digests with the
locked checkpoint and generation before using its digest.

The fourth exact-veto recovery freezes one field-complete `F_ANCHOR` assertion
immediately after that anchor lock and before the prior-key lock or any effect.
Candidate-independent hostile tests must remove or substitute every equality,
change its operands/operator/failure family, and move digest use or an effect
before the fence. Candidate `0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d`
remains immutable rejected evidence; correction is pending a rebuilt candidate,
the full inherited deterministic packet and a fresh clean exact-HEAD veto.

Revision 77 contains 79 bounded incidents. Incident counts remain
workflow-improvement signals only.
