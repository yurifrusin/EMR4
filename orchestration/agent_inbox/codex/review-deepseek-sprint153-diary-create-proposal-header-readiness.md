# DeepSeek Flash — Sprint 153 Diary Create-Proposal Header Adversarial Review

| Item | Value |
|---|---|
| Sprint | 153 |
| Worker | DeepSeek Flash |
| Programme | Programme 2G / EMR4 API Spine |
| Review date | 2026-07-07 |
| Files examined | docs/diary/diary.js, app/routers/appointments.py, orchestration/api_spine_appointment_idempotency_create_proposal_minlength_readiness.md, tests/test_api_spine_create_proposal_header_alignment.py, docs/api-spine/openapi/appointment-commands.yaml |
| Status | Integrated by Ariadne |

## Scope

Adversarial lane for Sprint 153's recommendation: preflight/wire the real diary
create-proposal caller to send an 8+ character Idempotency-Key header. I
examine retry semantics, key stability, test gaps, and accidental runtime
minLength or replay-authority creep.

---

## 1. Findings

### 1.1 The Create-Proposal Caller Sends NO Idempotency-Key Header Today

docs/diary/diary.js:7392 posts to proposals/create through apiFetch:

```js
const propRes = await apiFetch(url, {
  method: "POST",
  body: JSON.stringify(payload)
});
```
apiFetch (line 2417) only adds Content-Type, 
ngrok-skip-browser-warning,
and Authorization headers. No call site passes Idempotency-Key via
opts.headers. Every create-proposal API call from diary.js therefore lacks
the header.

Since Sprint 151, app/routers/appointments.py:1037 calls
_normalize_create_proposal_idempotency_key(idempotency_key) which rejects
None/blank with 400 idempotency_key_required. **The current diary.js
create-proposal flow would fail against the current backend if deployed.**

This matches the Sprint 152 readiness document's admission: "the project has
not yet proved that create-proposal clients send a non-blank key."

### 1.2 The Same Gap Affects ALL Proposal and Confirm Endpoints

The gap is broader than just the create-proposal route:

| Endpoint | Backend header binding | diary.js sends header? |
|---|---|---|
| proposals/create (line 1031) | Header(None, alias="Idempotency-Key") → reject None/blank | **No** (line 7392) |
| proposals/update/:id (unwired) | Not bound (known gap) | **No** (line 7980) |
| proposals/delete/:id (unwired) | Not bound (known gap) | **No** (line 7675) |
| proposals/create/confirm-bernie (line 6936) | _normalize_idempotency_key → reject None/blank | **No** (lines 5169, 1734) |
| proposals/create/confirm (line 1290) | _normalize_idempotency_key → reject None/blank | **No** (line 7492, 7555) |
| Status/waiting-area confirm routes | _normalize_idempotency_key → reject None/blank | **No** (line 8070) |
| Delete confirm routes | _normalize_idempotency_key → reject None/blank | **No** (line 8114) |

This means the Sprint 152 posture — "one route wired, 3 unwired" — understates
the gap. All five backend routes that require a non-blank Idempotency-Key
header receive none from diary.js. Tightening just the create-proposal route's
client to send a key would leave the confirm and status/delete routes equally
broken.

The confirm routes may not be production-active yet (Bernie pilot), but the
Sprint 153 scope must acknowledge that wiring create-proposal alone does not
close the broader diary header gap.

### 1.3 Key Generation Options

The existing BernieSession class (line 162) has a getServerRouteIdempotencyKey()
method that uses crypto.randomUUID() (36-character UUID v4):

```js
generateEventId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();       // always 36 chars — satisfies minLength=8
  }
  return "evt-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();
}
```

This is appropriate for Bernie flows where keys are scoped to a session turn.
For the standalone booking modal (line 7389-7399), there is no BernieSession
context, so a different lifecycle applies.

### 1.4 Key Stability and Retry Semantics

**What makes a key stable:**
The same save attempt (same user, same payload, same modal session) must
produce the same key on retry. Different save attempts (different payload,
closed-and-reopened modal) must produce different keys.

**The Bernie path** (getServerRouteIdempotencyKey):
- Stable per kind | sessionId | turnKey | discriminator
- Same instruction + same turn → same key on retry
- New turn → new key
- This lifecycle is correct for the turn-based Bernie conversation

