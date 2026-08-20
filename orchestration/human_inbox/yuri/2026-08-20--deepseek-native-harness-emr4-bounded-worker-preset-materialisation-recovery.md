# DeepSeek native Harness bounded-worker preset materialisation — Yuri summary

Date: 2026-08-20

Timestamp: 2026-08-20T10:52:45.8367551+10:00 (Australia/Brisbane)

## Lay summary

The missing bounded-worker preset now exists as an exact, installation-ready
file. More importantly, we have proved what it does and what it does not do.
The two official filesystem plugins initially expose more capabilities than we
want, but the already accepted guard removes the surplus capabilities and
leaves exactly read, edit and file-pattern matching. The broker must still
enforce the same three-capability boundary independently.

The new, restored Gemini sign-in worked on its first review attempt. Gemini ran
all ten prescribed checks, including 101 tests, and passed the unchanged clean
candidate. There was no semantic rebuild and no repeated provider or native
harness attempt.

The small costs have not been hidden: several pre-commit inspection and test
authoring corrections, one lost test-summary rerun, a receipt-shape correction
and my corrected byte-count statement are all in the efficacy reading. They do
not justify adding new ceremony. This tranche is a good provisional example of
the clockwork reducing ambiguity while keeping honest cost measurable.

There was one less flattering closeout event. I repeated a previously recorded
mistake by failing to retain the session handle from a long-running
postpublication test command. The process completed, but its final test exit
was not admissible. I reran the unchanged suite once with the handle retained;
it passed to 100%. The clockwork publication was then preserved and rolled back
byte-for-byte so the recurrence could enter the error register before final
publication. This does not affect the candidate, but it is exactly the kind of
workflow cost the efficacy mechanism must make visible.

The next step is a single, tightly bounded provider-free native boot that puts
the now-proven pieces together. It will test harness discovery, service
activation and the final three-tool view, but still will not run a DeepSeek
worker or contact a model provider.

## Technical summary

- Accepted candidate:
  `962e91d9af90fbe977177d251f9f3e3134aaad19`.
- Materialised payload: 158 bytes, SHA-256
  `3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1`.
- Future install path:
  `.agent-presets/emr4-bounded-worker/agent.cordis.yml`.
- Exact local sources: six rc.7 cached packages with registry and member
  digests verified in memory.
- Raw surface: `edit`, `glob`, `grep`, `read`, `write`, plus conditional
  `read_image`.
- Guarded surface: exactly sorted `edit`, `glob`, `read`; broker allowlist
  independently remains required.
- Deterministic verification: 24 focused tests and 21 hostile variants.
- Independent review: first-attempt Gemini 3.7 Flash/high `pass`, ten exact
  zero-exit commands, 101 tests, unchanged HEAD and clean worktree.
- Closeout recovery: one repeated yielded-session-handle lapse; unchanged
  observed compatibility rerun passed to 100%; lease 53 preserved and rolled
  back byte-exactly at lease 54 for incident intake.
- Execution boundary: zero Node, native Harness, worker, agent, broker,
  DeepSeek model, provider, external network, Docker and database execution.
- Protected boundary: no product, API, client, feature flag, practice, data,
  production, deployment, release, Pages or protected-ref change.

Next: one separately frozen, network-denied provider-free native composition
boot combining the accepted service graph, exact preset, observability and
effective-tool guard. No agent/session/turn/broker/model/provider call is
authorised by that next step.
