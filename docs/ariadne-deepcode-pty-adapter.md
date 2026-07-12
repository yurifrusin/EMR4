# Ariadne Deep Code PTY Adapter

Date: 2026-07-11

Deep Code requires a real terminal and can remain alive after a packet artifact
has been written. That prevents its completion hook from firing and leaves stale
agent processes. The PTY adapter owns this transport lifecycle without granting
the worker additional authority.

The adapter:

- starts Deep Code in a real cross-platform PTY backed by `node-pty`;
- waits for the packet-declared artifact and validates its decision shape;
- sends `/exit` only after that artifact exists;
- writes a local untrusted PTY-completion event after controlled process exit;
- emits a machine-readable local receipt without storing terminal output; and
- stops immediately on a permission prompt instead of answering it.

Deep Code currently ignores graceful-exit keystrokes under Windows ConPTY. The
adapter retries the documented `/exit` and `Ctrl+D` controls for a bounded
period, then terminates the already-completed PTY. This is an accepted transport
completion only when the artifact is valid and the TUI reported the turn
completed. The receipt records `forced_cleanup: true`; no artifact or incomplete
turn still fails closed.

The packet, artifact, outbox, and receipt must all resolve inside the supplied
worker cwd. Live workers therefore run in disposable packet-scoped worktrees.
Before launch, the Python entry point creates a secret-free project settings
file when one is absent. It pre-authorizes in-worktree reads/writes, denies
out-of-worktree and destructive capabilities, and contains no API key. Existing
settings that do not allow bounded writes or still ask for them fail preflight.
The adapter event replaces reliance on Deep Code's configured notify launcher
for automated sessions. On Windows, that launcher invokes its target without a
shell and cannot reliably execute `.cmd` hooks. Manual TTY sessions may still
use the existing notify hook, but automated acceptance uses the PTY receipt and
adapter event. Neither is authority-bearing.

The PTY is transport containment, not integration authority. The protected
orchestrator must still validate the durable artifact, ownership boundaries,
mailbox event, and receipt before accepting work.

Install the adapter dependency once per harness installation:

```text
cd orchestration/deepcode_pty
npm ci
```

Run one packet from the repository root:

```text
python scripts/ariadne_deepcode_pty.py \
  --cwd <disposable-worktree> \
  --packet <packet-relative-path> \
  --artifact <artifact-relative-path> \
  --outbox local_data/ariadne-harness/deepcode-outbox \
  --receipt local_data/ariadne-harness/deepcode-receipt.json
```

Exit status `0` means artifact and mailbox event were observed. Exit status `3`
means an unexpected permission prompt blocked execution. Exit status `4` means
the artifact or mailbox completion contract failed. No nonzero result permits
dispatch continuation or integration.

The adapter is the single source of truth for completion-artifact identity. It
injects the normalized monitored artifact path into the live Deep Code prompt;
the model must write exactly that path and must not infer an alternate filename.
The same resolved path is used for containment checks, artifact validation,
mailbox completion, and the receipt.

The launcher also accepts explicit `--model deepseek-v4-flash|deepseek-v4-pro`
and `--reasoning high|max` controls. These write only model/reasoning fields to
the disposable worktree's project settings and never copy API keys or base URLs.
This supports `deepseek-pro-conductor-fallback` when Claude reports a real usage
limit; the receipt records the configured model and reasoning.