**The standalone booking modal path** (no session context):
- No key lifecycle mechanism exists today
- A naive "generate once per page load" would reuse the same key across
  different save attempts in the same session, silently replaying stale proposals
- A per-call crypto.randomUUID() would make every save look like a new attempt,
  defeating retry idempotency
- The correct lifecycle: create the key when the modal opens (or when the user
  clicks Save), and regenerate when the modal is closed and reopened

**Critical ambiguity:** Should the key be stable across edits within the same
modal open? Consider:
1. User opens the modal, fills in patient/time/reason, clicks Save
2. Proposals/create returns a proposal
3. User edits the time, clicks Save again

If the key is stable per modal open, the second proposals/create call would
get the same Idempotency-Key as the first. The backend's deterministic
re-evaluation model would recompute the proposal because there's no proposal
ledger — but it depends on the _normalize_create_proposal_idempotency_key
implementation. Currently the function only checks non-blank; it does not look
up the key in any ledger, so there's no actual replay protection yet. Adding
ledger-based replay would be a separate change outside Sprint 153 scope.

**Recommendation:** Generate the key once per modal session using
crypto.randomUUID(), stored in a local variable that lives as long as the
modal DOM element exists. Reset on modal close. This gives:
- Same payload + same save button click → same key (retry-safe)
- Different payload in same modal → same key (backend re-evaluates on each call)
- Closed-and-reopened modal → new key (fresh idempotency scope)

---

## 2. Test Gaps

### 2.1 Structural Tests That Should Exist

1. **Header send test**: Prove proposals/create requests from diary.js carry
   a non-blank Idempotency-Key header. A static AST/JS parse test that
   inspects the apiFetch call at line 7392 for headers containing
   "Idempotency-Key".

2. **Key length test**: Prove the generated key is ≥ 8 characters after trimming.
   A unit test on the key generation helper (whether generateEventId or a new
   modal-scoped helper).

3. **Key stability test (same save)**: Prove two identical save attempts from
   the same modal session produce the same key. This requires a stateful
   key-cache test.

4. **Key stability test (new modal)**: Prove closing and reopening the modal
   produces a different key. This tests that the key cache is scoped to the
   modal lifecycle, not the page lifecycle.

5. **Backend guard test**: Prove the existing
   test_fastapi_create_proposal_runtime_gate_is_non_blank_only_until_client_decision
   still holds after the diary.js change — i.e., short non-blank keys are still
   accepted, no minLength enforcement crept in.

6. **No replay ledger test**: Prove the updated client does not accidentally
   create a client-side proposal-replay cache. The key should only be used for
   idempotency on retry, not to store and replay prior proposal results.

### 2.2 Which Test File

The existing guard tests live in
tests/test_api_spine_create_proposal_header_alignment.py. Adding a
diary-js-client header alignment test alongside the existing OpenAPI/FastAPI
alignment tests is the natural home. A separate
tests/test_diary_js_idempotency_key_emission.py would also be acceptable for
diary-JS-specific static checks.

---

## 3. Accidental minLength and Replay-Authority Creep

### 3.1 Do NOT Enforce minLength=8 on the Client

The _normalize_create_proposal_idempotency_key function should remain
non-blank-only. Adding len(normalized) < 8 to the normalize function would
break all future short keys and bypass the Sprint 152 precondition that sibling
proposal routes are reviewed together. The OpenAPI minLength: 8 is the
contract target; the runtime should stay at non-blank until all five
preconditions in the readiness document are met.

### 3.2 Do NOT Use a Server-Assigned Key

The idempotency key must be generated client-side before the first request.
A server-generated key would defeat idempotency: if the network drops the
first request, the retry can't know what key to send.

### 3.3 Do NOT Create a Proposal-Replay Ledger

The idempotency key is for retry-only idempotency (same request → same
response). It must not become a proposal replay ledger where the client stores
proposal results keyed by Idempotency-Key and skips the backend on repeat
saves. The Sprint 152 decision explicitly forbids "no proposal ledger, no
stored proposal replay."

### 3.4 Do NOT Extend to Update/Status/Delete Proposal Routes Automatically

The key generation for create-proposal should be scoped to the create-only
modal. Update, status, and delete proposal routes have different caller paths
(lines 7675, 7980) and different modal lifecycles. Extending the same key to
them without explicit posture review would expand Sprint 153 scope
unintentionally.

