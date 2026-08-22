# Check-in relay-free recovery attempt 006 — lay and technical summary

Date: 2026-08-23

## Lay summary

We ran the sixth rehearsal exactly once, as authorised, and did not retry it.
It failed safely before PostgreSQL became ready and before any transaction or
product step. Everything it created was removed, no provider was called, no
patient or product data was used, and no ordinary check-in path was enabled.

This was not the same opaque failure again. We now know that the captured
server never left Docker's `created` state, the attachment process itself
failed, and its input channel was still open. That sharply moves the next
question from PostgreSQL transaction behavior to the exact Docker start/attach
boundary.

The clockwork did its most important job: it allowed one attempt, prohibited a
retry, preserved the terminal and verified cleanup. It still exposed several
small form-filling corrections around event labels, Git-object prose and text
length. Those cost time but did not consume another database attempt. The next
workflow improvement remains to generate those fields from typed readings.

## Technical summary

- Result: `failed_closed` at
  `environment/server_not_running_after_readiness`.
- Occupied execution count: `1`; automatic retries: `0`.
- Safe projection: `status=created`, `running=false`, `exit_code=0`,
  `oom_killed=false`, `restart_count=0`, attachment process
  `exited_nonzero`, attachment stdin `open_after_delivery`.
- Transaction phases reached: none. Attestation: absent.
- Success released: false; ordinary admission: `0`; product records: `0`.
- Cleanup: verified; matching containers/networks: `0`.
- Failure SHA-256:
  `3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd`.
- Envelope SHA-256:
  `52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c`.
- Postterminal validation: 4/4 passed; Ruff and compilation passed.
- DeepSeek/Gemini/native-subagent lanes: declined for the serial lifecycle;
  no provider request occurred.

Next is the narrow provider-free read-only diagnosis
`raisa-provider-free-read-only-check-in-server-start-attach-created-state-failure-coordinate-diagnosis`.
It authorises no new Docker object and no attempt 007.
