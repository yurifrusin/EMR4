# Ariadne Deep Code Mailbox Bridge

Date: 2026-07-11

The mailbox bridge adds a local return channel to Deep Code's interactive TTY.
It does not scrape terminal output or automate permission prompts.

## Flow

```text
orchestrator packet -> repository inbox -> human starts/resumes Deep Code TTY
Deep Code completion -> documented notify hook -> ignored local outbox event
orchestrator polls outbox -> validates durable packet artifact -> accepts/rejects result
```

`scripts/ariadne_deepcode_notify.cmd` is configured as Deep Code's user-level
`notify` hook. It receives the documented `STATUS`, `DURATION`, `FAIL_REASON`,
`BODY`, and `TITLE` variables and writes one local JSON event under
`local_data/ariadne-harness/deepcode-outbox/`. These events are ignored because
their body can contain code, prompts, or other sensitive worker output. They are
untrusted notifications, not verifier authority.

`scripts/ariadne_deepcode_mailbox.py` lists event metadata without printing
bodies. `--event <path>` displays one local event only when the orchestrator
needs to inspect a reply.

The bridge is asynchronous rather than a full terminal RPC: sending the next
message still requires the interactive operator to start or resume a Deep Code
TTY session. A future PTY bridge may automate only pre-approved read-only
turns; it must never answer permission prompts or silently grant an action that
is not in a verifier-passed capability packet.

The default user-level permissions are strict. Read-in-workspace, Git-log
queries, and `write-in-cwd` may be pre-authorized so the notify hook can return
an event without an operator approval on every turn. Deep Code applies that
write permission to its whole current working directory, not just the outbox.
For worker tasks, start Deep Code in a disposable packet-scoped worktree; the
packet is a semantic scope boundary and is not enforced by the CLI permission
system. Events remain untrusted, and no result is accepted without its
packet-scoped durable artifact and protected-orchestrator review.
Out-of-workspace reads/writes, deletion, Git mutation, network tools, and MCP
remain denied.
