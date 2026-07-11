# Ariadne-Local S4d Veto Fallback Review

DECISION: pass

Date: 2026-07-11
Reviewer: protected GPT Sol orchestrator
Independence: reduced; Antigravity stand-down fallback
Settings fingerprint: `sha256:14b8ae3439d6ce03bb1c4405dd42694acc62ca1fd4278f0812c480b57e7e775c`

## Antigravity Stand-Down

Antigravity/Gemini 3.5 Flash was invoked in plan mode at handoff `f2d3c0c1`.
It did not review the requested artifacts or return `DECISION: pass|veto`;
instead it described its CLI mode and claimed unrelated environment/process
inspection. Its worktree remained clean. No Antigravity review authority is
claimed, and independent-review breadth is explicitly reduced.

## Local Veto Checks

- Worker closeout provenance is non-transferable; the recovery policy forbids
  orchestrator rewriting of worker attestation.
- D1/D3 source is labelled untrusted candidate material, with worker failures,
  false evidence, timeout, and D3 ownership breach preserved.
- D3's out-of-scope PTY test edit was not integrated. GPT Sol owns the compact
  replacement in the planned mailbox-settings file.
- The protected resource is `openai-primary-orchestrator`, current model GPT
  Sol. The spawned `gpt-sol-conductor-fallback` is a distinct subagent resource
  with no integration authority.
- Conductor order is Fable, then Opus only for usage/availability failure, then
  the spawned GPT Sol fallback.
- The PTY adapter fails on permission prompts, requires artifact + completed
  turn before cleanup, confirms process cleanup, emits only untrusted transport
  evidence, and does not persist terminal output.
- The final diff is harness settings, docs, tests, fixtures, and evidence only;
  it opens no EMR4 runtime authority.

## Verification

Seventy focused Ariadne tests passed. The complete-settings allocator selected
Fable conductor, DeepSeek Flash verifier, and `openai-primary-orchestrator`.
The PTY npm package audit reported zero vulnerabilities. JSON and diff checks
passed.

## Residual Risks

- Windows Deep Code ignores graceful exit controls, so completed sessions use
  recorded forced cleanup.
- Some PTY behavior tests pin source-level JavaScript guards and will need
  maintenance if the runner is refactored.
- The GPT Sol subagent adapter observation is currently synthetic; actual
  reachability must be observed before that third fallback is selected.
- Antigravity supplied no independent veto, so S4d closes with reduced review
  independence rather than pretending that lane passed.
