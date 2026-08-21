# DeepSeek Harness source diagnosis — lay and technical summary

Date: 2026-08-21
Timestamp: 2026-08-21T13:26:54.8506659+10:00 (Australia/Brisbane)
Reviewed source: `f735e6c9f4412aea8e83e410c0292668ebe7853f`

## Lay summary

We have found a credible, narrow explanation for the Harness failing before it
reached DeepSeek. Our generated Harness profile handed its module loader a
Windows absolute path. The same rc7 Harness had already passed a provider-free
boot rehearsal when those module names were written relative to the profile.

This was established without launching the Harness or spending a provider
request. The evidence identifies one matching source branch rather than a list
of guesses. The sensible next step is a tiny provider-free repair of the two
module-name rows, followed later by a separately controlled boot proof. We are
not yet claiming the Harness is ready for EMR4 worker development.

## Technical summary

- accepted verdict: `unique_supported_coordinate`;
- owner: `profile_input`;
- reviewed Git object: `f735e6c9f4412aea8e83e410c0292668ebe7853f`;
- exact package: `@deepseek-ai/dsh@0.1.0-rc.7`;
- current forms: `quoted(proof / "sentinel.mjs")` and later
  `quoted(proof / "runner.mjs")`;
- accepted control forms:
  `../../../installation/proof/sentinel.mjs` and
  `../../../installation/proof/runner.mjs`;
- deterministic verification: 8 focused and 58 widened tests passed, with
  schema, Ruff, compilation and diff checks passed; and
- Node/Harness/broker/worker/model/provider/network counts: all zero.

The historical test that requires the attempt-004 latch was deliberately
deselected after the live latch advanced; it was not weakened. A grouped command
with two non-existent mnemonic test paths was also rejected and rerun from the
repository-resolved inventory. Both are retained for the workflow register.

No product behavior, data, runtime, deployment, Pages or protected ref changed.