### 3.5 Do NOT Use the Bernie Session Key for the Standalone Modal

The BernieSession.getServerRouteIdempotencyKey() is tied to the Bernie
session-turn lifecycle and generates keys via the server route parameter.
Using it from the standalone booking modal would require a running
BernieSession, which does not exist when the user opens the "New Appointment"
modal directly. Separate the key generation helper from the session object,
or create a standalone key utility with its own lifecycle.

---

## 4. Recommended Approach

### Key generation helper

Extract a standalone function from the existing BernieSession.generateEventId():

```js
function generateIdempotencyKey() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "idem-" + Date.now() + "-" + Math.random().toString(36).substring(2, 12);
}
```

crypto.randomUUID() is available in all modern browsers and Office.js runtime
environments (Edge WebView2, Office on the web, desktop Office with modern
WebView). It produces a 36-character RFC 4122 UUID, always ≥ 8 chars.

### Modal-scoped key lifecycle

Add a currentProposalKey variable outside the save handler, reset when the
modal is populated:

```js
let currentProposalKey = null;

function openBookingModal(/* ... */) {
  currentProposalKey = generateIdempotencyKey();
  // ... existing modal setup
}
```

Then pass it in the proposals/create call:

```js
const propRes = await apiFetch(url, {
  method: "POST",
  headers: { "Idempotency-Key": currentProposalKey },
  body: JSON.stringify(payload)
});
```

### Bernie flow

The Bernie flow already calls getServerRouteIdempotencyKey(). That method's
return value should be added to the confirm_endpoint call's headers, not
only to the body server_session_idempotency_key field. This covers the
confirm routes (gap 1.2).

---

## 5. Verdict

**No blockers to Sprint 153 proceeding**, with the following actionable
guidance:

1. **Must send a non-blank key** from the standalone booking modal. The
   crypto.randomUUID() generator is proven and always produces > 8 chars.

2. **Must scope the key to the modal lifecycle** — same modal open = same key
   on retry; close/reopen = fresh key.

3. **Must NOT enforce minLength=8 on the backend** as part of this sprint.
   Keep _normalize_create_proposal_idempotency_key non-blank-only.

4. **Must NOT create a client-side proposal replay cache.**

5. **Must acknowledge the broader header gap** — all confirm and proposal
   routes also lack headers from diary.js. This sprint wires only
   create-proposal, but the closeout should name the remaining surfaces.

6. **Must add structural tests**: header emission, key length, key stability
   on retry, key stability on modal reopen, and backend guard preservation.

---

## Dissent / Risks

- **Risk of scope creep:** Wiring Idempotency-Key on the standalone modal
  opens the question "what about update/status/delete proposal routes?" The
  Sprint 152 decision explicitly defers those. Ariadne must resist the
  temptation to wire all routes in one sprint.

- **Risk of key reuse across unrelated saves:** A long-lived page-scoped key
  (not modal-scoped) would silently replay stale proposal results. The modal
  lifecycle scoping in section 4 prevents this.

- **Risk of Office.js crypto availability:** crypto.randomUUID() is available
  in the Edge WebView2 that Office.js uses (Office 2019+ online and desktop).
  The fallback to "idem-" + Date.now() + Math.random() in the helper
  preserves behavior in older hosts, though the fallback is not deterministic
  for retry and should be a warning flag during testing.

- **Risk of confirm-route gap being ignored:** If only the create-proposal
  caller is wired but the Bernie confirm callers (lines 1734, 5169) remain
  headerless, the Bernie pilot flow will also fail against confirm routes.
  Sprint 153 should include the Bernie confirm path key emission or explicitly
  defer it.

---

## Files changed (this review only)

- orchestration/agent_inbox/codex/review-deepseek-sprint153-diary-create-proposal-header-readiness.md (created)

## Verification run

- Static inspection of all apiFetch call sites in docs/diary/diary.js
  (38 calls, zero with Idempotency-Key header)
- Static inspection of backend idempotency normalizers in app/routers/appointments.py
  (both _normalize_create_proposal_idempotency_key and _normalize_idempotency_key)
- Cross-referenced Sprint 152 readiness decision document
- Cross-referenced existing guard tests

## Remaining risks

See dissent section above. The primary risk is scope creep — this sprint should
wire create-proposal only and name the remaining surfaces, not attempt to wire
all proposal and confirm routes at once.

