# DeepSeek native Harness agent-factory diagnostic — paired closeout

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The new control layer worked. Instead of the DeepSeek Harness disappearing
after startup, its one process reported exactly how far it got: it successfully
entered the real agent factory, created the private in-memory Agent/Session
identity, and then stopped while trying to compose the three allowlisted tools.

Nothing became public, no DeepSeek model was contacted, no files were targeted,
and the temporary installation cleaned up completely. We have therefore reduced
an opaque failure to one small, named interval. This is meaningful progress
toward making DeepSeek workers controllable, but it is not yet a usable worker.

One report timestamp was mistakenly guessed into the future. The evidence was
not affected; the timestamp alone is formally rejected and future reports must
take their time from the machine clock or typed evidence.

## Technical summary

- Exact source: `33b4e061b1385abc91ecd170e4abdb563396c3ef`.
- Terminal: `closed_subcoordinate_failure`.
- Last stage: `private_identity_admitted`.
- Safe outer class: `unclassified_error`.
- Factory/private Agent/private Session: `1/1/1`.
- Published registries/lifecycle: all zero.
- Turn/request/broker/model/provider/network/database/Docker/target: all zero.
- Exit code 2 after a valid typed sidecar; no retry/resume.
- Process/root absent; bundle and 219 MB package seed unchanged.
- 22 focused/evidence tests pass; the exact 219-test inherited collection had
  already completed without failure before execution.

## Deliberately closed

No occupied worker or model request, target edit, product/data/API/database/
route/configuration change, ordinary-practice enablement, production runtime,
deployment, release, Pages or protected-ref action opened.

## Place in Raisa and next tranche

This is the first native attempt in this sequence to report its own bounded
factory stage rather than failing opaquely. The next frozen tranche connects
the effective-tool guard's already accepted safe sanitizer to the runner. One
distinct process may then identify the exact preset-composition coordinate—or,
if composition now succeeds, proceed to the prepublication veto—without a
model call or self-correction. Work continues under standing authority.
