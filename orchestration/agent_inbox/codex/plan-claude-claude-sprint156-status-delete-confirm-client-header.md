# plan-claude-claude-sprint156-status-delete-confirm-client-header

| Item | Value |
|---|---|
| From | claude |
| Branch | `claude/current` |
| Kind | Plan/review artifact (plan gate — no runtime wiring) |
| Programme | 2G — diary/API header discipline |
| Prior sprints | 152 (create-proposal minLength deferred-with-guard), 153 (create-proposal client sends 8+ char key), 154 (confirm-surface preflight), 155 (create-confirm client header) |

## Packet note

The referenced task packet
`orchestration/agent_inbox/claude/claude-sprint156-status-delete-confirm-client-header.md`
does **not** exist in this worker tree, and the Sprint 154/155 plans are present only as
**stale untracked** codex artifacts (ignored per instructions). This plan is grounded directly
in the current committed code. Ariadne should confirm the intended scope matches below before
releasing implementation.

## My Understanding

The 152→153→(154 preflight)→155 cadence has been closing the diary header gap one confirm leg
at a time: Sprint 153 fixed the create-**proposal** header; Sprint 155 fixed the
create-**confirm** leg. Sprint 156 takes the **next two confirm legs** named in the 154
preflight table — the **signed status-confirm** and **signed delete-confirm** POSTs. Both
currently send **no** `Idempotency-Key` and would `400 idempotency_key_required` the moment a
real `confirm_endpoint` is returned in live (non-smoke) mode.

### Verified backend enforcement (unchanged, correct as-is)

Both target confirm routes normalize the header with `_normalize_idempotency_key`
(`app/routers/appointments.py:1240`), which **raises `idempotency_key_required` (400) on a
missing/blank key**, then runs the real idempotency ledger (replay/conflict/in-progress/
stale/failed):

| Route | Route decorator | Normalize call |
|---|---|---|
| `POST /proposals/status-confirm` | `appointments.py:2552` | `appointments.py:2561` |
| `POST /proposals/delete-confirm` | `appointments.py:4662` | `appointments.py:4671` |

So — exactly as the confirm surface generally — these legs have **both** a client
header-required gap **and** a ledger-replay semantic that the deterministic proposal surface
never had.

### Verified diary call sites — no header today

| Leg | Helper | POST call site | Header sent? |
|---|---|---|---|
| Signed **status** confirm | `applySignedStatusProposal` (`diary.js:8075`) | `diary.js:8086` | ❌ none |
| Signed **delete** confirm | `applySignedDeleteProposal` (`diary.js:8119`) | `diary.js:8130` | ❌ none |

Both POST `normalizeApiPath(confirmEndpoint)` via `apiFetch` with only default headers
(`method: "POST", body: JSON.stringify(confirmPayload)`). In smoke mode the network is bypassed
(`isSmokeMode` branches at `diary.js:7742` and `8181`-region), so smoke tests **hide** the gap —
exactly as they did for create-proposal in 152 and create-confirm in 155.

### Where the proposals are staged (the sourcing detail)

Unlike the create flow (two Save clicks, key stashed on `saveBtn.dataset`), the status/delete
proposals are **fetched fresh immediately before confirm** and handed straight to the apply
helper. There are several staging paths, and the key must live on **whichever proposal object
actually reaches the confirm helper**:

- Booking-modal **cancel** flow: `POST /proposals/delete/{id}` (`diary.js:7691`) → on 404 falls
  back to `POST /proposals/status/{id}` (`diary.js:7709`) → `applySignedDeleteProposal(proposal, …)`
  (`diary.js:7746`). Note the **404 fallback swaps the proposal object**, so the key must be
  attached *after* the final proposal is chosen, not before.
- Direct **status-change** flow: `POST /proposals/status/{id}` (`diary.js:8197`) →
  `applySignedStatusProposal(appt, proposal, …)` (`diary.js:8255`).

Because there is no separate confirm button/retry click in these flows, the realistic retry is a
**network retry of the confirm POST itself**. A stable key on the staged proposal object makes
that retry hit the ledger's replay path instead of double-writing.

## Recommendation

**PROCEED to a client-only header fix for the status-confirm and delete-confirm legs in a
follow-on implementation sprint. Keep backend runtime enforcement exactly as-is** (non-blank
required; ledger unchanged). No route, schema, OpenAPI, or ledger change.

