# Reception One Stage 3B representative-staff readiness plan

Status: authorised readiness tranche
Authority source: Yuri's 2026-07-24 reply, “Let's do it”, to the proposed
provider-free representative-staff evaluation sequence
Continuity descendant:
`reception-one-stage3b-representative-staff-readiness`
Parent: `reception-one-visual-interaction-synthesis`

## Objective

Prepare a frozen, runnable formative evaluation of the accepted Reception One
visual and interaction synthesis with representative Australian general
practice reception staff. This tranche may build, locally rehearse and validate
the protocol. It must not claim participant evidence until real voluntary
sessions occur.

The readiness tranche ends as
`stage3b_study_ready_awaiting_participants` when the study kit and its
repository-local acceptance gates pass. Yuri retains the decision to nominate
or schedule participants. Codex must not contact, recruit or enrol anyone.

## Frozen authority

This work may:

- add a provider-free, repository-local facilitator instrument;
- use the existing authored-synthetic Reception One and ordinary Diary
  surfaces;
- perform automated protocol rehearsal and rendered browser QA;
- record only anonymous, structured observations during a later voluntary
  study; and
- update Ariadne Continuity, Compass and the live handover to describe the
  readiness result accurately.

It may not:

- use Vertex or another model/provider;
- access real, product-derived, patient, clinical or historical data;
- create, confirm, cancel or alter an appointment;
- change an API, database schema, command path, product authority or event
  runtime;
- record names, email addresses, practice identities, typed requests, free
  text, audio, video, screen recordings or transcripts;
- use cookies, local storage, session storage, analytics or background
  telemetry;
- contact participants, deploy, release, commit, push or move protected refs;
  or
- describe automated rehearsal as participant evidence.

The existing Reception One runtime remains deterministic and unoccupied. The
study instrument is a sidecar: it displays task cards, opens the accepted UI in
a separate window, times tasks locally and retains structured observations in
memory until an explicit JSON download.

## Participants and consent

The intended formative cohort is five to eight current or recent Australian
general-practice reception staff, preferably spanning at least two practices.
The cohort is sufficient for a bounded formative signal only; it cannot prove
population-wide usability or production readiness.

Before a session begins the facilitator must record:

- an anonymous code from `P01` to `P08`;
- an anonymous practice bucket, `practice-a` or `practice-b`;
- counterbalance arm `A` or `B`;
- voluntary participation and the right to stop;
- acknowledgement that every name and appointment is synthetic;
- acknowledgement that no typed words, free text, audio or recording will be
  retained; and
- acknowledgement that the session performs no appointment write.

No consent record may contain a person or practice identity.

## Frozen task protocol

Each participant receives the same eight authored-synthetic tasks. Arms A and B
reverse the route order for the paired tasks to reduce ordering bias.

1. Orient to the current Diary state and identify whether the surface shows
   committed truth, a selection or an unwritten proposal.
2. Find Margaret Thompson's upcoming appointments.
3. Inspect Dr Shera's bounded afternoon on the reference day.
4. Find a 30-minute option for Margaret Thompson with Dr Shera after 2 pm.
5. Select a time and prepare the proposal-review state, then state what has and
   has not happened.
6. Ask for “Alex” without a surname and resolve the ambiguity between the two
   authored-synthetic practitioners without assuming identity.
7. Return from a focused projection to its previous context and then to the
   ordinary Diary.
8. Recall Billy Fursin's afternoon appointment from the ordinary Diary or
   Reception One route assigned by the counterbalance.

The route displayed by the instrument is authoritative for the task. A
participant may use the ordinary-Diary escape when needed; the facilitator
records that as a fallback rather than preventing it.

## Structured observation contract

One record per task contains only:

- session, participant-code and task identifiers;
- practice bucket and counterbalance arm;
- assigned route and visited-route flags;
- monotonic elapsed milliseconds;
- outcome enum;
- correctness enum;
- state-comprehension enum;
- confidence enum;
- assistance count;
- ordinary-Diary fallback;
- safe-ambiguity disposition;
- proposal-boundary disposition;
- issue flags from a frozen allowlist; and
- an ISO recording timestamp.

The export is `reception_one.stage3b.study_export.v1`. It states explicitly
that prompt/transcript/free-text/audio/video and real patient data are absent.
Export is an explicit browser download. Reset destroys the in-memory session.

## Preserved acceptance thresholds

The Stage 3A provisional Stage 3B thresholds remain unchanged:

- at least 80% grid-free completion for Reception One-assigned tasks;
- at least 90% safe ambiguity recovery;
- at least 90% correct and reversible projections;
- at least 90% precision and recall for low-interruption notices when that
  event-attention family is tested;
- median conversational completion no slower than the ordinary Diary; and
- as a nonblocking signal, at least 20% faster appointment recall.

The current eight-task protocol does not exercise a live event-notice fixture.
It therefore reports the notice precision/recall threshold as `not_measured`,
not passed.

Absolute safety gates require:

- zero real or synthetic appointment writes from the study surface;
- zero identity assumptions after ambiguity;
- zero release of a proposal as a completed booking;
- zero retained prompt, transcript or free-text content; and
- no participant exposure to provider, credential or infrastructure detail.

Any absolute safety-gate failure stops the session and marks the study result
`revision_required`. Usability findings do not change the frozen product during
the cohort; they are collected for a separately authorised correction tranche.

## Readiness acceptance

The readiness tranche passes only when:

1. the sidecar is keyboard-operable, responsive and explicit about its
   synthetic/no-write boundary;
2. consent gates session start and the export contains only the schema's
   allowlisted fields;
3. tests prove there is no fetch/XHR/WebSocket, storage, credential, provider
   or product-write path in the sidecar;
4. deterministic scoring separates measured, passed, failed and
   `not_measured` thresholds without fabricating participant evidence;
5. desktop and tablet rendered browser checks pass against the sidecar and the
   accepted Reception One UI;
6. JSON, schema, JavaScript, Python, Compass and repository verification pass;
7. Continuity graph and Compass revisions match and the rendered Compass
   validates; and
8. the closeout names the remaining participant nomination/scheduling gate.

## Stop and closeout

Stop before real participant execution if representative volunteers are not
yet nominated, consent cannot be obtained, the authored-synthetic runtime is
unavailable, an appointment write becomes possible, or any real-person or
real-patient detail would be required.

Readiness evidence proves that the study can be run within this bounded
contract. It does not prove staff usability, clinical safety, operational
fitness, production readiness or representative participant performance.
