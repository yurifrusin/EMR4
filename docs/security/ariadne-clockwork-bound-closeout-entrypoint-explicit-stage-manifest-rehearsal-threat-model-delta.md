# Governance clockwork bound closeout entrypoint and explicit-stage manifest rehearsal — threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T21:18:20.9899474+10:00 (Australia/Brisbane)

Status: `frozen`

## Scope

This delta covers one provider-free local closeout driver, its nonpublishing
rehearsal and its machine-derived explicit-stage manifest. Product, data,
provider, runtime, deployment and protected integration remain closed.

## Threats and controls

| Threat | Control |
|---|---|
| A caller launches with system Python and the semantic gate rejects or runs under the wrong environment | The driver resolves `.venv/Scripts/python.exe`, asks that child to report `sys.executable`, and rejects any non-exact attestation before the tick. |
| A shortened or manually typed Git ID enters an evidence binding | The driver obtains HEAD from `git rev-parse --verify HEAD`, requires the exact 40-lower-hex result and accepts no caller-authored source ID. |
| Rehearsal accidentally publishes canonical state | Rehearsal invokes only the tick's verification-only mode; acceptance requires zero publication, zero lease advance and unchanged canonical pointer bytes. |
| A publication command returns before live state is validated | The existing publisher returns only from `validate_tick_live_state`; the driver validates the committed transaction facts and captures the returned source, generation, lease and status. Injected tests prove rejection of noncommitted substitutes. |
| Automation removes phase-sensitive tests | The five accepted postpublication files are a closed constant and run after the tick result; no skip or deselection option is accepted. |
| Tests mutate tracked files | Capture exact tracked status before and after the retained suite and reject any difference. |
| A path typo or broad staging command includes the wrong file | Derive allowed paths from the admitted intent and clockwork contract, intersect with NUL-delimited Git inventories, reject unexpected tracked paths and emit JSON only. The driver contains no Git-index mutation command. |
| Existing unrelated untracked files become a failure or are swept into the manifest | Count and exclude unallowlisted untracked paths; explicitly forbid `docs/branding/`; never delete, move or stage them. |
| A generated output path escapes the repository | Derive fixed sibling filenames from a validated repository-local `closeout-intent.json`; resolve and enforce repository containment. |
| A future live mode is mistaken for authority in this rehearsal | The plan and result label live invocation unexercised and unauthorised; canonical closeout uses the established writer. |

## Claim boundary

This controls local orchestration ergonomics only. It proves no live-driver
adoption, worker or Harness reliability, product behavior, provider safety,
production readiness, deployment, release or protected integration.
