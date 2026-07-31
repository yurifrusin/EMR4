# Product Platform, API, and Security Ledger

## Product architecture

EMR4 Centaur is an AI-native Australian General Practice management system.
FastAPI/PostgreSQL provides clinical and diary authority; the Microsoft Word
Office.js add-in is the clinical workspace. Word Online is the target Office
surface. The native browser diary grid supersedes the retired Word-table diary
for interactive scheduling.

The definitive phase and architecture plan is `implementation_plan.md`.
Current language-coverage work does not authorize unrelated route, GraphQL,
database, UI, deployment, or release changes.

## 2026-07-30 Reception One shared language boundary

Reception One now has one closed integer-coded PlanProgram shared by the model
and deterministic proofreader plus a separate independently screened
`operator_note`. The note is audit-only and cannot supply arguments, select an
operator, trigger execution or reach the product. The compiler performs only
frozen-table expansion; existing backend read/proposal adapters and human
confirmation boundaries remain authoritative. No GraphQL, REST command,
database, appointment-write or product-delivery authority was added.

The live authored-synthetic Vertex sequence exhausted its two-call ceiling
without a proofreader-admitted plan. Both HTTP 200 programs used invalid
prior-output indexes and released nothing. This leaves the provider-connected
planner closed while preserving the deterministic provider-free runtime.

## API Spine

Use the `docs/api-spine/` contracts and the EMR4 API steward rules whenever a
sprint touches GraphQL/read models, REST/OpenAPI commands, appointment
proposals/confirmations, Access AI boundaries, context frames, manifests,
async contracts, audit, security, or idempotency. A sprint must not claim API
Spine compatibility without running the relevant contract guards.

## Security posture

Production settings fail closed for default secrets and CORS uses an
allowlist. Open structural work includes PostgreSQL RLS defense-in-depth, the
full audit-log surface, JWT storage hardening, and field-level encryption.
Dependabot alert 5 remains open; do not force dependency overrides. Security,
deployment, external-patient access, and release gates remain explicit user
decision boundaries.

## Environment and deployment orientation

- Full local stack: `run_dev.ps1` (`-Down` stops it).
- Backend: `.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001`.
- Migrations: `.venv\Scripts\python.exe -m alembic upgrade head`.
- Taskpane source: `EMR4 Sidebar/src/taskpane/`; published copy:
  `docs/taskpane/`; synchronize with `sync_taskpane.py`.
- Command Centre: `docs/command-centre/`.
- Native Diary: `docs/diary/`.

GitHub Pages must deploy from canonical `master`; a stale worker-branch deploy
can overwrite the live artifact. Word Online is strict about OOXML element
order, so raw OOXML insertions must respect schema ordering.

The immutable pre-compaction handover preserves detailed phase history,
environment credentials guidance, file maps, historical defects, and deploy
gotchas. Treat source and current docs as authority when old narrative and live
code differ.

## 2026-07-17 post-certification security transition

The failed Python Security workflow was traced to `python-jose`'s transitive
`ecdsa` advisory. The auth boundary now uses `PyJWT==2.13.0` with configuration
restricted to `HS256`; focused auth/API tests and `pip-audit` pass. Bandit runs
with `always()` and an exact two-item baseline for SHA-1 used solely to
reproduce Git blob identities. Historical-diary leakage lint remains clean.

Dependabot alert 5 is dev-only: the production npm audit is clean, while the
latest supported `@microsoft/teamsfx-core` still requests vulnerable
`uuid@^8.3.2`. A non-forced lock refresh did not remove the alert and was not
retained. No override or dismissal is authorized.

The Secure SDLC review found strong existing design/verification controls but
a delivery-enforcement gap: GitHub reports unprotected `master`, secret push
protection disabled, and ten open CodeQL candidates classified high. The
candidates require reachability/validity triage and are not yet confirmed
vulnerabilities. Private vulnerability reporting is enabled and `SECURITY.md`
now documents the reporting route. See
`docs/security/emr4-secure-sdlc-review-2026-07-17.md` and the evidence-bound
portfolio under `docs/security/secure-sdlc-hardening/`.

