# Yuri closeout — matched clockwork ergonomics review

Date: 2026-08-23

Timestamp: 2026-08-23T18:08:50.3183802+10:00 (Australia/Brisbane)

## Lay summary

The new compact interface is worth keeping. After normalizing the old form
properly, its first real closeout used 61 scalar entries instead of 150—a 59.3%
reduction—with one successful publication and no rollback.

The review did catch two things rather than simply endorsing the work. The old
151-leaf comparison retained one incident-generated path, so the honest
baseline is 150. More importantly, the idempotent readback overwrote the
non-canonical publication evidence file with its readback result. The clock's
canonical transaction and pointer remained safe, but the publication's command
digests were no longer retained in that convenience file.

## Technical summary

The exact window spans four commits and 47 minutes 44 seconds from plan commit
to publication commit. One dry check ran zero commands; one publish ran and
passed three; one readback reran none. The 115-test suite ran three times. Two
test-only correction rounds occurred, with no product/provider rerun or
protected-ref movement.

The largest remaining ergonomic burden is outside the semantic intent. The
intent is 96 lines / 5,502 bytes, while seven runtime states and seven receipts
added 2,334 lines / 130,653 bytes—more than 24 times as much text.

The review closeout itself then supplied a further useful example. Its first
publication attempt failed safely because a test had copied a current leaf
count and graph position into permanent assertions. Those values legitimately
changed when the clock advanced. The test now derives both from its isolated
worktree; the two focused cases and all 115 governance tests pass, with no
canonical mutation from the failed attempt.

## Recommendation and boundaries

First repair idempotent evidence preservation inside the existing CLI. Then
derive the repeated serial continuation-state structure inside the existing
preflight and measure whether it actually removes most of those 2,334 lines.
Do not reduce the three test runs until an exact safety replacement is named.

No DeepSeek/Gemini/native worker, provider, product, data, deployment, release,
Pages or protected ref was used. Yuri's attention is not required.
