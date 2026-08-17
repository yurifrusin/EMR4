# Threat-model delta — Ariadne effectiveness and DeepSeek Harness adaptations

Date: 2026-08-17

Timestamp: 2026-08-17T09:47:18.3542784+10:00 (Australia/Brisbane)

Status: `frozen`

## Assets and trust boundaries

The protected assets are exact Git/ref identity, the primary repository and
Python environment, validation-result integrity, the active-operation latch,
protected evidence and the user-owned untracked workspace. New code remains in
the local development harness and receives no Raisa runtime authority.

## Threats and controls

- `DHAR-T01` — a human-authored commit ID is invented or stale. Receipt Git
  identity is populated only by fixed read-only Git argv and protected refs are
  compared with the configured exact expected commit.
- `DHAR-T02` — a compound validation masks an earlier failure. The validation
  runner accepts the existing shell-free structured argv schema, launches one
  process at a time and stops at the first nonzero exit.
- `DHAR-T03` — compaction or terminal-session loss erases command outcome. A
  canonical lifecycle receipt is written atomically before execution and after
  each terminal command result; incomplete state remains explicit.
- `DHAR-T04` — fixture-dependent pytest runs without repository conftest or
  shared-schema serialization. Direct pytest and `--noconftest` are rejected by
  the admitted runner/serial launcher; provider-free execution remains a
  distinct explicit launcher.
- `DHAR-T05` — a nonexistent or escaping test path is silently accepted. Test
  selectors are resolved inside the exact repository root and must exist before
  process launch.
- `DHAR-T06` — an external worker installs packages into the primary
  environment. The DeepSeek child receives no inherited virtual-environment or
  index configuration, pip is offline/noninteractive, and the instruction
  contract forbids package managers and environment mutation. This reduces the
  observed accidental path but does not claim hostile-process containment.
- `DHAR-T07` — command output leaks sensitive content through a durable receipt.
  Receipts store only byte counts and SHA-256 digests; full output is transient
  terminal text and remains governed by the command's existing data boundary.
- `DHAR-T08` — imported third-party harness code creates a supply-chain or
  compatibility dependency. No DeepSeek Harness code or dependency is copied,
  installed or executed; only independently implemented architectural patterns
  are used.

## Residual risk

The DeepSeek worker still has the capabilities granted by Claude Code and is
not OS-sandboxed by these changes. A determined process can override child
environment variables. Worker changes therefore remain untrusted until exact
worktree review and deterministic verification; package/environment mutation
outside the worktree remains a stop condition.

The validation runner proves process ordering and durable terminal metadata,
not semantic correctness of the commands it is given. Command selection and
acceptance remain Sol-owned and risk-weighted.
