# Ariadne Deep Code PTY Live Smoke

Date: 2026-07-11

A disposable Windows worktree proved the automated Deep Code lifecycle with
`deepseek-v4-flash` / high reasoning. The final run required no user permission
choice or terminal input and produced:

- one fresh packet-declared `DECISION: pass` artifact;
- a Deep Code turn-completion observation;
- four bounded graceful-exit signals;
- forced cleanup after the TUI ignored its documented exit controls;
- one adapter-generated untrusted mailbox event;
- no persisted terminal output; and
- no remaining process from the live run.

The local receipt status was `completed` with reason
`artifact_and_adapter_event_observed_forced_cleanup`. Raw smoke artifacts,
mailbox events, settings, and receipts remained ignored inside the disposable
worktree and were not committed.

Earlier manual Deep Code invocations left four stale processes because `-p`
did not terminate after producing a result. Those processes predated the PTY
adapter and were removed after their durable artifacts had already been
captured. Automated sessions must use the adapter rather than visible terminal
launches.
