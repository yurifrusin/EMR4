# plan-claude-claude-r29-native-action-grammar-foundation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/native-action-grammar-foundation` |
| Source Task | `claude-r29-native-action-grammar-foundation` |
| Status | pending_plan_review |
| Created | 2026-07-06 15:27 +1000 |
| Source HEAD | `9d759599` |

## Plan Summary

Add a pure, additive, versioned DiaryActionVerb grammar (create/move/resize/cancel/status_change/check_in/waiting_area_move/link_patient/slot_search/explain_schedule/handoff) as a backend/domain contract table binding each verb to tier, mutation class, staff-confirmation requirement, and existing DiaryConfirmAction/capability. No routes, no write-authority, no UI, no envelope-field change.

## My Understanding

Sprint +1 of Fable's grammar-before-labels ordering. Diary domain already has envelopes (free-string action_name), a capability registry, and 5 DiaryConfirmActions, but no canonical typed verb vocabulary that future semantic labelling can map onto. R29 fills exactly that gap as a scaffold, mirroring the capability-registry skeleton posture.

## Intended Surface / Boundary

New app/services/diary/action_grammar.py plus a bernie facade and package exports, and tests/test_diary_action_grammar.py. No HTTP or visual surface. Must NOT change: diary grid UI, taskpane, command centre, appointment proposal/confirm routes, confirm-evidence gate, envelopes.action_name behaviour, confirm_actions.py, capability rows, manifest golden output, migrations, provider code, H-series fixtures/docs.

## Out Of Scope

Write-authority/gate changes; new/renamed endpoints; wiring grammar into live dispatch or the manifest prompt; making action_name a strict enum; adding waiting-area/check-in confirm actions; frontend; migrations; provider calls; H15 semantic fixtures; raw local_data; ignored JSON; master/handoff movement.

## Files I Expect To Edit

NEW app/services/diary/action_grammar.py (DiaryActionVerb enum, DiaryActionVerbClass, DiaryActionVerbDescriptor, DIARY_ACTION_GRAMMAR table, GRAMMAR_SCHEMA_VERSION=diary.action_grammar.v1, lookup + assert_grammar_consistency helpers, non-breaking action_verb_for_envelope bridge); app/services/diary/__init__.py exports; NEW app/services/bernie/action_grammar.py facade; app/services/bernie/__init__.py exports; NEW tests/test_diary_action_grammar.py. capability_manifest.py NOT edited.

## Implementation Steps

1 Define DiaryActionVerb superset enum. 2 Define DiaryActionVerbClass (read_only/propose/confirm/meta) + mutating bool. 3 Define frozen DiaryActionVerbDescriptor and DIARY_ACTION_GRAMMAR binding implemented verbs to existing DiaryConfirmAction (create->staff_create/bernie_create, status_change->status, cancel->delete, move/resize->update) and marking check_in/waiting_area_move/link_patient implemented=False,confirm_action=None. 4 Lookup helpers + assert_grammar_consistency cross-checking DIARY_CONFIRM_ACTIONS and BERNIE_CAPABILITY_REGISTRY and enforcing mutating=>requires_staff_confirmation. 5 Optional non-breaking action_verb_for_envelope helper. 6 Facades + exports. 7 Pure unit tests. 8 Verify + submit.

## Visual / Behavioural Acceptance Checks

git diff --name-only lists only the 5 files; no docs/taskpane/command-centre/router change; from app.services.bernie import DiaryActionVerb works and is identical to diary-package objects; assert_grammar_consistency passes; mutating verbs cannot exist without staff confirmation; schema_version pinned diary.action_grammar.v1. pytest tests/test_diary_action_grammar.py -q plus regression on test_diary_action_envelopes/boundary_contracts/confirm_actions/capability_manifest/bernie_domain_package/rehome_compatibility, then full pytest tests -q.

## Risks / Ambiguities

move/resize both map to update confirm (flag: single reschedule verb vs two?); waiting-area/check-in have proposal but no confirm route so recorded implemented=False; version pinned v1 additive only; deliberate deferral of envelope strictness and manifest wiring to avoid breaking free-string callers and golden tests; module is a not-yet-consumed scaffold, the anchor for Sprint+2 replay harness and Sprint+3 H22 gate packet.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
