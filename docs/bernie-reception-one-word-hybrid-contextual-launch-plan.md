# Reception One Word Hybrid contextual-launch foundation plan

Status: authorised provider-free development tranche
Recorded: 2026-07-31
Predecessor: `reception-one-bureau-post-admission-runtime-hardening`

## Authority and durable product decision

Yuri selected the recommended Hybrid direction:

- Word Online remains the clinical workspace;
- a later compact Reception One companion may accept a request and display a
  concise proofreader-admitted result; and
- detailed Diary work opens in the full native Diary/Bureau window.

This descendant establishes only the contextual native-window foundation. It
does not attempt to build the later conversational Word companion.

## Objective

1. Repair the visible Reception One request textarea so one- and two-line text
   is vertically legible and the field grows within a bounded height before
   scrolling.
2. Add a distinct `Open Reception One in Diary` action to the Word taskpane.
3. Reuse the existing Office dialog and authentication handshake while sending
   a separate typed, non-authoritative launch context after the child reports
   ready.
4. Make the native Diary validate that context, move to its exact date first,
   and then open Reception One over the still-authoritative Diary.

## Boundary classification

This is a UI access-surface and minimal context-frame change under the API
Spine. It is not a GraphQL read, provider invocation or command mutation.

The launch context is in-memory navigation intent only. It must contain:

- exact contract version and message type;
- source and target surface identifiers;
- one valid local `reference_date`;
- an opaque correlation identifier;
- `open_projection=true`;
- `planner_mode=deterministic`; and
- explicit false command, provider and patient-context authority flags.

It must not contain a patient identifier, patient name, request text,
appointment identifier, clinical text, access token, provider credential,
confirmation evidence or command payload. Authentication continues in the
existing separate `auth` message.

## Frozen behaviour

- The existing calendar action continues to open the ordinary native Diary.
- The new Reception One action opens the same native Diary in an Office dialog
  and sends the typed launch context only after the child reports ready.
- The v1 taskpane launch date is the current local calendar date. A future
  compact companion may supply a user-selected date under a later contract.
- The native Diary validates an exact allowlist and rejects malformed or
  additional fields.
- A valid context navigates the underlying Diary to the requested date before
  opening the projection.
- The projection remains proposal-only. Standard remains the zero-provider
  default and no Isolated request is made.
- No contextual value is placed in the Diary URL.
- A popup retry retains only the same validated non-sensitive launch context
  and remains bounded to the existing one automatic stale-dialog retry.
- Source and published taskpane copies remain synchronized.

## Acceptance

1. One- and two-line request text is vertically centred within the visible
   content area, grows from its minimum to its bounded maximum and then uses an
   internal scrollbar without clipping.
2. The ordinary Diary and Reception One launch actions are visibly distinct.
3. A deterministic contract test rejects extra fields, patient/appointment
   identifiers, request text, tokens and malformed dates.
4. A route-intercepted browser exercise proves that the Word action produces
   one exact launch context and the native Diary receives it, verifies the
   requested date and opens Reception One.
5. The launch URL contains no patient, appointment, request, token or context
   query value.
6. No provider, ADC, backend mutation, database write, appointment
   confirmation, deployment or release occurs.
7. Relevant taskpane, Diary, API Spine, Continuity and Compass tests remain
   green; JavaScript, Python, JSON/schema and diff checks pass.

## Protected-evidence incident

During pre-plan inspection, one over-broad repository search entered a
protected holdout fixture path and printed fixture text. The search was stopped
immediately. No protected content may be analysed, reused, copied, tested
against, transmitted, hashed or referenced by this work. Subsequent inspection
is restricted to explicit taskpane, native Diary, API Spine and named
acceptance paths. Historical nodes remain unchanged.

## Closed gates

No live provider call, ADC read, patient/product-derived/clinical data,
historical Diary material, embedded Word model runtime, appointment command,
confirmation, write, voice, participant session, production, deployment or
release is authorised.
