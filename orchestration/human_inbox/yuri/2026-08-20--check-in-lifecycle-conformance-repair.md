# Check-in lifecycle conformance repair — paired closeout

Date: 2026-08-20

Timestamp: 2026-08-20T16:04:16.4951745+10:00 (Australia/Brisbane)

## Lay summary

The repair did what we wanted on the server side. The database server's input
channel will now stay open after its credential is delivered, cleanup has one
clear owner, and a future stopped server will leave a small safe reading of its
exit state instead of an opaque “not running” result.

The one no-DeepSeek Harness probe still stopped early, but it stopped at a more
useful point: preset discovery passed and preset validation did not. It made no
provider request, used no tokens, retried nothing and cleaned itself up. This is
evidence about the Harness seam, not about DeepSeek's intelligence.

Gemini found one real portability bug in our controller—the worker directory
was being appended twice inside an isolated review checkout. That was corrected,
covered by a regression, and a fresh review passed. Your attention is not
required. The next step is to split preset validation into smaller deterministic
readings before considering another provider-disabled process.

## Technical summary

- corrected candidate: `7d39641c3170fc0fec76fadce5cd45309bdffdb2`;
- stdin delivery: one write, one flush, open through verification;
- cleanup: sole closer, close at most once, bounded terminate/kill fallback;
- post-readiness projection: exact closed nine-key vocabulary;
- native process/retries: `1/0`;
- first missing marker: `PRESET_VALIDATION_PASSED`;
- agents/turns/provider/model/network/Docker/database requests: all `0`;
- cleanup: process and disposable root absent;
- deterministic verification: 52 provider-free tests plus Ruff, compile and
  schema/static checks;
- independent review: initial `revision_required`, one bounded correction,
  corrected Gemini 3.7 Flash/high `pass`, all nine commands zero, clean HEAD;
- workflow register: revision 572, eight new contained/corrected incidents,
  none open; and
- protected refs: all remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Deliberately closed: retry of the consumed process, occupied DeepSeek work,
attempt 006, ordinary-practice check-in, generic-status `Arrived`, route/flag/
allowlist/grammar/client/waiting-area changes, product or protected data,
production, deployment, release, Pages and protected-ref movement.

Next tranche:
`raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery`.

