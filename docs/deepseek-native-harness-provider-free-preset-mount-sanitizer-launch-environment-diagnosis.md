# DeepSeek native Harness preset-mount sanitizer launch-environment diagnosis

Date: 2026-08-22

Timestamp: 2026-08-22T05:29:55.2718766+10:00 (Australia/Brisbane)

Three local Node fixture processes were consumed without a sanitizer result.
Attempts 001 and 002 retained only `node_fixture_exit_nonzero`; their numeric
exit and stream lengths were not observed. Attempt 003 added the content-free
envelope and observed exit 134, zero stdout and 715 stderr bytes. No stream
content was retained.

All three launchers passed `env={}`. The accepted repository Node fixture
rehearsal at
`scripts/deepseek_native_harness_provider_free_structured_diagnostic_wrapper_node_fixture_rehearsal.py`
does not override `env`, and therefore inherits the host launch environment.
The empty child environment is the narrowest shared, source-visible launch
difference. It is a recovery hypothesis, not a proven cause of exit 134.

The successor therefore preserves the exact sanitizer and wrapper bytes and
changes only the child environment to the validated five-key Windows minimum:
`SystemRoot`, `WINDIR`, `ComSpec`, `TEMP` and `TMP`. Values will be passed to the
child but never persisted. `PATH`, `NODE_OPTIONS`, credentials and all other
ambient variables remain excluded.
