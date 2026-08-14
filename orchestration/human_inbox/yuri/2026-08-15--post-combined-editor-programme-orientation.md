# Post-combined-editor programme orientation

Date: 2026-08-15

Timestamp: 2026-08-15T06:42:00+10:00 (Australia/Brisbane)

Status: accepted; your programme choice is required

## Lay summary

Reception One's first action console is now a genuine milestone. Status has one
complete command path, while doctor, time and duration share one complete
update path. The programme has no remaining high-value automatic successor
inside its current authority.

My recommendation is appointment cancellation. Before exposing it, the safest
small tranche is a read-only review of the existing cancellation path. The
ordinary Diary has both a dedicated delete family and a compatibility fallback
to `Cancelled` status; Reception One has no cancellation bridge yet. We should
decide the single authoritative meaning before adding a destructive control.

And yes: a future patient's delegation to email, SMS, Siri or another assistant
must be revocable. Revocation stops future acts under that grant, including a
pending but uncommitted confirmation. It does not retrospectively remove an
appointment already committed to Diary truth; that requires its own authorised
cancellation or rescheduling transaction.

## Technical summary

The accepted repository-static orientation at
`2ca3a111d2ee9277571ea3c905f22ce78c8e9745` found:

- four current Reception One controls and no cancellation bridge;
- a presentation-only cancellation candidate;
- distinct delete proposal/confirm OpenAPI operations;
- a native Diary 404 fallback from delete proposal to `Cancelled` status which
  omits `cancellation_reason`; and
- no evidence that the fallback is unsafe, only that it needs exact readiness
  classification before reuse.

Eight focused assertions, 115 independent-review tests and the 196-test fast
profile passed. Gemini independently passed all ten review challenges at an
unchanged clean candidate. No product or runtime source changed.

## Decision requested

Should Reception One pursue appointment cancellation next, beginning with the
provider-free read-only cancellation command-path readiness review?

The principal alternatives remain patient-channel identity/delegation,
check-in/waiting-area composition, representative Stage 3B sessions, another
explicitly chosen event family, or later operational durability work.
