# Ariadne active-operation latch — lay and technical closeout

Date: 2026-08-13

Timestamp: 2026-08-13T09:31:31+10:00 (Australia/Brisbane)

Result: **passed**

## Lay summary

The workflow now keeps a durable note of what it was actually doing, where it
had reached and what must happen next. After a context compaction, an old side
question can no longer legitimately masquerade as the main job merely because
it is the last prompt retained in chronological order.

While work is marked in progress, a side question is answered and the work
resumes. A status question behaves the same way. Added instructions are folded
in and work resumes. A final handback is disallowed unless the work genuinely
finishes, becomes blocked, or you explicitly pause or redirect it.

I have also adopted your requested document convention: new tranche documents
will show a Brisbane timestamp as well as the date. Formal closeouts are kept
under `docs/`, with their technical acceptance, machine evidence and this paired
lay/technical mailbox copy in their respective orchestration directories.

## Technical summary

The new `ariadne.active_operation_latch.v1` exact schema and pure validator are
required by all ten orchestrator continuation events. Receipts now project the
operation ID, tranche, status, source HEAD, completed/next stages, resume flag,
attention state and terminal-handback decision. `in_progress` plus terminal
intent deterministically yields `revision_required`.

Thirty-nine hostile mutations fail closed. Eighty-one focused tests pass. The
canonical fast profile passes Ruff, compilation of 208 maintained sources, 193
tests, Diary JavaScript syntax and whitespace. One mechanical compactness issue
was caught and repaired: the first policy wording made `AGENTS.md` 502 lines;
the same rules were compressed to 495 lines.

## Deliberately closed

No patient/product data, route or database execution, provider, credential,
network, command, deployment, production, release, Pages, protected evidence or
protected-ref movement was opened. The control does not technically intercept
the host UI's final-channel function; it makes misuse inconsistent with the
required durable state and receipt.

## Place in the project and next work

This repairs the continuity machinery around the project rather than adding a
clinical or Diary feature. It protects the ability to keep moving safely
through the programme without turning every interruption into a handback.

The active latch now resumes the provider-free read-only status-confirm
route-mounting readiness re-review. That review will determine which of the ten
route-convergence dimensions are now satisfied by the accepted off-route
composition and which concrete application adapters still have to exist before
mounting can safely be considered.

Yuri attention required: **no**.
