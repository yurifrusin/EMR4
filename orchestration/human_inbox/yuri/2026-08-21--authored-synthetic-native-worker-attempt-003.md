# Yuri update — native Harness attempt 003

Date: 2026-08-21

Timestamp: 2026-08-21T07:35:11.0925861+10:00 (Australia/Brisbane)

Attention required: `no`

## Lay summary

We ran the newly authorised native-Harness attempt once, with no retry. The
Harness failed before it reached DeepSeek, so there was no provider chargeable
request and no evidence yet about DeepSeek's coding performance.

The new clockwork gear did improve the result: instead of an unexplained exit,
we now have a safe, validated reading that the process started, failed before
its first live-reload milestone, matched none of the known safe error groups,
and was therefore honestly left “unclassified.” Everything was then cleaned
up exactly.

So the conclusion is mixed but clear: control and traceability improved;
operational readiness did not. The Harness is still not ready to entrust with
EMR4 work under this profile.

## Technical summary

- one rc.7 native process; exit `1`; 11,241 ms;
- zero HMR events, runner requests, provider requests, tools and file changes;
- safe stage `native_process_started_before_first_hmr_event`;
- safe cause `unclassified_nonzero_exit`; zero matched signature groups;
- zero retry/fallback/auxiliary calls; raw streams not retained;
- Harness, broker and disposable root absent;
- eight deterministic post-terminal commands pass;
- four clockwork/schema mistakes were caught before action and corrected;
- register revision 578: 732 contained incidents, none open. This includes two
  read-only closeout-shape rejections, both corrected before publication.

Deliberately closed: another occupied attempt, retry, product or patient data,
database/runtime work, ordinary-practice changes, production, deployment,
release, Pages and protected refs.

Next under standing authority: a provider-disabled, source-static recovery to
find a more useful non-secret structured diagnostic seam for these currently
unclassified pre-HMR exceptions. It launches no Harness, broker, worker or
provider request.
