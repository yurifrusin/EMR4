# LC4V6 Sol Source Freeze

Date: 2026-07-16

Decision: `fresh_v6_source_sealed_unconsumed`

GPT Sol alone authored the 288-scenario Gold/adjudicated V6 source after the
content-blind framework and frozen thresholds were independently accepted and
all external sessions were closed. No parser or policy evaluation was run
during authorship or structural validation.

The protected source commit is
`0527848bb7d4c86a4c138f49016472c447c05757`. The exact bindings are:

- source: `sha256:d0ea315cbe2da3c2fbb68cd2934484e4d96e59db1ae8a164f7394fab48482a64`
- corpus: `sha256:10fef42500f5fd379248c67d0348e5bd75176be62445f9180c9a18618aa1bdfa`
- manifest: `sha256:4892e7144549d25c522f3e0eafc6faaed0af61b33e0fc05ca8a3f460a01cdd9a`
- framework: `sha256:5d3b90126cf0e3d5077b7670883128c01496b9240693499765241ea7e841ce5f`
- evaluator bundle: `sha256:485acda0a4f9c54fd9d2d890e228cac8fe58bfa73d4f140499c0b5ea2c4cc220`

The evaluator bundle binds the non-intercepted evaluator, the already frozen
acceptance rule, and the protected one-shot runner. The manifest records 24
families, 288 unique scenarios/cells, 72 multi-turn and 216 one-shot scenarios,
all six actions, and two repeats. The unconsumed source seal exists while the
attempt marker, aggregate report, and durable attempt lock do not.

After this freeze is committed, the source and its tests are protected. The
only authorized content load is the exact named pre-run validation immediately
followed by the single `lc4v6-fresh-attempt-001` evaluation. After that run,
only the aggregate report, production receipt, marker, consumed seal, and lock
may be inspected. No case-level artifact may be written or committed.
