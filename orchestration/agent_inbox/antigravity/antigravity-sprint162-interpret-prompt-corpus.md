# Antigravity Sprint 162 - Interpret Prompt Corpus Lane

## Mission

Review the receptionist/product shape of the first executable Bernie prompt
thread corpus after Fable's recommendation.

## Scope

- `tests/fixtures/bernie_scenarios/interpret_*.yaml`
- `tests/fixtures/bernie_scenarios/README.md`
- `tests/bernie_scenarios/README.md`

## Expected Lens

- Are the prompt threads receptionist-like enough to be useful?
- Do the fixtures cover the first sensible multi-turn slice: full request,
  clarification, changes to date/time/duration/practitioner, no prior-frame
  merge, confirm-required no-write, past-date block, and selected-slot pivot?
- Are evidence labels honest: `fake-provider, route-level`, not live-backend,
  live-provider, provider-quality, or training evidence?
- Do the fixtures avoid raw historical diary trove, H15/H-series runtime
  imports, provider calls, memory/RAG/GraphRAG, and model-to-database writes?

## Current Implementation Notes

Antigravity was invoked through the project-scoped CLI path documented in
`AGENTS.md`:

```powershell
C:\Users\sarashera\AppData\Local\agy\bin\agy.exe --add-dir C:\Users\sarashera\emr4 --print-timeout 15m --print "<Sprint 162 review prompt>"
```

The CLI wrote the durable review packet
`orchestration/agent_inbox/antigravity/antigravity-sprint162-interpret-prompt-corpus-cli.md`.
Codex had briefly misidentified the desktop executable as the only available
entry point; Yuri corrected that context drift before closeout, and the actual
`agy.exe` lane was run successfully.

## Review Result

The Antigravity CLI review found no blocking issues and recorded a clear pass.
It accepted the first corpus slice as sensible fake-provider, route-level
contract coverage with no H15/H-series/trove/provider/memory gate opening and no
appointment/audit writes.

Accepted polish:

- Clarified that executable `interpret_*` fixtures are authored synthetic
  receptionist-style contract fixtures.
- Changed the missing-practitioner follow-up wording from "Change that to Dr
  Shera" to "With Dr Shera please" so it reads as fill-in rather than
  replacement.

Deferred suggestion:

- A future past-date fixture can use more natural wording once the fake
  interpreter supports phrases such as "last Wednesday" or "the first of July";
  this sprint keeps the ISO date because it is the current deterministic route
  contract.
