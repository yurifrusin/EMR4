# DeepSeek native Harness future-runner materialisation identity-binding recovery

Date: 2026-08-21

Timestamp: 2026-08-21T21:54:38.7791038+10:00 (Australia/Brisbane)

Status: `frozen recovery`

Reasoning level: `high`

## Rejected first contract

The first materialisation contract reused the new outer tranche operation,
attempt and planning-source identity when generating the diagnostic helper.
The helper source embeds all three values, so its machine hash became
`4a8733501ddd78c703068a629015546b37ace8689f01c433d9d32d5375c7fd8e`
rather than the accepted helper binding
`bd2995a62c7d8bbf37b29c0cd5b5a88c3570341255d1644d9cb98cbef0bd490e`.
The generator rejected `source_binding_mismatch` before evidence output.

## Narrow correction

Separate the outer evidence identity from the embedded accepted bundle
identity. The outer operation remains the active materialisation tranche. The
disposable bundle, helper, sidecar, broker reading and controller terminal use
the exact already accepted embedded fixture identity from the predecessor:

- operation:
  `deepseek-native-harness-provider-free-post-hmr-pre-request-diagnostic-sidecar-integration-rehearsal`;
- attempt: `future-post-hmr-sidecar-static-fixture-001`; and
- candidate: `cc75a9f8991120b66bf64ee12d415462f2cbfbb3`.

This preserves the exact accepted helper hash and allows the bundle to prove
the already accepted gears as one connected fixture. It does not reclassify
that embedded identity as a new attempt and does not authorise occupied use.
Both target-coordinate rebinding and embedded operation/attempt identity
rebinding remain visible later gates.

## Boundary

No accepted source or consumed attempt changes. No Node, Harness, broker,
worker, model or provider process runs. The rejected contract is a worktree
draft only; canonical evidence remains absent until the corrected generator
passes write plus idempotent check.
