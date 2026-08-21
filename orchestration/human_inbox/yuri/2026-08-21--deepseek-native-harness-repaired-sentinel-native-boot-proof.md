# DeepSeek native Harness repaired-sentinel boot — lay and technical summary

Date: 2026-08-21

## Lay summary

The new Harness still did not reach its ready state. We gave the repaired setup
one tightly controlled local start. It exited after about 7.3 seconds before
the sentinel announced that it had loaded. We did not retry it.

The controls worked well: no DeepSeek call was made, no worker or broker was
created, no network request occurred, no raw error output was retained, and
the process plus its temporary files were completely removed. This is useful
evidence because it tells us the relative-path repair alone was not the whole
problem. The next step is a static source diagnosis, not another speculative
run.

The new record-keeping clockwork also caught one vocabulary mismatch in its
own successor record: the meaning stayed closed, but one standard boundary
label was absent. It rolled that publication back exactly and the corrected
record now carries both the standard label and the more specific denial. This
did not restart the Harness.

## Technical summary

- reviewed candidate: `b99d961e225f355a17e74ec15d6e82fb61d83532`;
- attempt: `repaired-sentinel-native-boot-attempt-001`;
- native process count / retry count: 1 / 0;
- exit / duration: 1 / 7,310 ms;
- HMR event sequence: empty;
- readiness observed: false;
- changed runner / broker / worker sessions: 0 / 0 / 0;
- model / provider / network requests: 0 / 0 / 0;
- raw stream retention: false;
- process and disposable root absent: true / true; and
- protected refs remain fixed at the accepted protected commit.

Clockwork verification: the first lease-109 generation passed 97/98 extended
checks, was rolled back byte-exactly at lease 110, and is being republished
from a corrected typed boundary set. Provider and native-process counts for
the correction are zero.

The terminal's structured result is `failed_closed` at
`native_process_exited_before_readiness`. Its generic claim sentence is too
affirmative for a failed result; the closeout records that defect without
altering immutable execution evidence.

Next:
`deepseek-native-harness-provider-free-repaired-sentinel-preactivation-source-coordinate-diagnosis`,
provider-free and static only. No native retry is authorised.
