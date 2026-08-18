# Threat-model delta: provider-free clockwork governance projection consolidation repair

Date: 2026-08-19
Timestamp: 2026-08-19T08:41:24.0023767+10:00 (Australia/Brisbane)
Scope: provider-free private-shadow governance projections only

## Added assets

- One typed semantic observation bound to an acknowledged clock tip.
- Prospective incident-register, recurrence, command, Continuity, Compass, Current Baton and latch projections.
- An immutable thirteen-rerun replay ledger and maintained-surface retirement map.
- Separate construction, steady-state and break-even readings.

These contain repository-local orchestration facts only. They contain no prompt, reasoning, secret, credential, product payload, patient, practice, health, clinical, protected-holdout or historical-diary data.

## Threats and required controls

| Threat | Control | Required evidence |
|---|---|---|
| A short/stale Git OID or remembered count enters a closeout | Reducer resolves Git and derives all identifiers, revisions and counts; public observation schema has no such fields | Exact-key rejection and zero caller-derived fields |
| Category and origin diverge | One closed `failure_class` maps atomically to both values | Every configured class passes; supplied category/origin rejects |
| Attempt identity spans different actor/resource envelopes | Attempt ID is derived from the full actor/resource/tick tuple | Split-resource and reused-attempt probes reject |
| Peer links survive attempt regrouping | Peer set is reduced from final derived attempt groups | Stale/cross-attempt peer probes reject |
| A command omits its required output or carries a wildcard/shell expansion | Closed command catalogue emits executable plus argument array and required output; no raw command field exists | Output-omission, wildcard and shell-string probes reject |
| Register/Continuity/latch vocabularies are confused | One factual gate result maps through separate closed vocabulary tables | `revision_required`-as-Continuity and `complete`-with-attention probes reject |
| Baton/count/recurrence/latch projections drift independently | All prospective views reduce from one typed state and validate against one digest | Four stale-projection probes reject in one pass; no partial publication |
| Next-work boundary loses a still-applicable constraint | Next-work projection is selected from a closed boundary set and binds every inherited constraint | Mutable-current-fixture omission probe rejects |
| The repair hides its own cost | Construction retries derive from the live latch/register delta and remain separate from steady-state replay | Evidence reports sunk, repair, steady-state and both break-even values |
| A wrapper adds a second control plane instead of shrinking one | Every legacy maintained binding needs one generated owner and an explicit future-retirement disposition | At least 50% maintained-surface reduction and zero unmapped/dual-live bindings |
| Hostile coverage is relabelled as efficiency | All thirteen rerun probes and predecessor gauge coverage remain immutable denominators | 13/13 and 9/9 coverage with no denominator override |
| Private projections silently become canonical | Output path is a non-current private-shadow sibling and canonical controls remain unchanged | Atomic rollback tests, zero live adoption and protected-ref readback |

## Residual risk

The rehearsal cannot prove safe live migration, simultaneous canonical-file replacement, operational adoption, or native-Harness/provider behaviour. Narrative quality and acceptance judgment remain human responsibilities. Even a pass authorises only a separately reviewable adoption/retirement proposal; it does not replace current governance controls.
