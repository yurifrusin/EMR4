# Ordinary Diary cancellation compatibility review — paired summary

Date: 2026-08-17

Timestamp: 2026-08-17T18:41:05.9642049+10:00 (Australia/Brisbane)

Status: accepted; continuing

## Lay summary

We found the remaining mismatch between the older ordinary Diary cancellation
screen and the newer truth-kernel contract already used by Reception One. The
database can correctly cancel an appointment, but the older screen expects the
wrong shape of reply and can display an error after success while leaving the
old appointment visible. It can also quietly substitute a different kind of
cancellation when its preferred route is unavailable.

Nothing in the product was changed during this review. We have frozen a small,
client-only correction: use only the dedicated cancellation route, accept the
proper receipt, never fall back to a different command, and always reload
current Diary truth before saying what happened or allowing another attempt.

This moves Raisa toward one deterministic meaning across multiple visual
adapters. Reception One and the conventional Diary may look different, but
they will speak the same command language and measure their display against the
same backend truth.

## Technical summary

Accepted source `0f3b0c73fef0a2a52186a8f86bae8cf351d1a8df`
proves five repository-static findings: minimal-envelope incompatibility,
404-to-status semantic downgrade, widened cancellation endpoint/proposal
admission, success-only reconciliation and stale smoke-fixture semantics. The
later change is limited to `docs/diary/diary.js`, the `diary.html` cache
reference if needed, and focused tests. It must reuse strict proposal/receipt
validation, admit only the canonical delete-confirm endpoint and fail into a
refresh-required disabled state if fresh reconciliation cannot be completed.

The accepted evidence includes 88 focused checks, the 200-test canonical fast
profile, 296 error-register tests, Ruff, 217 compilation checks, JavaScript
syntax, whitespace and one clean eight-command Gemini 3.7 Flash/high veto.
AER-0387 contains one stale historical route-contract suite; its attempted
reason-only change was reverted and its failures are excluded.

Three closeout harness controls also required correction: the generic Compass test still
named an old position, and the first register update omitted its exact metadata
and pattern refresh; the first terminal latch draft also retained its resume and
next-stage fields. AER-0388 through AER-0390 preserve those failures; revision
343 corrects them without changing product source.

## Deliberately closed

No product route or database was called or changed. Providers, ADC,
credentials/IAM, patient/product/clinical data, database/source/watcher access,
backend/API/schema/migration changes, raw compatibility writes, deployment,
production, release, Pages and protected refs remain closed. Branding and all
unrelated untracked files remain preserved.

## Next tranche

Proceed immediately with the provider-free ordinary Diary client-only
canonical cancellation convergence described above. Yuri's attention is not
required.
