# Ariadne agent-error register revision 70

Date: 2026-08-07

Status: current candidate digest provenance corrected before independent review

Revision 70 adds AER-0069. The rebuilt function-and-trigger-body contract and
structural schema both bound
`sha256:8871663b121dedff089b7517406f8223a3df2153bce66716d624b2f321e20dde`,
but the design's current-candidate label still named rejected predecessor
digest
`sha256:631773f9112e7804f5e2ea15b04d4cd4cb4c699502d3491b516d57d14e6f35d5`.

Sol detected the mismatch during the mandatory pre-dispatch comparison, before
the fresh reviewer was admitted. Only the provenance label changed; the
builder-derived contract and schema remained unchanged and the review worktree
was not used. The corrected candidate must receive a new exact HEAD and fresh
worktree/preflight before dispatch.

Revision 70 contains 69 bounded incidents. Incident counts remain
workflow-improvement signals only.
