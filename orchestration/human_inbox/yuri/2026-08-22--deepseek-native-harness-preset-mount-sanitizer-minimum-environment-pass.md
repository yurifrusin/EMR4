# DeepSeek Harness sanitizer minimum-environment result

Date: 2026-08-22

Timestamp: 2026-08-22T06:03:42.6115665+10:00 (Australia/Brisbane)

## Lay summary

The single permitted test passed. Giving the local sanitizer process only the
five Windows basics it actually needs was sufficient for the unchanged code to
return all fifteen expected safe answers. The important gain is not merely a
green test: Raisa now controls the child environment, counts the one process,
records a content-free reading before interpreting it, and prevents a hidden
retry.

This still was not a DeepSeek work session. It tested the safety instrument that
will sit around that session. The next step connects that instrument to a
runner on paper and in deterministic tests before allowing another native
Harness process.

## Technical summary

- Execution candidate: `ceac8b2600530bf858394bb84e66a42ec3d016f4`.
- One Node process; exit 0; stderr 0; exact fifteen-result vector.
- Child keys exactly: `SystemRoot`, `WINDIR`, `ComSpec`, `TEMP`, `TMP`.
- `PATH`, `NODE_OPTIONS`, provider configuration, credentials and all unlisted
  keys were absent; values and stream content were not retained.
- Sanitizer/wrapper hashes matched the frozen plan.
- Native Harness, worker, model/provider, network and product activity stayed
  at zero.
- Deterministic readback plus 33 relevant tests and static checks passed.
- Three contained low-severity caller-shape errors are recorded as AER-0891 to
  AER-0893; none consumed another Node process or altered evidence.

Next: deterministic provider-free preset-mount sanitizer runner bridge; no
native process yet.
