# DeepSeek native worker attempt 001 diagnosis

Date: 2026-08-20

Timestamp: 2026-08-20T13:59:59.8510361+10:00 (Australia/Brisbane)

Status: `failed_closed_pre_provider_consumed_no_retry`

## Result

The one admitted DeepSeek native-Harness worker attempt failed closed before
any DeepSeek request or model step. The broker became ready, the stock headless
HMR seam reached readiness and the changed runner activated, but agent creation
ended at `EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED` before the effective
tool view existed.

The exact terminal evidence records:

- provider calls started/completed/failed: `0/0/0`;
- model request count and model usage steps: `0` and `[]`;
- tool calls and model-executed tests: `0`;
- automatic retries: `0`, resume permitted: `false`;
- harness exit code: `1`, wall clock: `6874 ms`;
- broker and harness absent at close;
- raw stdout, stderr, prompts, responses, sessions and logs not retained; and
- the temporary Harness home absent.

The worker's two owned files retain their exact predispatch placeholder hashes:
`e8771c0a65be449a330e4ce9b401a32ea24ac2e014f7c6be74766ae222ba74e6`
and `4ad7e4ccb57dc02913a73dcde67a53935455a5b5816008e903c38e6c637e99e7`.
The terminal's `changed_paths` field therefore names the two pre-existing
untracked owned paths; it is not evidence of model edits.

## Classification

This is a Harness composition and diagnostic-coordinate failure, not a
DeepSeek reasoning or coding failure. The accepted guard deliberately maps all
preset-mount exceptions to one sanitized coordinate, so the retained terminal
cannot establish whether discovery, preset validity, standing composition or
another mount substage supplied the underlying exception. A later provider-free
Harness repair may reproduce that path, but this worker attempt is consumed and
must not be retried or resumed.

## Prospective controls

Before a future occupied worker latch is consumed:

1. execute the identical full-profile `agents.create(...setup...)` preset-mount
   path in a provider-disabled boot that exits before model selection or turn;
2. split safe preset discovery, resolution, validity, standing-mount and scope
   binding coordinates so a mount failure remains sanitized but diagnosable;
3. derive `changed_paths` from before/after hashes, excluding unchanged
   pre-created placeholders; and
4. derive all dependency packet paths and full Git object IDs from machine
   resolvers rather than hand-entered workflow vocabulary.

These controls are incident intake for the Harness workflow. They do not widen
attempt 005, create a retry, or delay Sol's plan-authorised direct completion of
the exact adapter-and-test package.