All ten high-classified CodeQL candidates were then validated individually.
Seven focused backend-boundary tests passed and both flagged reporting CLIs
emitted aggregate-only output. No candidate survived as a reportable high
security finding: four client/demo bypass alerts are defeated by mock-only or
independently authenticated backend boundaries; three random-value alerts use
correlation/idempotency values rather than credentials; one selector alert
receives UUID/fixed-mock IDs; and two logging alerts print asserted aggregates.
The alerts were not dismissed. Diary defence-in-depth remediation and GitHub
protection settings are now the user decision boundary. See
`docs/security/codeql-high-validation-2026-07-17.md`.

## 2026-07-30 Reception One extended proposal runtime

The default-off authored-synthetic product route now covers four proposal-only
families beyond appointment creation: move, duration change, cancellation
review and squeeze-in assessment. Trusted backend code keeps the selected
appointment UUID practice-scoped, replaces it with an opaque request handle
before planning and reuses existing update/delete proposal services solely as
non-mutating safety adapters. The deterministic proofreader remains the only
release gate; confirmation and appointment-write endpoints remain closed.

A disposable real browser/FastAPI/PostgreSQL acceptance passed all four
families with zero writes, unchanged appointment/audit/command/event hashes
and complete cleanup. The separately occupied Sydney Vertex move study did
not produce an admitted candidate in either of its two authorised calls, so no
live model planner is wired into this route. See
`docs/bernie-reception-one-extended-proposal-runtime-closeout.md`.

Yuri authorized both decisions. The resulting material cross-layer tranche
hardwired risk-triggered red/blue/purple review into Ariadne, structurally
separated local mock Diary loading from token-gated live loading, allowlisted
confirmation destinations, removed insecure random fallback and selector
construction, and passed all representative PR checks without dismissing a
CodeQL result. GitHub now enforces secret push protection and protected
`master` with strict Python/JavaScript CodeQL plus Python/Node security checks,
administrators included. See
`docs/security/secure-sdlc-red-blue-diary-hardening-closeout-2026-07-17.md`.

The transition review also completed metadata-only corpus triage. The public
appointment-call dataset was promising enough for Yuri to authorize a local
quarantine pilot. Its preliminary provenance and licence-authority gate stopped
before content download: clinic/data-controller identity, jurisdiction,
collection basis, uploader authority, content rights, redaction method, and a
residual-identifier audit remain undocumented. No content was downloaded or
admitted. MedInstruct is synthetic medical instruction data, not receptionist
evidence. See `docs/bernie-dialogue-corpus-source-assessment.md` and
`docs/bernie-appointment-call-quarantine-pilot-closeout.md`.

## 2026-07-30 Reception One minimal context bridge

The accepted read-only synthetic Diary-context descendant now proves the
intended product seam without granting the model database authority. The
authenticated trusted backend constructs the existing typed
`reception.one.bureau.plan-input.v1` frame, keeps the raw identifier map, and
passes only minimal request-scoped opaque context to the isolated model cell.
The deterministic proofreader reuses the complete backend-held frame and is
the only release gate. Its occupied result was one non-writing,
human-confirmation-required `proposeAppointmentUpdate` candidate.

The next API Spine increment is deliberately default-off and development-only:
the existing product-context route will retain deterministic planning as its
default and may select the isolated Vertex planner only for an exact
authored-synthetic practice allowlist under a separate gate. Both planners must
converge on the same typed proofreader and proposal response. No new
confirmation route, write authority, real-data use, frontend provider access,
production, deployment or release is opened.

## 2026-07-30 Reception One default-off dual-planner route

That API Spine increment now passes. The request schema exposes only
`deterministic` or `isolated_vertex`; callers cannot supply provider, model,
project, identity, location, hostname or credential values. Deterministic mode
remains the default. Isolated mode requires a separate disabled-by-default
feature gate, development environment, exact authored-synthetic practice
allowlist and the frozen Sydney binding.

Trusted backend code alone reads product context and retains raw identifiers.
The isolated cell receives request-scoped opaque handles and no database or
cloud credential. Both planners release through the same proofreader and
existing create/update/delete proposal adapters. Every response states that
human confirmation is required and that no write or confirmation occurred.

