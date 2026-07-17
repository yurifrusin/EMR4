# Final red packet — CodeQL recovery exact-head veto

Decision format: `DECISION: pass` or `DECISION: revision_required`.

Worktree: `C:\Users\sarashera\EMR4-worktrees\security-hardening-codeql-red`.
Branch: `gemini/security-hardening-codeql-red`.
Frozen candidate: `a248f659545975ada9662e08f89962c87952e77f`.
Security delta: `4efe9ff3363c3f563a03a1f5bd0978998ca55d07..a248f659545975ada9662e08f89962c87952e77f`.

Use a fresh Antigravity project. Do not read earlier red/blue review artifacts,
purple acceptance, Sol acceptance rationale, or protected holdout/provider/
historical-data surfaces.

Attempt to prove that URL-controlled smoke/dev state can still reach the
authenticated Diary loader or any live appointment/API path without a token.
Check direct calls, DOMContentLoaded ordering, refreshes, post-auth messages,
and smoke interactions. Verify the shared renderer cannot select live data
from a URL-controlled value, and that `data:`, `blob:`, remote GitHub Pages,
and non-loopback hosts cannot activate smoke. Also look for regression in
local file/localhost smoke, authenticated refresh, practitioner-directory
loading, confirmation allowlisting, random generation, and selector safety.

Run serially:

- the focused 45-test command used by Sol;
- `pytest review/test_diary_smoke.py -q` (139 cases);
- `node --check docs\diary\diary.js`;
- `git diff cc6925f9 --check -- . ':!orchestration/agent_inbox/antigravity/security-hardening-red-review.md'`.

Write only
`orchestration/agent_inbox/antigravity/security-hardening-codeql-final-red-review.md`
and commit it. Do not implement fixes, integrate, push, alter GitHub settings,
or read prohibited material.
