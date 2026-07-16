# LC4V10 Framework Review 4 Metadata Incident

Date: 2026-07-17

Decision: `review_pass_not_accepted_scope_breach_fresh_veto_required`

Gemini review 4 reproduced 114/114, both scoped whitespace checks, all eight
closed framework defects, and no V10 content, then returned `DECISION: pass` at
reviewer commit `0295a7d2`.

The worker receipt nevertheless records that the fresh project listed both
`orchestration/agent_inbox/antigravity/` and
`orchestration/agent_inbox/codex/`. The packet authorized exact files only.
Directory listing may enumerate protected prior-holdout receipt filenames, so
it breaches the protected metadata boundary even though the review reports no
protected content read and no implementation change.

The pass is preserved but is not accepting evidence. It grants no access,
reuse, authorship, or certification authority. A final fresh reviewer must use
only exact file reads and exact path-scoped Git/test commands, with directory
listing, globbing, broad search, and broad diff-name enumeration explicitly
forbidden. Framework source remains unchanged at `d56db482`; no V10 content or
protected artifact exists.
