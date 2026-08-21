# DeepSeek native Harness source-repaired boot — lay and technical closeout

Date: 2026-08-21
Timestamp: 2026-08-21T16:33:56.0458572+10:00 (Australia/Brisbane)

## Lay summary

The source repair worked: the native DeepSeek harness loaded our sentinel and
the sentinel announced that it was active. The harness itself then exited
before its normal headless environment announced readiness. That is a useful,
traceable result because it separates the repaired custom code from the next
failure coordinate.

We used exactly one local harness process and did not retry it. DeepSeek was not
called, no worker task ran, no network request was made, and all disposable
files and raw output were destroyed. The harness is therefore not yet ready for
EMR4 development work, but the problem is now narrower and reproducible: after
sentinel activation, before stock headless readiness.

The next step is a process-free source diagnosis of that narrow exit window,
not another launch. Yuri's attention is not required.

## Technical summary

- Exact executed candidate: `84a9327d98812a9891af0ef5724045f7599eb3a5`.
- Attempt: `source-repaired-sentinel-native-boot-attempt-001`, consumed once.
- Terminal: `failed_closed` / `native_process_exited_before_readiness`.
- Observed HMR sequence: one `sentinel_activated`; no
  `stock_headless_hmr_ready`.
- Process: one, exit code 1, 5,617 ms, zero retries.
- Retention: stdout 0 bytes, stderr 79 bytes; only digests/counts retained.
- Activity: zero broker, worker, prompt, tool, model, provider, network, Docker
  and database actions.
- Cleanup: process absent, distinct disposable root absent, raw environment and
  copied package tree absent.
- Verification: 71/71 applicable tests plus Ruff and `py_compile` pass.
- Governance: 562/562 broad clockwork/Continuity/Compass/register/latch tests
  pass after publication; Continuity 368 / Compass 350 / lease 114 reports
  canonical drift zero.
- Two predecessor digest selectors remain preserved historical evidence.
- Six contained workflow corrections are recorded in register revision 591;
  none are open.
- Protected refs remain fixed; `docs/branding/` and unrelated untracked paths
  remain preserved.
- The usual non-PHI Pushover closeout notification passed.
