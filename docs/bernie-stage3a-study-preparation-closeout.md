# Bernie Stage 3A Study Preparation Closeout

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision: `stage3a_study_ready_awaiting_yuri_run`

## Outcome

Yuri's approved six-decision package is now a durable Stage 3A contract, and a
functional local study surface is ready for the Yuri-only formative run.

The surface proves the interaction shape without pretending to be the deferred
final visual design. It supports typed deterministic requests, labelled answer /
clarification / proposal / block states, reversible patient-, practitioner-,
time-, availability-, and event-centred projections, an ordinary-grid
comparison, deterministic attention filtering, and in-memory structured
observation capture.

This is `stage3a_study_ready`, not `stage3a_pass`. Yuri has not yet supplied the
participant observations, and the separate authoritative confirmation scenario
has not been rerun in this preparation tranche.

## Exact evidence boundary

The browser surface uses `authored_synthetic_fixture_browser` evidence. It:

- contains only authored synthetic people, appointments, practices, events and
  read models;
- makes no FastAPI, GraphQL, REST command, provider, WebSocket, EventSource,
  microphone, speech, telemetry, cookie, or browser-storage call;
- cannot create, move, cancel, confirm or otherwise mutate an appointment;
- labels deterministic interpretation as not language-model evidence;
- labels fixture events as fixtures rather than live or committed-backend
  evidence; and
- keeps structured observations in memory until Yuri explicitly downloads
  them.

S3A-06 remains deliberately unavailable in the fixture harness. The eventual
Yuri run must exercise it separately through the accepted visible local
Diary → FastAPI → PostgreSQL confirmation path before a full Stage 3A result can
claim the exactly-one appointment/audit/command/receipt invariant.

## Prepared artifacts

- `docs/bernie-stage3-conversational-diary-decision.md` — accepted six-decision
  record and Stage 3A/Stage 3B split;
- `docs/bernie-stage3a-yuri-formative-validation-plan.md` — frozen authority,
  tasks, gates, evidence, retention, corrections and execution sequence;
- `docs/diary/stage3a/index.html` — isolated study surface;
- `docs/diary/stage3a/stage3a-data.js` — authored synthetic task, Diary and
  event fixtures;
- `docs/diary/stage3a/stage3a-core.js` — deterministic interpretation,
  counterbalance and attention decisions;
- `docs/diary/stage3a/stage3a.js` — accessible interaction, projections, grid,
  observation and export behavior;
- `docs/diary/stage3a/stage3a.css` — functional low-fidelity responsive layout;
  and
- `tests/test_bernie_stage3a_study_artifacts.py` — protected-safe authority,
  semantics, retention and fixture tests.

## Verification

- deterministic Stage 3A artifact population: 8 passed;
- combined Stage 3A, API Spine, live-handover and Ariadne receipt population:
  57 passed;
- event attention: one relevant concise notice, five correct suppressions, zero
  interruptive notices;
- deterministic answer/proposal/clarification/block/boundary states: pass;
- counterbalance A/B reversal: pass;
- browser runtime/provider/voice/persistence prohibition scan: pass;
- Node syntax for all three Stage 3A JavaScript files: pass;
- focused Ruff for the new Python test: pass;
- canonical repository fast profile: pass, including 60 focused API Spine,
  handover, receipt and maintenance tests;
- rendered desktop page identity, non-blank state, authority banner, console
  health, typed answer, projection, return-to-context, event filtering and
  structured-observation interaction: pass;
- rendered mobile 375-pixel content width: 14 scenarios present, zero document
  horizontal overflow and zero console warnings/errors; and
- `git diff --check`: pass.

The rendered validation used the local browser against a static localhost
server. It is fixture evidence, not live backend evidence.

## Protected integration

Candidate commits `4b043f3a3762d26daba7176dc1dafedfc1403e4c` and
`0d90c1804448730e0cd8f83c3d643fd5ff033658` were pushed only to
`codex/bernie-stage3a-yuri-study`. Protected PR 45 then passed:

- Python Security;
- Node and Office add-in manifest/security validation;
- Diary smoke review;
- CodeQL Python;
- CodeQL JavaScript/TypeScript; and
- the aggregate CodeQL context.

The PR had no reviews, comments, or unresolved review threads. It was promoted
from draft only after every required context passed and squash-merged without
admin bypass, check dismissal, review dismissal, force push, or direct protected
branch write as `25f8d4e61cf5ee5ca3726d4eed5fc99bb4e895da`.

## How Yuri begins

From `C:\Users\sarashera\emr4`:

```powershell
Start-Process -FilePath 'C:\Users\sarashera\emr4\.venv\Scripts\python.exe' `
  -ArgumentList @('-m','http.server','8765','--bind','127.0.0.1') `
  -WorkingDirectory 'C:\Users\sarashera\emr4\docs\diary' `
  -WindowStyle Hidden
```

Then open:

`http://127.0.0.1:8765/stage3a/`

Choose counterbalance A for the first run, start S3A-01, follow each displayed
goal, and record only the structured outcome controls. Do not enter any real
patient, staff or practice information. Download the structured observation
file only after the run is complete.

## Boundaries preserved

No Stage 3B participant, Claude Fable/subscription, external model, provider
call, prompt transmission, voice, push-to-talk, ambient listening, event
producer/outbox/broker/consumer/subscription, GraphQL mutation, new appointment
action, PII, production, deployment, or release authority moved.

## Next gate

Yuri performs the formative run. Sol then reviews the structured observations,
runs the separate S3A-06 authoritative local confirmation check, makes only any
logged narrow Stage 3A corrections permitted by the plan, and returns an exact
`stage3a_pass`, `stage3a_partial`, or `revision_required` decision.
