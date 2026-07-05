# Bernie Native Diary Agent Notes

This file records Ariadne/Yuri architecture discussion while the Fable 5
consulting plan is under review. It is not an implementation packet and does
not authorize code changes.

## 2026-07-03 - N1 Amendment Under Review

Fable's consult recommends a first implementation sprint, N1, that creates a
new `app/services/diary/` domain package and rehomes the diary action catalog,
typed action envelopes, and temporal policy there while leaving
`frames.py`/`policy.py` in `app/services/bernie/` unless the ordinary diary UI
starts building frame sets itself.

Ariadne and Yuri currently lean toward moving the reception evidence frames and
deterministic reception policy into the new diary domain immediately, because
the target architecture is for Bernie, the ordinary receptionist UI, Rayleen,
and later Davida to share the same diary/reception evidence language.

Proposed amended N1 direction:

- Create `app/services/diary/` as the native diary/reception domain home.
- Move or facade the following into that domain in a no-behaviour-change slice:
  - native diary action catalog
  - action intent/proposal/confirmation envelopes
  - diary event vocabulary
  - canonical temporal/date policy
  - typed reception evidence frames
  - deterministic policy over those frames
- Keep `app/services/bernie/` focused on:
  - natural-language interpretation into diary action intents
  - Bernie conversation/session statechart
  - Bernie narration/voice over typed outcomes
  - compatibility facades during migration

Architecture distinction to preserve:

- **Diary/reception frames** are evidence about proposed diary work: recognised
  patient, requested action, roster checked, slot search result, conflict,
  advisory future booking, proposal prepared, guardrail outcome.
- **Bernie session state** is conversational memory: awaiting clarification,
  candidate selected, proposal previewed, confirmation requested, stale after
  navigation, terminal/abandoned.

The goal of the amendment is to avoid building the shared diary/reception
grammar in Bernie's private namespace and then extracting it later after other
agents or UI paths have depended on it.

## 2026-07-03 - Multi-Author Suggested Next Actions

Fable's section 4.1 listed `suggest_next_actions` as a read-only action with
Bernie as the author. Ariadne and Yuri think that is too narrow for the intended
future architecture.

The long-run conversation should be two-way and eventually multi-agential:
human receptionists, Bernie, Rayleen, Davida, and other bounded agents may all
suggest possible next actions. A human suggestion may arrive as natural language
or UI gesture rather than as a typed action, but before the diary is mutated it
must still be normalized into a typed `DiaryActionIntent`, validated by the
deterministic diary domain, and confirmed where required.

Refined principle:

> Any participant may suggest. Only the diary domain may validate. Only
> confirmed typed actions may mutate state.

Proposed refinement to the action grammar:

- Treat `suggest_next_actions` as a meta/read-only action with potential authors
  `human`, `bernie`, `rayleen`, `davida`, and future bounded agents.
- Consider splitting the concept into clearer stages:
  - `propose_next_action`: any participant suggests a possible next diary move.
  - `normalize_next_action`: the suggestion is compiled into a typed
    `DiaryActionIntent`.
  - `validate_next_action`: deterministic diary policy decides whether the
    intent can be offered, blocked, or needs clarification.
- Preserve a strict boundary between conversational suggestion and diary
  mutation: free-form human or agent suggestions are first-class conversation
  inputs, but they are not executable diary writes until typed, validated,
  evidence-gated, and confirmed.

After Yuri and Ariadne finish reviewing Fable's plan, this amendment should be
included in the compiled response sent back to Fable for confirmation and
stress-testing.

## 2026-07-05 - Schema-Literate Bernie, Not Code-Authoritative Bernie

Yuri raised that EMR4 is now building "muscles, sinews and moveable limbs" for
the Diary: native state transitions, validation paths, receptionist scenarios,
reason-code policy, freshness checks, and explicit confirmation boundaries.
Because Gemini has a large context window and strong domain reasoning, Bernie
should eventually understand the intricacies of this diary/reception language
well enough to feel native to the Diary system.

The principle to preserve:

> Bernie should be schema-literate, not code-authoritative.

Recommended architecture:

- Give Bernie a compact, versioned, read-only Diary Capability Manifest that
  describes diary entities, states, transitions, permissions, reason-code rules,
  roster semantics, patient-link semantics, audit evidence, and confirmation
  boundaries.
- Prefer curated generated artifacts over dumping raw code into the model
  context. The manifest may be derived from constants, backend schemas, and
  deterministic tests, but the runtime code and backend state machine remain the
  source of authority.
- Bernie's role is to translate receptionist language into typed diary movement
  proposals such as slot search, appointment move/resize, status change,
  cancellation with reason, patient link, or clarification request.
- The deterministic diary domain remains the adjudicator for authorization,
  freshness, collision checks, roster policy, reason-code validity, audit
  evidence, and required human confirmation.
- Gemini's large context window should be used for ambiguity handling, domain
  fluency, long-range consistency, and explanation, not for bypassing typed
  contracts or inventing new write paths.
- Bernie explanations should expose why a proposed action is allowed, blocked,
  or needs clarification in terms of the manifest and server-confirmed evidence.

Future sprint candidate:

- **Bernie Diary Capability Manifest v1**: create a read-only manifest and
  golden tests proving Bernie-facing prompt/context material matches the native
  diary action vocabulary and cannot grant write authority by itself.
