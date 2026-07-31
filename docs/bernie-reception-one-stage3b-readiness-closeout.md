# Reception One Stage 3B readiness closeout

Result: `stage3b_study_ready_awaiting_participants`
Continuity descendant:
`reception-one-stage3b-representative-staff-readiness`
Data class: authored-synthetic only
Provider: disabled / not used
Product write: not exercised
Participant sessions: zero

## Outcome

The bounded readiness tranche passes. Reception One now has a frozen,
provider-free representative-staff formative protocol and a runnable study
sidecar. The sidecar:

- gates entry on four explicit consent attestations;
- admits only participant codes `P01`–`P08` and anonymous practice buckets;
- counterbalances Reception One and ordinary-Diary routes;
- presents eight authored-synthetic reception tasks;
- records allowlisted structured outcomes in memory;
- has no free-text, prompt, transcript, audio, video, storage, telemetry,
  provider or product-write path;
- exports only `reception_one.stage3b.study_export.v1` after an explicit
  download action; and
- destroys the in-memory session on reset.

This result does not claim that Stage 3B usability thresholds pass. No
representative participant has been recruited, consented or observed.

## Repairs made during readiness

Rendered and live-local rehearsal found and repaired ordinary repository-local
defects:

1. The study workspace was initially visible before consent because its grid
   rule overrode the native `hidden` state. A fail-closed `[hidden]` rule and
   regression assertion now preserve the gate.
2. A scripted `window.open` handoff was treated as blocked under `noopener`
   even when a browser tab opened. It is now an explicit, inspectable local
   link with `noopener noreferrer`.
3. Minimum control sizes were raised to 44 pixels, including task navigation.
4. The ambiguity task originally depended on two patients not present in the
   accepted live-local fixture. It now uses the real authored-synthetic
   `Alex Shera` / `Alex Chen` practitioner ambiguity and proves clarification
   without silently choosing a person.
5. Task wording now pins the ordinary Diary to Monday 27 July 2026 and uses
   the accepted deterministic “today” request grammar only after that date is
   visible.
6. Product-task verification moved from the pre-existing IPv4 review server to
   the established disposable IPv6/PostgreSQL harness. This prevents review
   state from being mistaken for a reproducible study fixture.

## Evidence

### Study sidecar

`browser-acceptance-evidence.json` passes at:

- desktop 1440×900;
- tablet 768×1024; and
- phone 390×844.

Before consent, the workspace is hidden. After consent, it is visible. Every
viewport has zero horizontal overflow and zero measured controls below 44
pixels. The automated structured-record rehearsal records one allowlisted
observation, defaults the identity-ambiguity task to safe clarification, emits
no unexpected network request and reports no console error.

The six exact PNGs are hashed in the evidence. They are layout evidence, not
participant evidence.

### Accepted product task population

`product-task-acceptance-evidence.json` passes against a newly created,
marker-verified disposable IPv6 local runtime with real loopback
FastAPI/PostgreSQL and no route or API interception:

- Margaret Thompson's four authored-synthetic upcoming appointments render;
- “Alex” produces a clarification between Alex Chen and Alex Shera;
- a combined Margaret Thompson / Dr Shera / half-hour / after-2 request reaches
  current availability;
- selecting a time and preparing a proposal still states that no appointment
  has been created and that appointment write authority is false;
- the booking-review handoff may be visible but was not activated; and
- Ordinary Diary exits cleanly from Reception One.

Before and after database counts and SHA-256 digests are identical. Appointment
audit, idempotency, booking-session and session-event write surfaces remain
zero. The exact disposable database is then dropped after its ownership marker
is verified. No IPv4 review server, external host, confirmation route, session
route, provider or cloud credential is contacted.

`final-residue-evidence.json` independently confirms zero task-owned process,
IPv6 listener, browser process, container, network, image or disposable
database residue while preserving the three pre-existing IPv4 review
listeners.

### Verification

The focused readiness, Stage 3A, visual synthesis, functional meta-grid,
combined-scope, API Spine artifact, Ariadne Continuity, Compass and
orchestrator-preflight populations pass as one 118-test integrated run.
JavaScript syntax, Python compilation and Ruff, JSON/schema validation,
Compass rendering, `git diff --check`, and independent
process/network/database residue checks also pass. The only test warnings are
the pre-existing Starlette/httpx and Google GenAI Python deprecation notices.

## Frozen participant execution

The next action is not another implementation loop. Yuri must nominate or
schedule five to eight voluntary current or recent Australian
general-practice reception staff, preferably from at least two practices.
Codex must not contact or enrol them.

During the cohort:

- the accepted product and protocol remain frozen;
- each participant uses an anonymous code and supplies all consent
  attestations;
- the operator launches the established disposable authored-synthetic runtime;
- only the structured JSON export is retained;
- any absolute safety failure stops the session; and
- usability findings wait for a separately authorised post-batch correction
  tranche.

The Stage 3A thresholds remain frozen. The current protocol does not exercise a
live event-notice fixture, so low-interruption notice precision and recall must
remain `not_measured`.

## What this proves

It proves that the study protocol and accepted product task population can run
locally with authored-synthetic data, deterministic consent and retention
boundaries, responsive controls, no provider, no appointment confirmation,
unchanged database truth and complete isolation cleanup.

It does not prove representative-staff usability, threshold attainment,
population generalisability, clinical safety, production fitness, provider
residency, voice interaction, real-data handling, deployment or release.
