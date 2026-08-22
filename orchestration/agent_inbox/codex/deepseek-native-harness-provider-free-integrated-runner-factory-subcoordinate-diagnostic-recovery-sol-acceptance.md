# Sol acceptance: integrated-runner factory-subcoordinate diagnostic recovery

Date: 2026-08-22

Timestamp: 2026-08-22T19:05:50.6495370+10:00 (Australia/Brisbane)

Decision: `accepted_bounded_negative`

Reasoning level: high

I accept the immutable one-process result only as a bounded provider-free
negative and deterministic fixture diagnosis.

Accepted facts are:

- the exact occupied runner and guard have a four-argument/three-parameter
  interface mismatch that source analysis maps to
  `EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID`;
- the single Node fixture stopped before AgentRegistry because it projected
  unscoped package paths;
- both emitted import targets are absent and both exact scoped targets are
  present;
- exit, stream byte counts/digests, zero stdout, zero retry and complete cleanup
  are preserved without raw error retention; and
- Harness, broker, worker, model and provider counts remain zero.

Not accepted are a dynamically observed guard coordinate, installed factory
success, DeepSeek behavior, useful worker output or general Harness
reliability. The current fixture cannot be retried. The only eligible successor
is the separately identified exact import-path recovery with mandatory
prelaunch target-existence checks.

Product, data, ordinary-practice, runtime, deployment, release, Pages and
protected-ref boundaries remain closed.
