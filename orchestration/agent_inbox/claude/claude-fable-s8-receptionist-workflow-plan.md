# Fable Conductor Packet - S8 Receptionist Workflow

Date: 2026-07-13
Role: Conductor
Resource: `claude-fable-conductor` (`claude-fable-5`, high reasoning)
Expected artifact:
`orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md`

## Current State

S5 audited the receptionist taskpane-to-diary workflow and returned Conditional
Go. S6 repaired the production AHPRA regression and restored all 139 diary
browser tests. S7 completed the Ariadne cross-boundary contract audit and added
an executable independent-review acceptance gate. `master` and
`handoff/current` are synchronized at `559bc0ac` when this packet is authored.

The current complete-settings fingerprint is
`sha256:58313bbfd011f4eb70234fc320b1c0393f2a6a56dd537f329baacd830010cb24`.

## Sol Advisory Direction

Return to substantial EMR4 product work. Plan S8 as the first coherent
receptionist workflow implementation sprint, beginning with:

1. diary launch reliability across local/development/deployed environments;
2. visible, useful failure handling for Word desktop/online dialog or popup
   launch failures.

Sequence the remaining S5 usability findings behind that tranche:

- cancellation/DNA/NoShow reason-code affordance and validation recovery;
- date-picker fallback for embedded Office webviews;
- same-day appointment search/filtering;
- easier read-only access to appointment reasons/notes.

The auto-refresh selection blocker and diary smoke failures are already fixed.
Do not repeat those repairs.

Terminal-to-active appointment-status transitions remain a separate product
policy question. Do not silently choose block/warn/allow in S8 and do not let
that deferred decision prevent the launch-reliability sprint.

This direction is advisory. The Conductor has final authority to accept,
counter, narrow, sequence, define the sprint, and allocate available workers.
If the direction is accepted, end the dialogue and publish the executable plan.
Sol may issue at most one rejoinder if there is a material counterproposal.

## Required Plan Content

Produce a bounded but substantial implementation plan, not another inventory or
documentation-only audit. Record:

- direction dialogue disposition;
- verified settings fingerprint;
- exact implementation and test surfaces after inspecting current code;
- worker allocation from the current pool, including model/reasoning and
  fallback handling;
- non-overlapping ownership and durable artifact paths;
- acceptance evidence, independent review needs, and the S7 executable review
  gate where applicable;
- regular commit/push checkpoints;
- closed gates and any genuine user decision boundary.

Prefer Antigravity/Gemini for a consumer UX lane when available and DeepSeek
Flash for implementation/test/review lanes as their capabilities fit. Do not
allocate workers merely to fill slots. No monetary or wall-clock task caps are
active.

Do not open provider/live-provider, database migration, deployment/production,
external patient-client, H15/H-series, historical diary, memory/RAG/GraphRAG,
Bernie D5 expansion, schema, or new model-write authority without a separately
justified boundary decision.

Write the final plan to the expected artifact path and end it with
`STATUS: complete`.
