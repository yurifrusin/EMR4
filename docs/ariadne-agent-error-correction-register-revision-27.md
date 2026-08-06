# Ariadne agent-error register revision 27

Date: 2026-08-06

Status: packet-only correction exhausted; schema-constrained verifier egress pending proof

## AER-0032: first duplicate output contained

The first authenticated review remains rejected. Its one packet-only correction
was exercised through a genuinely fresh exact-head project and did not repair
the invariant, so AER-0032 is contained rather than relabelled successful.

## AER-0033: corrected packet still emitted three terminal markers

The bounded retry emitted three exact terminal markers. No decision or finding
was admitted, no ordinary worker receipt was written, and exact source HEAD
`1289f9b822c571341b224ab9c6b5caaeefaf0c71` remained clean and unchanged.
Packet-only retries are now closed.

The stronger recovery uses Antigravity CLI 1.1.8's native structured-output
surface. The launcher defaults to a closed JSON object containing exactly one
`decision` and one `review`, rejects missing or conflicting unique envelopes,
forbids embedded legacy decision markers, and retains the text-line parser only
behind an explicit compatibility flag. Focused harness and policy tests pass.
A fresh exact-head review must prove this egress before AER-0033 can close.

Revision 27 contains 33 bounded incidents: 25 agent-behaviour observations,
three harness failures, two repository defects and three transport timeouts.
AER-0033 is the only open incident. Counts remain workflow-improvement signals
only and do not establish model, provider, transport or role causation.
