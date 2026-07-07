# plan-claude-claude-sprint154-diary-api-header-gap-preflight

| Item | Value |
|---|---|
| From | claude |
| Branch | `claude/current` |
| Kind | Plan/review artifact (plan gate — no runtime wiring) |
| Programme | 2G — diary/API header discipline preflight |
| Prior sprints | 152 (create-proposal minLength deferred-with-guard), 153 (create-proposal client sends 8+ char key) |

## My Understanding

Sprint 153 closed the create-*proposal* header gap: the diary booking modal now sends an
8+ char `Idempotency-Key` on `POST /appointments/proposals/create`. Sprint 154 preflights
the **next** header surface named in the AGENTS.md baton: the **confirm** endpoints
(create-confirm, confirm-bernie, update-confirm, status-confirm, delete-confirm), plus the
plain create-proposal's sibling `proposals/update/{id}` non-blank header question.

**Key finding — the confirm surface is materially different from create-proposal.**
Unlike `/proposals/create` (non-blank-only, deterministic re-evaluation, *no* ledger), every
confirm route normalizes the header with `_normalize_idempotency_key`
(`app/routers/appointments.py:1240`), which **raises `idempotency_key_required` (400) on a
missing/blank key**, and then runs a **real idempotency ledger** with replay / conflict /
in-progress / stale / failed-transient decisions (`_handle_create_confirm_idempotency_decision`,
lines 1251-1283). So the confirm surface has both:
1. a **header-required client gap** (same shape as Sprint 152/153), and
2. an **idempotency-semantics decision** the proposal surface never had — the client should
   reuse a **stable** key across retries of the same confirmation so a retried confirm hits
   *replay* rather than double-writing.

### Backend confirm routes (all require a non-blank key + ledger)

| Route | Line |
|---|---|
| `POST /proposals/create/confirm` | `appointments.py:1286` |
| `POST /proposals/update/confirm` | `appointments.py:1454` |
| `POST /proposals/status-confirm` | `appointments.py:2551` |
| `POST /proposals/delete-confirm` | `appointments.py:4661` |
| `POST /proposals/create/confirm-bernie` | `appointments.py:6932` |

Each takes `idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")` and calls
`_normalize_idempotency_key(...)` before touching the ledger.

### Diary confirm call sites — none currently send the header

| Flow | Call site | Header sent? |
|---|---|---|
| Booking modal — update confirm | `diary.js:7508` | ❌ none |
| Booking modal — create confirm | `diary.js:7571` | ❌ none |
| Reschedule / drag — update confirm | `diary.js:8044` | ❌ none |
| Signed status confirm | `diary.js:8086` | ❌ none |
| Signed delete confirm | `diary.js:8130` | ❌ none |
| Bernie supervised confirm | `diary.js:5169` | ❌ none |
| Bernie tool-intent confirm | `diary.js:1734` | ❌ none |

All post `normalizeApiPath(confirm_endpoint)` via `apiFetch` with only the default headers
(`apiFetch` at `diary.js:2417` injects Content-Type / ngrok-skip / Authorization only). In
live (non-smoke) mode every one of these would **400 `idempotency_key_required`** the moment
a real `confirm_endpoint` is returned. Smoke mode bypasses the network, so smoke tests hide
the gap — exactly as it did for create-proposal in Sprint 152.

## Recommendation

**PROCEED to a client-only header fix for the confirm surface in a follow-on implementation
sprint. Keep backend runtime enforcement exactly as-is (non-blank required; ledger unchanged).**
No route, schema, or ledger change this programme step.

Two defensible options for the implementation sprint; I recommend **Option A**:

- **Option A (recommended) — stable per-proposal confirm key.** Generate one 8+ char key at
  the moment the client stages a confirmation (i.e. per proposal/`confirm_payload`), stash it
  alongside the staged proposal, and send that **same** key on the confirm POST *and on any
  retry of that same confirm*. This is the only option that actually exercises the ledger's
  replay path correctly: a network retry of a submitted confirm returns the prior result
  instead of racing a second write. Reuse the existing `generateClientIdempotencyKey()` helper
  added in Sprint 153 (standalone `crypto.randomUUID` with fallback — already ≥8 chars, not a
  hard `bernieSession` dependency).
