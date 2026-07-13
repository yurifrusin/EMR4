# Ariadne DeepCode Runtime Observability

The DeepCode PTY adapter keeps artifact-marker completion, detached supervision,
controlled exit, and permission fail-closed behaviour unchanged. It now records
bounded diagnostic evidence in the caller's local outbox by default:

- `outbox/receipt.json.terminal.jsonl` contains sanitized `pty_data` events only.
- The transcript is capped at 256 events and 64 KiB, and is created under the
  worker `--cwd`; `--transcript` can select another path under that same cwd.
- Authorization headers, token/key-shaped values, JWTs, and common provider key
  prefixes are redacted before persistence and before the diagnostic window is
  evaluated. Raw unbounded terminal output is never persisted.
- The receipt records the relative transcript path, byte/event counts, cap and
  truncation flags, and redaction metadata. Transcript paths remain caller-owned
  local evidence and must be kept in an ignored receipt/outbox area.

## Liveness Observer

`python scripts/ariadne_deepcode_liveness.py` is a non-destructive observer. It
can read/write a caller-selected local state/evidence file:

```text
python scripts/ariadne_deepcode_liveness.py \
  --cwd <worker-worktree> \
  --artifact <artifact.md> \
  --receipt <receipt.json> \
  --outbox <outbox> \
  --state <ignored/liveness-state.json> \
  --evidence <ignored/liveness-evidence.json> \
  --watch <relevant-file> \
  --process-pid <supervisor-or-child-pid>
```

Each observation records artifact state, Git HEAD/status/diff fingerprints,
watched-file metadata and digests, process presence/activity when available,
receipt state, mailbox event metadata, changed signals, and the classification.
The reusable `capture_snapshot()`, `classify_liveness()`, and
`observe_liveness()` functions are importable from the same script module.

The only classifications are:

- `completed`: a valid canonical artifact marker was observed.
- `progressing`: one or more non-time signals changed from the prior snapshot.
- `idle_observed`: no signal changed, or a first baseline was established.
- `process_missing`: all explicitly observed process IDs are absent and the
  artifact is incomplete.

Elapsed time is recorded as advisory evidence and is never used by the
classifier. The observer does not send signals, kill processes, alter receipts,
or grant worker/integration authority.
