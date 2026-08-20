# Check-in lifecycle conformance repair report

- Result: `failed_closed`
- Server stdin remains open after credential delivery: `true`
- Final cleanup is the sole stdin closer: `true`
- Closed server diagnostic keys: `9`
- Native Harness terminal: `PRESET_VALIDATION_PASSED`
- Effective tools: ``
- Native processes / retries: `1 / 0`
- Model / provider / network / Docker / database requests: `0 / 0 / 0 / 0 / 0`
- Process and disposable-root absence: `true / true`

The sole native process failed closed before `agents.create` and preset mount; `PRESET_VALIDATION_PASSED` is the first missing lifecycle marker. The terminal proves zero agent, turn, model and provider activity, not a successful native mount. It is not attempt 006, an occupied DeepSeek worker, a
model-quality result or product/runtime admission.
