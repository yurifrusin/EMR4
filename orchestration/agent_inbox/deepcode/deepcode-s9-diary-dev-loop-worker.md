# S9 Worker - Local Diary Development Loop

Role: implementation owner
Resource: `deepseek-flash-workers` instance 1
Model: `deepseek-v4-flash` / high
Parent plan:
`orchestration/agent_inbox/codex/plan-deepseek-pro-s9-local-diary-dev-loop.md`
Expected artifact:
`orchestration/agent_inbox/codex/review-deepseek-s9-diary-dev-loop.md`

Implement the corrected S9 plan only.

## Ownership

- `EMR4 Sidebar/webpack.config.js`
- `review/test_taskpane_diary_launch.py`
- this completion artifact

Configure webpack-dev-server 6 to serve `docs/diary/` at `/diary` and
`docs/images/` at `/images`, using paths resolved from the existing config
location. Do not copy assets, change production builds, alter taskpane URL
resolution, or touch clinical/runtime contracts.

Add deterministic static/config tests and, when practical, start the real HTTPS
dev server to prove `/diary/diary.html` and `/images/emr_cube1.png` return 200.
Use the injected shared Python and Node paths before claiming tools unavailable.
Do not weaken the 13 existing taskpane launch tests.

Run focused pytest, Node syntax, whitespace, and any bounded live HTTP probe.
Create a local candidate commit. Record exact commands/counts, branch/SHA,
remaining risks, and closed-gate compliance in the artifact. End with
`STATUS: complete` and finish normally.

No network beyond localhost verification, push, integration, `master`,
`handoff/current`, deployment, or product-policy authority.