- **Option B (weaker) — fresh key per confirm attempt.** Satisfies the non-blank requirement
  but every retry gets a new key, so double-submits become double-writes rather than replays.
  Only acceptable if we accept no retry-dedup. Not recommended given the ledger already exists.

`proposals/update/{id}` (the plain update *proposal*, `appointments.py:1503`) takes **no**
Idempotency-Key header and is deterministic like create-proposal — **leave it out of scope**;
it is not a confirm and needs no key. It is the natural "next proposal-only non-blank surface"
only if a later sprint chooses to standardize proposal headers, but it is not the confirm gap.

## Intended Surface / Boundary (for the implementation sprint)

- **Affected surface:** the 7 diary confirm call sites listed above — add an `Idempotency-Key`
  header to each confirm POST, sourced from a stable per-proposal key.
- **Explicitly NOT changed:** the diary *grid* rendering, booking-modal layout, waiting-area /
  status *cards*, panels, slot stacking, or any visual affordance. This is a header-plumbing
  change on already-existing network calls; no DOM, CSS, or user-visible behaviour changes
  except that live confirms stop 400ing.

## Out of Scope (hard boundaries)

- Do **not** change `_normalize_idempotency_key` / `_normalize_create_proposal_idempotency_key`
  runtime behaviour, add OpenAPI `minLength`, or alter the confirmation ledger semantics
  (replay/conflict/in-progress/stale/failed).
- Do **not** touch raw compatibility writes (`POST /appointments`, `PUT /appointments/{id}`,
  `DELETE /appointments/{id}`, `PATCH /appointments/{id}/status`) — the non-confirm fallback
  branches deliberately stay header-free.
- No providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material.
- No `master` / `handoff/current` movement; plan gate only — no code edited in this artifact.

## Files the Implementation Sprint Would Edit

- `docs/diary/diary.js` — add `headers["Idempotency-Key"] = <stable proposal key>` to the 7
  confirm call sites; thread a stable key through the staged-proposal objects. Bump diary
  `?v=N` cache-bust.
- Tests: extend the API-spine confirm contract tests to assert the header is required and that
  a repeated key replays (backend already covers this); add a static/structural check that each
  diary confirm call site attaches an Idempotency-Key (smoke mode can't cover it).
- No `app/`, OpenAPI, or migration changes.

## Suggested Verification (for Ariadne / implementer)

- `node --check docs/diary/diary.js`
- `pytest tests/test_api_spine_create_proposal_header_alignment.py tests/test_api_spine_create_proposal_idempotency_route_contract.py -q`
- Focused confirm-ledger tests (create/update/status/delete confirm + confirm-bernie
  idempotency), plus any new static "confirm call sites send Idempotency-Key" guard.
- `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q` (note: smoke does
  not exercise the header — a structural check is required for real coverage).

## Risks / Ambiguities

1. **Stable-key sourcing is the real design point.** A per-attempt fresh key satisfies the
   400 but defeats replay dedup. The implementer must persist one key per staged proposal and
   reuse it on retry (Option A). This is the single most important correctness detail.
2. **Multiple staged proposals in one save flow.** The booking modal can chain confirm + a
   follow-on `PATCH /status` (e.g. create then set Arrived, `diary.js:7611`). The status PATCH
   is a raw compatibility write (no key) and stays that way; only the *proposal confirm* leg
   gets a key. Don't accidentally reuse one proposal's key across two different confirmations.
3. **Bernie confirm paths (5169, 1734) share the pattern** but flow through
   `bernieSession`/envelope objects; the stable key must live on the envelope, not a modal
   button dataset. Verify the key survives the Bernie CONFIRMING transition.
4. **Smoke mode masks the gap** — any acceptance evidence must be a static/structural check or
   a live (dev-credential) confirm, not the smoke harness.
5. **No tests were run in this plan gate.** Read-only/static review only; Ariadne should run
   the commands above before and after implementation.

## Boundary Confirmation

This artifact is plan/review only. No production code, tests, OpenAPI, diary UI, taskpane, or
migrations were edited. No runtime behaviour was wired. Recommendation preserves the deliberate
Sprint 152/153 posture: backend stays non-blank-required with the existing ledger; the fix is
purely client-side header emission on the confirm surface.
