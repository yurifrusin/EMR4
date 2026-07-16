# LC4V6 Sol Recovery Amendment

Date: 2026-07-16

Decision: `deepseek_self_pass_rejected_conceptual_recovery_invoked`

DeepSeek V4 Flash/high completed through Claude Code `--bare` and returned a
75-test self-pass. The exact candidate is preserved at worker commit
`70d462d15aa7260981277118d3ece74b292c572c`, adopted as untrusted at
`34afc94b`. No existing file, protected holdout, corpus, manifest, content,
seal, report, or acceptance rule was changed by the worker.

Sol rejected the candidate as acceptance evidence because its central
fail-closed claims were conceptual rather than mechanical:

- its documented atomic transition used three ordinary writes with no lock or
  crash-closed state;
- it erased the source seal instead of retaining and binding a consumed seal;
- it hard-coded repeat variance to zero and emitted empty slices;
- it validated hash prefixes rather than exact bindings;
- it did not validate exact scenario/repeat/dimension populations or slice
  arithmetic; and
- it could not permanently consume a structurally valid evidence-invalid run.

Under the recovery lease, Sol replaced only the new framework and its new empty
tests. Recovery adds exact manifest/observation populations, measured variance,
recursive aggregate leakage guards, exact dimension/action/slice arithmetic,
strict hash/seal binding, a durable exclusive attempt lock, atomic per-file
replacement, retained consumed-seal and marker hashes, and separate structural
versus evidence-valid validation so any commenced one-shot run becomes
permanently non-rerunnable even when evidence is invalid.

The recovered empty suite passes 36/36. It contains no V6 natural-language
content and imports no product interpreter or historical holdout surface. No
same-lane correction is authorized. A fresh exact-head Gemini veto is required
before Sol may author any V6 content.
