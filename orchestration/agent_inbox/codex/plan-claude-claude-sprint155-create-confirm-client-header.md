# plan-claude-claude-sprint155-create-confirm-client-header

| Item | Value |
|---|---|
| From | claude |
| Branch | `claude/current` |
| Kind | Plan/review artifact (plan gate — no runtime wiring) |
| Programme | 2G — diary/API header discipline |
| Prior sprints | 152 (create-proposal minLength deferred-with-guard), 153 (create-proposal client sends 8+ char key), 154 (confirm-surface preflight) |

## Packet note

The referenced task packet
`orchestration/agent_inbox/claude/claude-sprint155-create-confirm-client-header.md`
does **not** exist in this worker tree, and the Sprint 154 preflight plan is present only as a
**stale untracked** artifact (ignored per instructions). This plan is therefore grounded directly
in the current committed code, not in either of those. Ariadne should confirm the intended scope
matches below before releasing implementation.

## My Understanding

Sprint 153 closed the create-**proposal** header gap (booking modal now sends an 8+ char
`Idempotency-Key` on `POST /appointments/proposals/create` — `diary.js:7400-7405`, helper
`generateClientIdempotencyKey()` at `diary.js:7018`). Sprint 155 takes the **first confirm-leg
slice**: the diary booking modal's **create-confirm** POST, which currently sends **no**
`Idempotency-Key` and would 400 the moment a real `confirm_endpoint` is returned in live mode.

### Verified backend enforcement (unchanged, correct as-is)

`_normalize_idempotency_key` (`app/routers/appointments.py:1240`) strips the header and
**raises `idempotency_key_required` (400)** on missing/blank (`_idempotency_key_required_error`,
line 1223). Every confirm route calls it before touching the ledger — create-confirm at
`appointments.py:1296`, then runs the real idempotency ledger
(`_handle_create_confirm_idempotency_decision`, line 1251) with replay/conflict/in-progress/
stale/failed decisions. So confirm has **both** a client header-required gap **and** a
ledger-replay semantic that the deterministic proposal surface never had.

### Verified diary create-confirm call site — no header today

| Leg | Call site | Header sent? |
|---|---|---|
| Booking modal — **create** confirm | `docs/diary/diary.js:7562-7574` (POST at 7571) | ❌ none |

The POST at `diary.js:7571` sends `method: "POST", body: JSON.stringify(confirmPayload)` with only
`apiFetch`'s default headers. In smoke mode the network is bypassed (`isSmokeMode` branch at
`diary.js:7543`), so smoke tests **hide** the gap — exactly as they did for create-proposal in 152.

## Recommendation

**PROCEED to a client-only header fix for the create-confirm leg in a follow-on implementation
sprint. Keep backend runtime enforcement exactly as-is** (non-blank required; ledger unchanged).
No route, schema, OpenAPI, or ledger change.

**Use a stable per-proposal confirm key (Option A from the 154 preflight).** Generate one 8+ char
key when the client stages the create confirmation and reuse the **same** key on the confirm POST
and on any retry of that same confirm. This is the only option that exercises the ledger's replay
path correctly — a network retry returns the prior result instead of racing a second write. Reuse
`generateClientIdempotencyKey()` (already ≥8 chars, `crypto.randomUUID` with fallback). A fresh
key per attempt satisfies the 400 but turns double-submits into double-writes; not acceptable given
the ledger already exists.

**Sourcing detail (the real design point):** the create leg reaches confirm on the *second* Save
click (`isConfirmed` path). The Sprint 153 create-**proposal** key lives on
`saveBtn.dataset.idempotencyKey` and is deliberately cleared by `resetProposalConfirmation()`
(`diary.js:7031`). The confirm key must be a **distinct** value from the proposal key but equally
stable across confirm retries — stash it on the staged proposal/`confirm_payload` object (or a
second `saveBtn.dataset.confirmIdempotencyKey`) so a retried confirm reuses it, and clear it in the
same reset path once the booking completes.

## Intended Surface / Boundary (for the implementation sprint)

- **Affected:** the single create-confirm POST at `diary.js:7571` — add an `Idempotency-Key` header
  sourced from a stable per-proposal confirm key.
- **Explicitly NOT changed:** diary grid rendering, booking-modal layout, status/waiting-area
  cards, slot stacking, or any visual affordance. Header-plumbing only; no DOM/CSS/user-visible
  change except that live create-confirms stop 400ing.

## Out of Scope (hard boundaries)

- The **other confirm legs** (update-confirm `diary.js:7508`, reschedule/drag update-confirm
  ~`8035`, status-confirm ~`8077`, delete-confirm ~`8121`, Bernie confirm `5169`/`1734`) — these
  are the 154 preflight's remaining surfaces and belong to **later** slices, not this one. Keep this
  sprint to the create leg unless Ariadne widens scope explicitly.
- Do **not** change `_normalize_idempotency_key` /
  `_normalize_create_proposal_idempotency_key`, add OpenAPI `minLength`, or alter ledger semantics.
- Do **not** touch raw compatibility writes (`POST /appointments`, `PUT /appointments/{id}`,
  `PATCH /appointments/{id}/status`) — the non-confirm fallback branches stay header-free (e.g. the
  status PATCH at `diary.js:7532` remains keyless).
- No providers, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material.
- No `master` / `handoff/current` movement; plan gate only — no code edited in this artifact.

## Files the Implementation Sprint Would Edit

- `docs/diary/diary.js` — attach `Idempotency-Key` to the create-confirm POST (7571) from a stable
  per-proposal confirm key; thread/clear that key alongside the staged proposal. Bump diary
  `?v=N` cache-bust in `docs/diary/diary.html` (currently `v=175`).
- Tests: a static/structural guard that the create-confirm call site attaches an
  `Idempotency-Key` (smoke can't cover it). Backend confirm-ledger required/replay behaviour is
  already covered.
- No `app/`, OpenAPI, or migration changes.

## Suggested Verification (for Ariadne / implementer)

- `node --check docs/diary/diary.js`
- `pytest tests/test_api_spine_create_proposal_header_alignment.py tests/test_api_spine_create_proposal_idempotency_route_contract.py -q`
- Focused create-confirm idempotency ledger tests (required + repeated-key replay).
- `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q` (smoke does **not**
  exercise the header — a structural check is required for real coverage).

## Risks / Ambiguities

1. **Stable-key sourcing is the correctness crux** — reuse one key per staged create confirmation
   across retries; do not mint a fresh key per attempt.
2. **Two distinct keys in one flow** — the create-proposal key (153) and the create-confirm key
   (155) must not collide or be reused across each other; both should be cleared on booking
   completion / `resetProposalConfirmation()`.
3. **Smoke mode masks the gap** — acceptance evidence must be a static/structural check or a live
   dev-credential confirm, not the smoke harness.
4. **Scope creep to the other confirm legs** — tempting since they share the pattern, but keeping
   this to the create leg matches the incremental 152→153→155 cadence and limits blast radius.
5. **No tests were run in this plan gate** — read-only/static review only; run the commands above
   before and after implementation.

## Boundary Confirmation

This artifact is plan/review only. No production code, tests, OpenAPI, diary UI, taskpane, or
migrations were edited; no runtime behaviour was wired. The recommendation preserves the deliberate
Sprint 152/153/154 posture: backend stays non-blank-required with the existing ledger; the fix is
purely client-side header emission on the diary create-confirm leg.