The single occupied request was admitted as a 45-minute resize proposal. A
post-response Windows cleanup race was repaired and the route/adapter replayed
with the deterministic planner and zero provider calls. Database counts and
hashes remained unchanged. The next UI work may surface only admitted typed
proposal fields and bounded non-secret provenance in a provider-free,
development-only authored-synthetic tranche; it does not open frontend
provider access, confirmation, writes, real data, production, deployment or
release.

## 2026-07-30 Reception One Bureau runtime UI seam

The UI seam now passes without changing the existing API Spine authority:

- ordinary Diary/Bureau use has no planner selector;
- the authored-synthetic development gate exposes a selector that defaults to
  `deterministic`;
- the client may submit only `deterministic` or `isolated_vertex`;
- backend code still owns context, identity resolution, freshness,
  proofreading and proposal adaptation;
- the browser receives only admitted proposal fields, planner mode,
  proofreader disposition, bounded provider-call count and an opaque audit
  reference; and
- no confirmation or mutation surface was added.

The real local Standard route passed with zero provider calls and unchanged
database truth. The disabled isolated route failed before context/provider use
without fallback or stale provenance. Another occupied call, product-derived
data, writes, voice, Word, production, deployment and release remain closed.

## 2026-07-31 Reception One Word Hybrid contextual launch

Yuri selected the Hybrid access model: Word remains the clinical workspace, a
compact Reception One companion may grow there, and detailed Diary work opens
in the full authoritative native Diary/Bureau.

The first provider-free foundation now passes. The existing ordinary Diary
button is preserved and a distinct `Reception One — Open in Diary` action
sends one closed zero-authority navigation context after the child-ready
handshake. Authentication remains separate. The launch URL carries no context,
patient, appointment, request or token data. The native Diary revalidates the
message, verifies the requested-date read and only then opens Reception One.
No API Spine command, confirmation or backend mutation was added.

The request textarea was also repaired: one- and two-line content is legible at
desktop and phone widths, it grows only to a 96 px ceiling and then scrolls
internally. Route-intercepted authored-synthetic Chromium evidence and 128
focused/relevant tests passed with zero provider calls, credential reads,
database reads or writes.

Continuity graph revision 168 and Compass map revision 149 bind the accepted
result. Actual authenticated Word Online dialog behavior, the conversational
companion, patient/product context, provider use, voice, writes, production,
deployment and release remain separate gates.

## 2026-07-31 Reception One Word compact companion

The next Hybrid descendant now passes as a default-off, provider-free,
authored-synthetic local shell. Word sends separate authentication,
zero-authority launch and closed companion-request messages. The native Diary
verifies the requested date, retains every detailed appointment and returns
only a generic summary after deterministic proofreading. Word validates the
summary again and derives its visible sentence from an allowlisted local
template.

The request grants no patient context, appointment context, provider, command
or write authority. The summary contains no request text, person name,
appointment record, provider draft or free text. Route-intercepted evidence
records zero provider, credential, backend, database, confirmation, command
and appointment-write activity. Continuity graph revision 169 and Compass map
revision 150 bind the accepted result.

This is local stubbed-Office-host evidence, not proof of authenticated Word
Online interoperability, backend authorization, provider interpretation,
real-data safety, production, deployment or release. The next candidate is a
supervised provider-free authenticated Word Online dialog check.

## 2026-07-31 Reception One Word desktop host proof

The closed companion contract now passes in the installed Word desktop host:
one blank task document, one disposable HTTPS-loopback sideload, one
authored-synthetic request, native-Diary-only detail and one exact generic
proofreader-admitted summary. No existing document content or Office
account/credential material was inspected, and the blank document body was
neither read nor written.

The taskpane repair keeps exact companion mode out of normal token/login and
backend initialization. Provider, credential, backend, database,
confirmation, command and appointment-write counts remain zero. Disposable
Word, sideload, listener, server and temporary-file residue is absent.

Continuity graph revision 170 and Compass map revision 151 bind the result.
The prior Word Online localhost path remains platform-blocked and is not
reinterpreted by the desktop pass. Office tenant identity, live provider or
backend context, patient/product data, voice, writes, production, deployment
and release remain separate gates.

## 2026-07-31 Raisa candidate dual-host foundation