**Use a stable per-proposal confirm key (Option A, consistent with 154/155).** Generate one
8+ char key at the moment the client stages the confirmation, attach it to the staged proposal
object, and send that **same** key on the confirm POST and on any retry of that same confirm.
Reuse the existing `generateClientIdempotencyKey()` helper (`diary.js:7018`, ≥8 chars,
`crypto.randomUUID` with fallback). A fresh key per attempt satisfies the 400 but turns
double-submits into double-writes; not acceptable given the ledger already exists.

**Sourcing:** attach the key to the proposal object (e.g. a non-serialized field the helper
reads, or pass it as an explicit argument), set **after** the final proposal is selected in the
delete→status 404 fallback. Do not reuse the create-proposal key (153) or create-confirm key
(155); each confirmation gets its own distinct-but-stable key.

## Intended Surface / Boundary (for the implementation sprint)

- **Affected:** the two confirm POSTs at `diary.js:8086` (status-confirm) and `diary.js:8130`
  (delete-confirm) — add an `Idempotency-Key` header sourced from a stable per-proposal confirm
  key threaded through the staging paths (`7691`/`7709`/`8197`).
- **Explicitly NOT changed:** diary grid rendering, booking-modal layout, status/waiting-area
  cards, slot stacking, or any visual affordance. Header-plumbing only; no DOM/CSS/user-visible
  change except that live status/delete confirms stop 400ing.

## Out of Scope (hard boundaries)

- The **other confirm legs** — update-confirm (`diary.js:7508`), reschedule/drag update-confirm
  (`~8035`), Bernie supervised confirm (`5169`), Bernie tool-intent confirm (`1734`), and
  create-confirm (`7562`, owned by Sprint 155) — belong to their own slices, not this one.
- Do **not** change `_normalize_idempotency_key`, add OpenAPI `minLength`, or alter ledger
  semantics.
- Do **not** touch raw compatibility writes — the non-confirm fallback branches stay header-free:
  the status `PATCH /appointments/{id}/status` (`diary.js:8108`) and the delete
  `DELETE /appointments/{id}` (`diary.js:8148`) remain keyless.
- No providers, H15/H-series, memory/RAG/GraphRAG, or historical diary trove material.
- No `master` / `handoff/current` movement; plan gate only — no code edited in this artifact.

## Files the Implementation Sprint Would Edit

- `docs/diary/diary.js` — attach `Idempotency-Key` to the status-confirm (8086) and delete-confirm
  (8130) POSTs from a stable per-proposal confirm key; thread/attach that key on the staging paths
  (including the 404 delete→status swap). Bump diary `?v=N` cache-bust in `docs/diary/diary.html`.
- Tests: a static/structural guard that both confirm call sites attach an `Idempotency-Key`
  (smoke can't cover it). Backend status/delete confirm-ledger required/replay behaviour is
  already covered.
- No `app/`, OpenAPI, or migration changes.

## Suggested Verification (for Ariadne / implementer)

- `node --check docs/diary/diary.js`
- Focused status-confirm and delete-confirm idempotency ledger tests (required + repeated-key
  replay).
- `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q` (smoke does **not**
  exercise the header — a structural check is required for real coverage).

## Risks / Ambiguities

1. **Delete→status 404 fallback swaps the proposal object** — the stable key must be attached to
   the finally-selected proposal, or a status-fallback confirm will still be keyless. This is the
   single most important correctness detail for this sprint.
2. **Stable-key sourcing** — reuse one key per staged confirmation across retries; do not mint a
   fresh key per attempt.
3. **Distinct keys across legs** — the status and delete confirm keys must not collide with the
   create-proposal (153) or create-confirm (155) keys, and each staged proposal gets its own.
4. **Smoke mode masks the gap** — acceptance evidence must be a static/structural check or a live
   dev-credential confirm, not the smoke harness.
5. **No tests were run in this plan gate** — read-only/static review only; run the commands above
   before and after implementation.

## Boundary Confirmation

This artifact is plan/review only. No production code, tests, OpenAPI, diary UI, taskpane, or
migrations were edited; no runtime behaviour was wired. The recommendation preserves the
deliberate Sprint 152/153/154/155 posture: backend stays non-blank-required with the existing
ledger; the fix is purely client-side header emission on the diary status-confirm and
delete-confirm legs.
