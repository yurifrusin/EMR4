# S4d Orchestrator Recovery Lease

**Approved by:** Yuri
**Date:** 2026-07-11
**Risk class:** low
**Orchestrator:** `openai-primary-orchestrator`, current model GPT Sol

## Scope

Adopt D1's `tests/test_ariadne_deepcode_adapter_settings.py` and D3's
`tests/test_ariadne_deepcode_mailbox_settings.py` as untrusted candidate source.
Do not adopt any worker-authored closeout as a replacement attestation. Reject
D3's out-of-scope edit to `tests/test_ariadne_deepcode_pty.py`.

GPT Sol may amend only the two planned test files, run deterministic focused
and adjacent harness tests, perform diff/ownership review, and write a separate
S4d integration record. No runtime, provider, frontend, database, GraphQL,
H-series, D5, deployment, release, or worker reallocation is authorized.

## Preserved Failures

- D1's first closeout contradicted the three-part completion rule; two
  artifact-only retries timed out.
- D3's first revision falsely claimed tests ran; its next retry edited an
  unowned test file, wrote an artifact before turn completion, and was blocked
  on a permission prompt.
- The recovery verifier wrote a late artifact after the adapter's artifact
  deadline and therefore did not satisfy its transport contract.
