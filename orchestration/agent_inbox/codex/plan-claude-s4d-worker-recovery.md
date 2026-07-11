# Ariadne Conductor Decision: S4d Worker Recovery

Date: 2026-07-11
Settings fingerprint: `sha256:cfb5534ea58bb22bdf602ce4f572ea1bc8b68b9ca581f4b4d88d59d060b4a072`

## Decision

D2 is accepted and integrated after orchestrator review. D1 and D3 require a
bounded recovery cycle; protected-orchestrator self-acceptance is prohibited.
No fourth DeepSeek lane is added.

- D1 reuses lane D1 and its existing owned source. A lightweight recovery may
  write only the missing corrected durable artifact. It must accurately state
  that completion requires artifact + PTY event + receipt, while only the
  artifact is authority-bearing.
- D3's scope-breaching retry is discarded. A fresh D3 disposable worktree may
  rewrite only its owned mailbox-settings test and artifact from the committed
  recovery packet. It must not edit the PTY test file or claim tests were run.

Both recovery outputs require fresh artifact/event/receipt evidence and a
verifier pass before integration. GPT Terra remains sole integrator, committer,
and pusher. No runtime scope is opened.

This is a Conductor recovery decision only; it grants no dispatch, integration,
commit, or push authority to the Conductor or workers.
