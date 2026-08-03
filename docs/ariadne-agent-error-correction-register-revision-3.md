# Ariadne agent-error register revision 3

Date: 2026-08-03

Status: corrected before Sol acceptance

Revision 3 adds two preserved fifth-pair incidents.

`AER-0009` records the Diary worker's first invalid rehydration envelope. The
deterministic preflight rejected four exact contract errors before any task or
browser action. A distinct settings-compliant receipt passed before work began.

`AER-0010` records a shared PostgreSQL pytest collision. Parallel product work
was valid, but instruction-only test serialization was not strong enough: both
lanes entered repository pytest and one schema lifecycle removed `practices`
under the other. Both results were rejected. Exclusive reruns then passed 9
Diary tests and 31 Davida plus 36 API Spine tests.

The first repair added `scripts/ariadne_serial_pytest.py`, but independent
review correctly rejected a wrapper-only gate because direct pytest could
bypass it. The durable control now lives in `tests/conftest.py`: every normal
repository pytest entry acquires one OS-enforced cross-process lock stored
outside the repository before shared-schema setup. The shell-free launcher
remains required and supplies the bounded wait; direct pytest is serialized by
the same conftest lifecycle. Contention waits or fails closed rather than
corrupting the shared schema.

Neither incident establishes model or provider causation. The original failure
receipts remain immutable and linked to their exact corrections.

## Operating correction loop

The register is the intake and evidence layer for a deterministic behaviour-
correction loop:

1. fail closed and preserve the rejected attempt;
2. classify origin, category, role, resource and normalized signature without
   inventing causation;
3. link the exact correction and its prevention control;
4. aggregate only exact composite recurrences in the pattern report;
5. promote the narrowest useful prevention control into a packet, wrapper,
   policy or acceptance gate;
6. add a regression that proves the control fails closed; and
7. admit a corrected attempt only after that regression and the original
   acceptance gate both pass.

The duplicate-terminal-decision pattern already drives the verifier wrapper's
single-decision admission gate. AER-0010 now demonstrates the same loop for a
harness failure: an instruction became a conftest-enforced OS lock with direct-
entry contention and recovery tests. Future corrections should prefer
enforceable controls over prompt wording when the invariant can be made
deterministic.

This is controlled workflow learning, not autonomous model fine-tuning. The
register may inform packets and gates, but it cannot alter authority, select a
provider, make causal quality claims, waive a failed acceptance result or tune
against protected evidence.
