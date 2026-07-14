# Claude Code bare worktree isolation

## Purpose

DeepSeek workers launched through Claude Code `--bare` must operate only in a
disposable packet-scoped worktree. The protected integration worktree remains
owned by the GPT Sol orchestrator.

This guard responds to the LC4R4 isolation incident in which a worker received
a disposable `--cwd` but left rejected candidate copies in the protected
master worktree. The copies were detected before integration, preserved in a
named stash, and never accepted.

## Launcher contract

`scripts/ariadne_deepseek_claude.py` resolves the supplied worker worktree and
uses that same absolute path for all three directory signals available to the
Claude Code process:

- the child process working directory;
- inherited `PWD` and `INIT_CWD` environment values; and
- an `AUTHORIZED_WORKTREE_ROOT` boundary prepended to the durable worker
  packet.

The prompt boundary is semantic defence in depth. The process working
directory and environment pinning are the deterministic launcher controls.
They do not make Claude Code an integration authority and do not prove that an
external tool cannot violate the boundary.

## Orchestrator observations

Every Claude Code bare lane additionally requires protected-master cleanliness
observations:

1. immediately before worker launch;
2. while the worker is active; and
3. after the worker exits, before candidate review or integration.

Any unexpected protected-worktree change is a scope breach. The orchestrator
must reject candidate acceptance, preserve the evidence reversibly, restore a
clean integration worktree without discarding user work, and document the
reconciliation before considering another dispatch.

The outer process launcher must also set its own working directory to the
disposable worktree. Packet artifacts and worker commits remain untrusted
candidates until Sol review and the ordinary acceptance gates complete.