The Word add-in now has one pure host-neutral capability profile shared by the
existing clinician and Reception One surfaces. Authored desktop, web, mobile
and unknown fixtures pass, profiles are deeply immutable, and profile
construction invokes no observed capability. Host readiness is explicitly
separate from authentication, role, data and action authority.

The durable feature inventory covers the earlier patient-file, consultation,
background-analysis, audio-capture, scribe-submission and clinician-finalise
paths as well as the newer Diary launch, contextual launch and compact
companion. Legacy direct-backend clinician paths are recorded as migration
work, not treated as newly accepted dual-host behavior.

Yuri's integrated-reception direction is also frozen: Reception One is one
backend-owned domain with role-scoped receptionist, doctor and future patient
surfaces. Future online booking receives only the patient booking contract and
future Rayleen arrival registration only the patient arrival contract, while
both converge on the same identity, availability, appointment, arrival, audit
and event truth. A third-party product is not selected as the primary
booking/arrival surface or a parallel source of truth.

The candidate delivery model is cloud-first practice management as a service;
any future local model is subordinate and cannot own parallel clinical,
reception or audit truth. Raisa and Clinician One are candidate names only. No
public rename, cloud resource, tenancy, patient surface, provider, microphone,
document operation, backend access, command, write, production, deployment or
release occurred. Continuity graph revision 172 and Compass map revision 153
bind the accepted result.

## 2026-07-31 Clinician One read-only document context

The first Clinician One operation now sits behind the accepted shared Word
host foundation. After an explicit click and authored-synthetic attestation,
it may consume exactly one current Word selection into a typed, deeply
immutable, in-memory `current_consult_note` frame. The one-use adapter rejects
replay, empty, oversized, over-line, malformed, mobile, unknown and not-ready
inputs; the 1,200-character and 40-line ceilings never truncate.

The taskpane exposes only source, host and counts. Raw selected text is neither
logged nor persisted, and the ordinary-browser state remains disabled.
Provider, backend, database, network, microphone, patient, diagnostic, command,
document-write and clinical-finalisation authority are all false. Dependency-
injected desktop and web fixtures and a fail-closed browser rendering pass, but
they do not prove real Word selection semantics, authenticated Word Online,
Office identity or role authorization, clinical-data safety or production
fitness.

Continuity graph revision 174 and Compass map revision 155 bind the accepted
result. The next bounded step is a supervised task-created authored-synthetic
desktop Word exercise, followed separately by an authorised non-loopback HTTPS
Word Online development-host exercise. Product, real, patient and clinical
data, provider use, document mutation, clinical action, production, deployment
and release remain closed.

## 2026-07-31 Clinician One installed-Word selection check

The first typed Clinician One operation now has one supervised installed-host
observation. A disposable `ReadDocument`-only HTTPS-loopback sideload in one
new unsaved blank Word document consumed one authored-synthetic exact current
selection. The taskpane released only source, host and counts. Word included
its terminal paragraph marker in the returned selection; the adapter preserved
that exact semantic rather than silently altering it.

No existing document, account, tenant, credential or protected data was
inspected. Provider, backend, database, microphone, diagnostic, clinical,
command and document-write counts remained zero. Yuri confirmed the task
document was closed without saving; the exact document, sideload, listener and
task logs were removed.

Continuity graph revision 175 and Compass map revision 156 bind the result.
Authenticated Word Online, a public HTTPS host, cloud tenancy, real-data
safety, provider or backend integration, production, deployment and release
remain unproven and separately gated.

## 2026-07-31 Raisa Cloud Run public-host readiness

The non-loopback Word Online dependency now has a repository-local,
synthetic-only deployment package. A deterministic 20-file context contains
the compiled taskpane, required native Diary development assets, a
dependency-free static server and non-secret provenance. The production build
now has one taskpane runtime path, no source maps and no placeholder
deployment origin.

The digest-pinned image passed as numeric non-root with a read-only root
filesystem, no host mounts, all capabilities dropped, no-new-privileges,
bounded resources and an internal-only network. Local mode and a simulated
exact Sydney `run.app` mode both passed. The hosted policy is exact-origin
bound, authored-synthetic and carries seven zero-authority fields.

