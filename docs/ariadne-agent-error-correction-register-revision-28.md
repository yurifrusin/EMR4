# Ariadne agent-error register revision 28

Date: 2026-08-06

Status: schema-constrained Antigravity egress proved; no incident remains open

## AER-0033 corrected

The fresh exact-head Antigravity process used the new closed JSON schema and
returned exactly one admissible `revision_required` decision with one review
body. The wrapper wrote one ordinary worker receipt, and exact source HEAD
`1289f9b822c571341b224ab9c6b5caaeefaf0c71` remained clean and unchanged.

This closes the repeated terminal-marker failure. The admitted reviewer found a
separate evidence-reproducibility defect: the committed acceptance artifact was
bound to a pre-commit Git HEAD and checkout-specific text bytes. That is an
ordinary candidate defect, not another agent incident. Its repair removes the
impossible containing-commit self-reference, canonicalizes text hashes across
LF/CRLF worktrees and leaves exact Git HEAD binding to the independent receipt.

Revision 28 contains 33 bounded incidents: 25 agent-behaviour observations,
three harness failures, two repository defects and three transport timeouts.
No incident remains open. Counts remain workflow-improvement signals only and
do not establish model, provider, transport or role causation.
