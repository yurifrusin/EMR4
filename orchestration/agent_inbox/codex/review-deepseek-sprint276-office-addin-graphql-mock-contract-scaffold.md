# DeepSeek Sprint 276 Office Add-in GraphQL Mock Contract Scaffold Review

Verdict: PASS with concerns integrated.

DeepSeek reviewed the planned tests-only/mock-only scaffold for future Office
add-in consumption of `Query.practice.practitioners`.

Integrated concerns:

- The helper operates at raw mocked response level and does not route through
  `apiFetch`.
- HTTP `401` requests logout, while GraphQL `FORBIDDEN` and `BAD_USER_INPUT`
  response-body errors do not.
- `practice = null` is the canonical no-leak mismatch case and emits no
  practice fields.
- `defaultLocation = null` is asserted as data shape only, not a UI rendering
  string.
- Projection drift behavior is explicitly `discard`; extra raw fields are absent
  from helper output.
- Gate disabled behavior is parameterized and does not depend on the current
  date.
- Future REST fallback is represented as an event, not orchestration.
- The helper asserts error classifications rather than user-copy strings.
- The helper imports no `app` modules.
- A `DRIFT.md` file records why the scaffold is not the future JavaScript
  taskpane runtime wrapper.