The in-app browser rendered only the Clinician One synthetic-selection card
at normal and narrow taskpane widths. The synthetic acknowledgement worked and
the selection action remained fail-closed without Word. No EMR backend or
provider request was observed. A materialized HTTPS fixture manifest passed
Microsoft validation with `ReadDocument`; 98 focused inherited and new tests
pass.

No Google Cloud API, repository, service account, IAM policy, image push,
Cloud Run service, Office tenant, deployment or release state changed. All
task containers, networks, images, listeners, build contexts and browser tabs
were removed. Continuity graph revision 176 and Compass map revision 157 bind
the result. External cloud entitlement and creation, public IAM, authenticated
Word Online, real-data safety, processing geography, production and release
remain separately gated.

## 2026-07-31 Raisa Cloud Run private deployment and public-policy block

The authorised Sydney deployment created the exact Docker repository, pushed
the closed static image at immutable digest
`sha256:6696b3c97682ba8d02d3b18bab3d5d3d131f8c56c613c1adfca32400f94b3f5d`
and created `raisa-office-web-dev`. The ready private service uses the exact
returned `run.app` origin, the zero-project-role keyless runtime identity,
minimum zero and maximum one instances, and no secret, volume, VPC or Cloud SQL
configuration.

Effective Domain Restricted Sharing rejected the exact `allUsers` /
`roles/run.invoker` binding. No public binding or alternative access mechanism
was applied. Public route, browser, manifest and Word Online checks therefore
did not run. All task-owned local build and temporary credential residue was
removed; the authorised repository, image and min-zero private service remain.

Continuity graph revision 178 and Compass map revision 159 bind
`blocked_organization_policy_public_invocation`. Public testing now requires
Yuri's explicit choice to disable the Invoker IAM check on only this service,
or a narrow organisation-policy exception from an authorised operator.

## 2026-07-31 Raisa public access and Word Online upload intervention

Yuri authorised `--no-invoker-iam-check` on only
`raisa-office-web-dev` in `bernie-emr4-dev/australia-southeast1`. The exact
service is now publicly reachable on revision
`raisa-office-web-dev-00005-w82`, with zero `allUsers` IAM bindings, the
existing zero-project-role keyless runtime identity and the frozen no-secret,
no-volume and no-network-attachment posture.

The public route matrix, hosting policy, security headers, hosted companion and
Office manifest resources pass. Word Online reached its developer Upload
Add-in dialog but transmitted no manifest because Chrome extension file-URL
access is not enabled. No document content, provider, backend, database,
confirmation or command path ran. Two blank task-created Word documents require
deletion after the terminal Word result. Continuity graph revision 179 and
Compass map revision 160 bind the accepted partial result.

## 2026-07-31 Raisa Word Online authenticated companion verification

Yuri enabled the documented Chrome file-upload prerequisite and selected the
already validated task-specific `ReadDocument` manifest. The first hosted
Office-dialog attempt failed closed because the public taskpane admitted its
exact zero-authority policy while the Diary still limited `smoke` and
`reception_one_companion_demo` to loopback.

The exact repository-local repair loads and verifies that same origin-bound
policy in the Diary and admits only those two authored-synthetic capabilities.
It keeps backend, provider, credential, microphone, command, document-write and
production authority false. The repaired closed image was deployed only to the
existing Sydney service as revision `raisa-office-web-dev-00006-xf9`, immutable
digest
`sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324`.
The origin, zero-project-role/keyless runtime identity, min-zero/max-one
limits, no-secret/no-volume/no-VPC/no-Cloud-SQL posture, disabled Invoker IAM
check and zero `allUsers` bindings remain unchanged.

The rerun opened the native Diary, retained three authored-synthetic
appointment matches there and returned only the generic proofreader-admitted
count to Word. Observed taskpane and Diary traffic contained zero API,
credential and provider requests. No document body, backend, database,
appointment command, confirmation or microphone path ran.

Both task-created blank documents were moved to the recoverable OneDrive
Recycle Bin; the pre-existing named synthetic document was preserved and all
task-local build, image, container, network and temporary credential residue is
zero. Continuity graph revision 180 and Compass map revision 161 bind
`raisa_word_online_authenticated_companion_verification_pass`. EMR4
application authentication, clinician-role authorization, organisational
Office deployment, real-data safety, processing geography, production and
release remain unproved and closed.
