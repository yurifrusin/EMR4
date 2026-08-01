# Reception One Word compact companion shell plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `accepted_closed`

## 1. Authority and purpose

Yuri accepted the recommended Hybrid direction and instructed the work to
continue. This descendant adds the smallest useful Reception One companion to
the Word taskpane while preserving the native Diary as the detailed Bureau and
the sole scheduling surface.

The increment is provider-free and local-development-only. It demonstrates one
authored-synthetic natural-language request moving from Word to the existing
deterministic Reception One projection, followed by a generic, independently
validated status summary moving back to Word.

It builds on:

- `reception-one-integrated-bureau-baseline`;
- `reception-one-bureau-post-admission-runtime-hardening`; and
- `reception-one-word-hybrid-contextual-launch`.

Historical Continuity nodes and consumed ledgers remain unchanged.

## 2. Product contract

The Word companion is deliberately compact:

- one calm Reception One heading;
- one short natural-language request field;
- one `Prepare in Diary` action;
- one concise returned status; and
- one ordinary `Open Reception One` path for detailed work.

The native Diary remains open in a separate Office dialog window. It verifies
the requested date before interpreting the request, shows the detailed
projection there, and returns only an allowlisted status envelope to Word.

Word must not render appointment records, patient or practitioner names, the
submitted request, an unverified draft, raw proofreader findings, or any
provider output.

## 3. Contract separation

Three messages remain distinct:

1. the existing `auth` message carries the current Office-to-Diary session
   token;
2. the unchanged
   `reception.one.word-launch-context.v1` message carries only zero-authority
   date/navigation context; and
3. a new `reception.one.word-companion-request.v1` message carries one bounded
   authored-synthetic request.

The request message must have an exact closed shape, a fresh request id, the
same correlation id and reference date as its launch context, deterministic
planner mode, and explicit false patient-context, appointment-context,
provider, command and write authority.

The returned `reception.one.word-companion-summary.v1` message must also have
an exact closed shape. It may release only:

- request and correlation bindings;
- reference date;
- a projection-family enum;
- result count;
- an allowlisted disposition and summary code;
- deterministic planner and proofreader labels;
- the native-Diary detail-surface identifier; and
- explicit false authority and detail-release flags.

Word derives its visible sentence locally from the summary code and count. No
free text from the Diary is rendered in Word.

## 4. Proofreader and failure behavior

The native Diary builds a summary only after deterministic checks of:

- exact request/launch correlation and date binding;
- deterministic planner mode;
- supported projection family and state;
- non-stale current projection;
- zero appointment-write and command authority;
- allowed result-count bounds; and
- exact summary output fields.

An admitted current projection produces `proofreader_disposition: admit`.
Clarification produces a closed `human_gate` status envelope. A blocked,
malformed, stale, mismatched or unknown result produces `edge_abort`. Neither
failure envelope releases draft or appointment detail.

No retry, provider fallback, deterministic substitution for a selected
provider, or product write is introduced.

## 5. Default-off development boundary

The companion appears only when:

- the taskpane is served from loopback; and
- `reception_one_companion_demo=true` is explicitly present.

The child Diary accepts the request only under the matching loopback capability
flag. The capability marker may appear in the dialog URL; the request,
correlation, names, token and context may not.

The accepted evidence uses authored-synthetic fixtures and
`route_intercepted_browser` labelling. It performs:

- zero provider calls;
- zero credential reads;
- zero database reads or writes;
- zero appointment commands; and
- zero production or deployment actions.

## 6. Acceptance gates

### Gate A - rehydration and revision binding

- Read the active Hybrid, Bureau and API Spine materials.
- Restore AGENTS.md sections 5 and 6.
- Verify the five Git refs and preserve every unrelated worktree change.
- Generate a passing five-source Ariadne receipt.
- Increment Continuity and Compass together for durable programme-state
  changes and validate their exact revision binding and rendered Compass
  report.

### Gate B - request contract

- The request schema is Draft 2020-12 valid and closed.
- Input is one non-empty string of at most 280 characters.
- Request and launch correlation/date bindings match exactly.
- Token, patient/appointment identifiers, provider fields, command payloads
  and unknown fields reject.
- The request is absent from the dialog URL and from durable evidence.

### Gate C - native deterministic handling

- The launch date is verified before request interpretation.
- Only the Standard deterministic planner is available.
- The existing detailed Reception One projection remains in the native Diary.
- The companion request adds no backend or provider call and no appointment
  mutation affordance.
- Duplicate request ids or correlation mismatches fail closed.

### Gate D - returned summary

- The summary schema is valid, closed and cross-field constrained.
- The native proofreader releases only the declared field manifest.
- Word validates the exact summary shape again before rendering.
- Word copy is generated locally from an allowlisted summary code.
- Admitted, clarification and blocked outcomes have deterministic distinct
  dispositions.
- Names, request text, detailed records and drafts do not return to Word.

### Gate E - product and accessibility

- The companion is visually subordinate to the patient banner and detailed
  Diary Bureau.
- The request field does not clip or overlap its action at narrow taskpane
  widths.
- Enter with a modifier or the visible action submits without breaking
  multiline entry.
- Busy, admitted, clarification, blocked and rejected states are announced.
- The existing ordinary Diary and contextual Reception One launch actions
  remain unchanged.

### Gate F - verification

- Use the in-app browser first for rendered taskpane and Diary inspection.
- Run focused schema, message, Word/Diary and existing Hybrid tests.
- Run relevant API Spine tests and the repository-only Ariadne verifier.
- Validate JSON, schemas, Python compilation/static checks and JavaScript
  syntax.
- Synchronise source and published taskpane artifacts.
- Run `git diff --check`.
- Check task-owned process, listener, browser and container residue.

## 7. Closed boundaries

This plan grants no live provider call, API-key or ADC access, patient
identifier authority, appointment identifier authority, product-derived or
historical data, clinical data, database read, database write, appointment
command, confirmation authority, voice, production, deployment or release.

Protected holdout fixture paths and sealed historical Diary material remain
unopened and unused. No URL-carried PHI is permitted.

Any live provider, real data, backend mutation, external account change,
deployment or broader capability requires a new authority decision.

## 8. Candid evidence limit

A pass will prove only that the local provider-free Word shell, typed
cross-window exchange, deterministic native projection and generic validated
return summary work with authored-synthetic route-intercepted fixtures. It will
not prove authenticated Word Online interoperability, provider interpretation,
live backend or database behavior, representative receptionist usability,
clinical safety, production readiness or release readiness.
