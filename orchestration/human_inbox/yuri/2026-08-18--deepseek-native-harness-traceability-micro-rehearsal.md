# DeepSeek native Harness micro-rehearsal — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T14:37:03.9470128+10:00 (Australia/Brisbane)

Status: accepted bounded no-call result; sprint engine continuing

Yuri attention required: no.

## Lay summary

You do not need to download or install the new Harness. I used its official
pinned pre-release package in a temporary, isolated folder and removed that
folder and its cache afterwards.

The tiny run did not reach DeepSeek. The Harness stopped in about two seconds
because one of my safety settings was internally inconsistent: I set retries
to zero and also supplied an empty list of retryable errors, which its runtime
does not allow. Crucially, it reported that exact cause and returned a clear
failure code. It made no provider request, incurred no provider cost, created
no session trace and was not rerun.

So there is a modest positive signal on traceability: this failure was much
easier to locate than DeepSeek's recent silent Claude Code failures. There is
still no evidence about DeepSeek model reliability or coding performance,
because the model was never called. I have not changed the default worker
transport. A future comparison would first include a credential-free boot
check so configuration errors cannot consume the one provider-capable attempt.

## Technical summary

`@deepseek-ai/dsh@0.1.0-rc.7` matched npm version, shasum and SHA-512 integrity.
The headless composition selected `deepseek-official/deepseek-v4-flash` at high
reasoning, capped output at 64 tokens, set `maxRetries: 0`, disabled telemetry
and the title LLM, and disabled every model-facing tool row. The provider-
capable process returned exit 1 in 2002 ms, stdout length 0, stderr length 5302
and sanitized boot error `retryPolicy.retryableCodes must not be empty`.

A key-absent diagnostic reproduced the same plugin-tree failure, proving the
failure preceded credential resolution and provider I/O. No `$DSH_HOME/sessions`
directory existed. Sanitized evidence contains hashes and file metadata only;
no raw reasoning, request/response, key or environment dump was retained.

Register revision 391 records seven corrected/contained orchestration issues,
445 total and none open. No product source, patient/clinical data, feature
flag, route admission, client, waiting-area action, deployment, Pages or
protected ref changed. The next tranche is a provider-free read-only
orientation for later ordinary check-in admission and one atomic two-client
cutover; it makes no product change.
