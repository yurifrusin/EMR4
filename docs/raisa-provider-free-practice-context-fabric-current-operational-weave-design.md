# Practice Context Fabric Current operational weave design

Date: 2026-08-06

Status: provider-free authored-synthetic design

## API Spine classification

This is a scoped read/context composition. It adds no API surface. The existing
GraphQL prototypes remain read-only; REST/OpenAPI remains the only future
command plane. The weave consumes sealed projections only after their ordinary
backend authorization has completed and cannot invoke a source itself.

## Existing source families

| Operational frame | Existing read family | Exact source-contract id | Authority ceiling |
|---|---|---|---|
| `current_diary_projection` | appointment-first `DiaryDay` read context | `api_spine.appointment_diary_read.v1` | read context only |
| `current_waiting_room_projection` | Rayleen A4 waiting-room frame | `emr4.waiting_room_context_frame.v1` | data/read context only |
| `active_practitioner_directory` | application-session active-only practitioner read | `practice-practitioner-directory-read.v1` | read context only |
| `private_application_session_state` | native-Diary application-session statechart snapshot | `emr4.native_diary_application_session_state.v1` | private read context only |

The fourth shape carries only session generation/request revision, visible Diary
date/location, optional focused appointment or active practitioner and proposal
freshness. It excludes prompts, responses, turns, private narrative, credentials,
authority envelopes, reader functions and cached source rows.

## Authority and scope

The candidate proposes Bureau, purpose, frame/source classes, locations,
requested disclosure fields, required sources, a half-open UTC window,
freshness and limits. It cannot carry principal, practice, role, session,
consent, retention or authority.

Trusted backend context supplies those values in a sealed authority binding.
The grant is the stable intersection of candidate and binding. Empty mandatory
intersections yield the same external `NOT_AVAILABLE` disposition; protected
reduction detail remains only in the trace.

Every source envelope binds the same practice and a digest of the current
principal/session/session-generation tuple. This digest is comparison evidence,
not authentication material and is never accepted from the candidate.

## Weave rules

- Verify all seals before reading payload fields.
- Allow exactly one source envelope for each admitted frame type.
- Require exact frame/source/source-contract triples and authored-synthetic
  evidence/data labels.
- Reject any source observed after assembly, outside the effective interval,
  expired at assembly, older than the freshness cap or bound to a non-admitted
  location.
- Canonically order frames as Diary, waiting room, directory, session.
- Preserve source revision, observation time, expiry and source digest on every
  output frame.
- Compute output expiry as the minimum of binding, grant and admitted source
  expiries; never extend a source lifetime.
- Intersect requested disclosure fields with the backend allowlist, then omit
  every optional field outside that effective set.
- Apply result and canonical-byte limits before sealing the frame set.

## Cross-source coherence

The projection families remain distinct but may be checked against one another:

- waiting-room appointment refs must occur in the admitted Diary projection;
- practitioner refs in Diary, waiting-room and session frames must resolve to
  an active admitted directory entry;
- waiting-room and Diary locations must agree;
- session visible date/location must agree with the Diary frame;
- session focus appointment, when present, must occur in the Diary frame; and
- a stale/superseded session or stale proposal can be reported as state but can
  never become command evidence.

These are consistency checks over already-admitted read shapes, not joins that
retrieve new data.

## Same-packet proofreading

The proofreader receives the exact candidate, authority binding, need, grant,
source envelopes, source trace, weave trace and frame set. It recomputes every
digest and coherence rule using the same caller-supplied clock. Release is
atomic: either the whole current operational weave is admitted or none of its
frames is released.

## Non-authority statement

An operational frame explains what an authorised read reported at a bounded
time. It does not prove identity, grant present access after expiry, reserve an
appointment, confirm a proposal, execute a command or establish provider-model
memory. Any consequential future action must re-authorize and re-read through
its ordinary REST/OpenAPI command boundary.
