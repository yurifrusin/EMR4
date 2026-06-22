# plan-codex-codex-command-proposal-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/command-proposal-review-harness` |
| Source Task | `codex-command-proposal-review-harness` |
| Status | integrated |
| Created | 2026-06-23 01:08 +1000 |
| Source HEAD | `9fb853d` |

## Plan Summary

Review harness and API snippets for proposal layer

## My Understanding

Create documentation and reusable review material for the formal command/proposal workflow so future agents and the user can exercise safe, warning, and blocked proposal paths consistently, starting with the existing appointment create proposal endpoint. This is a non-runtime workstream.

## Intended Surface / Boundary

Orchestration and developer-review documentation only: review harness/checklists, sprint closeout notes, and PowerShell/API snippets. No diary grid, waiting room panel, booking modal, taskpane, Command Centre, backend route, schema, migration, or Bernie runtime surfaces should change.

## Out Of Scope

Production backend/frontend changes; migrations; diary UI; taskpane; Command Centre; Bernie runtime; modifying Claude/Antigravity packets after dispatch; changing appointment proposal semantics.

## Files I Expect To Edit

Likely orchestration/sprint_closeout.md; a focused orchestration review harness/checklist document if one exists or a new one under orchestration/; possibly docs/emr4-development-environment-dummys-guide.md or another existing developer guide if it is the right place for API snippets; the AZ task packet completion notes only after approved implementation.

## Implementation Steps

Survey existing orchestration closeout/review docs and developer guide patterns; identify the current create proposal endpoint contract and available examples without changing production code; add a compact reusable harness covering auth setup, safe proposal, warning proposal, blocked proposal, expected response fields/classes, and confirmation-boundary language; update sprint closeout/review guidance so Codex knows how to use the harness when integrating AX/AY; keep wording precise around surfaces: booking slots are API examples only, not diary-grid geometry or UI slots; run diff/snippet verification after approval.

## Visual / Behavioural Acceptance Checks

Plan captured first; after approval, docs clearly distinguish safe, warning, and blocked proposal paths; examples are copy-pasteable PowerShell/API snippets or explicitly marked pseudo-snippets if they depend on local IDs; no runtime files are changed; future agents can reuse the harness without reading this chat; git diff --check passes; executable snippet/schema verification is noted if practical.

## Risks / Ambiguities

The create proposal endpoint may be evolving in parallel with AX/AY, so examples may need placeholders or a note to re-check final field names during integration; warning-path test data may require specific local appointments/breaks/provisional patients; too much detail in a developer guide could drift, so prefer concise snippets with expected response classes over duplicating backend schema internals.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
