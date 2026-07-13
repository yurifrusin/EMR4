# S13 Terra Acceptance - Registered Envelope Authority

Decision: accepted on staging after a Terra-owned correction. Protected master
is not touched; S14 and S15 remain closed pending Sol authorization of the
separate exact S13 manifest.

## Accepted Scope

The pure Diary envelope layer now validates registered capability names at
construction time. Direct registry names resolve before grammar aliases, so
`propose_booking` and the other registered proposal names cannot pass through
as unknown free strings. Grammar aliases still resolve via their descriptor
capability name. Truly unregistered names remain compatible.

No router, REST/OpenAPI command, GraphQL artifact, schema/database model,
migration, provider, UI, deployment, confirmation action/route, audit write,
or terminal-to-active policy changed. The API Spine remains mixed: GraphQL is
read-only, and existing appointment proposal/confirmation REST commands retain
their idempotency, freshness, evidence, revalidation, and audit boundaries.

## Worker Evidence

The accepted same-lane DeepSeek Flash/high completion artifact is
`orchestration/agent_inbox/deepcode/s13-envelope-authority-completion.md`.
Its retry receipt is local-only under
`local_data/ariadne-harness/s13-w1/receipt-retry.json`:

- `status: completed`, one mailbox event, canonical terminal artifact marker,
  no permission prompt, process cleanup confirmed, and released owner lock;
- `artifact_deadline_active: false` on the accepted retry;
- bounded transcript: 72 events, 65,535 bytes, byte-truncated, and no
  redactions needed;
- advisory duration from receipt timestamps: about 211 seconds.

The completion artifact reports candidate `6595bf78`. It is preserved as the
worker's durable result, not rewritten to conceal the subsequent Terra fix.

## Terra Correction

Initial acceptance review found that the candidate began lookup through
`action_verb_for_envelope()`. Direct registered names such as
`propose_booking` are not grammar aliases, so they incorrectly passed through
without enforcement. Terra corrected the resolver to look up the registry
first, then fall back to grammar aliases, and added direct-name tier and author
regressions. This is the final product/test correction work for S13.

## Verification

All deterministic tests passed from the staging worktree:

```text
22 passed: tests/test_envelope_capability_policy.py
195 passed: envelope, boundary, capability-manifest, grammar, route-contract,
route-coverage, workflow-chain, and API-Spine artifact suites
```

`python -m py_compile` for the changed Diary modules and `git diff --check`
also pass. Test evidence is deterministic and local; it is not live-provider,
live-backend, or external-client evidence.

## S13 Metrics

| Metric | Result |
| --- | --- |
| Sol interventions / escalation reason | 1 / progress-based recovery after source/test signals stopped changing without artifact, receipt, or commit |
| Terra planning/acceptance corrections | 1 deadline-configuration correction (`1800` to `0`); 1 final direct-registry acceptance correction |
| Worker launches / stalls / retries | 2 worker sessions after one pre-worker adapter setup failure; 1 stall; 1 same-lane retry; 0 marker corrections |
| Lifecycle defects | 2: missing local lockfile-pinned `node-pty` dependency, then an active wall-clock deadline conflicting with inactive-deadline policy |
| Consultations | 0 Conductor, 0 verifier |
| Invalid integrations / manifest variances | 0 / 0 |
| Duplicated-context events | 0 |
| Models used | Terra and DeepSeek 4 Flash/high. Gemini, DeepSeek Pro, Claude, and a verifier were unnecessary because one pure-domain lane and deterministic gates were sufficient. |
| Advisory durations | Stalled session: about 13 minutes from lock acquisition to recorded termination; accepted retry: about 211 seconds from receipt timestamps. |
| Coordination vs product/test added lines | 339 / 660 through S13 acceptance |
| Final correction work | Direct registered-name resolution plus two regression cases; no scope or authority expansion. |

The initial adapter failure occurred before a Deep Code worker session started,
so it is counted as a lifecycle setup defect rather than a second worker stall.
The accepted retry is the only worker retry counted above.
