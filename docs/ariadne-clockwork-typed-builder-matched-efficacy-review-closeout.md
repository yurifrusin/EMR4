# Governance clockwork typed-builder matched efficacy review — closeout

Date: 2026-08-23

Timestamp: 2026-08-23T18:08:50.3183802+10:00 (Australia/Brisbane)

Status: `accepted_pending_single_semantic_publication`

Exact reviewed source:
`8c856e69827a401bcedb0fe0c02ca3bda8e48c15`

## Lay outcome

Keep the new compact clockwork interface. Its first use was 59.3% smaller than
the like-for-like old form, published once with no rollback, and preserved the
canonical safety mechanism.

The review also found where the next work belongs. First, an idempotent
readback must stop overwriting the preceding publication's convenience
evidence. Second, most remaining clerical bulk now lies in repeated
continuation states and receipts rather than in the closeout intent.

## Corrected measurements

- the incident-bearing legacy intent has 176 leaves;
- its observation has 25 leaves, but its generated revision path has one more;
- the normalized no-incident baseline is therefore 150, not the frozen 151;
- the representative semantic fixture has 64 leaves;
- the actual intent has 61 leaves, 5,502 bytes and 96 lines;
- the normalized reduction is 89 leaves / 59.3%;
- one publication, one lease advance and zero rollback passed;
- the 115-test suite ran three times and two test-only correction rounds were
  required; and
- seven runtime states plus seven receipts added 2,334 lines and 130,653 bytes.

## Findings and disposition

AER-1129 corrects the residual incident-path baseline error. AER-1130 records
the repository defect in which idempotent `--publish` replaced the operation's
publication evidence pair with its readback evidence. The latter did not alter
canonical state, but it lost the durable command digests from the convenience
file. No digest is reconstructed.

The builder is retained. Repeated `--publish` readback is contained until the
selected repair preserves publication evidence. The review makes no source
change.

## Ranked next work

Proceed under standing authority with
`ariadne-provider-free-governance-clockwork-idempotent-publication-evidence-preservation-repair`.
It must preserve the original publication evidence and record any idempotent
reading separately or without overwrite inside the existing CLI, with no new
operator document or control layer.

After that repair, the next ergonomic target is one typed serial-continuation
projection inside the existing orchestrator preflight, measured against the
14-file / 2,334-line burden. Test-cadence reduction remains closed until an
exact invariant-preserving replacement is frozen.

No Harness/provider, authority-allocation, product, data, runtime, deployment,
release, Pages, protected-evidence or protected-ref authority opens.
