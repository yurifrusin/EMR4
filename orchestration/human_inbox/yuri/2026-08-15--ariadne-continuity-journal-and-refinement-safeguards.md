# Ariadne continuity journal and refinement safeguards — paired summary

Date: 2026-08-15

Timestamp: 2026-08-15T19:47:44+10:00 (Australia/Brisbane)

Attention required: `no`

Development engine: `continuing_to_delete_confirm_scaffold`

## Lay summary

We kept three genuinely useful ideas from Prime Agent, but only inside the
Ariadne development harness.

First, Ariadne can now reason from a small operation journal after an
interruption: it can tell the difference between genuinely new work, an exact
completed result, a conflicting repeat, work that is still running and work
whose outcome is uncertain. Secondly, it can avoid pointlessly rerunning a
deterministic check when the code, evidence, command and toolchain are all
unchanged—without ever turning a failure or uncertainty into a success.
Thirdly, proposed improvements to the harness can be kept in quarantine,
tested and reviewed, then explicitly accepted or rolled back through a new
recorded generation.

These are guardrails and memory aids, not a self-improving autonomous agent.
They cannot execute commands, edit their own instructions, install Prime Agent
or reach Raisa's product, database, provider or patient surfaces.

The first mechanical implementation looked green but independent review found
several semantic gaps. Those were corrected and recorded. The final candidate
passed 200 focused tests, all 167 hostile mutations, the broader repository
profile and one fresh Gemini 3.7 Flash/high veto. The reviewer left the exact
candidate clean and unchanged.

We are now returning to Raisa product work as you requested. The next tranche
is the still-unmounted delete-confirm schema-and-transaction scaffold.

## Technical summary

Accepted result:
`ariadne_provider_free_continuity_journal_and_refinement_promotion_safeguards_pass`
at exact reviewed source `79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce`.

The sidecar freezes:

- append-only `(generation, sequence)` journals with request/result identity,
  exact recovery uncertainty and snapshot-required stale cursors;
- composite gate fingerprints over candidate source/tree, evidence, command
  manifest, relevant inputs and toolchain;
- exact reuse/diagnose/resolve decisions with contradictory evidence rejected;
- bounded inert refinement proposals bound to source, base, evidence and
  validation-manifest digests;
- exact Sol promoter authority, pairwise-distinct global review and immutable
  terminal decision history; and
- rollback of only one real, latest eligible promoted state into exactly the
  next generation.

Evidence: 200 focused tests, 167/167 hostile mutations rejected, canonical
Ruff/210-source-compile/196-test/Diary-syntax/whitespace pass, and one fresh
schema-constrained Gemini 3.7 Flash/high pass with clean exact-HEAD
preflight/postflight. AER-0331 records the rejected worker self-pass;
AER-0332/0333 record the harmless outer/inner timeout mismatch and its local
recurrence. The control now requires derived timeout margins, existing-process
inspection before retry and separately run later gates.

Deliberately closed: runtime persistence, supervisor/daemon, command execution
or replay, automatic refinement application, Prime Agent installation, Raisa
application/API/database/network/provider/data surfaces, credentials/IAM,
deployment, production, release, Pages and protected refs.
