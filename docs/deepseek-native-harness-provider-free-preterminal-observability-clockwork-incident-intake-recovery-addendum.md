# Preterminal observability clockwork incident-intake recovery addendum

Date: 2026-08-20

Timestamp: 2026-08-20T07:02:03.1346660+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`de96a7e4d75b53f1dd38495b5bdda16fd8f326f6`

Parent operation:
`deepseek-native-harness-provider-free-preterminal-observability-corrected-veto-recovery`

## Reason and objective

The corrected Gemini veto passed, but the earlier review was rejected because
its packet asserted 137 tests while the exact command contained 85. AGENTS.md
requires a qualifying rejected review to enter the closed agent-error register
before the corrected attempt is accepted. The live clockwork currently owns
the register surface but permits only byte-preserving register closeouts, so a
manual register update would violate the accepted sole-writer boundary.

Add the narrowest clockwork-owned incident-intake gear: a backward-compatible
clean-closeout intent version may contain a bounded semantic incident
observation; the clockwork alone derives the next incident identifier, stable
attempt identifier, origin, peer links, closed status, register revision,
source cutoff and pattern report, then publishes those bytes in the same
pointer-last generation as Continuity, Compass, latch and baton.

## Exact owned surface

- `orchestration_harness/governance_clockwork_tick.py`;
- `scripts/ariadne_agent_error_register.py` only to expose its existing
  pattern reducer as a pure in-memory function;
- `tests/test_ariadne_governance_clockwork_tick.py` and the narrowest exact
  agent-error-register compatibility assertions required by the derived
  projection;
- this addendum, its threat delta, exact review evidence and current closeout
  intent.

Existing intent v1, blocked, user-decision and checkpoint transitions remain
byte-compatible. Historical generations and the current canonical register
remain unchanged until a successful `--publish`.

## Acceptance

1. Intent v1 still validates and preserves register/pattern bytes.
2. Intent v2 rejects caller-authored incident IDs, register revisions, counts,
   origins, peer IDs, status and pattern aggregates.
3. V2 validates every evidence path, closed enum and correction object using
   the canonical register schema before generation.
4. One semantic observation deterministically yields the exact next AER ID,
   one stable attempt ID, the schema-defined origin, empty peer links, closed
   status, revision +1 and source cutoff no earlier than the observation.
5. The pattern report is generated from exactly the prospective register by
   the existing pure reducer; register and pattern digests are generation-bound.
6. The baton register row is derived from the prospective register and a
   caller-supplied bounded semantic summary; no count or revision is copied by
   the caller.
7. Check remains read-only, publish remains pointer-last and injected-failure
   rollback stays byte-exact across all ten canonical surfaces.
8. The current rejected-review incident is published only with the parent
   closeout after deterministic tests and one fresh independent review of the
   clockwork change.

## Parallelism assessment

- **DeepSeek:** `declined`, negative leverage. The defect is in the canonical
  clockwork writer and the native/model lane remains closed.
- **Gemini:** `reserved`, required independent leverage after deterministic
  admission because the patch changes governance publication semantics.
- **Native subagents:** `declined`, negative leverage. Developer policy bars
  proactive delegation and the single canonical writer plus generation replay
  form a serial evidence chain.

No native Harness, DeepSeek model, broker, product/API/configuration/client,
ordinary-practice enablement, patient/product/clinical data, Docker/database,
production, deployment, release, Pages, protected evidence or protected-ref
movement is authorised. Preserve `docs/branding/` and every unrelated
untracked file; stage explicit paths only.
