"""Raisa recovery admission adapter and read-only installed-core assessment.

This route reads a fixed set of ordinary files. It never imports candidate code,
discovers settings, loads historical policy, or executes a commit/push. Its
distinct decision establishes policy eligibility only. The reviewed publisher
must also establish complete scope, source/review authority, leases and readback.
An expected binding digest comes from the trusted caller, never the candidate.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from orchestration_harness import configuration_core, raisa_policy, trusted_git

PROFILE = raisa_policy.G1B_PROFILE
TASK_CLASS = "g1b_persistence_recovery_lease_and_narrative"
REQUEST_VERSION = "ariadne.bounded_g1b_request.v1"
BINDING_VERSION = "ariadne.bounded_g1b_binding.v2"
SCOPE_VERSION = "ariadne.g1b_completion_scope.v1"
SCOPE_PATH = "orchestration/programme/g1b-completion-scope.json"
STATE = "orchestration/programme/current-state.json"
GATES = "orchestration/programme/gates.yaml"
OVERLAY = "orchestration/harness_settings/programme_recovery.yaml"
PROJECT = "orchestration/harness_settings/project.yaml"
CONTINUATION = "orchestration/harness_settings/autonomous_continuation.yaml"
LATCH = "orchestration/continuity/ariadne-active-operation-latch/current.json"
G1B1_SURFACE = "orchestration/programme/g1b1-accepted-surface.yaml"
JOURNAL_SCOPE = "orchestration/programme/g1b2-journal-replay-scope.yaml"
AGENTS = "AGENTS.md"
RECOVERY_REF = "refs/heads/codex/raisa-ariadne-recovery-g0"
REMOTE_URL = "https://github.com/yurifrusin/emr4"
PROTECTED = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
JOURNAL_COMMIT = "723e42fc70841b0e8ceed7fd5a2f63e0eecd573e"
JOURNAL_PARENT = "d512399aa52fdc1d43b68e3e5117d3142037671d"
JOURNAL_TREE = "7bcbaa456c508ccfedb386893e64784f69734e7a"
OLD_PROFILE = "G1B.2_PURE_JOURNAL_REPLAY_KERNEL_ACTIVE"
OLD_PREAMBLE = "Gate G1B.2 is active only for the pure versioned journal and deterministic replay kernel"
NEW_PREAMBLE = raisa_policy.G1B_PREAMBLE

KERNEL_PINS = {
    "orchestration_harness/clockwork_journal.py": "98686ae95c8477511e0ebee0170e0232ee39c5270b14d1cdcba74def11791b6c",
    "orchestration_harness/clockwork_state.py": "6e54a4414c3fb22a46caa6b471749d31a4e9fcc356f90f011e9fd8d17a31d052",
    "tests/test_clockwork_journal.py": "53f9daef9c2051e2422924f179a23bd953dbc3cceedbfe956bf3dd4744620126",
}
BASELINE_PINS = {
    STATE: "0410f8aff9c633d704765f4d454893f8d48ff42c49108f368eef36f4bdbd3232",
    GATES: "02a1fea8f12b26a892b2d035671a5e8cd689d2ca8d843547e5c2412a42030339",
    OVERLAY: "a9c1b1d7ad601ec26b41ea62efcee9062fa8f4273511dc281a777b9e207207bb",
    AGENTS: "7b56fe9c15d17db44cdfc3cf8b7b79f480bd30766dc3baae4151469c9a466715",
}
FROZEN_PINS = {
    G1B1_SURFACE: "2d189829518f3525b3da34a10931985f3e1e48e4fd6a08346efdb6ad9112c3a8",
    PROJECT: "a3835edf35116088ef1808e2590c0b7ab837171ab40457b51f96f8519a235f84",
    CONTINUATION: "0a205c109383ed64c6c87435b259bbdd5a1989f834de6f505385bbf6c52bbd0d",
    LATCH: "f1bc5b3545293834365b7992882ebc09e6c83ccd63687c28fd443ac049e2e437",
    JOURNAL_SCOPE: "8c3ed98d0111e5e9314a7e20561235dc6a6f6f5e434ead6c45ae7f60e3033779",
    **KERNEL_PINS,
}
EVIDENCE_PINS = {
    "admission/review-subject.json": "c52012b8bacd02c9c0913d181eeac1b0ab355bf9a6d66b502e2a72921c87ca9e",
    "admission/independent-review-transcription.md": "96adb86f86a95006c92c7fa2e6b6d90102c1e24480937563e6581e6bfb3b17b4",
    "admission/verification-summary.json": "37659de2dc169592cdc777fb13f9d6547d6b75235249d806e19394e97e82a11c",
    "admission/six-tests.stdout.json": "6ccc59097a279282fe9d75bdf262687421b89f5948a15a4cd3e2d44f7883eaa6",
    "admission/exhaustive.stdout.json": "949dfa4f66961abecd92b60d16cc0c52ee525d6199ebda86d00689187d6f2fca",
    "publication/commit-receipt.json": "7d772cb914988e85bb4d98741c880718047b8e684880f12d4fb970281bd6ff75",
    "publication/push-receipt.json": "dc81592c371eb707e23a2be582e7de191e385162124a2ad27d52a642028c3f93",
    "publication/post-publication-readback.json": "128bdab8ca9c3fa244de51bc0797c4b15c96255e1d7a7d932a330de2e68896f4",
    "current-control-evidence.json": "80b688756a13dabf93ee60debbf7cee1a766d88b20260370f199ae49ccd50f8f",
}
SOURCE_PATHS = frozenset({
    "orchestration_harness/configuration_core.py",
    "orchestration_harness/raisa_policy.py",
    "orchestration_harness/bounded_g1b.py",
    "orchestration_harness/trusted_git.py",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_recovery_preflight.py",
})
INPUT_PATHS = frozenset({STATE, GATES, OVERLAY, PROJECT, CONTINUATION, LATCH,
                         G1B1_SURFACE, JOURNAL_SCOPE, AGENTS, SCOPE_PATH, *KERNEL_PINS})
TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, SCOPE_PATH})
COMPLETION_PATHS = frozenset({"orchestration_harness/clockwork_persistence.py",
                              "tests/test_clockwork_persistence.py"})
CRITERIA = (
    "versioned_journal_entry_vocabulary",
    "fixed_genesis_and_exact_previous_digest_chain",
    "canonical_entry_bytes_and_sha256_digest",
    "replay_rederives_every_result_with_accepted_G1B1_reducer",
    "closed_tamper_gap_reorder_mismatch_and_type_rejection",
    "pure_no_filesystem_git_process_network_database_clock_randomness_or_existing_clockwork_imports",
)
FORBIDDEN = frozenset({"provider_invocation", "integration", "protected_ref_movement",
                       "deployment", "pages", "real_data_access", "product_behavior_change",
                       "dependency_change", "migration_change", "existing_clockwork_runtime_mutation",
                       "autonomous_worker_dispatch"})
EFFECTS = frozenset({"repository_read", "control_plane_edit", "task_branch_commit", "task_branch_push"})
LIMITS = ("policy eligibility is not publication authority", "no complete physical worktree attestation",
          "no full-suite or whole-loader acceptance", "G1B completion and G1C remain unaccepted")

G1C_PROFILE = raisa_policy.G1C_PROFILE
G1C_TASK = "g1c_finite_budgets_and_progress_governor"
G1C_PREAMBLE = raisa_policy.G1C_PREAMBLE
G1C_SCOPE = "orchestration/programme/g1c-governor-scope.json"
COST = "orchestration/harness_settings/cost_controls.yaml"
COST_PIN = "9ed7844a22dfafa33c064cb1c26ca62779cc08f2195b93c3c7f436417cb0473f"
PROFILE_PREAMBLES = raisa_policy.BOUNDED_PROFILE_PREAMBLES
BOUNDED_SCOPE_PATHS = frozenset({SCOPE_PATH, G1C_SCOPE})
G1B_BASELINE_PINS = {
    AGENTS: "5901c286901ca6bf49ccee71e6d6e7419db177226c19aaf634d55ed6d3fe90da",
    STATE: "6147906ffb7e20b4f070d5ffbfa0c223d6f50c4a5814be5d35d218ceca6b0a87",
    GATES: "cdc87526fe78910f81735e55b4e8922f80b9a2ed34af3d386f657b8e33589f39",
    OVERLAY: "37b99386aeb07c34d10c7ea1a6fac9c73606a4db88e5329c088d583deb4a6f65",
    SCOPE_PATH: "023a9307fb4b02e44136cece07ad697f0cf6c952e82bbcc162a7b7c57eb4814d",
}
PERSISTENCE_PUBLICATION = {
    "commit": "9a1a2a44cfd7f083398671cc7a44d5f7c16c8d5a",
    "parent": "257b5e9fb7839b114b34712161fd4bf85d5e3d9f",
    "tree": "e46587bf13ee83c2c0e81b7931b2f3eb1fbdbb1a",
}
PERSISTENCE_PINS = {
    "orchestration_harness/clockwork_persistence.py": "b9f1db70f0cad685253522ce3a732b8b8265da140560d9fc5a47b3d778a18166",
    "tests/test_clockwork_persistence.py": "cbdc38a0f7b89af0d91b630b18e333968c9b9825234e5fac2db8ed664f52c0c6",
}
G1B_EVIDENCE_PINS = {
    **EVIDENCE_PINS,
    "g1b-evidence/implementation-review.json": "bd786906c98380b840dbae08f73a0d48cc9d965436be81f6b0b7127c3fffc2e9",
    "g1b-evidence/windows-test-2.stdout.json": "406b254d9d09a0cf335935a15ee666098f794be85107fd1402dec51b1d818da1",
    "g1b-evidence/fresh-readback.json": "3d7f0b55d71fe7455542df866b1fa0bcaf6484a5495be1cbd8d8176b5d4464ba",
    "g1b-evidence/candidate-manifest-v2.json": "705345c96b7be2ecd277d321f3ce5bd0300a2bef41caa076903c68a4bcf8442a",
}
G1B_CRITERIA = ("closed_state_machine_implemented", "append_only_versioned_event_journal",
                "invalid_transition_rejected", "crash_recovery_deterministic", "stale_lease_cannot_commit",
                "narrative_generated_from_structured_state")
G1C_CRITERIA = ("finite_retry_cost_token_and_wall_clock_budgets", "global_red_enters_repair_only_mode",
                "no_progress_stops_or_quarantines", "wip_and_stack_limits_enforced",
                "high_risk_human_authority_enforced", "structured_stop_reason")
G1C_INPUT_PATHS = INPUT_PATHS | {G1C_SCOPE, COST}
G1C_TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G1C_SCOPE})
GOVERNOR_PATHS = frozenset({"orchestration_harness/clockwork_governor.py",
                           "orchestration_harness/clockwork_persistence.py", "tests/test_clockwork_governor.py"})
G1C_LIMITS = ("policy eligibility is not publication authority", "no complete physical worktree attestation",
              "no full-suite or whole-loader acceptance", "G1C implementation and operational multi-task control remain unaccepted",
              "providers, existing writers, worker dispatch, product work and protected refs remain closed")
OPERATION_PATHS = {"accept_journal": TRANSITION_PATHS, "complete_g1b": COMPLETION_PATHS,
                   "accept_g1b": G1C_TRANSITION_PATHS, "implement_g1c": GOVERNOR_PATHS}

G1D_PROFILE = raisa_policy.G1D_PROFILE
G1D_TASK = "g1d_observed_provenance_and_independent_verification"
G1D_PREAMBLE = raisa_policy.G1D_PREAMBLE
G1D_SCOPE = "orchestration/programme/g1d-provenance-scope.json"
G1C_BASELINE_PINS = {
    AGENTS: "e320b14f1bdd9f813892a0d8c8a0fc471eac20c513ec0561e0f37d437f312a8e",
    STATE: "74ea3399c148bcfecab429884a02cde41d0bb4d2a6af5acffd9ca7e4b6647db2",
    GATES: "eae6d337d300c7e7bd7ea681436d9177430235b5779710397929466d13b3ccfb",
    OVERLAY: "325b282a3fdc65fea1da6172664f3b49bb6a94070bb94ccab63d5e2e16af1cb0",
    G1C_SCOPE: "e37b0acd28dfa1c61bfded97f1b17844271dfdf4b75d631f81d8a30d4748ce88",
}
GOVERNOR_PUBLICATION = {
    "commit": "c4deef05e40b855c8f398456df98bb7590773257",
    "parent": "e57aa0d3735ba803b2c3869fc7cf8684b172de56",
    "tree": "b2888b3de5b9cc491b99099259e0d8b255677baf",
}
GOVERNOR_PINS = {
    "orchestration_harness/clockwork_governor.py": "d17143de860e2d671c4af67c03f9265591f66e840a3bb2196697d08253407795",
    "orchestration_harness/clockwork_persistence.py": "e2c81e22539642b0245dc92bfed8aff62fabdf773c28dbae6503154ac64a4ff8",
    "tests/test_clockwork_governor.py": "595723e6bc2a90467c179a5423c11178a3cb742dbc9572977a2bda154ab4914e",
}
PROVENANCE_DEPENDENCY_PINS = {
    "orchestration_harness/verdict.py": "8c7683fea46e98ddc467823ec11dde497c166123c549d49f938ef8fcdc5ff7cd",
    "orchestration/harness_settings/operating_model.yaml": "0181a3b007f800cc7b610d8f16a9ac551daf7345da15232e464f40dda1e3ca6f",
    "orchestration/harness_settings/verifier_execution_policy.yaml": "92721606167a0bcb6b65d40e62061d9aaba25b2e57e72d9a2ee0445d51d5258d",
    "orchestration/harness_settings/security_review_protocol.yaml": "861e5f577b98e8e3928333d28b8fade24d7e214f0cd666961f665fbce153dc70",
}
G1C_EVIDENCE_PINS = {
    "g1c-evidence/implementation-review-windows.json": "a2f076026f60586670a898127a644a7b3309519a416c0c4bd5f79ce27b72d6a8",
    "g1c-evidence/operation-review.json": "f186946e9f64224b9078b834a192a0e2d10a54b1aa8f57807659a5e1e1657cb4",
    "g1c-evidence/fresh-readback.json": "c44551d5b1658c1a5f4e7366e337dc43bfccd1189b5abc0b9d6b8922c6d1db8d",
    "g1c-evidence/windows-governor-1.stdout.json": "8ab07396da4a4af0d2912c88ef284590155047deafe5d274131e8a72d65e52d0",
    "g1c-evidence/windows-persistence-1.stdout.json": "006d3315e09bcd1f596e32af8ddcdd94ca6f44abeee0940d7f203b7f7477aa30",
    "g1c-evidence/candidate-manifest-v1.json": "e1551690b6cf0c23bc6782ed6547f84307cde2141b6a2dcdb246a9a2a65817a7",
}
G1D_CRITERIA = ("execution_and_context_provenance_machine_checkable", "generating_worker_not_sole_verifier",
                "declared_unproven_independence_rejected", "risk_tiered_independent_verification")
PROVENANCE_PATHS = frozenset({"orchestration_harness/clockwork_provenance.py",
                            "orchestration_harness/clockwork_observer.py", "tests/test_clockwork_provenance.py"})
G1D_TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G1D_SCOPE})
G1D_INPUT_PATHS = G1C_INPUT_PATHS | {G1D_SCOPE, *GOVERNOR_PINS, *PROVENANCE_DEPENDENCY_PINS}
G1D_LIMITS = ("policy eligibility is not publication authority", "no complete physical worktree attestation",
              "no full-suite or whole-loader acceptance", "G1D component and operational multi-task control remain unaccepted",
              "only reviewed local authored verification; no provider or live-model context authority",
              "existing writers, autonomous worker dispatch, product work and protected refs remain closed")
BOUNDED_SCOPE_PATHS = BOUNDED_SCOPE_PATHS | {G1D_SCOPE}
OPERATION_PATHS.update(accept_g1c=G1D_TRANSITION_PATHS, implement_g1d=PROVENANCE_PATHS)

G1E_PROFILE = raisa_policy.G1E_PROFILE
G1E_PREAMBLE = raisa_policy.G1E_PREAMBLE
G1E_TASK = "g1e_configuration_core_assessment"
G1E_SCOPE = "orchestration/programme/g1e-configuration-core-scope.json"
G1D_BASELINE_PINS = {
    AGENTS: "4bfb127ab2b139ea2d3df910c2fed4246a9d0e6233d96ac7d066e7419509a823",
    STATE: "b47b9760ce0e5ba5e30b48f28bc7f066e33e0739c96992aefc01c235d13071e4",
    GATES: "d434c9b723f49e158ba16b4f2908dd3c8771f7f4bc5a91ad58a0ac88955c315b",
    OVERLAY: "d14236058aeaa46274a4155825d77c608f91961ce5c7b929b4496a32179bf8c6",
    G1D_SCOPE: "a1fe6c4f5cafa0f5c7137bfc4a5c7950e10715bbcdfc07ed5ba9f7b2fccd649b",
}
PROVENANCE_PUBLICATION = {
    "commit": "8145d098df1ee7eef9ba095211e979cebc40629a",
    "parent": "35b24c25e7b29b88e3fdd4de321da71f2a2ad587",
    "tree": "1131916eed6a249417e34b5bef64116370284629",
}
PROVENANCE_PINS = {
    "orchestration_harness/clockwork_provenance.py": "c078d669a6bb9f24400d214a5b3ae9e6b0ce7f39210c135b467bfdff2b503e63",
    "orchestration_harness/clockwork_observer.py": "740ae18929fce0b306110de680894a5285ec50155db75c5db090801f48f8de26",
    "tests/test_clockwork_provenance.py": "08e927689a8e5f5f32818e0923912a6f301c6b59d154949b3e8ab4e0d37340a6",
}
G1D_EVIDENCE_PINS = {
    "g1d-evidence/implementation-review.json": "c07c3d7f81a7ff285e676b7dcfd50446b435cc2aa1511ff563762491e1021f4c",
    "g1d-evidence/operation-review.json": "7c5233668cb17be9f6d6a27eb5a6e9ea50e3f863dbc8a4bffbca513178ad8c52",
    "g1d-evidence/fresh-readback.json": "647702a1074bc40187e7eeede251d3af6843c50d64828bd83c94c0296bfd6490",
    "g1d-evidence/windows-test-2.stdout.json": "4284d197bf2d3f4c70f4219a0cb3072394288682c54c2428188085090f540ee8",
    "g1d-evidence/windows-validation-v2.json": "5557e8ef7babb0225390c3254d0320af64faa9cd18449a93510b853363ffe1bc",
    "g1d-evidence/source-manifest-v3.json": "3b800dc0eb4e879e85b3f7e4a2c927be43645289bfa5e24390121a9399ba3ff7",
}
CONTROLLER_PATHS = frozenset({"orchestration_harness/configuration_core.py", "orchestration_harness/raisa_policy.py",
    "orchestration_harness/bounded_g1b.py", "orchestration_harness/programme_admission.py", "tests/test_bounded_g1b.py"})
CONFIGURATION_PATHS = raisa_policy.POLICY_PATHS
CONFIGURATION_LEAF_PINS = {
    "orchestration/harness_settings/direction_collaboration.yaml": "d54f0e6719b42b3cb641406cd35d138437726f344a6d22636226a119353e6bf9",
    "orchestration/harness_settings/evidence_led_workflow.yaml": "1e07de52436019029751bdc82547693a9cc2ed5182e856b3b7b96c9f5cfded8b",
    "orchestration/harness_settings/deepseek_cost_calibration.yaml": "d84c35cb0aeea0e5a47f91845b6c5775b1af1ff489ba777a3ce33ea1c386f307",
}
G1E_CRITERIA = ("all_referenced_policy_files_exist_and_validate", "duplicated_authority_logic_removed",
                "ariadne_core_interface_defined", "raisa_specific_policy_behind_adapter", "chaos_and_compatibility_tests_pass")
G1E_TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G1E_SCOPE})
G1E_INPUT_PATHS = G1D_INPUT_PATHS | {G1E_SCOPE, *PROVENANCE_PINS, *CONTROLLER_PATHS, *CONFIGURATION_PATHS}
G1E_LIMITS = ("validation grants no execution or publication authority", "read-only installed-controller assessment",
              "no repository-wide collection, whole-loader or application CI acceptance",
              "providers, live-model context, existing writers, worker dispatch, product work and protected refs remain closed")
BOUNDED_SCOPE_PATHS = BOUNDED_SCOPE_PATHS | {G1E_SCOPE}
OPERATION_PATHS.update(accept_g1d=G1E_TRANSITION_PATHS, assess_g1e=frozenset())

G2_PROFILE = raisa_policy.G2_PROFILE
G2_PREAMBLE = raisa_policy.G2_PREAMBLE
G2_TASK = "g2_confirmation_family_fixture_repair"
G2_SCOPE = "orchestration/programme/g2-baseline-repair-scope.json"
G2_FIXTURE = "tests/test_api_spine_confirmation_family_idempotency_integration.py"
G2_FIXTURE_BEFORE = "3834f8101023728af11bd66f5b72aad1922d3ee92b712d112b95d055af31e130"
G2_ORIGINAL_FIXTURE_AFTER = "55be615610fdcd98c9bd4b73eed53e640a2ccc525e651597a66fc24967df884f"
G2_FIXTURE_AFTER = "64e6459b3cca707a966e464e9fbed8d7f71ef77b43ff4d79a9ee8502608f4fd3"
G2_COLD_IMPORT = "app/services/reception_one_proposal_runtime.py"
G2_REPAIR_PINS = {
    G2_FIXTURE: {"before_sha256": G2_FIXTURE_BEFORE, "after_sha256": G2_FIXTURE_AFTER},
    G2_COLD_IMPORT: {"before_sha256": "d15282a6a7c6f46207caf2a6490e29aa7d0a46f27c296489042e6afea564a817",
                     "after_sha256": "72da706fe90376a0eb7613aa76e1858ff5a64f03509f72b152fdac4791c42b22"},
}
G1E_BASELINE_PINS = {
    AGENTS: "42ad5ffa741d2b9df1568cc4ac35f32e49fb0a3d019079c5c65d3aea8145cb6b",
    STATE: "b43a1fb2be8d914ea47854f723ef867e4c5d12c4f16f29a38e1ff8ce314edd2c",
    GATES: "9ccfc924ea0015d78543178864527595636bd31315ff24117f1bbe7448dfdf02",
    OVERLAY: "94caacaa5ef51a69f17007ef7aa27ae881d239233b2b87a959973b726f7224d5",
    G1E_SCOPE: "f32c05eadf4a24ab377bde42de4a56b5de126ea1294b2c2e25e6b6be54c4e021",
}
G1E_PUBLICATION = {
    "commit": "167e5d7245d6d0cec87b61568036869d0126f543",
    "parent": "8145d098df1ee7eef9ba095211e979cebc40629a",
    "tree": "a36008121ee63edca94b8957edcaed114768f031",
}
G1E_ACTIVATION = {
    "commit": "144d792c9e83e82b99c873c09ba5e6df616560e5",
    "parent": G1E_PUBLICATION["commit"],
    "tree": "3c7524c1cb98dd2d9148d301331c148cd524477c",
}
# Historical assessed bytes, distinct from the installed G2 controller binding.
G1E_SOURCE_PINS = {
    "orchestration_harness/bounded_g1b.py": "73cb024a15297ddced538fe2a53d72182c571dd8d64a6dd6bfa83499b8bc8485",
    "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
    "orchestration_harness/programme_admission.py": "9c6814b30b331f3f3e32f1e4d92b08f31b856b26d51859fec3ad8f00cad782aa",
    "orchestration_harness/raisa_policy.py": "bbf16e19f583727f262fdab604e2f1fff476a4970f063d51550e383c132f490b",
    "tests/test_bounded_g1b.py": "24b0b617dce4077ec1f9c645cf8bf1dbc2b1e47281fda40069b519237c7ab402",
}
G1E_EVIDENCE_PINS = {
    "g1e-evidence/criteria-review.json": "d7eb21c867fe49fb5ae40554f6fab3cc36f90591b3e1074809649b1e8cdf9711",
    "g1e-evidence/assessment.stdout.json": "c2a6250c9f259a37a0a533e956ebdfd1fba422feec3fb2713e23a4724b2e9eb9",
    "g1e-evidence/assessment-binding.json": "fb5da1f532d83284c194ba90c943c91f4e719062a4edafb8c72564b254489f95",
    "g1e-evidence/fresh-readback.json": "12eb107dbc12ccc82e36a92e82af6322f5ec08a8244282b4c06019199ff57b97",
    "g1e-evidence/isolated-test-contract.json": raisa_policy.g2_test_exception()["contract_sha256"],
    "g1e-evidence/owner-runtime-approval.json": raisa_policy.g2_test_exception()["owner_approval_sha256"],
    "g1e-evidence/fixture-refinement-source.json": "daa51a817d05dea7445be67a6cb69bc5a59d45ffdb8e50730c50301f8354ff1d",
    "g1e-evidence/fixture-refinement-independent-review.json": "d698a16f8e2407136578256add5b39b76b7c72143c5fc95a2a2050fbea317cfa",
    "g1e-evidence/cold-import-source-review.json": "92ea00cd43855b17a15ff79ad052294e82c88ab3a789e86533212e94fc150555",
    "g1e-evidence/cold-import-independent-review.json": "6221c16c4217c57e7f5f814600eb90e353a3a80f4dae5c12c04dfd49832abe9e",
}
G2_CRITERIA = (
    "repository_wide_collection_and_tests_pass", "required_application_migration_and_safety_ci",
    "dependency_audit_pass_or_explicit_exception", "destructive_migration_removed",
    "empty_and_populated_alembic_paths_pass", "no_public_audio_or_phi_path", "no_implicit_patient",
    "cross_tenant_tests_application_and_database_pass", "appointment_concurrency_database_enforced",
    "ai_outputs_draft_until_human_attestation",
    "production_profile_excludes_dev_hosts_and_browser_bearer_storage",
    "no_unresolved_critical_or_high_stop_ship_risk",
)
G2_TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G2_SCOPE})
G2_INPUT_PATHS = G1E_INPUT_PATHS | {G2_SCOPE, *G2_REPAIR_PINS}
G2_LIMITS = (
    "policy eligibility grants no execution or publication authority",
    "only the reviewed confirmation-family fixture and cold-import prerequisite bytes are admitted",
    "isolated synthetic tests require the owner contract and independent execution-binding review",
    "no global CI, G2 completion, feature, provider, real-data or protected-integration acceptance",
)
BOUNDED_SCOPE_PATHS = BOUNDED_SCOPE_PATHS | {G2_SCOPE}
OPERATION_PATHS.update(accept_g1e=G2_TRANSITION_PATHS, repair_g2_fixture=frozenset(G2_REPAIR_PINS))


# The first G2 activation remains historical authority. New candidate hashes live
# in reviewed bindings, never in a controller source constant.
# Retain the task identifier recognized by the unchanged no-context guard.
G2_BATCH_TASK = G2_TASK
G2_BATCH_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v1"
G2_BATCH_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v1"
G2_BATCH_PATHS = frozenset({
    G2_FIXTURE, G2_COLD_IMPORT,
    "app/services/appointment_status_physical.py",
    "app/services/appointment_delete_physical.py",
    "app/services/appointment_status_composition.py",
    "app/services/appointment_delete_composition.py",
})
G2_BATCH_CONTROL_PATHS = frozenset({STATE, OVERLAY, G2_SCOPE})
G2_BATCH_CODE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py", "orchestration_harness/raisa_policy.py",
    "tests/test_bounded_g1b.py",
})
G2_BATCH_MAINTENANCE_PATHS = G2_BATCH_CODE_PATHS | G2_BATCH_CONTROL_PATHS
G2_BATCH_INPUT_PATHS = G2_INPUT_PATHS | G2_BATCH_PATHS
G2_BATCH_KINDS = frozenset({"enable_g2_batches", "extend_g2_catalogue", "repair_g2_batch"})
G2_CATALOGUE_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v2"
G2_CATALOGUE_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v2"
G2_CATALOGUE_PATHS = frozenset(raisa_policy.G2_CATALOGUE_PATHS)
G2_CATALOGUE_POLICY_PATHS = G2_INPUT_PATHS - G2_BATCH_PATHS
G2_CATALOGUE_PREDECESSOR = {'commit': '1af384bb2f914ed10cd7d59625d9f47f8a4c0e92',
 'parent': 'f6881e198f73d26f6410ff63de850e743f715254',
 'source_sha256': {'orchestration_harness/bounded_g1b.py': '8b1ce5a5ebb6e83c5db547957c4929e65cd3f24a246366e392f4603d457217ec',
                   'orchestration_harness/configuration_core.py': 'f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5',
                   'orchestration_harness/programme_admission.py': 'ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181',
                   'orchestration_harness/raisa_policy.py': '71ea2842fbb044e543c999cd9fb317cf6fa1803d004f5b03bc1c148cec54ec04',
                   'tests/test_bounded_g1b.py': '3bdefe5a38852164ea3917f2c611612718f005d715e183fe1ce498a8b16edb53'},
 'tree': '35bb039f3ca14dc781cd9702889e60f6cc3866b2'}
G2_CATALOGUE_PREDECESSOR_POLICY = {'AGENTS.md': 'fb96aced8c29739a7a98c7d837a752094690972d271219fb0a265ccc9f88c7ad',
 'orchestration/harness_settings/programme_recovery.yaml': '06ce34ee62f0dcff5b46b5ee2f695fea165bfc10faa079231d1f47ea5f0eebd2',
 'orchestration/programme/current-state.json': 'ef01727a117be3892d701ed4af79509d43bf8fbfb75f1d9704ed37b3dd89a635',
 'orchestration/programme/g2-baseline-repair-scope.json': 'cf3b6a0e9db12a57454e63768b08ec1c8a74458959d5350fdd6f5c88354a9b7e',
 'orchestration/programme/gates.yaml': '115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341'}
G2_BATCH_EFFECTS = EFFECTS | {"product_behavior_change"}
G2_BATCH_LIMITS = (
    "only the reviewed literal-file baseline repair in this binding is eligible",
    "source-level defect repair grants no application or database execution authority",
    "isolated synthetic tests retain the owner contract and independent execution binding",
    "no G2 completion, feature, provider, real-data, protected-evidence or integration acceptance",
)
G2_INITIAL_CONTROLLER = {'commit': 'a8b5a1aaa91f1953beca73c94218e2a057c8b7d9',
 'parent': '144d792c9e83e82b99c873c09ba5e6df616560e5',
 'source_sha256': {'orchestration_harness/bounded_g1b.py': 'faeaa3ed84f782616e812810e1c3fb1b73018bbef0132783c4ff79b036428519',
                   'orchestration_harness/configuration_core.py': 'f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5',
                   'orchestration_harness/programme_admission.py': 'ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181',
                   'orchestration_harness/raisa_policy.py': '625c3619af42277134908878851bfd675b67be63ecc04e79f18c126143c1c7d2',
                   'tests/test_bounded_g1b.py': 'd8912f19b2b7cb39aef1917155ca64e7dc89b5b73064fb46867dcaa4d8e6615f'},
 'tree': '586e53ab9ab1db88b409d06ee9605d431f5ed954'}
G2_INITIAL_POLICY_PINS = {'AGENTS.md': 'fb96aced8c29739a7a98c7d837a752094690972d271219fb0a265ccc9f88c7ad',
 'orchestration/harness_settings/programme_recovery.yaml': '80697adf9b63180ddc43928336b15533c0f3a884b3137bbbf5539ea15b163850',
 'orchestration/programme/current-state.json': '9bcf3351704514df6c992ffa679d64c658e1e2a6915709cb3e9ccc19e961a811',
 'orchestration/programme/g2-baseline-repair-scope.json': '9b70a5b441d3aec55c5197ecc0a9d0c4aafa9b147998c00ab480d581966bcc66',
 'orchestration/programme/gates.yaml': '115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341'}
G2_INITIAL_ACTIVATION = {
    "commit": "9b9c4400a99b9d1f57b36cd108fd5f64456502a5",
    "parent": G2_INITIAL_CONTROLLER["commit"],
    "tree": "b34d4ac985e5c96061a575c4c14f39dce643d59d",
}
G2_INITIAL_REPAIR = {
    "commit": "f6881e198f73d26f6410ff63de850e743f715254",
    "parent": G2_INITIAL_ACTIVATION["commit"],
    "tree": "d673fba4a1d11369677dd4cdeb57bc9d0962a276",
}
G2_MIGRATION_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v3"
G2_MIGRATION_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v3"
G2_MIGRATION_PATHS = frozenset(raisa_policy.G2_MIGRATION_PATHS)
G2_MIGRATION_ADDITION = "tests/test_phase0_migration_preservation.py"
G2_MIGRATION_EFFECTS = G2_BATCH_EFFECTS | {"migration_change"}
G2_MIGRATION_PREDECESSOR = {
    "commit": "0371fc14a6e0333305641189193f4054adb5c11d",
    "parent": "1af384bb2f914ed10cd7d59625d9f47f8a4c0e92",
    "tree": "d32dbfa1f43c65755df32fafae249f3923439497",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "e163b8d1c4aabd28d94169acc9ec0af830fe0c209716125e9379e1e40c13bb21",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "b54740083d90a06949bc3019fc60d9fbb7568980be93c16c37e4253adbad7e48",
        "tests/test_bounded_g1b.py": "be6b8ad18d517b8922da61a05e1126eed235abe1fe58fd9c7c29470cca1c19fe",
    },
}
G2_MIGRATION_PREDECESSOR_POLICY = {
    AGENTS: "fb96aced8c29739a7a98c7d837a752094690972d271219fb0a265ccc9f88c7ad",
    STATE: "dc1b557d01614cc45c5e064f3309c3101726da8e748348b2e1492d4900f8c746",
    OVERLAY: "1f18ba0a822c6a9b78c8dcc7742e3229f50368bd4f0f329f7db3901b963d8cf1",
    G2_SCOPE: "6b67b5e5f553f62be848919fb08c5ef081f4eb580523140e746f4b0dee580406",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_migration", "repair_g2_migration"}
G2_MAINTENANCE_KINDS = frozenset({"enable_g2_batches", "extend_g2_catalogue", "enable_g2_migration"})
OPERATION_PATHS.update(enable_g2_batches=G2_BATCH_MAINTENANCE_PATHS,
                       extend_g2_catalogue=G2_BATCH_MAINTENANCE_PATHS,
                       repair_g2_batch=G2_BATCH_PATHS,
                       enable_g2_migration=G2_BATCH_MAINTENANCE_PATHS,
                       repair_g2_migration=G2_MIGRATION_PATHS)

# This successor aligns only the published owner instruction change. Historical
# activation pins above and the migration profile remain unchanged.
G2_INSTRUCTIONS_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v4"
G2_INSTRUCTIONS_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v4"
G2_INSTRUCTIONS_SHA256 = "1477744869ac675faf7d7ef5093bec18e058a050a5e1e15c5c2d0bf4af0f21c5"
G2_INSTRUCTIONS_PUBLICATION = {
    "commit": "7ec6e974f61c9e474228649d66a24ad0f054ebc9",
    "parent": "e3c6e185b1a754e4b144707a20b5974d18a4d23b",
    "tree": "a753f22942a0adbed7ef1a754d50554dc32e60b2",
}
G2_INSTRUCTIONS_PREDECESSOR = {
    "commit": "84c6b3520fb96971a9afc6f21027b4957c0dd63c",
    "parent": "e7e9be69fe4343775c6912bf68eba3fc4a9852c3",
    "tree": "9c61e3650a0e41efc9f7889ca7723e1a99401453",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "7d2450b2439e7ab6410a38a06d9876197251dc874ce9f998dc6d90d8c5488833",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "3f1df407698e17087fc35289d9276f7074d297e961c8a047b42563a50e5fe30b",
        "tests/test_bounded_g1b.py": "d666e6cfe0e3971d44c5b41b4a1b91470da631d71520daf640ee81f7c9e71655",
    },
}
G2_INSTRUCTIONS_PREDECESSOR_POLICY = {
    AGENTS: "fb96aced8c29739a7a98c7d837a752094690972d271219fb0a265ccc9f88c7ad",
    STATE: "2b17cc2b02076bb757be6fe0e9815be93bc75ef93eaaa09aa70f68d14803f570",
    OVERLAY: "73f719feba004b1d2a8efd52d88d0f546516b279e8badfe50ba80a919556a2f7",
    G2_SCOPE: "25cb1df22f28216b75de03c404b1f92b5a0f36c5da06bb41711e6fee1e769104",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_INSTRUCTIONS_MAINTENANCE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py", "tests/test_bounded_g1b.py", STATE, G2_SCOPE})
G2_BATCH_KINDS = G2_BATCH_KINDS | {"align_g2_instructions"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"align_g2_instructions"}
OPERATION_PATHS["align_g2_instructions"] = G2_INSTRUCTIONS_MAINTENANCE_PATHS

# A v5 successor activates one exact audio-privacy source repair. The installed
# v4 controller and all earlier publications remain historical authority.
G2_AUDIO_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v5"
G2_AUDIO_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v5"
G2_AUDIO_PATHS = frozenset(raisa_policy.G2_AUDIO_PRIVACY_PATHS)
G2_AUDIO_ADDITION = "tests/test_consultation_audio_privacy.py"
G2_AUDIO_EFFECTS = G2_BATCH_EFFECTS
G2_AUDIO_PREDECESSOR = {
    "commit": "8f27fcc622933ba256dc33142f85ac92849d6b89",
    "parent": G2_INSTRUCTIONS_PUBLICATION["commit"],
    "tree": "0d13644799ac636f9eeb802daab76fe954db9489",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "87fa503900f47168481820daa3499d9e08b4b2f52a99eff59aba58e0030b3bed",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "3f1df407698e17087fc35289d9276f7074d297e961c8a047b42563a50e5fe30b",
        "tests/test_bounded_g1b.py": "22fcdab3131c8827d2ca0b6592c9b0e7d82226108cdf5688d043efa865dad0eb",
    },
}
G2_AUDIO_PREDECESSOR_POLICY = {
    AGENTS: G2_INSTRUCTIONS_SHA256,
    STATE: "802438d220e50331e6868a748a3b76a1b837e782abad81cf330ae33d1d035f23",
    OVERLAY: "73f719feba004b1d2a8efd52d88d0f546516b279e8badfe50ba80a919556a2f7",
    G2_SCOPE: "c03f3a329a334ae2a59619d807853be2b9dbbbb68399e29dfc49eb93e4a5ac65",
    GATES: G2_INITIAL_POLICY_PINS[GATES],
}
G2_AUDIO_TRUSTED_GIT_PUBLICATION = {
    "commit": "9e271036c1e7d4aec842f1e1a4a3f9c1666411dd",
    "parent": "eaabb48b0df6c6c1f9e0ba086d1c360009b54e03",
    "tree": "4451dea5d6ffae12e89a03706eabacac42fa7b47",
}
G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256 = {
    "orchestration_harness/trusted_git.py": "4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527",
    "orchestration_harness/controller_maintenance_record.py": "d93b8f106b4c96aa7a6ba5c26518232d9f152b4927b10d32db5d066d03ccc1b5",
    "tests/test_programme_target_index.py": "69b7711049d5b3046eeed4aeaded8becbcf4e8055484891789f570cbe998adab",
}
G2_AUDIO_INSTRUCTIONS_SHA256 = "254c906919e49c69b53c82fa2a678953b45e20d5e2ce2503184583daf09f8cc7"
G2_AUDIO_INSTRUCTIONS_PUBLICATION = {
    "commit": "e787fd8e92c70e4aa7f58d13c98b8f04ec6fee0a",
    "parent": G2_AUDIO_TRUSTED_GIT_PUBLICATION["commit"],
    "tree": "5ff10cc3775b5b4d292d443b15c9d05df48aed5f",
}
G2_AUDIO_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_AUDIO_LIMITS = (
    "only the reviewed literal four-file audio privacy repair in this binding is eligible",
    "source scope removes only application-created persistent or public audio files and bounds browser object URL lifetime",
    "framework or operating-system multipart temporary storage, endpoint authorization and full PHI safety are not accepted",
    "admission grants no application, database, provider or test-runtime execution authority",
    "no G2 completion, feature, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_audio_privacy", "repair_g2_audio_privacy"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_audio_privacy"}
OPERATION_PATHS.update(enable_g2_audio_privacy=G2_AUDIO_MAINTENANCE_PATHS,
                       repair_g2_audio_privacy=G2_AUDIO_PATHS)

# A v6 successor activates one exact no-implicit-patient repair. The installed
# v5 controller and the published audio repair remain independently pinned.
G2_PATIENT_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v6"
G2_PATIENT_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v6"
G2_PATIENT_PATHS = frozenset(raisa_policy.G2_PATIENT_BINDING_PATHS)
G2_PATIENT_ADDITION = "tests/test_consultation_patient_binding.py"
G2_PATIENT_EFFECTS = G2_BATCH_EFFECTS
G2_PATIENT_PREDECESSOR = {
    "commit": "77b4e285c31d961d1fdda9779f2f7c3a52d6773b",
    "parent": G2_AUDIO_INSTRUCTIONS_PUBLICATION["commit"],
    "tree": "5c31e61c04245f030c9e986558fdc4f468dff7a7",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "7d8e37f830432134a9af941d78f1de0b8ecfad833ad70ff1dfca228d76670414",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "de7a62c15c293b0afa7882e81c08f26c553543bebc91aafee3b399249c9532fc",
        "tests/test_bounded_g1b.py": "acb69b65143b15b538aa7b2c60b1ab7480fe53372f6377ba5747205b4372b640",
    },
}
G2_PATIENT_PREDECESSOR_POLICY = {
    AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256,
    STATE: "9e25ce165fe54414e60bbd30201c44a8171b61ecb871b92ce24e40c2d291634e",
    OVERLAY: "5d87880bc927b003e00d74e4267a6469a0e0ef0241ce45d9d01b48e4c3918ccf",
    G2_SCOPE: "92222e77419479234ddce8e7524ef890bafcbeb82535f6e06b2b2e7f1a49ebad",
    GATES: G2_INITIAL_POLICY_PINS[GATES],
}
G2_AUDIO_REPAIR_PUBLICATION = {
    "commit": "03e18f8ef007d9f8ecd4d39d6af2fe0b5fb4ddd5",
    "parent": G2_PATIENT_PREDECESSOR["commit"],
    "tree": "f2084fac4171f390d50bdfd182229d5a5eab6ed2",
}
G2_AUDIO_REPAIR_SOURCE_SHA256 = {
    "app/main.py": "43047906b436a3d6f2bc0dda32a1625977cd583f99c072b34f99c0039affd7bc",
    "app/routers/consultation.py": "6c6bdf6a392b322d013984c8dc7160a2db9d7ebc2e8b496eebead59130b2eb77",
    "EMR4 Sidebar/src/taskpane/taskpane.js": "c759e196569a04bff6d80644773a6b92950eb72514ff1554cd897516ac1e801d",
    "tests/test_consultation_audio_privacy.py": "52ddad2e1d52936bfa5e0e7a4f67bdf982b5bedf80c59c6680fcd6f9b024759e",
}
G2_PATIENT_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_PATIENT_LIMITS = (
    "only the reviewed literal four-file no-implicit-patient repair in this binding is eligible",
    "analysis is draft-only and finalization requires an explicit UUID patient in the current practice",
    "the existing audio privacy assertions remain required while their legacy finalize fixture gains explicit patient binding",
    "admission grants no application, database, provider or test-runtime execution authority",
    "endpoint authorization, actor or practitioner provenance, and full application or database tenant isolation are not accepted",
    "no G2 completion, attestation, tenant-wide acceptance, feature, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_patient_binding", "repair_g2_patient_binding"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_patient_binding"}
OPERATION_PATHS.update(enable_g2_patient_binding=G2_PATIENT_MAINTENANCE_PATHS,
                       repair_g2_patient_binding=G2_PATIENT_PATHS)


# A v7 successor repairs consultation transaction atomicity without adding
# clinical-role or practitioner-attestation authority.
G2_ATOMICITY_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v7"
G2_ATOMICITY_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v7"
G2_ATOMICITY_PATHS = frozenset(raisa_policy.G2_CONSULTATION_ATOMICITY_PATHS)
G2_ATOMICITY_ADDITION = "tests/test_consultation_finalize_atomicity.py"
G2_ATOMICITY_EFFECTS = G2_BATCH_EFFECTS
G2_ATOMICITY_PREDECESSOR = {
    "commit": "65aec51154a48fa375cac23cc2add52b752f67f5",
    "parent": G2_AUDIO_REPAIR_PUBLICATION["commit"],
    "tree": "fc1b16b3db42ceb51c71efa97030e0a4673f39aa",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "4198c1614bc752693a2c902d126ce1b877f8dd56fa63e7bee737b3a8e5c8cf75",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "4209113c351a7a822a7859577044884b7405fc1db0d425dc79ad54ad235b1eeb",
        "tests/test_bounded_g1b.py": "371496e2480a2701d76c9b1eaf984f5c61df38c8152bc6d3f808ebde00e2ce99",
    },
}
G2_ATOMICITY_PREDECESSOR_POLICY = {
    AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256,
    STATE: "c1eb738c4979625d4538c2f6cdf8ea624ff48ed8c618ab93a77d06028ad71ab6",
    OVERLAY: "a6ce84d31a06d3afa303cc244a0c48a5742aefb39b81af702d24f049f4d0491a",
    G2_SCOPE: "c6040347ba4a9c9294e873680acfbaffca16583afca9648a9ac9756c6a6c3a13",
    GATES: G2_INITIAL_POLICY_PINS[GATES],
}
G2_PATIENT_REPAIR_PUBLICATION = {
    "commit": "bc7800e3fa297942f6444e792094f679f37bb70e",
    "parent": G2_ATOMICITY_PREDECESSOR["commit"],
    "tree": "978c6e8e74c783e356fff40205f189e6567edf34",
}
G2_PATIENT_REPAIR_SOURCE_SHA256 = {
    "app/main.py": "43047906b436a3d6f2bc0dda32a1625977cd583f99c072b34f99c0039affd7bc",
    "app/routers/consultation.py": "37c942807859ae6ca6317d7be788e15eee4193428aa606018971df1f67de7069",
    "EMR4 Sidebar/src/taskpane/taskpane.js": "c61d2184e837064a3f6cfffb03404dca296c0a44e5e2093ec30414fc5b1758bf",
    "tests/test_consultation_audio_privacy.py": "e0c19552eb200d8f18d00466082ae1182804a3540109dc568736da0c5c9d4d2a",
    "tests/test_consultation_patient_binding.py": "dc55f6d92b9d0f5fb1a7f7a2ef5bc980345ca7217703b3eb8747f3874649df5a",
}
G2_ATOMICITY_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_ATOMICITY_LIMITS = (
    "only the reviewed literal four-file consultation transaction-atomicity repair in this binding is eligible",
    "encounter and child records form one commit and rollback unit while explicit patient and practice binding are preserved",
    "existing audio privacy, draft-only analysis and patient-binding assertions remain required with the UUID helper return contract",
    "admission grants no application, database, provider or test-runtime execution authority",
    "clinical-role restrictions, actor or practitioner provenance and human-attestation policy are not accepted or changed",
    "no G2 completion, tenant-wide acceptance, feature, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_consultation_atomicity", "repair_g2_consultation_atomicity"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_consultation_atomicity"}
OPERATION_PATHS.update(enable_g2_consultation_atomicity=G2_ATOMICITY_MAINTENANCE_PATHS,
                       repair_g2_consultation_atomicity=G2_ATOMICITY_PATHS)


# V8 binds the owner's GP-only attestation policy and persistent fictional
# fixture authority. Admission still grants no application/test execution.
G2_CLINICAL_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v8"
G2_CLINICAL_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v8"
# Semantic V8 remains stable; this is its fourth reviewed source revision.
G2_CLINICAL_SOURCE_REVISION = 4
G2_CLINICAL_PATHS = frozenset(raisa_policy.G2_CLINICAL_AUTHORITY_PATHS)
G2_CLINICAL_EFFECTS = G2_BATCH_EFFECTS
G2_CLINICAL_PREDECESSOR = {
    "commit": "64ec9fce6396b9fd14710ff3610a369c215446a1",
    "parent": G2_PATIENT_REPAIR_PUBLICATION["commit"],
    "tree": "a655774e2a0f7f07e93c3111c0be0515f12abf7e",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "7d1b709320ad25c8b08eeabb961ad4e542f22087d8ae6917b915d204d0250020",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "709b1aaf25a39c2e4f7b4e45b6ac1585787eeacd05a1df10e4aa1e1d7fbff1c0",
        "tests/test_bounded_g1b.py": "fce46ea3b6ddc0e3a9a069031d44cb51eaa14a51ae1f6dabc31509b9fa6189b1",
    },
}
G2_CLINICAL_PREDECESSOR_POLICY = {
    AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256,
    STATE: "e9c2d3b10840cc9e72633fa51fb49e4cfe46a3873f32813847d13faa5916f20d",
    OVERLAY: "ffd763fd9dc5cd3c9d68d9f00d6bab3e48d2c85a23e70d2577792dea4a5ad1a9",
    G2_SCOPE: "6777a39980defdb95b7c287ef21cffe7f039e2bde9aa4cb13685c53f0b2504c7",
    GATES: G2_INITIAL_POLICY_PINS[GATES],
}
G2_ATOMICITY_REPAIR_PUBLICATION = {
    "commit": "be98c2c856c3c02e10aed1a9fbb3c2e1123be399",
    "parent": G2_CLINICAL_PREDECESSOR["commit"],
    "tree": "8d64ae76aec9568baf374dc21724fcf19b349c5d",
}
G2_ATOMICITY_REPAIR_SOURCE_SHA256 = {
    "app/routers/consultation.py": "c6f7bd690f0c5761e60afbdeb217f13c6760c94d88a4947d192b9070cb09d61e",
    "app/services/ai/audit_events.py": "d30f5a35f4bd4ab1ce2c854510ab17c7a094635ccc283a7bdc6aa88971ac81fd",
    "EMR4 Sidebar/src/taskpane/taskpane.js": "c61d2184e837064a3f6cfffb03404dca296c0a44e5e2093ec30414fc5b1758bf",
    "tests/test_consultation_audio_privacy.py": "691d0d1ab2be2d0c831e210afdd34fe9ddfcdea1fb6e4c4aa12fe3075ecb5fa4",
    "tests/test_consultation_patient_binding.py": "10185cba2d30214cb2bae6732c054e65f586d3bc6debdcde45e7c45646ce2229",
    "tests/test_consultation_finalize_atomicity.py": "c7eab22811afbc89b1a3c5a16f84cf96b2572ebd52e5abd24ccb2d7f8cac737d",
}
G2_CLINICAL_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_CLINICAL_LIMITS = (
    "only the reviewed literal six-file clinical authority, binding, receipt and attestation repair in this binding is eligible",
    "the owner selected active GP plus active linked same-practice practitioner, exact locked-patient document binding and explicit clinician attestation",
    "strict typed input and one canonical saved projection bind clinical rows, response and server-computed reviewed-content hash",
    "a unique server UUIDv5 receipt precedes clinical rows in the same transaction; replay is exact and conflicts fail closed without automatic retry",
    "MbsClaim practitioner attribution and Submitted state are internal synthetic database semantics, not real billing submission acceptance",
    "admission grants no runtime, G2 completion, live clinical, billing or credential authority, feature, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_clinical_authority", "repair_g2_clinical_authority"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_clinical_authority"}
OPERATION_PATHS.update(enable_g2_clinical_authority=G2_CLINICAL_MAINTENANCE_PATHS,
                       repair_g2_clinical_authority=G2_CLINICAL_PATHS)


G2_MIGRATION_GUARD_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v9"
G2_MIGRATION_GUARD_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v9"
G2_MIGRATION_GUARD_CODE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py", "tests/test_bounded_g1b.py",
})
G2_MIGRATION_GUARD_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_MIGRATION_GUARD_CODE_PATHS | {AGENTS}
G2_MIGRATION_GUARD_INSTRUCTIONS_SHA256 = "93ebf50187b6132fcee91cee7f4ba0b81bb59286ed9eaf52cdadab3a09ba20c1"
G2_MIGRATION_GUARD_PREDECESSOR = {
    "commit": "a0b8620b172f37648326d7fd86214c4019a5e275",
    "parent": "9ffd3b8cb2b3aea873458f9758bc29393ff44e2b",
    "tree": "3542610ba876074ec39b9342ee014dd134fef3e8",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "8deff19d46498ae2dfdd0bbb06f9d638f8621e1f120053139ff648ca25da3d43",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "c8d825067fad126383ec14f7ae34b277a5078898f06044eced9c40938bad6d75",
        "tests/test_bounded_g1b.py": "11b7922837b6045c0a7227ce46db4ca0dc86d1c9204261c96fe95109bd1bad48",
    },
}
G2_MIGRATION_GUARD_PREDECESSOR_POLICY = {
    AGENTS: "254c906919e49c69b53c82fa2a678953b45e20d5e2ce2503184583daf09f8cc7",
    STATE: "d66b7c336123e4c7168f442144d58fdf1a10be033638f72e0ac17ae99fb43f33",
    OVERLAY: "3cad4644d7f3799b755155dc803a7c5fd3e2e2f0f734c0db6548efaf95a472ba",
    G2_SCOPE: "bda7013d18e2497780e5938b213ad898ccd6421943abecece1f769d412baf5a2",
    GATES: G2_INITIAL_POLICY_PINS[GATES],
}
G2_MIGRATION_GUARD_PRIOR_ACCEPTANCE = {
    "path": "C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/g2-entry/migration-preservation/repair-v1/native-acceptance.json",
    "sha256": "3d28829c3e6406dbdd1a7a280bdb008c70f968d301696ba5e49e9ea5aaa8ce5d",
    "role": "opaque_historical_reference_only_no_new_runtime_or_criterion_acceptance",
}
G2_MIGRATION_GUARD_CLINICAL_ACCEPTANCE = {
    "path": "C:/Users/there/EMR4-tools/g2-clinical-product5-publish-20260915-v1/resume-20260916/actual-post-publication-acceptance.json",
    "sha256": "2e47c6a1900c0204281e6d51bceed659cc76a40d339d5fa3604ff74f05ab7683",
    "role": "opaque_historical_publication_acceptance_not_runtime_authority",
}
G2_MIGRATION_GUARD_REPAIR_PINS = {
    "alembic/versions/d4787e8e3629_phase_0_baseline.py": "d2c66aadecb0e35f75b6aab369189a9075fa7db26d304ea2993944d5d0fd9732",
    "tests/test_phase0_migration_preservation.py": "d3792958aca0ac7bb9d98510f895b41b22fa20b7108190a9b57fdc06ba9d8e79",
}
G2_MIGRATION_GUARD_LIMITS = (
    "only the two existing migration downgrade-guard source and regression paths are eligible",
    "the owner-supported migration contract and all historical latches and acceptance remain unchanged",
    "the prior 25-case migration acceptance is an opaque historical reference, not new execution authority",
    "admission grants no runtime, G2 completion, feature, provider, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_migration_downgrade_guard", "repair_g2_migration_downgrade_guard"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_migration_downgrade_guard"}
OPERATION_PATHS.update(enable_g2_migration_downgrade_guard=G2_MIGRATION_GUARD_MAINTENANCE_PATHS,
                       repair_g2_migration_downgrade_guard=G2_MIGRATION_PATHS)


G2_APPOINTMENT_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v10"
G2_APPOINTMENT_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v10"
G2_APPOINTMENT_CODE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py",
    "orchestration_harness/raisa_policy.py",
    "tests/test_bounded_g1b.py",
})
G2_APPOINTMENT_PATHS = frozenset(raisa_policy.G2_APPOINTMENT_CONCURRENCY_PATHS)
G2_APPOINTMENT_ADDITIONS = frozenset({
    "app/services/appointment_conflicts.py",
    "alembic/versions/y4z5a6b7c8d9_enforce_practitioner_appointment_no_overlap.py",
    "tests/test_appointment_concurrency.py",
})
G2_APPOINTMENT_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_APPOINTMENT_CODE_PATHS | {AGENTS}
G2_APPOINTMENT_INSTRUCTIONS_SHA256 = "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e"
G2_APPOINTMENT_PREDECESSOR = {
    "commit": "c8f1fbb75e701163d4bb8b04f170ee4d74653016",
    "parent": "5b386240baa53b7882219832dc6057d66999ca61",
    "tree": "53bbd4b805a55b9e97dd30a808d904a736913f9f",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "cb0f43df7dfc3770c81b2de613e2fef03415f5cdc78bcc7ec9c704966c061dca",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "c8d825067fad126383ec14f7ae34b277a5078898f06044eced9c40938bad6d75",
        "tests/test_bounded_g1b.py": "47aad2690c5926d9f08ab9a47c2218b73704579f626e055e1a91423a6b00b09f",
    },
}
G2_APPOINTMENT_PREDECESSOR_POLICY = {
    AGENTS: G2_MIGRATION_GUARD_INSTRUCTIONS_SHA256,
    STATE: "c6a7feabf91fb86dc992ec80a11219582d630305ec7db473c499c68446fc09c3",
    OVERLAY: "73f719feba004b1d2a8efd52d88d0f546516b279e8badfe50ba80a919556a2f7",
    G2_SCOPE: "16910ab6b4da530de132072462520ba45f869f6e36c33eec6cbb38dc2050b891",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_APPOINTMENT_REPAIR_PINS = {
    "app/models/appointments.py": "4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794",
    "app/schemas/appointments.py": "ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90",
    "app/routers/appointments.py": "8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08",
    "app/services/appointment_status_composition.py": "1bde039d39a3b9d3e041585d9e4a38f403409a438f21be4bb37fd3891fe9a2dc",
    "app/services/appointment_conflicts.py": None,
    "alembic/versions/y4z5a6b7c8d9_enforce_practitioner_appointment_no_overlap.py": None,
    "tests/test_appointment_concurrency.py": None,
}
G2_APPOINTMENT_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/EMR4-tools/g2-migration-product-guard-20260916/publication-v1/independent-post-publication-acceptance.json",
    "sha256": "febb30567cc6a01c5575d7f3d538fca5207673bd80784fcbe5788b936789a6b7",
    "role": "opaque_historical_migration_guard_publication_acceptance_not_operation_authority",
}
G2_APPOINTMENT_INVARIANT = {
    "scope": "same_practice_same_practitioner_blocking_appointments",
    "overlap": "half_open_intervals_overlap_when_each_start_is_before_the_other_end",
    "location_independent": True,
    "null_location_included": True,
    "insertion_order_independent": True,
    "tenant_scope_preserved": True,
}
G2_APPOINTMENT_LIMITS = (
    "only the exact seven appointment concurrency product paths in this binding are eligible",
    "the three fixed additions must be absent and the four existing paths must match their exact accepted preimages",
    "same-practice same-practitioner blocking overlaps are rejected across every location including NULL and independent of order",
    "the accepted migration guard publication and every earlier latch remain historical and are never replayed or rewritten",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no runtime, G2 completion, feature, provider, real-data, protected-evidence or integration acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_appointment_concurrency", "repair_g2_appointment_concurrency"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_appointment_concurrency"}
OPERATION_PATHS.update(enable_g2_appointment_concurrency=G2_APPOINTMENT_MAINTENANCE_PATHS,
                       repair_g2_appointment_concurrency=G2_APPOINTMENT_PATHS)


G2_PRODUCTION_PROFILE_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v11"
G2_PRODUCTION_PROFILE_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v11"
G2_PRODUCTION_PROFILE_CODE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py",
    "orchestration_harness/raisa_policy.py",
    "tests/test_bounded_g1b.py",
})
G2_PRODUCTION_PROFILE_PATHS = frozenset(raisa_policy.G2_PRODUCTION_PROFILE_PATHS)
G2_PRODUCTION_PROFILE_ADDITIONS = frozenset({"tests/test_production_profile.py"})
G2_PRODUCTION_PROFILE_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_PRODUCTION_PROFILE_CODE_PATHS
G2_PRODUCTION_PROFILE_INSTRUCTIONS_SHA256 = "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e"
G2_PRODUCTION_PROFILE_PREDECESSOR = {
    "commit": "777e0170779e717123856b119ddb747db89e6aba",
    "parent": "849e03a98d87cbded4ac8c67856b68ecc0f93f90",
    "tree": "1c52c53b2baf83e80c7e3b11c958de8464053371",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "740c55df5e4baea0a793a193b2fd111b76196977458a53290998758af6547273",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "8549950809fbf44e0af510f49140a741f9a9a7eef93e04e6cf4a57fd0bc36c23",
        "tests/test_bounded_g1b.py": "5ec0cfa754631e9aa211452e00e3499a550edecf0a6c57f6a6cb319b5c656dce",
    },
}
G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY = {
    AGENTS: G2_PRODUCTION_PROFILE_INSTRUCTIONS_SHA256,
    STATE: "8543d8ba1f37f3b1686b4167cf03870e4651d2da122429f4de4591977e45b76d",
    OVERLAY: "a40c5bc99a6ece93e008010ca578d867218677abaa6d6ff969b7df8a421bda57",
    G2_SCOPE: "f83ec94b4fa641a3ce95a0212f45b009e4327f8d98c015358e86a69058e7160e",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_PRODUCTION_PROFILE_REPAIR_PINS = {
    "app/config.py": "f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e",
    "app/main.py": "43047906b436a3d6f2bc0dda32a1625977cd583f99c072b34f99c0039affd7bc",
    "tests/test_consultation_audio_privacy.py": "71a6e2b9beaa7578a0c4dbbaa5a5c62d32d2645d3dcc659fbd0454c108a7a246",
    "tests/test_production_profile.py": None,
}
G2_PRODUCTION_PROFILE_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/appointment-product-publication-effect-acceptance-v1.json",
    "sha256": "5bb1069c8cd53e2cb4a13474f08ae04374150b124033557ea77398903c2d16f1",
    "role": "opaque_historical_appointment_publication_acceptance_not_operation_authority",
}
G2_PRODUCTION_PROFILE_INVARIANT = {
    "canonical_profiles": ["dev", "staging", "production"],
    "non_development_cors_origins": [],
    "non_development_interactive_docs_served": False,
    "non_development_taskpane_served": False,
    "non_development_bernie_fixture_router_included": False,
    "machine_openapi_and_backend_api_retained": True,
    "development_surfaces_preserved": True,
    "browser_session_integration_claimed": False,
}
G2_PRODUCTION_PROFILE_LIMITS = (
    "only the exact four production-profile product and test paths in this binding are eligible",
    "the fixed test addition must be absent and the three existing paths must match their exact accepted preimages",
    "staging and production retain the backend API and machine OpenAPI while excluding legacy taskpane, interactive docs, development fixtures and all cross-origin browser origins",
    "the accepted appointment publication and every earlier latch remain historical and are never replayed or rewritten",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no runtime, G2 completion, browser session integration, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_production_profile", "repair_g2_production_profile"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_production_profile"}
OPERATION_PATHS.update(enable_g2_production_profile=G2_PRODUCTION_PROFILE_MAINTENANCE_PATHS,
                       repair_g2_production_profile=G2_PRODUCTION_PROFILE_PATHS)


G2_DEPENDENCY_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v12"
G2_DEPENDENCY_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v12"
G2_DEPENDENCY_CODE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py",
    "orchestration_harness/raisa_policy.py",
    "tests/test_bounded_g1b.py",
})
G2_DEPENDENCY_PATHS = frozenset(raisa_policy.G2_DEPENDENCY_REPAIR_PATHS)
G2_DEPENDENCY_ADDITIONS = frozenset({"tests/test_dependency_compatibility.py"})
G2_DEPENDENCY_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_DEPENDENCY_CODE_PATHS
G2_DEPENDENCY_EFFECTS = G2_BATCH_EFFECTS | {"dependency_change"}
G2_DEPENDENCY_PREDECESSOR = {
    "commit": "db55dc48ca128d96e70a2e6697fb297b75abba8c",
    "parent": "ec0fecc87c169cd4fd5f2dcf2f4c028140ca178a",
    "tree": "e497557f4f26bb8c4ffc1e8d65169530ba83ac95",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "a67b908c6d77d29bed51c202841e3e0deff702aa6a224414262361a74fa9d22b",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "53ac795980f28a4b7120f0c75375bdb4a558730ae67849ccb6b21b5a5c375a7a",
        "tests/test_bounded_g1b.py": "3dac7e06c2cd904ac93e87417948d7c23be32f49cdd04f4df409afb72a71068e",
    },
}
G2_DEPENDENCY_PREDECESSOR_POLICY = {
    AGENTS: G2_PRODUCTION_PROFILE_INSTRUCTIONS_SHA256,
    STATE: "8590911880f29cc1bddbe89fd56598e5ecd07a1dd73c7fd2d770ac3a86d8bf52",
    OVERLAY: "16bb9055829b7373dd9385e2570a85b8664ab1d73a3a8a54d43533a1fa74482b",
    G2_SCOPE: "d84f5baea02990ed7ebee083931af9b1e02d710f07370c4300a3da62424ec509",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_DEPENDENCY_REQUIREMENTS_COMMITTED_BEFORE_SHA256 = "6af2b87d7595af4b0da67c4e1603edc4c04d196feb399f05cea6a5ab4c73033c"
G2_DEPENDENCY_REQUIREMENTS_WORKTREE_BEFORE_SHA256 = "56426e781c912feb3ad569a250f060a9584bfc6a13512db68b2c6396748b7e6b"
G2_DEPENDENCY_REPAIR_PINS = {
    # This pin is compared with the predecessor Git blob and repair_sha256.before.
    "requirements.txt": G2_DEPENDENCY_REQUIREMENTS_COMMITTED_BEFORE_SHA256,
    "tests/test_dependency_compatibility.py": None,
}
G2_DEPENDENCY_REQUIREMENTS_AFTER_SHA256 = "47d852c442ea25c041aa70fca5dff01846fd18f3eebfa3c7d288aec3e0a54b90"
G2_DEPENDENCY_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/production-profile-product-publication-v1/independent-publication-effect-review-v1.json",
    "sha256": "b49b37a4b010b44282ef4faac3263941c5b33c199ad55e68466949f0581fee27",
    "role": "opaque_historical_production_profile_publication_acceptance_not_operation_authority",
}
G2_DEPENDENCY_INVARIANT = {
    "root_change": {"package": "cryptography", "before": "48.0.1", "after": "50.0.1"},
    "all_other_24_roots_unchanged": True,
    "compatibility_test_path": "tests/test_dependency_compatibility.py",
    "requirements_worktree_before_sha256": G2_DEPENDENCY_REQUIREMENTS_WORKTREE_BEFORE_SHA256,
    "requirements_after_sha256": G2_DEPENDENCY_REQUIREMENTS_AFTER_SHA256,
    "metadata_audit_is_not_runtime_or_g2_acceptance": True,
}
G2_DEPENDENCY_LIMITS = (
    "only the exact requirements change and fixed compatibility-test addition are eligible",
    "the requirements candidate digest is fixed; the test addition must be absent at the predecessor",
    "the accepted production-profile publication and every earlier latch remain historical",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no runtime, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_dependency_repair", "repair_g2_dependency_repair"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_dependency_repair"}
OPERATION_PATHS.update(enable_g2_dependency_repair=G2_DEPENDENCY_MAINTENANCE_PATHS,
                       repair_g2_dependency_repair=G2_DEPENDENCY_PATHS)


G2_CI_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v13"
G2_CI_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v13"
G2_CI_CODE_PATHS = G2_DEPENDENCY_CODE_PATHS
G2_CI_PATHS = frozenset(raisa_policy.G2_CI_SELECTION_PATHS)
G2_CI_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_CI_CODE_PATHS
G2_CI_EFFECTS = G2_BATCH_EFFECTS
G2_CI_PREDECESSOR = {
    "commit": "aeae8084c3905fe250a2e7f58b78edd4e995e2f3",
    "parent": "ef11f276baeca15ebb6c084bbe4db274ec6c6c36",
    "tree": "b7f41b6bd8ec425da205f033268e068262025010",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "baf28b70c8545e0ea5d16c89c421c2a4be66aa84e9ae06b70dfee32db5ec0fe6",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "d0fbb43722ea27429806a1ee1cebe66f4b64a1192103bb0cd2e34794a7dbce2d",
        "tests/test_bounded_g1b.py": "3e53c0bd33a3b0bf24e779a697d4d3cde406ea77166ed6a531a686c7e932eca6",
    },
}
G2_CI_PREDECESSOR_POLICY = {
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    STATE: "5e5f483646cb1c433332da23568abd8f9fb5f41852b04e82959df33c2984b5b6",
    OVERLAY: "e4785e1e976080ebdc6726a43a177473c6b9dac5cd6d3adcec3fbabe9c02036e",
    G2_SCOPE: "03ed6ce100aa76b764ced54322bc4c34a4b7e0aa567901c47b0fc00e09145152",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_CI_REPAIR_PINS = {
    "scripts/verify_repository.py": "f491dd7ac2222de4a9493ba43a6144726f85a586d8398947a83a7c0f9c8d4c83",
    "scripts/python_source_state.py": "202f9b7c733eac0eba00b453013e65590c18c2c2dc8bfb008bf097b26045cfeb",
    "orchestration/harness_settings/python_source_state.json": "56e909a248efb2eda3f6c922ee6da4950309b43cb803da05fd10fd2263bf4b09",
    "scripts/security_bandit_gate.py": "5353eef7198ae51d36cefa0842a1c8458326bb792818c0d1d28809b71dac3eef",
    "scripts/historical_diary_leakage_lint.py": "91ca85a069cfe18d435c89853ce68a5b63ccb5d1f9ea3a4ed35638ceaa3625c2",
    "tests/test_python_source_state.py": "b97fd5a1ddb5c58aabaea0c005b5200e01ae6f5e8f23acbe77dbce69adc07913",
    "tests/test_repository_maintenance.py": "e18101b509d5be9b70014604436882578f59328a8c8b114160bd08152af90412",
}
G2_CI_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/dependency-product-publication-v1/independent-publication-effect-review-v1.json",
    "sha256": "3668084ae65e572c95f712af3fdadb2dd55bb40827c5e97bc99a0a0c34a1b5ef",
    "role": "opaque_historical_dependency_publication_acceptance_not_operation_authority",
}
G2_CI_INVARIANT = {
    "literal_file_count": 7,
    "verification_runtime_changed": False,
    "repository_wide_complete": False,
    "ci_b_and_g2_acceptance_claimed": False,
    "tool_and_runtime_binding_separately_required": True,
}
G2_CI_LIMITS = (
    "only the exact seven verification-selection files are eligible",
    "all seven committed preimages are fixed and every candidate digest belongs in the reviewed binding",
    "the accepted dependency publication and every earlier latch remain historical",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no runtime, whole-repository CI, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_ci_selection", "repair_g2_ci_selection"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_ci_selection"}
OPERATION_PATHS.update(enable_g2_ci_selection=G2_CI_MAINTENANCE_PATHS,
                       repair_g2_ci_selection=G2_CI_PATHS)


G2_CIM_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v14"
G2_CIM_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v14"
G2_CIM_CODE_PATHS = G2_CI_CODE_PATHS
G2_CIM_PATHS = frozenset(raisa_policy.G2_CI_MIGRATION_PATHS)
G2_CIM_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_CIM_CODE_PATHS
G2_CIM_EFFECTS = G2_BATCH_EFFECTS
G2_CIM_PREDECESSOR = {'parent': '826ac77d825e646b83dec0c6083e56c686007457', 'tree': '7ec765cd5d01e846ff54a08c6a5e1de7ffc0e6bc', 'commit': 'eb989f5e0e3a46f7ad51a2f8b2365cf7b6605a5f', 'source_sha256': {'orchestration_harness/bounded_g1b.py': 'a119d66e275265e571cf49c6d7bc5d0ee82a3dd3b34d33bcc32771032a70d6e6', 'orchestration_harness/configuration_core.py': 'f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5', 'orchestration_harness/programme_admission.py': 'ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181', 'orchestration_harness/raisa_policy.py': 'd63d99eb0633080d112e408e336291bf74732ae0151e088acbd6891e14ffd421', 'tests/test_bounded_g1b.py': 'ce440cc7f724f81973034eacde256c393b568bca1f6d37980084aeabae60f70f'}}
G2_CIM_PREDECESSOR_POLICY = {
    AGENTS: '97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e',
    STATE: '44faf6f11b15d61b3c318bb2a5239aa688918053f6e8a1c508844e47f84c2ad5',
    OVERLAY: 'b69f301d8c16843caaaaf1ccbb486493243e25270a6e9bd47d0f8e4746e76804',
    G2_SCOPE: 'ec504c3d944666f9bfbeacde11f88aaf731dacbccbfca73af38b1b9d96df6350',
    GATES: '115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341',
}
G2_CIM_REPAIR_PINS = {'scripts/verify_empty_database_migrations.py': 'ac514418f77672defbf0844c28ceae4e83391d207eabdff8f01253acfb0731e9', 'tests/test_repository_maintenance.py': '5e31ef3b71f04bf27dd5f09d9e0add39b614c3c78fb7293394e2b3daad99bbbb'}
G2_CIM_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-a-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json",
    "sha256": "ca9864fd2020afe1575d44634826f36f4f12d1781a5ad04b43337d16eb775ef5",
    "role": "opaque_historical_ci_selection_publication_acceptance_not_operation_authority",
}
G2_CIM_INVARIANT = {
    "literal_file_count": 2,
    "explicit_owned_disposable_database_required": True,
    "primary_and_cleanup_outcomes_separate": True,
    "total_deadline_includes_cleanup_reserve": True,
    "verification_runtime_changed": False,
    "migration_schema_changed": False,
    "runtime_binding_separately_required": True,
    "repository_wide_and_g2_acceptance_claimed": False,
}
G2_CIM_LIMITS = (
    "only the exact migration-verification helper and its existing maintenance tests are eligible",
    "both committed preimages are fixed and every candidate digest belongs in the reviewed binding",
    "the accepted CI selection publication and every earlier latch remain historical",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no runtime, migration-schema change, whole-repository CI, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_ci_migration", "repair_g2_ci_migration"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_ci_migration"}
OPERATION_PATHS.update(enable_g2_ci_migration=G2_CIM_MAINTENANCE_PATHS,
                       repair_g2_ci_migration=G2_CIM_PATHS)


G2_TENANT_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v15"
G2_TENANT_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v15"
G2_TENANT_CODE_PATHS = G2_BATCH_CODE_PATHS
G2_TENANT_PATHS = frozenset(raisa_policy.G2_TENANT_MIGRATION_PATHS)
G2_TENANT_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_TENANT_CODE_PATHS
G2_TENANT_EFFECTS = EFFECTS | {"migration_change"}
G2_TENANT_PREDECESSOR = {
    "commit": "28ce5f5d8489cf43508da22f6f819343bf7ff3c6",
    "parent": "911669f9d8090a386734e84f90b1ec10a9020857",
    "tree": "9d2efb67aaaa9d41a7ac2dc198082a8afadaa074",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "a6262b3258d4ad5f5143c2d5e6b5c3e0a06b015cf2458aa2a780db0e0e2d88df",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "6cf58cff8458ba38f67e8b437996c8e65b613a933d8ce53cd9388c2b57a6935e",
        "tests/test_bounded_g1b.py": "ba527e56b9445e035f2ca607452d513b4665a95fe6e982ff702d7a3de232e540",
    },
}
G2_TENANT_PREDECESSOR_POLICY = {
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    STATE: "ab686fece7b243b33d1eebe5c2e49fe814066b61f91c4d6fcf2757c85fa49d2e",
    OVERLAY: "ee580358b410aa9bfb02870f4014357931ec0f510d86b2fcdd11bc317a6638e2",
    G2_SCOPE: "c0c651d1abe6c51e5199cd334dd29a4f23be6b70555b6b44a911e42a06bb9fb7",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_TENANT_REPAIR_PINS = {path: None for path in G2_TENANT_PATHS}
G2_TENANT_CANDIDATE_PINS = {
    "alembic/versions/z5a6b7c8d9e0_enforce_clinical_tenant_rls.py":
        "bdd401fc08f4ba102a30804b9c0b3f68d1ba405ef695d47874ef5d8e69b4dfe8",
    "tests/test_tenant_isolation.py":
        "13461a2895db56100d73e6e316d07caaa13c14039c277012b7e05e6fb27c87f3",
}
G2_TENANT_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-b-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json",
    "sha256": "0487de4cc7797523b88263a9d3408262dfb0bfdad59880917553e1d340a3ab63",
    "role": "opaque_historical_ci_migration_publication_acceptance_not_operation_authority",
}
G2_TENANT_INVARIANT = {
    "literal_file_count": 2,
    "creation_only": True,
    "migration_schema_changed": True,
    "existing_files_changed": False,
    "candidate_sha256": dict(G2_TENANT_CANDIDATE_PINS),
    "runtime_binding_separately_required": True,
    "repository_wide_and_g2_acceptance_claimed": False,
}
G2_TENANT_LIMITS = (
    "only the exact new tenant-isolation migration and test are eligible",
    "both additions must be absent at the accepted predecessor and match the reviewed candidate digests",
    "the accepted CI migration publication and every earlier latch remain historical",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no database runtime, whole-repository CI, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_tenant_migration", "repair_g2_tenant_migration"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_tenant_migration"}
OPERATION_PATHS.update(enable_g2_tenant_migration=G2_TENANT_MAINTENANCE_PATHS,
                       repair_g2_tenant_migration=G2_TENANT_PATHS)


G2_RELATIONSHIP_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v16"
G2_RELATIONSHIP_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v16"
G2_RELATIONSHIP_CODE_PATHS = G2_BATCH_CODE_PATHS
G2_RELATIONSHIP_PATHS = frozenset(raisa_policy.G2_TENANT_RELATIONSHIP_PATHS)
G2_RELATIONSHIP_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_RELATIONSHIP_CODE_PATHS
G2_RELATIONSHIP_EFFECTS = EFFECTS | {"migration_change"}
G2_RELATIONSHIP_PREDECESSOR = {
    "commit": "7026ea069600471c1c0a7c7c4fd0d0b806184e4a",
    "parent": "d7b2c443fdef3c12d0bc934e4d17e6d3baa06b9f",
    "tree": "e9576dcdc219b94432fd9f211881a11e2bbacfe1",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "eebc18b64caf116bf82129dd44517e9004e09bb74c67f36bdf7c603a85709716",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "63d6e39e3605eb06045849e38fdcdb5f5826c3cd0f3758e177234c9e8acd6937",
        "tests/test_bounded_g1b.py": "0dc0b4c491a7b781a5a1f7785fffaabde9a45d7ac8c08f4517121b72b2f6523d",
    },
}
G2_RELATIONSHIP_PREDECESSOR_POLICY = {
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    STATE: "b95c28a1023b7f3ddc54978ce15ad0aa6ded0cd0bb89bfa42e9fe76b7af618bb",
    OVERLAY: "df50c163b0c74f9bd32c8949824597b7d25ec6f6ebd50a951d0c02e2c1595515",
    G2_SCOPE: "7266cf18ed8bc881a6c589fbdbb8e953a9187c21922de1cfb9cb8bb56fe2c8ed",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_RELATIONSHIP_REPAIR_PINS = {path: None for path in G2_RELATIONSHIP_PATHS}
G2_RELATIONSHIP_CANDIDATE_PINS = {
    "alembic/versions/a6b7c8d9e0f1_enforce_related_practice_refs.py":
        "ffce11266c8f09b6e2327d58999d61e4e7c453e5fcc41d63759be87009004a8f",
    "tests/test_tenant_relationships.py":
        "73a66852fd94022788ceec670148ffc0a6934037f7bfd0c0b448936ef13691e4",
    "tests/tenant_relationship_helpers.py":
        "befcd507d0563d28fc51ef0fe77359c0326095923fe9c49c88b19c4daa70c123",
}
G2_RELATIONSHIP_PRESERVED_TENANT_PINS = dict(G2_TENANT_CANDIDATE_PINS)
G2_RELATIONSHIP_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-c-preparation-v1/tenant-migration-candidate-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json",
    "sha256": "76088b8ca820bf5acfd9cb56aa1a7a4cc2d932bca9f122f7bc2b93fb03af3188",
    "role": "opaque_historical_tenant_migration_publication_acceptance_not_operation_authority",
}
G2_RELATIONSHIP_INVARIANT = {
    "literal_file_count": 3,
    "creation_only": True,
    "migration_schema_changed": True,
    "existing_files_changed": False,
    "test_helper_included": True,
    "candidate_sha256": dict(G2_RELATIONSHIP_CANDIDATE_PINS),
    "runtime_binding_separately_required": True,
    "repository_wide_and_g2_acceptance_claimed": False,
}
G2_RELATIONSHIP_LIMITS = (
    "only the exact new same-practice migration, acceptance test and helper are eligible",
    "all three additions must be absent at the accepted predecessor and match reviewed candidate digests",
    "the accepted tenant migration publication and every earlier latch remain historical",
    "one reviewed batch is eligible; operational multi-task acceptance remains false",
    "admission grants no database runtime, whole-repository CI, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_tenant_relationships", "repair_g2_tenant_relationships"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_tenant_relationships"}
OPERATION_PATHS.update(enable_g2_tenant_relationships=G2_RELATIONSHIP_MAINTENANCE_PATHS,
                        repair_g2_tenant_relationships=G2_RELATIONSHIP_PATHS)


G2_COMPLETENESS_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v17"
G2_COMPLETENESS_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v17"
G2_COMPLETENESS_CODE_PATHS = G2_BATCH_CODE_PATHS
G2_COMPLETENESS_PATHS = frozenset(raisa_policy.G2_CI_COMPLETENESS_PATHS)
G2_COMPLETENESS_MAINTENANCE_PATHS = G2_BATCH_CONTROL_PATHS | G2_COMPLETENESS_CODE_PATHS
G2_COMPLETENESS_EFFECTS = G2_BATCH_EFFECTS
G2_COMPLETENESS_PREDECESSOR = {
    "commit": "1230bb8201d0fcca69777663c37a868d626b312f",
    "parent": "3eb64c6a3783b50e69aa6224d37647421eeb6356",
    "tree": "066494d6d6942ca8c0a739b0218f881223d72eb5",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "c8fe4b34da965335ab5aded61da87c5b7fc273c320edbaf78c8e4e923ae34bac",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
        "orchestration_harness/raisa_policy.py": "1b3ccb52c73d650d2bcc72fa19c7f9a55dba06060a49dee762950c89553670d4",
        "tests/test_bounded_g1b.py": "d6f09fb547f30e6463bb3565ad552dcd41ad223bf580a3cf679f3e6dc75930df",
    },
}
G2_COMPLETENESS_PREDECESSOR_POLICY = {
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    STATE: "4bb258ce435c50d765ac040401ae23d500aaaab1da4bbaa047078505b2e1bf1c",
    OVERLAY: "52909e9830920ace93bcd00c3edf615401818322fe94658c003d95c140696b3b",
    G2_SCOPE: "74bcee3dec174930012edd2b34d8e098be4b2f16d8822bace2f96b4b6884f626",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_COMPLETENESS_REPAIR_PINS = {
    "scripts/python_source_state.py": "f7e77f2785dc1b405fdaa038acff494ad27a6a005754aa5ee43665dd92ad2aa5",
    "scripts/verify_repository.py": "da5477e5036d10a7813d7d5384ebd66fe20c98aa3acf4a555d1f87112220cce3",
    "tests/test_python_source_state.py": "6e17f4682b9ff65ae9aabab6b2d2b436d8496784acc3496c961e5bcdfb21ab29",
}
G2_COMPLETENESS_CANDIDATE_PINS = {
    "scripts/python_source_state.py": "deda2e86f7a6cfc1f8da56e45dc420c896a24749324e326cfc54e576e11528de",
    "scripts/verify_repository.py": "51d9e529c7f8846b0beb41cfacd95ae816577fffdb87f189b1739d64121ac8e5",
    "tests/test_python_source_state.py": "3c7fdefb9aeae9defc1208948083533da3a8531f9664e4538ca3a781e223163d",
}
G2_COMPLETENESS_PRESERVED_RELATIONSHIP_PINS = dict(G2_RELATIONSHIP_CANDIDATE_PINS)
G2_COMPLETENESS_PUBLICATION_ACCEPTANCE = {
    "path": "C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-c-preparation-v1/tenant-relationship-repair-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json",
    "sha256": "d3676fee74afcdd17f78333c23c6ca4f3d7e98d26fe3d5d39c575ccc7da982fa",
    "role": "opaque_historical_relationship_publication_acceptance_not_operation_authority",
}
G2_COMPLETENESS_INVARIANT = {
    "literal_file_count": 3,
    "existing_files_changed": True,
    "allowed_additions": [],
    "candidate_sha256": dict(G2_COMPLETENESS_CANDIDATE_PINS),
    "complete_ci_claimed": False,
    "bounded_ci_remains_eligible": True,
    "runtime_binding_separately_required": True,
}
G2_COMPLETENESS_LIMITS = (
    "only three exact existing CI source and test files may change",
    "a complete-CI claim without a complete ordinary source population must fail closed",
    "bounded selected CI checks remain eligible without asserting repository-wide coverage",
    "the accepted relationship publication and every earlier latch remain historical",
    "admission grants no whole-CI success, database runtime, G2 completion, provider, real-data, protected-evidence or deployment acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_ci_completeness", "repair_g2_ci_completeness"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_ci_completeness"}
OPERATION_PATHS.update(enable_g2_ci_completeness=G2_COMPLETENESS_MAINTENANCE_PATHS,
                       repair_g2_ci_completeness=G2_COMPLETENESS_PATHS)


# V18 is a separate exact PyJWT successor; consumed V12 and V17 remain intact.
G2_PYJWT_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v18"
G2_PYJWT_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v18"
G2_PYJWT_PREDECESSOR = {
    "commit": "387a472f9c08fcedb8269a4ed60be4ac00a7ce01",
    "parent": "3e6722d04438265834a9a36c17c61de68552cfa6",
    "tree": "4fd151118f18b101692f529d9a62624b74619257",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "1d46654b5aec960c13968dd787b221883c75ba85591d9c5c752e24e5995f65fa",
        "orchestration_harness/raisa_policy.py": "1f1024ef88a20be9f4c78b05f196bc318e65380ab3faf751551bc33449df0de1",
        "tests/test_bounded_g1b.py": "ea85511138fa3720871a2b4a9e9f8cf1f41d2fcca394c068529fadf9345ada53",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181"
    }
}
G2_PYJWT_PREDECESSOR_POLICY = {
    "AGENTS.md": "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    "orchestration/programme/current-state.json": "00db434a907723764b6dfb9e2d80c2e0217f4d511e72eee0e7f38dfdb765d9b9",
    "orchestration/harness_settings/programme_recovery.yaml": "2989f1372fc7d28a07a2d0b5e5a67384a30b99d4e95c1ba30a71720efbb0f1f0",
    "orchestration/programme/g2-baseline-repair-scope.json": "a0ad9df4ea4aa4768b934bee74f042ca0a92f7282941bb9b2cc0557d13d6a280",
    "orchestration/programme/gates.yaml": "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341"
}
G2_PYJWT_REPAIR_PINS = {
    "requirements.txt": "47d852c442ea25c041aa70fca5dff01846fd18f3eebfa3c7d288aec3e0a54b90",
    "tests/test_dependency_compatibility.py": "249eeeb3e506691cdcf608a5ef42671b6a5244a37aed55693bc541f73d78861b"
}
G2_PYJWT_CANDIDATE_PINS = {
    "requirements.txt": "420960358508eb631081b578e972e22b42807e4fc58c362997620e4c4656d82b",
    "tests/test_dependency_compatibility.py": "253be1556dafd34d06bd72746d0426c245c4763e8f860bd84c8d90e84ec67f8e"
}
G2_PYJWT_PRIOR_CI_SCOPE = json.loads("{\"allowed_additions\":[],\"allowed_effects\":[\"control_plane_edit\",\"product_behavior_change\",\"repository_read\",\"task_branch_commit\",\"task_branch_push\"],\"allowed_paths\":[\"scripts/python_source_state.py\",\"scripts/verify_repository.py\",\"tests/test_python_source_state.py\"],\"appointment_concurrency_invariant\":{\"insertion_order_independent\":true,\"location_independent\":true,\"null_location_included\":true,\"overlap\":\"half_open_intervals_overlap_when_each_start_is_before_the_other_end\",\"scope\":\"same_practice_same_practitioner_blocking_appointments\",\"tenant_scope_preserved\":true},\"candidate_authority\":\"independently_reviewed_exact_operation_binding\",\"ci_completeness_invariant\":{\"allowed_additions\":[],\"bounded_ci_remains_eligible\":true,\"candidate_sha256\":{\"scripts/python_source_state.py\":\"deda2e86f7a6cfc1f8da56e45dc420c896a24749324e326cfc54e576e11528de\",\"scripts/verify_repository.py\":\"51d9e529c7f8846b0beb41cfacd95ae816577fffdb87f189b1739d64121ac8e5\",\"tests/test_python_source_state.py\":\"3c7fdefb9aeae9defc1208948083533da3a8531f9664e4538ca3a781e223163d\"},\"complete_ci_claimed\":false,\"existing_files_changed\":true,\"literal_file_count\":3,\"runtime_binding_separately_required\":true},\"ci_selection_invariant\":{\"ci_b_and_g2_acceptance_claimed\":false,\"literal_file_count\":7,\"repository_wide_complete\":false,\"tool_and_runtime_binding_separately_required\":true,\"verification_runtime_changed\":false},\"claim_limits\":[\"only three exact existing CI source and test files may change\",\"a complete-CI claim without a complete ordinary source population must fail closed\",\"bounded selected CI checks remain eligible without asserting repository-wide coverage\",\"the accepted relationship publication and every earlier latch remain historical\",\"admission grants no whole-CI success, database runtime, G2 completion, provider, real-data, protected-evidence or deployment acceptance\"],\"clinical_authority_contract\":{\"active_authenticated_user_required\":true,\"active_linked_same_practice_practitioner_required\":true,\"admission_grants_runtime_authority\":false,\"attestation_audit\":{\"ai_invocation_claimed\":false,\"audit_failure_rolls_back_all_clinical_rows\":true,\"capability\":null,\"client_hash_accepted\":false,\"content_hash\":\"server_sha256_sorted_compact_utf8_json_effective_saved_projection\",\"decision\":\"recorded\",\"event_type\":\"clinical.consultation.attested\",\"metadata_keys\":[\"attested\",\"normalization_policy_id\",\"patient_id\",\"practitioner_id\",\"reviewed_content_sha256\",\"server_policy_id\"],\"metadata_type_equality\":\"strict_including_attested_is_True_not_1_equals_True\",\"method\":null,\"normalization_policy_id\":\"emr4.clinical-finalization.saved-projection.v1\",\"raw_clinical_text_or_document_url_metadata\":false,\"server_policy_id\":\"emr4.clinical-finalization.gp-linked-practitioner.v1\",\"source_surface\":\"api\",\"target_resource_type\":\"encounter\",\"typed_fields\":[\"event_id\",\"correlation_id\",\"actor_user_id\",\"actor_roles\",\"practice_id\",\"event_timestamp\",\"event_type\",\"decision\",\"source_surface\",\"capability\",\"method\",\"target_resource_type\",\"target_resource_id\"]},\"attestation_transport\":{\"client_role_or_practitioner_fields_confer_authority\":false,\"false\":\"reject_403_before_clinical_writes\",\"field\":\"clinician_attested\",\"missing_or_non_boolean\":\"reject_422\",\"only_literal_true_authorizes\":true,\"required\":true,\"type\":\"strict_json_boolean\"},\"authority_transaction\":{\"authorization_and_document_binding_before_writes\":true,\"flush_unique_receipt_before_clinical_rows\":true,\"fresh_command_owned_session\":true,\"integrity_conflict_handling\":{\"automatic_retry\":false,\"fresh_scope_recheck_after_rollback\":true,\"rollback_before_classification\":true},\"lock_and_recheck_order\":[\"User\",\"Practitioner\",\"Patient\"],\"locks_held_through_receipt_clinical_and_audit_commit\":true,\"postgresql_isolation_level\":\"READ COMMITTED\",\"preallocate_Encounter_uuid_before_receipt\":true,\"provider_or_await_work_inside_transaction\":false,\"receipt_and_clinical_rows_one_transaction\":true,\"transaction_local_practice_context\":true},\"canonical_saved_projection\":{\"built_once_after_strict_validation\":true,\"hash_projection_fields\":[\"normalization_policy_id\",\"patient_id\",\"document_id\",\"exact_document_context\",\"effective_consultation_type\",\"clinical_text\",\"canonical_child_dtos\"],\"normalization_policy_id\":\"emr4.clinical-finalization.saved-projection.v1\",\"raw_clinical_text_or_document_url_in_audit\":false,\"same_projection_for\":[\"clinical_row_values\",\"reviewed_content_sha256\",\"successful_response\",\"matching_replay_response\"],\"successful_response\":{\"_saved\":true,\"fields\":[\"encounter_id\",\"generated_clinical_note\"],\"matching_replay_is_exactly_equal\":true}},\"clinical_rows_and_typed_attestation_audit_one_commit\":true,\"explicit_clinician_attestation_required\":true,\"fresh_command_transaction_authority_recheck_required\":true,\"g2_completion_claimed\":false,\"idempotency_receipt\":{\"command_document_id\":\"canonical_uuid_distinct_from_word_identity\",\"event_id\":{\"algorithm\":\"server_uuidv5\",\"canonical_name\":\"{name_prefix}:{canonical_practice_uuid}:{canonical_document_id_uuid}\",\"client_event_id_accepted\":false,\"name_prefix\":\"emr4.clinical-finalization.receipt.v1\",\"namespace_uuid\":\"7b56fb23-fdc5-5bd9-951f-80a7b9b94b2e\"},\"matching_content_replay\":{\"additional_audit_writes\":false,\"additional_clinical_writes\":false,\"same_response_projection\":true},\"mismatch_or_corruption\":{\"generic_indistinguishable_response\":true,\"status\":409},\"receipt_fields\":{\"actor_roles\":[\"GP\"],\"actor_user_id\":\"fresh_authenticated_User.id\",\"capability\":null,\"correlation_id\":\"canonical_document_id_uuid\",\"decision\":\"recorded\",\"event_id\":\"server_uuidv5_receipt_event_id\",\"event_timestamp\":\"timezone_aware_server_timestamp\",\"event_type\":\"clinical.consultation.attested\",\"metadata\":{\"attested\":true,\"normalization_policy_id\":\"emr4.clinical-finalization.saved-projection.v1\",\"patient_id\":\"freshly_locked_Patient.id\",\"practitioner_id\":\"freshly_locked_Practitioner.id\",\"reviewed_content_sha256\":\"server_computed_canonical_projection_hash\",\"server_policy_id\":\"emr4.clinical-finalization.gp-linked-practitioner.v1\"},\"method\":null,\"practice_id\":\"fresh_transaction_practice_id\",\"source_surface\":\"api\",\"target_resource_id\":\"preallocated_Encounter.id\",\"target_resource_type\":\"encounter\"},\"retention_and_schema\":{\"bounded_finalization_path_never_updates_or_deletes_receipt\":true,\"database_immutability_enforced\":false,\"database_retention_enforced\":false,\"detectable_receipt_or_target_corruption\":\"generic_409_no_writes\",\"guarantee_scope\":\"bounded_synthetic_retained_records_only\",\"known_receipt_loss_or_mutation\":\"stop_no_retry_pending_separate_repair_and_review\",\"production_durable_idempotency_accepted\":false,\"receipt_loss_or_undetectable_mutation_outside_accepted_guarantee\":true,\"receipt_retention_required_for_replay\":true,\"schema_migration_required\":false},\"storage\":{\"existing_database_unique_constraint\":true,\"model\":\"AccessAiAuditLog\",\"unique_column\":\"event_id\"},\"target_validation\":{\"actor_practice_patient_practitioner_and_hash_must_match\":true,\"command_id_must_match_correlation_id\":true,\"matched_core_fields\":[\"id\",\"practice_id\",\"patient_id\",\"practitioner_id\",\"status\"],\"metadata_values_and_types_must_match\":true,\"resource_must_be_finalized_Encounter\":true,\"status\":\"finalized\"},\"typed_field_requirements\":{\"capability\":null,\"correlation_id\":\"UUID\",\"event_id\":\"UUID\",\"event_timestamp\":\"timezone_aware_datetime\",\"method\":null}},\"no_administrative_or_nurse_bypass\":true,\"owner_decision\":{\"evidence_path\":\"g2-clinical-policy/owner-policy.json\",\"sha256\":\"c67d52473f6255758ea444e07b8e3ccce683cc5676ecb8a220c37f98f42bbd2f\"},\"practitioner_attribution\":{\"Encounter.practitioner_id\":\"server_resolved_Practitioner.id\",\"MbsClaim.Submitted\":\"internal_synthetic_database_state_only\",\"MbsClaim.practitioner_id\":\"server_resolved_Practitioner.id\",\"Prescription.prescribed_by\":\"server_resolved_Practitioner.id\",\"real_billing_submission_policy_accepted\":false,\"source\":\"fresh_active_same_practice_User.practitioner_id\"},\"raw_clinical_text_in_audit_metadata\":false,\"real_clinical_operation_authorized\":false,\"roles\":[\"GP\"],\"runtime_scope\":\"isolated_synthetic_development_only\",\"semantic_version\":\"v8\",\"server_owned_practitioner_and_prescriber_identity\":true,\"source_revision\":4,\"synthetic_staff_practitioners_and_patients_standing_authority\":{\"ai_is_clinician_or_attester\":false,\"appropriate_to_active_reviewed_scope\":true,\"existing_independent_review_and_finite_runtime_budgets_preserved\":true,\"fictional_entities_only\":true,\"permitted_entities\":[\"fictional_staff\",\"fictional_practitioners\",\"fictional_patients\"],\"persistent\":true,\"real_identity_or_professional_credential_claim\":false},\"taskpane_confirmation\":{\"ai_does_not_authorize\":true,\"ambiguous_retry\":{\"fresh_confirmation_required\":true,\"same_exact_command_snapshot_required\":true,\"silent_or_automatic_retry\":false},\"cancel_or_unavailable_confirmation_sends_nothing\":true,\"command_centre_interlock\":{\"opening_blocked_while\":[\"consultation_start\",\"consultation_finalization\",\"ambiguous_submitted_snapshot\"],\"taskpane_finalization_blocked_while_command_centre_open\":true},\"confirmed_response\":{\"empty_or_arbitrary_string\":\"reject\",\"encounter_id\":\"canonical_uuid_string\"},\"explicit_personal_clinician_review_and_authorization\":true,\"invalidate_prior_binding_before_patient_await\":true,\"one_shot_confirmation_of_exact_request_snapshot\":true,\"patient_document_url_getter\":{\"failure\":\"cancel_without_request\",\"fallback_or_synthetic_url\":false,\"real_getter_required\":true},\"patient_or_reviewed_content_change_requires_fresh_confirmation\":true,\"patient_or_session_change_during_word_read_cancels_request\":true,\"per_binding_in_flight_guard\":true,\"per_start_binding\":{\"boundary_markers\":{\"date_or_age_prose_is_never_a_boundary\":true,\"fail_closed_if_end_missing_duplicate_invalid_or_crosses_section\":true,\"insert_both_for_each_new_consult\":true,\"legacy_regex_fallback_for_new_consults\":false,\"paragraph_selection\":\"all_and_only_strictly_between_exact_markers\",\"same_document_id_uuid_required\":true,\"uuid_bound_end_marker\":true,\"uuid_bound_start_marker\":true},\"exact_document_context_url\":true,\"new_full_canonical_document_id_uuid\":true},\"reusable_attestation_state\":false,\"second_read_mismatch\":\"cancel_without_request\",\"second_word_and_form_read_after_confirmation\":true},\"typed_finalization_request\":{\"declared_aliases\":{\"both_present\":\"require_exact_equal_values\",\"conflict\":\"reject_422\",\"implicit_or_undeclared_aliases\":false},\"document_context\":{\"extra_fields\":\"forbid\",\"must_exactly_match_freshly_locked_Patient.document_url\":true,\"required\":true,\"strip_or_normalize_url\":false,\"url\":\"strict_nonblank_string\",\"url_max_length\":2048,\"url_scheme\":\"http_or_https\"},\"document_id\":{\"client_generated_per_start\":true,\"distinct_from_word_document_identity\":true,\"required\":true,\"type\":\"canonical_uuid_string\",\"word_identity_confers_command_authority\":false},\"maximum_items_per_nested_list\":100,\"maximum_lengths\":{\"clinical_text\":100000,\"consultation_type\":255,\"diagnosis_code\":50,\"diagnosis_term\":255,\"mbs_description\":2048,\"mbs_item_number\":10,\"medication_dose\":2048,\"medication_drug\":255},\"nested_dto_extra_fields\":\"forbid\",\"strings\":\"strict_nonblank_required_without_coercion\"}},\"controller_source_sha256\":{\"orchestration_harness/bounded_g1b.py\":\"1d46654b5aec960c13968dd787b221883c75ba85591d9c5c752e24e5995f65fa\",\"orchestration_harness/configuration_core.py\":\"f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5\",\"orchestration_harness/programme_admission.py\":\"ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181\",\"orchestration_harness/raisa_policy.py\":\"1f1024ef88a20be9f4c78b05f196bc318e65380ab3faf751551bc33449df0de1\",\"tests/test_bounded_g1b.py\":\"ea85511138fa3720871a2b4a9e9f8cf1f41d2fcca394c068529fadf9345ada53\"},\"current_instruction_policy\":{\"authority\":\"owner_requested_worker_allocation_parallel_delivery_identity_relay_and_compaction_rehydration_update\",\"path\":\"AGENTS.md\",\"previous_sha256\":\"93ebf50187b6132fcee91cee7f4ba0b81bb59286ed9eaf52cdadab3a09ba20c1\",\"sha256\":\"97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e\"},\"current_operation\":{\"completion_accepted\":false,\"operation_id\":\"g2-ci-completeness-repair\",\"profile\":\"G2_BASELINE_REPAIR_ACTIVE\",\"status\":\"active\",\"supersedes\":{\"historical_latch_preserved\":true,\"operation_id\":\"g2-tenant-relationship-repair\",\"scope_commit\":\"1230bb8201d0fcca69777663c37a868d626b312f\",\"scope_path\":\"orchestration/programme/g2-baseline-repair-scope.json\",\"scope_sha256\":\"74bcee3dec174930012edd2b34d8e098be4b2f16d8822bace2f96b4b6884f626\"},\"task_class\":\"g2_confirmation_family_fixture_repair\"},\"dependency_invariant\":{\"all_other_24_roots_unchanged\":true,\"compatibility_test_path\":\"tests/test_dependency_compatibility.py\",\"metadata_audit_is_not_runtime_or_g2_acceptance\":true,\"requirements_after_sha256\":\"47d852c442ea25c041aa70fca5dff01846fd18f3eebfa3c7d288aec3e0a54b90\",\"requirements_worktree_before_sha256\":\"56426e781c912feb3ad569a250f060a9584bfc6a13512db68b2c6396748b7e6b\",\"root_change\":{\"after\":\"50.0.1\",\"before\":\"48.0.1\",\"package\":\"cryptography\"}},\"enable_operation\":\"enable_g2_ci_completeness\",\"execution_authorized\":false,\"existing_clockwork_writers_activated\":false,\"feature_work_eligible\":false,\"forbidden_effects\":[\"autonomous_worker_dispatch\",\"dependency_change\",\"deployment\",\"existing_clockwork_runtime_mutation\",\"integration\",\"migration_change\",\"pages\",\"protected_ref_movement\",\"provider_invocation\",\"real_data_access\"],\"g1e_complete\":true,\"g2_complete\":false,\"g2_exit_requirements\":[\"repository_wide_collection_and_tests_pass\",\"required_application_migration_and_safety_ci\",\"dependency_audit_pass_or_explicit_exception\",\"destructive_migration_removed\",\"empty_and_populated_alembic_paths_pass\",\"no_public_audio_or_phi_path\",\"no_implicit_patient\",\"cross_tenant_tests_application_and_database_pass\",\"appointment_concurrency_database_enforced\",\"ai_outputs_draft_until_human_attestation\",\"production_profile_excludes_dev_hosts_and_browser_bearer_storage\",\"no_unresolved_critical_or_high_stop_ship_risk\"],\"global_gate\":\"red_repair_only\",\"historical_ci_migration_invariant\":{\"explicit_owned_disposable_database_required\":true,\"literal_file_count\":2,\"migration_schema_changed\":false,\"primary_and_cleanup_outcomes_separate\":true,\"repository_wide_and_g2_acceptance_claimed\":false,\"runtime_binding_separately_required\":true,\"total_deadline_includes_cleanup_reserve\":true,\"verification_runtime_changed\":false},\"historical_relationship_invariant\":{\"candidate_sha256\":{\"alembic/versions/a6b7c8d9e0f1_enforce_related_practice_refs.py\":\"ffce11266c8f09b6e2327d58999d61e4e7c453e5fcc41d63759be87009004a8f\",\"tests/tenant_relationship_helpers.py\":\"befcd507d0563d28fc51ef0fe77359c0326095923fe9c49c88b19c4daa70c123\",\"tests/test_tenant_relationships.py\":\"73a66852fd94022788ceec670148ffc0a6934037f7bfd0c0b448936ef13691e4\"},\"creation_only\":true,\"existing_files_changed\":false,\"literal_file_count\":3,\"migration_schema_changed\":true,\"repository_wide_and_g2_acceptance_claimed\":false,\"runtime_binding_separately_required\":true,\"test_helper_included\":true},\"historical_relationship_operation\":{\"completion_accepted\":false,\"operation_id\":\"g2-tenant-relationship-repair\",\"profile\":\"G2_BASELINE_REPAIR_ACTIVE\",\"status\":\"active\",\"supersedes\":{\"historical_latch_preserved\":true,\"operation_id\":\"g2-tenant-migration-repair\",\"scope_commit\":\"7026ea069600471c1c0a7c7c4fd0d0b806184e4a\",\"scope_path\":\"orchestration/programme/g2-baseline-repair-scope.json\",\"scope_sha256\":\"7266cf18ed8bc881a6c589fbdbb8e953a9187c21922de1cfb9cb8bb56fe2c8ed\"},\"task_class\":\"g2_confirmation_family_fixture_repair\"},\"historical_tenant_migration_invariant\":{\"candidate_sha256\":{\"alembic/versions/z5a6b7c8d9e0_enforce_clinical_tenant_rls.py\":\"bdd401fc08f4ba102a30804b9c0b3f68d1ba405ef695d47874ef5d8e69b4dfe8\",\"tests/test_tenant_isolation.py\":\"13461a2895db56100d73e6e316d07caaa13c14039c277012b7e05e6fb27c87f3\"},\"creation_only\":true,\"existing_files_changed\":false,\"literal_file_count\":2,\"migration_schema_changed\":true,\"repository_wide_and_g2_acceptance_claimed\":false,\"runtime_binding_separately_required\":true},\"historical_tenant_operation\":{\"completion_accepted\":false,\"operation_id\":\"g2-tenant-migration-repair\",\"profile\":\"G2_BASELINE_REPAIR_ACTIVE\",\"status\":\"active\",\"supersedes\":{\"historical_latch_preserved\":true,\"operation_id\":\"g2-ci-migration-repair\",\"scope_commit\":\"28ce5f5d8489cf43508da22f6f819343bf7ff3c6\",\"scope_path\":\"orchestration/programme/g2-baseline-repair-scope.json\",\"scope_sha256\":\"c0c651d1abe6c51e5199cd334dd29a4f23be6b70555b6b44a911e42a06bb9fb7\"},\"task_class\":\"g2_confirmation_family_fixture_repair\"},\"initial_activation\":{\"commit\":\"9b9c4400a99b9d1f57b36cd108fd5f64456502a5\",\"parent\":\"a8b5a1aaa91f1953beca73c94218e2a057c8b7d9\",\"tree\":\"b34d4ac985e5c96061a575c4c14f39dce643d59d\"},\"initial_scope\":{\"path\":\"orchestration/programme/g2-baseline-repair-scope.json\",\"sha256\":\"9b70a5b441d3aec55c5197ecc0a9d0c4aafa9b147998c00ab480d581966bcc66\"},\"initial_source_repair\":{\"commit\":\"f6881e198f73d26f6410ff63de850e743f715254\",\"parent\":\"9b9c4400a99b9d1f57b36cd108fd5f64456502a5\",\"tree\":\"d673fba4a1d11369677dd4cdeb57bc9d0962a276\"},\"maximum_changed_files\":3,\"migration_supported_paths\":{\"criterion\":\"empty_and_populated_alembic_paths_pass\",\"criterion_acceptance_claimed\":false,\"data_destruction_authorized\":false,\"directory_records_preserved\":[\"mbs_directory\",\"snomed_directory\"],\"downgrade\":{\"fresh_directory_tables\":\"drop_only_if_empty\",\"legacy_directory_tables\":\"retained\",\"populated_or_unsupported_state\":\"refuse_unchanged\"},\"historical_gate_definition_rewritten\":false,\"owner_decision\":{\"evidence_path\":\"g2-migration-evidence/owner-supported-paths.json\",\"sha256\":\"20f2bd2b29abdb3ca20cc45f729a4d1640484aa2b82dff35f79f5ead46a0b8f2\"},\"populated_legacy_conversion_required\":false,\"recognised_empty_core_tables\":[\"clinical_diagnoses\",\"encounters\",\"mbs_claims\",\"patients\",\"prescriptions\"],\"refusal_preserves\":[\"data\",\"schema\",\"enums\",\"alembic_revision\"],\"refused_unchanged_paths\":[\"populated_legacy_core_database\",\"partial_legacy_core_schema\",\"unsupported_schema_or_revision\"],\"successful_paths\":[\"fresh_database\",\"recognised_empty_core_database\"],\"supported_legacy_path_allows_populated_directories\":true},\"operational_multi_task_control_accepted\":false,\"owner_test_runtime_exception\":{\"active_test_environments\":1,\"admission_grants_runtime_authority\":false,\"automatic_retry_after_uncertain_effect\":false,\"collection_attempts\":1,\"contract_sha256\":\"49548a67c22720f5101b9bc1ae030ccf0884e00121a803cce132439154631386\",\"independent_execution_binding_required\":true,\"maximum_minutes_per_test_attempt\":10,\"maximum_runtime_minutes_including_collection\":35,\"owner_approval_sha256\":\"c5b4e40e59847b9ec7b2ebfa19788ea9dccdcdd71f3195f503d4106152baf546\",\"profile\":\"isolated_synthetic_application_postgresql_tests\",\"test_attempts\":3},\"prior_atomicity_activation\":{\"commit\":\"64ec9fce6396b9fd14710ff3610a369c215446a1\",\"scope_sha256\":\"6777a39980defdb95b7c287ef21cffe7f039e2bde9aa4cb13685c53f0b2504c7\"},\"prior_audio_activation\":{\"commit\":\"77b4e285c31d961d1fdda9779f2f7c3a52d6773b\",\"scope_sha256\":\"92222e77419479234ddce8e7524ef890bafcbeb82535f6e06b2b2e7f1a49ebad\"},\"prior_catalogue_activation\":{\"commit\":\"0371fc14a6e0333305641189193f4054adb5c11d\",\"scope_sha256\":\"6b67b5e5f553f62be848919fb08c5ef081f4eb580523140e746f4b0dee580406\"},\"prior_clinical_publication_acceptance\":{\"path\":\"C:/Users/there/EMR4-tools/g2-clinical-product5-publish-20260915-v1/resume-20260916/actual-post-publication-acceptance.json\",\"role\":\"opaque_historical_publication_acceptance_not_runtime_authority\",\"sha256\":\"2e47c6a1900c0204281e6d51bceed659cc76a40d339d5fa3604ff74f05ab7683\"},\"prior_instruction_alignment\":{\"commit\":\"8f27fcc622933ba256dc33142f85ac92849d6b89\",\"scope_sha256\":\"c03f3a329a334ae2a59619d807853be2b9dbbbb68399e29dfc49eb93e4a5ac65\"},\"prior_instruction_policy\":{\"authority\":\"accepted_meeting_insertion_owned_by_exact_maintenance_candidate\",\"path\":\"AGENTS.md\",\"previous_sha256\":\"254c906919e49c69b53c82fa2a678953b45e20d5e2ce2503184583daf09f8cc7\",\"sha256\":\"93ebf50187b6132fcee91cee7f4ba0b81bb59286ed9eaf52cdadab3a09ba20c1\"},\"prior_migration_acceptance\":{\"path\":\"C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/g2-entry/migration-preservation/repair-v1/native-acceptance.json\",\"role\":\"opaque_historical_reference_only_no_new_runtime_or_criterion_acceptance\",\"sha256\":\"3d28829c3e6406dbdd1a7a280bdb008c70f968d301696ba5e49e9ea5aaa8ce5d\"},\"prior_migration_activation\":{\"commit\":\"84c6b3520fb96971a9afc6f21027b4957c0dd63c\",\"scope_sha256\":\"25cb1df22f28216b75de03c404b1f92b5a0f36c5da06bb41711e6fee1e769104\"},\"prior_patient_activation\":{\"commit\":\"65aec51154a48fa375cac23cc2add52b752f67f5\",\"scope_sha256\":\"c6040347ba4a9c9294e873680acfbaffca16583afca9648a9ac9756c6a6c3a13\"},\"production_profile_invariant\":{\"browser_session_integration_claimed\":false,\"canonical_profiles\":[\"dev\",\"staging\",\"production\"],\"development_surfaces_preserved\":true,\"machine_openapi_and_backend_api_retained\":true,\"non_development_bernie_fixture_router_included\":false,\"non_development_cors_origins\":[],\"non_development_interactive_docs_served\":false,\"non_development_taskpane_served\":false},\"published_appointment_product_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/appointment-product-publication-effect-acceptance-v1.json\",\"role\":\"opaque_historical_appointment_publication_acceptance_not_operation_authority\",\"sha256\":\"5bb1069c8cd53e2cb4a13474f08ae04374150b124033557ea77398903c2d16f1\"},\"commit\":\"777e0170779e717123856b119ddb747db89e6aba\",\"parent\":\"849e03a98d87cbded4ac8c67856b68ecc0f93f90\",\"tree\":\"1c52c53b2baf83e80c7e3b11c958de8464053371\"},\"published_atomicity_repair\":{\"commit\":\"be98c2c856c3c02e10aed1a9fbb3c2e1123be399\",\"parent\":\"64ec9fce6396b9fd14710ff3610a369c215446a1\",\"source_sha256\":{\"EMR4 Sidebar/src/taskpane/taskpane.js\":\"c61d2184e837064a3f6cfffb03404dca296c0a44e5e2093ec30414fc5b1758bf\",\"app/routers/consultation.py\":\"c6f7bd690f0c5761e60afbdeb217f13c6760c94d88a4947d192b9070cb09d61e\",\"app/services/ai/audit_events.py\":\"d30f5a35f4bd4ab1ce2c854510ab17c7a094635ccc283a7bdc6aa88971ac81fd\",\"tests/test_consultation_audio_privacy.py\":\"691d0d1ab2be2d0c831e210afdd34fe9ddfcdea1fb6e4c4aa12fe3075ecb5fa4\",\"tests/test_consultation_finalize_atomicity.py\":\"c7eab22811afbc89b1a3c5a16f84cf96b2572ebd52e5abd24ccb2d7f8cac737d\",\"tests/test_consultation_patient_binding.py\":\"10185cba2d30214cb2bae6732c054e65f586d3bc6debdcde45e7c45646ce2229\"},\"tree\":\"8d64ae76aec9568baf374dc21724fcf19b349c5d\"},\"published_audio_repair\":{\"commit\":\"03e18f8ef007d9f8ecd4d39d6af2fe0b5fb4ddd5\",\"parent\":\"77b4e285c31d961d1fdda9779f2f7c3a52d6773b\",\"source_sha256\":{\"EMR4 Sidebar/src/taskpane/taskpane.js\":\"c759e196569a04bff6d80644773a6b92950eb72514ff1554cd897516ac1e801d\",\"app/main.py\":\"43047906b436a3d6f2bc0dda32a1625977cd583f99c072b34f99c0039affd7bc\",\"app/routers/consultation.py\":\"6c6bdf6a392b322d013984c8dc7160a2db9d7ebc2e8b496eebead59130b2eb77\",\"tests/test_consultation_audio_privacy.py\":\"52ddad2e1d52936bfa5e0e7a4f67bdf982b5bedf80c59c6680fcd6f9b024759e\"},\"tree\":\"f2084fac4171f390d50bdfd182229d5a5eab6ed2\"},\"published_ci_migration_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-b-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_ci_migration_publication_acceptance_not_operation_authority\",\"sha256\":\"0487de4cc7797523b88263a9d3408262dfb0bfdad59880917553e1d340a3ab63\"},\"commit\":\"28ce5f5d8489cf43508da22f6f819343bf7ff3c6\",\"parent\":\"911669f9d8090a386734e84f90b1ec10a9020857\",\"tree\":\"9d2efb67aaaa9d41a7ac2dc198082a8afadaa074\"},\"published_ci_selection_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-a-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_ci_selection_publication_acceptance_not_operation_authority\",\"sha256\":\"ca9864fd2020afe1575d44634826f36f4f12d1781a5ad04b43337d16eb775ef5\"},\"commit\":\"eb989f5e0e3a46f7ad51a2f8b2365cf7b6605a5f\",\"parent\":\"826ac77d825e646b83dec0c6083e56c686007457\",\"tree\":\"7ec765cd5d01e846ff54a08c6a5e1de7ffc0e6bc\"},\"published_clinical_repair\":{\"commit\":\"a0b8620b172f37648326d7fd86214c4019a5e275\",\"parent\":\"9ffd3b8cb2b3aea873458f9758bc29393ff44e2b\",\"tree\":\"3542610ba876074ec39b9342ee014dd134fef3e8\"},\"published_dependency_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/dependency-product-publication-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_dependency_publication_acceptance_not_operation_authority\",\"sha256\":\"3668084ae65e572c95f712af3fdadb2dd55bb40827c5e97bc99a0a0c34a1b5ef\"},\"commit\":\"aeae8084c3905fe250a2e7f58b78edd4e995e2f3\",\"parent\":\"ef11f276baeca15ebb6c084bbe4db274ec6c6c36\",\"tree\":\"b7f41b6bd8ec425da205f033268e068262025010\"},\"published_migration_guard_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/EMR4-tools/g2-migration-product-guard-20260916/publication-v1/independent-post-publication-acceptance.json\",\"role\":\"opaque_historical_migration_guard_publication_acceptance_not_operation_authority\",\"sha256\":\"febb30567cc6a01c5575d7f3d538fca5207673bd80784fcbe5788b936789a6b7\"},\"commit\":\"c8f1fbb75e701163d4bb8b04f170ee4d74653016\",\"parent\":\"5b386240baa53b7882219832dc6057d66999ca61\",\"tree\":\"53bbd4b805a55b9e97dd30a808d904a736913f9f\"},\"published_patient_repair\":{\"commit\":\"bc7800e3fa297942f6444e792094f679f37bb70e\",\"parent\":\"65aec51154a48fa375cac23cc2add52b752f67f5\",\"source_sha256\":{\"EMR4 Sidebar/src/taskpane/taskpane.js\":\"c61d2184e837064a3f6cfffb03404dca296c0a44e5e2093ec30414fc5b1758bf\",\"app/main.py\":\"43047906b436a3d6f2bc0dda32a1625977cd583f99c072b34f99c0039affd7bc\",\"app/routers/consultation.py\":\"37c942807859ae6ca6317d7be788e15eee4193428aa606018971df1f67de7069\",\"tests/test_consultation_audio_privacy.py\":\"e0c19552eb200d8f18d00466082ae1182804a3540109dc568736da0c5c9d4d2a\",\"tests/test_consultation_patient_binding.py\":\"dc55f6d92b9d0f5fb1a7f7a2ef5bc980345ca7217703b3eb8747f3874649df5a\"},\"tree\":\"978c6e8e74c783e356fff40205f189e6567edf34\"},\"published_production_profile_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/production-profile-product-publication-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_production_profile_publication_acceptance_not_operation_authority\",\"sha256\":\"b49b37a4b010b44282ef4faac3263941c5b33c199ad55e68466949f0581fee27\"},\"commit\":\"db55dc48ca128d96e70a2e6697fb297b75abba8c\",\"parent\":\"ec0fecc87c169cd4fd5f2dcf2f4c028140ca178a\",\"tree\":\"e497557f4f26bb8c4ffc1e8d65169530ba83ac95\"},\"published_relationship_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-c-preparation-v1/tenant-relationship-repair-preparation-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_relationship_publication_acceptance_not_operation_authority\",\"sha256\":\"d3676fee74afcdd17f78333c23c6ca4f3d7e98d26fe3d5d39c575ccc7da982fa\"},\"commit\":\"1230bb8201d0fcca69777663c37a868d626b312f\",\"parent\":\"3eb64c6a3783b50e69aa6224d37647421eeb6356\",\"tree\":\"066494d6d6942ca8c0a739b0218f881223d72eb5\"},\"published_tenant_migration_repair\":{\"acceptance\":{\"path\":\"C:/Users/there/.codex/visualizations/2026/09/15/01a0a72f-a9bd-72f3-b259-0de184339a44/ci-c-preparation-v1/tenant-migration-candidate-v1/product-publication-preparation-v1/independent-publication-effect-review-v1.json\",\"role\":\"opaque_historical_tenant_migration_publication_acceptance_not_operation_authority\",\"sha256\":\"76088b8ca820bf5acfd9cb56aa1a7a4cc2d932bca9f122f7bc2b93fb03af3188\"},\"commit\":\"7026ea069600471c1c0a7c7c4fd0d0b806184e4a\",\"parent\":\"d7b2c443fdef3c12d0bc934e4d17e6d3baa06b9f\",\"tree\":\"e9576dcdc219b94432fd9f211881a11e2bbacfe1\"},\"recorded_at\":\"2026-09-27T09:45:40+00:00\",\"repair_operation\":\"repair_g2_ci_completeness\",\"repair_preimage_sha256\":{\"scripts/python_source_state.py\":\"f7e77f2785dc1b405fdaa038acff494ad27a6a005754aa5ee43665dd92ad2aa5\",\"scripts/verify_repository.py\":\"da5477e5036d10a7813d7d5384ebd66fe20c98aa3acf4a555d1f87112220cce3\",\"tests/test_python_source_state.py\":\"6e17f4682b9ff65ae9aabab6b2d2b436d8496784acc3496c961e5bcdfb21ab29\"},\"schema_version\":\"ariadne.g2_reviewed_batch_scope.v17\",\"transition_base_commit\":\"1230bb8201d0fcca69777663c37a868d626b312f\",\"trusted_git_successor\":{\"commit\":\"9e271036c1e7d4aec842f1e1a4a3f9c1666411dd\",\"parent\":\"eaabb48b0df6c6c1f9e0ba086d1c360009b54e03\",\"source_sha256\":{\"orchestration_harness/controller_maintenance_record.py\":\"d93b8f106b4c96aa7a6ba5c26518232d9f152b4927b10d32db5d066d03ccc1b5\",\"orchestration_harness/trusted_git.py\":\"4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527\",\"tests/test_programme_target_index.py\":\"69b7711049d5b3046eeed4aeaded8becbcf4e8055484891789f570cbe998adab\"},\"tree\":\"4451dea5d6ffae12e89a03706eabacac42fa7b47\"}}")
G2_PYJWT_COMPATIBILITY_ACCEPTANCE = {
    "path": "C:/Users/there/EMR4/.codex/successor-preparation/pyjwt2151-capsule-v2/independent-result-review-v1.json",
    "sha256": "36a00c074df6ec391e4b82fe6e1d964b5433cf0f8d690214e7bb7ff73fb30e7c",
    "role": "accepted_isolated_library_result_not_product_or_g2_acceptance",
}
G2_PYJWT_LIMITS = (
    "only exact existing requirements and compatibility-test afterimages are eligible; no additions",
    "PyJWT2.13.0 to2.15.1 only; cryptography50.0.1 and all other24 roots unchanged",
    "unfinished V17 CI scope and historical consumed latches remain preserved, not accepted",
    "isolated compatibility acceptance grants no audit, application, runtime, publication or G2 acceptance",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_pyjwt_repair", "repair_g2_pyjwt_repair"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_pyjwt_repair"}
OPERATION_PATHS.update(enable_g2_pyjwt_repair=G2_DEPENDENCY_MAINTENANCE_PATHS,
                       repair_g2_pyjwt_repair=G2_DEPENDENCY_PATHS)


# V19 is a new owner-directed fixed transport batch. Historical V18 remains
# incomplete. These roots are installed reviewed controller constants, not
# candidate-selected trust roots or runtime grants.
G2_TRANSPORT_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v19"
G2_TRANSPORT_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v19"
G2_TRANSPORT_PATHS = frozenset(raisa_policy.G2_TRANSPORT_REPAIR_PATHS)
G2_TRANSPORT_ADDITIONS = frozenset({"tests/taskpane_synthetic_transport.cjs"})
G2_TRANSPORT_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_TRANSPORT_HISTORICAL_V18_SCOPE_COMMIT = "f233f3622c0c5c72448380c706e15b6efbc6be7e"
G2_TRANSPORT_PREDECESSOR = {
    "commit": "a276031269aaf285e13f36d6fc4a6b80b3915be4",
    "parent": "f38bcbe65ddd8fb1f35f530b2c686cfcffab4ed3",
    "tree": "e7970dd10133dbbf451f23e0f19e503d8d9b0ae8",
    "source_sha256": {
        "orchestration_harness/bounded_g1b.py": "07790594cd9eb8e8412f1702b66547437f522e5c03a6fae0bfd37cf7a33d18ed",
        "orchestration_harness/raisa_policy.py": "ac42ecaeca273c0595d7e78ec322d8755d4d3935348023ac781937df470e1aa3",
        "tests/test_bounded_g1b.py": "148644ab962048c7c02bd8e510327af6218c49b6c9dc8611f8c311bbe3037ac9",
        "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
        "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
    },
}
G2_TRANSPORT_PREDECESSOR_POLICY = {
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    STATE: "a11297770c7c6eefac4b1aed5ed664fb147c4d94af08183938ee20d0374b8a4f",
    OVERLAY: "faa8119cc3d7ba7547c16d4df6016c350b79cbf9cab4c47bd403f8f187fbcbd5",
    G2_SCOPE: "b79e0619ea530ca3f5f8302f33885d2cd1da8afdc320fdee139c396901861cb0",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_TRANSPORT_REPAIR_PINS = {
    "EMR4 Sidebar/src/taskpane/taskpane.js": "68ff085ed2a77ed756b775f034f5c89a83c5cd6a56c2544392699dc6b6d07f2f",
    "tests/taskpane_synthetic_transport.cjs": None,
}
G2_TRANSPORT_OWNER_RECORD = "g2-owner-directive/owner-directive-20261008.txt"
G2_TRANSPORT_OWNER_SHA256 = "5292b7c727de10f5dac9d6857745fac9c01bdeddeb19c7c8d07586e1cf43b406"
G2_TRANSPORT_LIMITS = (
    "only the taskpane transport source and named synthetic test are eligible",
    "existing uncommitted taskpane repair must be preserved in the independently reviewed exact afterimage",
    "V18 and every prior latch or consumed execution grant remain historical and unrenewed",
    "admission grants no browser, application, database, provider, real-data, deployment or G2 acceptance",
    "future ordinary G2 files require a new independently reviewed successor amendment, not in-place widening",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_transport_repair", "repair_g2_transport_repair"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_transport_repair"}
OPERATION_PATHS.update(enable_g2_transport_repair=G2_TRANSPORT_MAINTENANCE_PATHS,
                       repair_g2_transport_repair=G2_TRANSPORT_PATHS)


# V20 is a fixed successor for one exact reviewed six-file repair subject.
# V19 and all historical scopes/grants remain unchanged and independently bound.
G2_SIX_BINDING_VERSION = "ariadne.bounded_g2_batch_binding.v20"
G2_SIX_SCOPE_VERSION = "ariadne.g2_reviewed_batch_scope.v20"
G2_SIX_SUBJECT_SHA256 = "65fc0f7e058da0e144bbacd6feac699a7ce69bedd27dc5806778238c1918b477"
G2_SIX_REPAIR_PINS = {'app/services/appointment_delete_product_adapter.py': {'before_sha256': 'a7e1702c61258acfb51f634883086ad5993c8ab63989eace9cfa1102b2532c59', 'after_sha256': 'c3bbdb64e9e5d982ff672a9bbf028e2ba10ed5c37fba493e9677fd3931f18f90'}, 'app/services/appointment_delete_composition.py': {'before_sha256': '7e3890dbb2cdc67c16bd407734f52f0107fc53c46b3a390bbe22da5ddb026b24', 'after_sha256': '8215bd117d1a358066962f55630255c022d355d4ea3a160cf62dcc370a7f979c'}, 'app/services/appointment_delete_physical.py': {'before_sha256': '2cfc90ae715fc7eb357aa6fb87aa3da103d7fb9bd4db3fffceac4c1d1c774c06', 'after_sha256': '061175cb371109fd57e39795a0748d0597d3fdbc34789796b5e811d6cdbc80ff'}, 'app/routers/appointments.py': {'before_sha256': '0f37cbdfcfa32d851d7228f9563b33c4c17883484a2597c680789a9a2d9e8e03', 'after_sha256': '9c9965871b622b16ab52900e50e86d650a04549d9fb1f2c5cefe2c8ae8788cef'}, 'tests/test_api_spine_status_confirm_idempotency_route_contract.py': {'before_sha256': '1379b2f506a8388097404c805d9eaa6599c854ea14b3aff4fc26a22f0aa98101', 'after_sha256': '119c1315551b8c50d1f3b4367d19ef6469bf2481fa18a810a9c637f3d870874e'}, 'tests/test_repository_maintenance.py': {'before_sha256': '716db9f4bc24a8b114377820124e2a52f8150a74d93c4286c50a428716ecf800', 'after_sha256': '159b7192299becf9b8815fab02edd9de99c604cf482b04eced6933acbaa392b7'}}
G2_SIX_PATHS = frozenset(G2_SIX_REPAIR_PINS)
G2_SIX_MAINTENANCE_PATHS = G2_BATCH_MAINTENANCE_PATHS
G2_SIX_PREDECESSOR = {'commit': '7d9edaa404d912b53316fe868cad4de0bbc8bf60', 'parent': '9329d7311fdb241d4b274b8e6ab9c77eacf8011e', 'tree': '475d206496ed2abb7d5156e1d236d669f639a82c', 'source_sha256': {'orchestration_harness/bounded_g1b.py': '0894e91f8608560c3bdfb632e4e6d208e248d4bba9f643c095f9c3b2e93dd7e5', 'orchestration_harness/configuration_core.py': 'f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5', 'orchestration_harness/programme_admission.py': 'ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181', 'orchestration_harness/raisa_policy.py': '1c542d0950491231d2c52c13acd2c81e89e048228c9e69cdbb5b4db388603f82', 'tests/test_bounded_g1b.py': '19231112595d4743885d4e4debd6801e60359ca64bc82cd1c749797524f84e34'}}
G2_SIX_PREDECESSOR_POLICY = {'AGENTS.md': '97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e', 'orchestration/programme/gates.yaml': '115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341', 'orchestration/programme/current-state.json': '5087cdff483130e6d358d3df968725a5fb108b8d308c57b0e89189c56f86677d', 'orchestration/programme/g2-baseline-repair-scope.json': '626fab356d8727b5fffa41126bf01ffe850ed50fef35caea5e8322d09dab262c', 'orchestration/harness_settings/programme_recovery.yaml': '1a0b2d5aa251eaed97decdb61f313ae24147e4ccb530b165ead1b0f0c6c338db'}
G2_SIX_PRIOR_RECORDED_AT = "2026-10-08T00:00:00+00:00"
G2_SIX_PUBLICATION_REVIEW_PINS = {
    "g2-six-predecessor/independent-commit-effect-review-v1.json": "dc93038d3805e671bf78ffa20471ca733fcac9ed1ea92aaecf3496d552d60405",
    "g2-six-predecessor/independent-push-effect-review-v1.json": "5d8451df025d85484f49c92c97dc1d4ac5947346c675e9f3e46382ef1fbd4421",
}
G2_SIX_LIMITS = (
    "only all six installed literal path/preimage/afterimage rows of subject65fc are eligible; no additions",
    "preserve V19 and every historical latch, accepted record and consumed grant without relabeling",
    "admission grants no runtime, retry, provider, real-data, deployment, protected integration or G2 acceptance",
    "any other source subject requires another independently reviewed successor; no caller-selected widening",
)
G2_BATCH_KINDS = G2_BATCH_KINDS | {"enable_g2_six_file_repair", "repair_g2_six_file_repair"}
G2_MAINTENANCE_KINDS = G2_MAINTENANCE_KINDS | {"enable_g2_six_file_repair"}
OPERATION_PATHS.update(enable_g2_six_file_repair=G2_SIX_MAINTENANCE_PATHS,
                       repair_g2_six_file_repair=G2_SIX_PATHS)


def _six_file_changes(binding: dict) -> dict:
    kind, rows = binding.get("operation_kind"), binding.get("repair_sha256")
    _need(binding.get("schema_version") == G2_SIX_BINDING_VERSION
          and kind in {"enable_g2_six_file_repair", "repair_g2_six_file_repair"},
          "bounded_g2_batch_binding_version")
    maintenance = kind == "enable_g2_six_file_repair"
    allowed = G2_SIX_MAINTENANCE_PATHS if maintenance else G2_SIX_PATHS
    _need(type(rows) is dict and len(rows) == len(allowed), "bounded_g2_batch_changes_invalid")
    _need(set(rows) == allowed, "bounded_g2_batch_path_not_allowed")
    for path, row in rows.items():
        _keys(row, {"before_sha256", "after_sha256"}, "bounded_g2_batch_change_schema")
        _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in row.values())
              and row["before_sha256"] != row["after_sha256"], "bounded_g2_batch_change_digest")
        if not maintenance:
            _need(row == G2_SIX_REPAIR_PINS[path], "bounded_g2_six_file_exact_subject")
    return rows


def _transport_changes(binding: dict) -> dict:
    kind, rows = binding.get("operation_kind"), binding.get("repair_sha256")
    _need(binding.get("schema_version") == G2_TRANSPORT_BINDING_VERSION
          and kind in {"enable_g2_transport_repair", "repair_g2_transport_repair"},
          "bounded_g2_batch_binding_version")
    maintenance = kind == "enable_g2_transport_repair"
    allowed = G2_TRANSPORT_MAINTENANCE_PATHS if maintenance else G2_TRANSPORT_PATHS
    _need(type(rows) is dict and len(rows) == len(allowed), "bounded_g2_batch_changes_invalid")
    _need(set(rows) == allowed, "bounded_g2_batch_path_not_allowed")
    for path, row in rows.items():
        _keys(row, {"before_sha256", "after_sha256"}, "bounded_g2_batch_change_schema")
        if not maintenance:
            _need(row["before_sha256"] == G2_TRANSPORT_REPAIR_PINS[path],
                  "bounded_g2_transport_repair_preimage")
        addition = not maintenance and path in G2_TRANSPORT_ADDITIONS
        digests = (row["after_sha256"],) if addition else row.values()
        _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in digests)
              and row["before_sha256"] != row["after_sha256"], "bounded_g2_batch_change_digest")
    return rows


def _batch_changes(binding: dict) -> dict:
    if (binding.get("schema_version") == G2_SIX_BINDING_VERSION
            or binding.get("operation_kind") in {"enable_g2_six_file_repair", "repair_g2_six_file_repair"}):
        return _six_file_changes(binding)
    if (binding.get("schema_version") == G2_TRANSPORT_BINDING_VERSION
            or binding.get("operation_kind") in {"enable_g2_transport_repair", "repair_g2_transport_repair"}):
        return _transport_changes(binding)
    kind = binding.get("operation_kind")
    rows = binding.get("repair_sha256")
    appointment = binding.get("schema_version") == G2_APPOINTMENT_BINDING_VERSION
    production = binding.get("schema_version") == G2_PRODUCTION_PROFILE_BINDING_VERSION
    pyjwt = binding.get("schema_version") == G2_PYJWT_BINDING_VERSION
    dependency = pyjwt or binding.get("schema_version") == G2_DEPENDENCY_BINDING_VERSION
    ci = binding.get("schema_version") == G2_CI_BINDING_VERSION
    cim = binding.get("schema_version") == G2_CIM_BINDING_VERSION
    tenant = binding.get("schema_version") == G2_TENANT_BINDING_VERSION
    relationship = binding.get("schema_version") == G2_RELATIONSHIP_BINDING_VERSION
    completeness = binding.get("schema_version") == G2_COMPLETENESS_BINDING_VERSION
    maintenance = kind in G2_MAINTENANCE_KINDS
    exact_count = (6 if (dependency or ci or cim or tenant or relationship or completeness) and maintenance else
                   3 if completeness or relationship else
                   2 if tenant else
                   2 if cim else
                   7 if ci else
                   2 if dependency else
                   7 if appointment else
                   6 if production and maintenance else
                   4 if production else None)
    size_valid = (type(rows) is dict and
                  (len(rows) == exact_count if exact_count is not None else 1 <= len(rows) <= 6))
    _need(kind in G2_BATCH_KINDS and size_valid,
          "bounded_g2_batch_changes_invalid")
    catalogue = binding.get("schema_version") == G2_CATALOGUE_BINDING_VERSION
    instructions = binding.get("schema_version") == G2_INSTRUCTIONS_BINDING_VERSION
    migration = instructions or binding.get("schema_version") == G2_MIGRATION_BINDING_VERSION
    audio = binding.get("schema_version") == G2_AUDIO_BINDING_VERSION
    patient = binding.get("schema_version") == G2_PATIENT_BINDING_VERSION
    atomicity = binding.get("schema_version") == G2_ATOMICITY_BINDING_VERSION
    clinical = binding.get("schema_version") == G2_CLINICAL_BINDING_VERSION
    guard = binding.get("schema_version") == G2_MIGRATION_GUARD_BINDING_VERSION
    _need((kind in {"enable_g2_migration", "repair_g2_migration", "align_g2_instructions"}) == migration
          and (kind != "align_g2_instructions" or instructions)
          and (not instructions or kind in {"align_g2_instructions", "repair_g2_migration"})
          and (kind in {"enable_g2_audio_privacy", "repair_g2_audio_privacy"}) == audio
          and (kind in {"enable_g2_patient_binding", "repair_g2_patient_binding"}) == patient
          and (kind in {"enable_g2_consultation_atomicity", "repair_g2_consultation_atomicity"}) == atomicity
          and (kind in {"enable_g2_clinical_authority", "repair_g2_clinical_authority"}) == clinical
          and (kind in {"enable_g2_migration_downgrade_guard", "repair_g2_migration_downgrade_guard"}) == guard
           and (kind in {"enable_g2_appointment_concurrency", "repair_g2_appointment_concurrency"}) == appointment
           and (kind in {"enable_g2_production_profile", "repair_g2_production_profile"}) == production
           and (kind in ({"enable_g2_pyjwt_repair", "repair_g2_pyjwt_repair"} if pyjwt else
                       {"enable_g2_dependency_repair", "repair_g2_dependency_repair"})) == dependency
           and (kind in {"enable_g2_ci_selection", "repair_g2_ci_selection"}) == ci
           and (kind in {"enable_g2_ci_migration", "repair_g2_ci_migration"}) == cim
           and (kind in {"enable_g2_tenant_migration", "repair_g2_tenant_migration"}) == tenant
            and (kind in {"enable_g2_tenant_relationships", "repair_g2_tenant_relationships"}) == relationship
            and (kind in {"enable_g2_ci_completeness", "repair_g2_ci_completeness"}) == completeness,
             "bounded_g2_batch_binding_version")
    allowed = (G2_COMPLETENESS_MAINTENANCE_PATHS if maintenance and completeness
                else G2_COMPLETENESS_PATHS if completeness
                else G2_RELATIONSHIP_MAINTENANCE_PATHS if maintenance and relationship
                else G2_RELATIONSHIP_PATHS if relationship
                else G2_TENANT_MAINTENANCE_PATHS if maintenance and tenant
                else G2_TENANT_PATHS if tenant
                else G2_CIM_MAINTENANCE_PATHS if maintenance and cim
               else G2_CIM_PATHS if cim
               else G2_CI_MAINTENANCE_PATHS if maintenance and ci
               else G2_CI_PATHS if ci
               else G2_DEPENDENCY_MAINTENANCE_PATHS if maintenance and dependency
               else G2_DEPENDENCY_PATHS if dependency
               else G2_PRODUCTION_PROFILE_MAINTENANCE_PATHS if maintenance and production
               else G2_PRODUCTION_PROFILE_PATHS if production
               else G2_APPOINTMENT_MAINTENANCE_PATHS if maintenance and appointment
               else G2_APPOINTMENT_PATHS if appointment
               else G2_MIGRATION_GUARD_MAINTENANCE_PATHS if maintenance and guard
               else G2_MIGRATION_PATHS if guard
               else G2_CLINICAL_MAINTENANCE_PATHS if maintenance and clinical
               else G2_ATOMICITY_MAINTENANCE_PATHS if maintenance and atomicity
               else G2_PATIENT_MAINTENANCE_PATHS if maintenance and patient
               else G2_AUDIO_MAINTENANCE_PATHS if maintenance and audio
               else G2_INSTRUCTIONS_MAINTENANCE_PATHS if maintenance and instructions
               else G2_BATCH_MAINTENANCE_PATHS if maintenance else G2_CLINICAL_PATHS if clinical
               else G2_ATOMICITY_PATHS if atomicity
               else G2_PATIENT_PATHS if patient
               else G2_AUDIO_PATHS if audio else G2_MIGRATION_PATHS if migration
               else G2_CATALOGUE_PATHS if catalogue else G2_BATCH_PATHS)
    _need(set(rows) <= allowed and (not (maintenance or guard or appointment or production or dependency or ci or cim or tenant or relationship or completeness)
                                      or set(rows) == allowed),
          "bounded_g2_batch_path_not_allowed")
    for path, row in rows.items():
        _keys(row, {"before_sha256", "after_sha256"}, "bounded_g2_batch_change_schema")
        if appointment and not maintenance:
            _need(row["before_sha256"] == G2_APPOINTMENT_REPAIR_PINS[path],
                  "bounded_g2_appointment_repair_preimage")
        if production and not maintenance:
            _need(row["before_sha256"] == G2_PRODUCTION_PROFILE_REPAIR_PINS[path],
                  "bounded_g2_production_profile_repair_preimage")
        if cim and not maintenance:
            _need(row["before_sha256"] == G2_CIM_REPAIR_PINS[path],
                  "bounded_g2_cim_repair_preimage")
        if tenant and not maintenance:
            _need(row["before_sha256"] is None,
                  "bounded_g2_tenant_repair_preimage")
            _need(row["after_sha256"] == G2_TENANT_CANDIDATE_PINS[path],
                  "bounded_g2_tenant_candidate_digest")
        if relationship and not maintenance:
            _need(row["before_sha256"] is None,
                  "bounded_g2_relationship_repair_preimage")
            _need(row["after_sha256"] == G2_RELATIONSHIP_CANDIDATE_PINS[path],
                  "bounded_g2_relationship_candidate_digest")
        if completeness and not maintenance:
            _need(row["before_sha256"] == G2_COMPLETENESS_REPAIR_PINS[path],
                  "bounded_g2_completeness_repair_preimage")
            _need(row["after_sha256"] == G2_COMPLETENESS_CANDIDATE_PINS[path],
                  "bounded_g2_completeness_candidate_digest")
        if ci and not maintenance:
            _need(row["before_sha256"] == G2_CI_REPAIR_PINS[path],
                  "bounded_g2_ci_repair_preimage")
        if dependency and not maintenance:
            _need(row["before_sha256"] == (G2_PYJWT_REPAIR_PINS if pyjwt else G2_DEPENDENCY_REPAIR_PINS)[path],
                  "bounded_g2_dependency_repair_preimage")
            if pyjwt:
                _need(row["after_sha256"] == G2_PYJWT_CANDIDATE_PINS[path],
                      "bounded_g2_pyjwt_candidate")
            elif path == "requirements.txt":
                _need(row["after_sha256"] == G2_DEPENDENCY_REQUIREMENTS_AFTER_SHA256,
                      "bounded_g2_dependency_requirements_candidate")
        addition = (not maintenance and row["before_sha256"] is None
                     and ((relationship and path in G2_RELATIONSHIP_PATHS)
                          or (tenant and path in G2_TENANT_PATHS)
                         or (dependency and path in G2_DEPENDENCY_ADDITIONS)
                         or (production and path in G2_PRODUCTION_PROFILE_ADDITIONS)
                         or (appointment and path in G2_APPOINTMENT_ADDITIONS)
                         or (migration and path == G2_MIGRATION_ADDITION)
                         or (audio and path == G2_AUDIO_ADDITION)
                         or (patient and path == G2_PATIENT_ADDITION)
                         or (atomicity and path == G2_ATOMICITY_ADDITION)))
        digests = (row["after_sha256"],) if addition else row.values()
        _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in digests)
              and row["before_sha256"] != row["after_sha256"], "bounded_g2_batch_change_digest")
        if guard and not maintenance:
            _need(row["before_sha256"] == G2_MIGRATION_GUARD_REPAIR_PINS[path],
                  "bounded_g2_migration_guard_repair_preimage")
    return rows


def batch_input_paths(binding: dict) -> frozenset[str]:
    """Catalogue authority is metadata; only fixed policy and selected files open."""
    changes = _batch_changes(binding)
    if binding.get("schema_version") in {G2_CATALOGUE_BINDING_VERSION, G2_MIGRATION_BINDING_VERSION,
                                         G2_INSTRUCTIONS_BINDING_VERSION, G2_AUDIO_BINDING_VERSION,
                                         G2_PATIENT_BINDING_VERSION, G2_ATOMICITY_BINDING_VERSION,
                                          G2_CLINICAL_BINDING_VERSION, G2_MIGRATION_GUARD_BINDING_VERSION,
                                          G2_APPOINTMENT_BINDING_VERSION,
                                          G2_PRODUCTION_PROFILE_BINDING_VERSION,
                                          G2_DEPENDENCY_BINDING_VERSION,
                                          G2_CI_BINDING_VERSION, G2_CIM_BINDING_VERSION,
                                           G2_TENANT_BINDING_VERSION, G2_RELATIONSHIP_BINDING_VERSION,
                                           G2_COMPLETENESS_BINDING_VERSION, G2_PYJWT_BINDING_VERSION, G2_TRANSPORT_BINDING_VERSION, G2_SIX_BINDING_VERSION}:
        return G2_CATALOGUE_POLICY_PATHS | frozenset(changes)
    return G2_BATCH_INPUT_PATHS


# A separately reviewed sealed manifest grants exact CI paths, never a prefix.
G2_CLOSEOUT_CI_KIND = "adopt_g2_complete_ci"
G2_CLOSEOUT_CI_BINDING_VERSION = "ariadne.g2_complete_ci_binding.v1"
G2_CLOSEOUT_CI_PREFIX = "orchestration/programme/g2-closeout-evidence/"
G2_CLOSEOUT_CI_CORE = frozenset({".github/workflows/python-security.yml",
    "scripts/verify_repository.py", "orchestration/harness_settings/python_source_state.json",
    "pyproject.toml", "tests/test_consultation_audio_privacy.py"})
G2_CLOSEOUT_CI_REQUIRED_CHANGES = frozenset({".github/workflows/python-security.yml",
    "orchestration/harness_settings/python_source_state.json", "tests/test_consultation_audio_privacy.py"})
OPERATION_PATHS[G2_CLOSEOUT_CI_KIND] = frozenset()  # Actual paths require the sealed map.


def _closeout_ci_path(path):
    _need(type(path) is str and 0 < len(path) <= 512 and "\\" not in path
          and not path.startswith("/") and ":" not in path
          and all(part not in {"", ".", ".."} for part in path.split("/"))
          and not any(ord(char) < 32 for char in path), "bounded_g2_ci_path")
    _need(path in G2_CLOSEOUT_CI_CORE or path.startswith(G2_CLOSEOUT_CI_PREFIX),
          "bounded_g2_ci_path")
    return path


def _validate_g2_ci_manifest(manifest):
    """Shape only. Independent prior review and the installed seal authorize it."""
    _keys(manifest, {"schema_version", "operation_kind", "product_subject_sha256", "changes",
        "caller", "complete_selection", "trusted_context", "proof_sha256", "stable_anchors"},
        "bounded_g2_ci_manifest_schema")
    _need(manifest["schema_version"] == "emr4.g2_complete_ci_adoption_manifest.v1"
          and manifest["operation_kind"] == G2_CLOSEOUT_CI_KIND
          and manifest["product_subject_sha256"] == G2_SIX_SUBJECT_SHA256,
          "bounded_g2_ci_manifest_subject")
    changes = manifest["changes"]
    _need(type(changes) is dict and G2_CLOSEOUT_CI_REQUIRED_CHANGES <= set(changes)
          and len(changes) <= 263, "bounded_g2_ci_changes")
    _need(all(type(p) is str for p in changes)
          and len({p.casefold() for p in changes}) == len(changes), "bounded_g2_ci_path_alias")
    for path, pair in changes.items():
        _closeout_ci_path(path)
        _keys(pair, {"before_sha256", "after_sha256"}, "bounded_g2_ci_pair")
        _closeout_digest(pair["after_sha256"])
        if pair["before_sha256"] is None:
            _need(path.startswith(G2_CLOSEOUT_CI_PREFIX), "bounded_g2_ci_core_absent")
        else:
            _closeout_digest(pair["before_sha256"])
            _need(pair["before_sha256"] != pair["after_sha256"], "bounded_g2_ci_unchanged_pair")
    caller = _keys(manifest["caller"], {"workflow", "verifier", "selection", "helper", "argv",
        "pin_authority_sha256"}, "bounded_g2_ci_caller")
    for key, path in (("workflow", ".github/workflows/python-security.yml"),
        ("verifier", "scripts/verify_repository.py"),
        ("selection", "orchestration/harness_settings/python_source_state.json"),
        ("helper", G2_CLOSEOUT_HELPER)):
        _keys(caller[key], {"path", "sha256"}, "bounded_g2_ci_caller")
        _need(caller[key]["path"] == path, "bounded_g2_ci_caller")
        _closeout_digest(caller[key]["sha256"])
        if path in changes:
            _need(caller[key]["sha256"] == changes[path]["after_sha256"], "bounded_g2_ci_caller")
    _need(caller["helper"]["sha256"] == G2_CLOSEOUT_HELPER_SHA256, "bounded_g2_ci_helper")
    _need(caller["verifier"]["sha256"] ==
          "01239f5459c9967cfceffc0201d969a77ec374db8887bf3149944dd93308c992",
          "bounded_g2_ci_verifier")
    _closeout_digest(caller["pin_authority_sha256"])
    proof = manifest["proof_sha256"]
    _need(type(proof) is dict and 0 < len(proof) <= 258
          and all(type(p) is str for p in proof)
          and len({p.casefold() for p in proof}) == len(proof), "bounded_g2_ci_proof")
    for path, digest in proof.items():
        _closeout_ci_path(path)
        _need(path.startswith(G2_CLOSEOUT_CI_PREFIX), "bounded_g2_ci_proof")
        _closeout_digest(digest)
        _need(changes.get(path, {}).get("after_sha256") == digest, "bounded_g2_ci_proof")
    _need({p for p in changes if p.startswith(G2_CLOSEOUT_CI_PREFIX)} == set(proof),
          "bounded_g2_ci_unreferenced_payload")
    for key in ("complete_selection", "trusted_context"):
        ref = _keys(manifest[key], {"path", "sha256"}, "bounded_g2_ci_complete")
        _need(proof.get(ref["path"]) == ref["sha256"], "bounded_g2_ci_complete")
    selection, context = manifest["complete_selection"], manifest["trusted_context"]
    _need(selection["path"] != context["path"], "bounded_g2_ci_complete")
    _need(caller["argv"] == ["python", "scripts/verify_repository.py", "--profile", "ci-complete",
        "--require-complete", "--selection", selection["path"], "--selection-sha256", selection["sha256"],
        "--trusted-context", context["path"], "--trusted-context-sha256", context["sha256"]],
        "bounded_g2_ci_complete_argv")
    anchors = _keys(manifest["stable_anchors"], {"source_sha256", "config_sha256", "tool_sha256"},
                    "bounded_g2_ci_anchors")
    for key, rows in anchors.items():
        _need(type(rows) is dict and rows and all(type(p) is str and p for p in rows),
              "bounded_g2_ci_anchors")
        for path, digest in rows.items():
            _closeout_digest(digest)
            if key != "tool_sha256":
                _need(path not in changes and path not in G2_CLOSEOUT_BEFORE_PATHS
                      and path not in G2_CLOSEOUT_PATHS and not path.startswith(G2_CLOSEOUT_CI_PREFIX),
                      "bounded_g2_ci_anchor_cycle")
    return manifest


def _validate_g2_ci_seal(seal):
    _keys(seal, {"manifest", "manifest_sha256", "review_path", "review_sha256"},
          "bounded_g2_ci_seal")
    _validate_g2_ci_manifest(seal["manifest"])
    _closeout_digest(seal["manifest_sha256"])
    _need(seal["manifest_sha256"] == _sha(_canonical(seal["manifest"])), "bounded_g2_ci_seal")
    _need(type(seal["review_path"]) is str and Path(seal["review_path"]).is_absolute(),
          "bounded_g2_ci_seal")
    _closeout_digest(seal["review_sha256"])
    return seal


def _validate_g2_ci_scope_review(seal, review):
    _validate_g2_ci_seal(seal)
    _need(review.get("schema_version") == "emr4.g2_complete_ci_adoption_scope_review.v1"
          and review.get("verdict") == "PASS_EXACT_G2_COMPLETE_CI_ADOPTION_SCOPE"
          and review.get("reviewer_agent") == "/root/g2_admission_review"
          and review.get("independent") is True and review.get("implementation_authorship") is False
          and review.get("blocking_findings") == []
          and review.get("manifest_sha256") == seal["manifest_sha256"]
          and review.get("ordinary_literal_paths") == sorted(seal["manifest"]["changes"])
          and review.get("complete_context_anchors_acyclic") is True
          and review.get("complete_v3_proof_independently_accepted") is True
          and review.get("caller_bytes_args_proofrefs_verified") is True
          and review.get("pin_authority_sha256") == seal["manifest"]["caller"]["pin_authority_sha256"]
          and review.get("caller_pin_authority_authenticated") is True,
          "bounded_g2_ci_scope_review")


def _validate_g2_ci_publication(approval):
    """Normalized actual publication/readback judgment; never an inferred pass."""
    row = _keys(approval, {"publication", "manifest_sha256", "review_path", "review_sha256"},
                "bounded_g2_ci_publication")
    _closeout_publication(row["publication"])
    _closeout_digest(row["manifest_sha256"])
    _closeout_digest(row["review_sha256"])
    _need(type(row["review_path"]) is str and Path(row["review_path"]).is_absolute(),
          "bounded_g2_ci_publication")
    return row


def _validate_g2_ci_pair_observations(manifest, before, after):
    changes = _validate_g2_ci_manifest(manifest)["changes"]
    _keys(before, set(changes), "bounded_g2_ci_observed_paths")
    _keys(after, set(changes), "bounded_g2_ci_observed_paths")
    for path, pair in changes.items():
        if pair["before_sha256"] is None:
            _need(before[path] is None, "bounded_g2_ci_addition_exists")
        else:
            _need(before[path] == pair["before_sha256"], "bounded_g2_ci_preimage")
        _need(after[path] == pair["after_sha256"], "bounded_g2_ci_afterimage")


def _validate_g2_ci_caller_bytes(manifest, workflow_raw):
    """Exact existing workflow step form with literal nonempty parent-reviewed pins."""
    _validate_g2_ci_manifest(manifest)
    workflow = _document(workflow_raw, ".github/workflows/python-security.yml")
    steps = workflow.get("jobs", {}).get("security", {}).get("steps")
    _need(type(steps) is list, "bounded_g2_ci_workflow")
    selected = [step for step in steps if type(step) is dict
                and step.get("name") == "Complete Python correctness and Bandit gate"]
    _need(len(selected) == 1, "bounded_g2_ci_workflow")
    step = selected[0]
    env = step.get("env")
    _need(type(env) is dict and env.get("COMPLETE_SELECTION_SHA256") == manifest["complete_selection"]["sha256"]
          and env.get("TRUSTED_CONTEXT_SHA256") == manifest["trusted_context"]["sha256"],
          "bounded_g2_ci_workflow_pins")
    run = step.get("run")
    _need(type(run) is str, "bounded_g2_ci_workflow_argv")
    lines = [line.strip() for line in run.replace("\\\n", " ").splitlines() if line.strip()]
    _need(len(lines) == 3 and lines[:2] == ['test -n "$COMPLETE_SELECTION_SHA256"',
          'test -n "$TRUSTED_CONTEXT_SHA256"'], "bounded_g2_ci_workflow_argv")
    command = lines[2].replace('"$COMPLETE_SELECTION_SHA256"', env["COMPLETE_SELECTION_SHA256"])
    command = command.replace('"$TRUSTED_CONTEXT_SHA256"', env["TRUSTED_CONTEXT_SHA256"])
    _need(command.split() == manifest["caller"]["argv"], "bounded_g2_ci_workflow_argv")


def _validate_g2_ci_publication_review(row, review):
    _validate_g2_ci_publication(row)
    _need(review.get("schema_version") == "emr4.g2_complete_ci_push_effect_review.v1"
          and review.get("verdict") == "PASS_EXACT_G2_COMPLETE_CI_PUSH_EFFECT"
          and review.get("reviewer_agent") == "/root/g2_admission_review"
          and review.get("independent") is True and review.get("implementation_authorship") is False
          and review.get("blocking_findings") == []
          and review.get("manifest_sha256") == row["manifest_sha256"]
          and all(review.get(k) == v for k, v in row["publication"].items())
          and review.get("whole_inverse_scope_verified") is True
          and review.get("caller_bytes_args_proof_readback_verified") is True
          and review.get("protected_refs_unchanged") is True
          and review.get("normal_nonforced_push") is True
          and review.get("same_attempt_remote_readback_verified") is True
          and review.get("remote_after") == {
              "refs/heads/codex/raisa-ariadne-recovery-g0": row["publication"]["commit"],
              "refs/heads/master": "2e34bdad732fdab32fbf778280b3d3c70d66d602",
              "refs/heads/handoff/current": "2e34bdad732fdab32fbf778280b3d3c70d66d602"},
          "bounded_g2_ci_publication_review")


def _validate_g2_ci_installed_policy(before):
    _keys(before, G2_CLOSEOUT_BEFORE_PATHS, "bounded_g2_ci_before_paths")
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    scope = _json(before[G2_SCOPE])
    seal = _validate_g2_ci_seal(scope.get("ci_adoption"))
    _need(scope.get("schema_version") == G2_CLOSEOUT_ENABLE_SCOPE_VERSION
          and state["current_gate"] == "G2" and state["current_gate_status"] == "active"
          and state["active_profile"] == G2_PROFILE and state["g2"]["status"] == "active"
          and state["g2"]["completion_accepted"] is False and "acceptance" not in state["g2"]
          and state["g2"]["scope_sha256"] == _sha(before[G2_SCOPE])
          and state["g2"]["current_operation"] == scope["current_operation"]
          and state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["task_selection"]["allowed_task_kinds"] == [G2_CLOSEOUT_CI_KIND, G2_CLOSEOUT_KIND]
          and overlay["active_profile"] == G2_PROFILE
          and overlay["profiles"][G2_PROFILE] == raisa_policy.g2_closeout_preparation_profile(
              sorted(G2_CLOSEOUT_PATHS | set(seal["manifest"]["changes"]))),
          "bounded_g2_ci_policy")
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G2"]["exit_checks"] == list(G2_CRITERIA)
          and by_id["G2"]["status"] == "active" and by_id["G3"]["status"] == "blocked_by_G2",
          "bounded_g2_ci_gate")
    return seal


def _load_g2_ci_adoption_inputs(context, target, source, evidence_root, scratch, q, read, snapshots):
    _keys(q, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
        "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
        "installed_controller", "ci_manifest", "preparation_review_path", "preparation_review_sha256"},
        "bounded_g2_ci_binding_schema")
    _need(q["schema_version"] == G2_CLOSEOUT_CI_BINDING_VERSION
          and q["operation_kind"] == G2_CLOSEOUT_CI_KIND, "bounded_g2_ci_binding_version")
    _need(type(q["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", q["operation_id"])
          and q["phase"] in {"development", "pre-push", "post-push"}, "bounded_g2_ci_phase")
    _need(all(type(q[k]) is str and re.fullmatch(r"[0-9a-f]{40}", q[k]) for k in
        ("base_commit", "base_tree", "candidate_tree", "expected_head", "expected_index_tree")),
        "bounded_g2_ci_git_binding")
    manifest = _validate_g2_ci_manifest(q["ci_manifest"])
    paths = frozenset(manifest["changes"])
    sources = _digest_map(q["source_sha256"], SOURCE_PATHS | CONTROLLER_PATHS, "bounded_g2_ci_sources")
    _need(sources["orchestration_harness/trusted_git.py"] ==
          "4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527", "bounded_g2_ci_sources")
    _validate_installed_controller(q["installed_controller"])
    _batch_publication(target, q["installed_controller"], q["base_commit"])
    for p, digest in sources.items():
        raw = read(source / p, digest)
        _need(raw == trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p),
              "bounded_g2_ci_source_not_installed")
        if p in CONTROLLER_PATHS:
            _need(q["installed_controller"]["source_sha256"][p] == digest, "bounded_g2_ci_sources")
    before = {p: trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p)
              for p in G2_CLOSEOUT_BEFORE_PATHS}
    seal = _validate_g2_ci_installed_policy(before)
    _need(_canonical(manifest) == _canonical(seal["manifest"]), "bounded_g2_ci_sealed_map_disagreement")
    _validate_g2_ci_scope_review(seal, _json(read(Path(seal["review_path"]), seal["review_sha256"])))
    required = G2_CATALOGUE_POLICY_PATHS | SOURCE_PATHS | CONTROLLER_PATHS | paths | {
        ref["path"] for ref in manifest["caller"].values() if type(ref) is dict}
    pins = _digest_map(q["payload_sha256"], required, "bounded_g2_ci_payload_paths")
    payloads = {p: read(target / p, digest) for p, digest in sorted(pins.items())}
    for p in required - paths:
        _need(payloads[p] == trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p),
              "bounded_g2_ci_unowned_changed")
    observed_before = {}
    for p, pair in manifest["changes"].items():
        if pair["before_sha256"] is None:
            _need(trusted_git.run_git_bytes(target, "ls-tree", "-z", q["base_commit"], "--", p) == b"",
                  "bounded_g2_ci_addition_exists")
            observed_before[p] = None
        else:
            observed_before[p] = _sha(trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p))
    _validate_g2_ci_pair_observations(manifest, observed_before,
                                    {p: _sha(payloads[p]) for p in paths})
    for ref in manifest["caller"].values():
        if type(ref) is dict:
            _need(pins[ref["path"]] == ref["sha256"], "bounded_g2_ci_caller_readback")
    _validate_g2_ci_caller_bytes(manifest, payloads[manifest["caller"]["workflow"]["path"]])
    _need(type(q["preparation_review_path"]) is str and Path(q["preparation_review_path"]).is_absolute(),
          "bounded_g2_ci_preparation_review")
    _closeout_digest(q["preparation_review_sha256"])
    review = _json(read(Path(q["preparation_review_path"]), q["preparation_review_sha256"]))
    _need(review.get("schema_version") == "emr4.g2_complete_ci_preparation_effect_review.v1"
          and review.get("verdict") == "PASS_EXACT_G2_COMPLETE_CI_PREPARATION_EFFECT"
          and review.get("reviewer_agent") == "/root/g2_admission_review" and review.get("independent") is True
          and review.get("implementation_authorship") is False and review.get("blocking_findings") == []
          and review.get("manifest_sha256") == seal["manifest_sha256"]
          and review.get("base_commit") == q["base_commit"] and review.get("base_tree") == q["base_tree"]
          and review.get("candidate_tree") == q["candidate_tree"]
          and review.get("whole_inverse_scope_verified") is True
          and review.get("inverse_tree") == q["base_tree"], "bounded_g2_ci_preparation_review")
    observation = trusted_git.attest_target_index(target,
        attested_paths=tuple(sorted(required - paths if q["phase"] == "development" else required)),
        expected_head=q["expected_head"], expected_index_tree=q["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", q["base_commit"] + "^{tree}") == q["base_tree"],
          "bounded_g2_ci_base_tree")
    if q["phase"] == "development":
        _need(q["expected_head"] == q["base_commit"] and q["expected_index_tree"] in
              {q["base_tree"], q["candidate_tree"]}, "bounded_g2_ci_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", q["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([x for x in headers if x.startswith("parent ")] == ["parent " + q["base_commit"]]
              and [x for x in headers if x.startswith("tree ")] == ["tree " + q["candidate_tree"]]
              and q["expected_index_tree"] == q["candidate_tree"], "bounded_g2_ci_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(q, before, payloads, {"scope_review": seal, "preparation_review": review}, observation)


def _validate_g2_ci_loaded_policy(inputs):
    _validate_g2_ci_installed_policy(inputs.before)
    try:
        configuration = raisa_policy.validate_recovery_configuration(
            documents={Path(p).name: inputs.payloads[p] for p in CONFIGURATION_PATHS},
            expected_sha256={Path(p).name: inputs.binding["payload_sha256"][p] for p in CONFIGURATION_PATHS},
            agents_text=inputs.payloads[AGENTS].decode("utf-8"), state=_json(inputs.payloads[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    return {p: inputs.payloads[p] for p in G2_TRANSITION_PATHS}, configuration


# G2 closeout is a distinct state-only operation, never a G3 implementation grant.
G2_CLOSEOUT_KIND = "accept_g2_closeout"
G2_CLOSEOUT_BINDING_VERSION = "ariadne.g2_closeout_binding.v1"
G2_CLOSEOUT_SCOPE_VERSION = "ariadne.g2_closeout_scope.v1"
G2_CLOSEOUT_SCOPE = "orchestration/programme/g2-closeout-scope.json"
G2_CLOSEOUT_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G2_CLOSEOUT_SCOPE})
G2_CLOSEOUT_BEFORE_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G2_SCOPE})
G2_CLOSEOUT_HELPER = "scripts/python_source_state.py"
G2_CLOSEOUT_HELPER_SHA256 = "f430803e889b4c3aa0269e12dbff4d965eea2dec0917ac051d8d78225c67b61c"
G2_CLOSEOUT_SOURCE_PATHS = SOURCE_PATHS | CONTROLLER_PATHS | {G2_CLOSEOUT_HELPER}
G2_CLOSEOUT_INPUT_PATHS = G2_CATALOGUE_POLICY_PATHS | G2_CLOSEOUT_SOURCE_PATHS | G2_SIX_PATHS | G2_CLOSEOUT_PATHS
G2_CI_RESEAL_KIND = "reseal_g2_complete_ci_workflow"
G2_CI_RESEAL_BINDING_VERSION = "ariadne.g2_ci_workflow_reseal_binding.v1"
G2_CI_RESEAL_PATHS = frozenset({STATE, G2_SCOPE}) | frozenset({
    "orchestration_harness/bounded_g1b.py", "tests/test_bounded_g1b.py"})
G2_CI_RESEAL_CODE_PATHS = frozenset({"orchestration_harness/bounded_g1b.py", "tests/test_bounded_g1b.py"})
G2_CI_RESEAL_BASE = {"commit": "9339bf63bc935a36d8dc8a27b7731a3cf7f8b445",
    "parent": "6f0ff52e9a4c95efa10bb475480cfb31245500e7",
    "tree": "3048a0b438e21ff95e25081be2fad028ec7f48fe"}
G2_CI_RESEAL_BEFORE = {STATE: "d2c5ffa60b7591d3b7cc054635957f250494deb69c7531f6e545f73e3e52be6f",
    G2_SCOPE: "342dc1da1098505154630ae489aaebc97cf4342e8403ee6b0e0bdf80632827fb",
    OVERLAY: "a67f862b86590fae335d0482d6e89b1ab991c75029da89490280e14e15768e4b",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    **{"orchestration_harness/bounded_g1b.py": "e72db832200b31c03cd9452b3112607d670b4b6db06d41e966ffaac8483635a2",
       "tests/test_bounded_g1b.py": "b6e4e5596b427eef437257a80902175493fda20f815c53137b008b16cfb1cbb8"}}
G2_CI_RESEAL_OLD_MANIFEST_SHA256 = "43347d327970acec761f1055627a1ea7a5dfe0728b5d9c69bdb0a2e9a7327e7d"
G2_CI_RESEAL_NEW_MANIFEST_SHA256 = "06de999f1ba3279d41564e8b3eb4ac95cb9b41549b5195c15261289f16c8b89f"
G2_CI_RESEAL_OLD_WORKFLOW_SHA256 = "23dcd6517ec1486ef7f93c3e63a2482f14b2a1512f4756f57d109898acee562e"
G2_CI_RESEAL_NEW_WORKFLOW_SHA256 = "f6b631cd619aabf221b2b79b8024e3f7d8697ce85dca48bdc565276a235bdec3"
G2_CI_RESEAL_INSTALLED_CONTROLLER = {**G2_CI_RESEAL_BASE, "source_sha256": {
    "orchestration_harness/bounded_g1b.py": G2_CI_RESEAL_BEFORE["orchestration_harness/bounded_g1b.py"],
    "tests/test_bounded_g1b.py": G2_CI_RESEAL_BEFORE["tests/test_bounded_g1b.py"],
    "orchestration_harness/raisa_policy.py": "9fb5ce31aebf880a8dba0f7190be15813077b86faca794bb4c47772901c9e2bf",
    "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
    "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181"}}
G2_CI_RESEAL_LIMITS = ("exact published G2 CI workflow reseal and four-file controller maintenance only",
    "G2 remains active; old admissions, scopes, latches and grants remain historical",
    "no G3, feature, runtime, provider, protected-ref, integration or deployment authority")
OPERATION_PATHS[G2_CI_RESEAL_KIND] = G2_CI_RESEAL_PATHS
G2_CLOSEOUT_CI_ROWS = ("python_compile", "ruff_e9_f401", "historical_diary_leakage",
    "ordinary_test_collection_and_execution", "bandit_medium_high", "dependency_audit",
    "empty_and_populated_migrations", "application_safety_controls")
G2_CLOSEOUT_LIMITS = ("G2 accepted closeout only; G3 needs separate admission",
    "no feature, runtime, provider, protected-ref, integration or deployment authority",
    "historical operations, scopes, latches and consumed grants remain unchanged")
OPERATION_PATHS[G2_CLOSEOUT_KIND] = G2_CLOSEOUT_PATHS
BOUNDED_SCOPE_PATHS = BOUNDED_SCOPE_PATHS | {G2_CLOSEOUT_SCOPE}


def _closeout_digest(value, reason="bounded_g2_closeout_digest"):
    _need(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None, reason)
    return value


def _closeout_publication(value):
    _keys(value, {"commit", "parent", "tree"}, "bounded_g2_closeout_publication")
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v) for v in value.values()),
          "bounded_g2_closeout_publication")
    return value


def _validate_g2_closeout_approval(approval):
    """Authenticate the shape of prior independent judgments, not a new verdict."""
    _keys(approval, {"schema_version", "verdict", "reviewer_agent", "implementer_ids",
        "independent", "implementation_authorship", "blocking_findings", "pending",
        "product_subject_sha256", "product_publication", "product_publication_review_sha256",
        "prior_policy_sha256", "complete_selection", "trusted_context", "complete_context",
        "criteria", "required_ci_map", "evidence_sha256", "ci_adoption"}, "bounded_g2_closeout_approval_schema")
    _need(approval["schema_version"] == "emr4.g2_prior_closeout_acceptance.v1"
          and approval["verdict"] == "accepted" and approval["pending"] == []
          and approval["blocking_findings"] == [], "bounded_g2_closeout_acceptance_pending")
    ids = approval["implementer_ids"]
    _need(approval["reviewer_agent"] == "/root/g2_admission_review"
          and approval["independent"] is True and approval["implementation_authorship"] is False
          and type(ids) is list and ids and all(type(x) is str and x for x in ids)
          and len(set(x.casefold() for x in ids)) == len(ids)
          and approval["reviewer_agent"].casefold() not in {x.casefold() for x in ids},
          "bounded_g2_closeout_independence")
    _need(approval["product_subject_sha256"] == G2_SIX_SUBJECT_SHA256,
          "bounded_g2_closeout_product_subject")
    _closeout_publication(approval["product_publication"])
    _closeout_digest(approval["product_publication_review_sha256"])
    _digest_map(approval["prior_policy_sha256"], G2_CLOSEOUT_BEFORE_PATHS,
                "bounded_g2_closeout_prior_policy")
    for key in ("complete_selection", "trusted_context"):
        _keys(approval[key], {"path", "sha256"}, "bounded_g2_closeout_complete_reference")
        _closeout_digest(approval[key]["sha256"])
    context = _keys(approval["complete_context"], {"plan_sha256", "authority_sha256", "source_sha256",
        "config_sha256", "runtime_sha256", "verifier_sha256", "result_id"},
        "bounded_g2_closeout_complete_context")
    for key in context:
        if key != "result_id":
            _closeout_digest(context[key])
    _need(type(context["result_id"]) is str and context["result_id"],
          "bounded_g2_closeout_complete_context")
    _validate_g2_ci_publication(approval["ci_adoption"])
    evidence = approval["evidence_sha256"]
    _need(type(evidence) is dict and 0 < len(evidence) <= 256,
          "bounded_g2_closeout_evidence")
    for digest in evidence.values():
        _closeout_digest(digest)
    _need(approval["product_publication_review_sha256"] in evidence.values(),
          "bounded_g2_closeout_publication_review_unbound")
    criteria = approval["criteria"]
    _need(type(criteria) is list and len(criteria) == len(G2_CRITERIA),
          "bounded_g2_closeout_criteria")
    seen = set()
    for row in criteria:
        _keys(row, {"id", "verdict", "evidence_sha256"}, "bounded_g2_closeout_criterion_schema")
        _need(row["id"] in G2_CRITERIA and row["id"] not in seen,
              "bounded_g2_closeout_criteria")
        _need(row["verdict"] == "passed" or (row["id"] == "dependency_audit_pass_or_explicit_exception"
              and row["verdict"] == "explicit_exception_accepted"),
              "bounded_g2_closeout_criterion_not_accepted")
        _need(type(row["evidence_sha256"]) is list and row["evidence_sha256"]
              and all(x in evidence.values() for x in row["evidence_sha256"]),
              "bounded_g2_closeout_criterion_evidence_unbound")
        seen.add(row["id"])
    duties = approval["required_ci_map"]
    _keys(duties, set(G2_CLOSEOUT_CI_ROWS), "bounded_g2_closeout_ci_duties")
    _need(all(type(ids) is list and ids and all(type(x) is str and x for x in ids)
              and len(ids) == len(set(ids)) for ids in duties.values()),
          "bounded_g2_closeout_ci_duties")


def _validate_g2_closeout_trusted_roles(approval, trusted):
    """Join the fixed platform reviewer to its proof-safe identity only."""
    _need(approval["reviewer_agent"] == "/root/g2_admission_review"
          and "g2_admission_review" in trusted["reviewers"]
          and set(trusted["implementers"]) == set(approval["implementer_ids"])
          and "g2_admission_review" not in {x.casefold() for x in approval["implementer_ids"]},
          "bounded_g2_closeout_trusted_context")


def build_g2_closeout_scope(recorded_at, transition_base, approval):
    """Pure scope of prior accepted evidence; final tree review stays external."""
    _validate_g2_closeout_approval(approval)
    try:
        aware = type(recorded_at) is str and datetime.fromisoformat(recorded_at).tzinfo is not None
    except ValueError:
        aware = False
    _need(aware, "bounded_g1b_timestamp_invalid")
    _need(type(transition_base) is str and re.fullmatch(r"[0-9a-f]{40}", transition_base),
          "bounded_g1b_transition_base_invalid")
    return {"schema_version": G2_CLOSEOUT_SCOPE_VERSION, "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "operation_kind": G2_CLOSEOUT_KIND,
        "allowed_paths": sorted(G2_CLOSEOUT_PATHS), "allowed_effects": sorted(EFFECTS),
        "prior_acceptance_sha256": _sha(_canonical(approval)),
        "prior_acceptance": copy.deepcopy(approval), "criteria": list(G2_CRITERIA),
        "required_ci_rows": list(G2_CLOSEOUT_CI_ROWS), "g2_complete": True,
        "g3_implementation_authorized": False, "execution_authorized": False,
        "feature_work_eligible": False, "claim_limits": list(G2_CLOSEOUT_LIMITS)}


def build_g2_closeout_transition(before, scope):
    """Close G2 only; never consume or rewrite an earlier operation record."""
    _keys(before, G2_CLOSEOUT_BEFORE_PATHS, "bounded_g2_closeout_before_paths")
    expected = build_g2_closeout_scope(scope.get("recorded_at"), scope.get("transition_base_commit"),
                                       scope.get("prior_acceptance"))
    _need(_canonical(scope) == _canonical(expected), "bounded_g2_closeout_scope")
    pins = scope["prior_acceptance"]["prior_policy_sha256"]
    _need(all(type(before[p]) is bytes and _sha(before[p]) == pins[p] for p in before),
          "bounded_g2_closeout_preimage")
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    _need(state["programme_mode"] == "recovery" and state["current_gate"] == "G2" and state["current_gate_status"] == "active"
          and state["active_profile"] == G2_PROFILE and state["g2"]["status"] == "active"
          and state["g2"]["completion_accepted"] is False and "acceptance" not in state["g2"]
          and state["g2"]["scope_sha256"] == _sha(before[G2_SCOPE])
          and state["g2"]["current_operation"] == _json(before[G2_SCOPE])["current_operation"]
          and state["feature_work_eligible"] is False and state["product_work_eligible"] is False,
          "bounded_g2_closeout_predecessor")
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G2"]["exit_checks"] == list(G2_CRITERIA)
          and by_id["G2"]["status"] == "active" and by_id["G3"]["status"] == "blocked_by_G2"
          and gates["programme"]["current_gate"] == "G2"
          and overlay["active_profile"] == G2_PROFILE,
          "bounded_g2_closeout_gate_predecessor")
    seal = _validate_g2_ci_installed_policy(before)
    _need(scope["prior_acceptance"]["ci_adoption"]["manifest_sha256"] == seal["manifest_sha256"],
          "bounded_g2_closeout_ci_adoption_unbound")
    raw = _canonical(scope) + b"\n"
    state.update(observed_at=scope["recorded_at"], current_gate_status="passed",
                 active_profile=raisa_policy.G2_CLOSED_PROFILE)
    state["g2"].update(status="passed", completion_accepted=True,
        acceptance={"scope_path": G2_CLOSEOUT_SCOPE, "scope_sha256": _sha(raw),
                    "prior_acceptance_sha256": scope["prior_acceptance_sha256"]})
    state["global_checks"]["current_required_ci_acceptance"] = copy.deepcopy(
        scope["prior_acceptance"]["complete_selection"])
    state["global_checks"]["global_gate"] = "g2_accepted_closed"
    state["task_selection"].update(allowed_task_kinds=[], next_eligible_tranche="G3",
        next_eligible_now=False, next_tranche_started=False,
        next_tranche_admission_requires_state_transition=True,
        next_eligibility_condition="G2_accepted_G3_requires_separate_reviewed_admission")
    gates["programme"].update(current_gate_status="passed", next_eligible_tranche="G3",
                               prepared_at=scope["recorded_at"])
    by_id["G2"]["status"] = "passed"
    by_id["G3"]["status"] = "blocked_pending_separate_admission"
    overlay["active_profile"] = raisa_policy.G2_CLOSED_PROFILE
    overlay["profiles"][raisa_policy.G2_CLOSED_PROFILE] = raisa_policy.g2_accepted_closed_profile()
    text = before[AGENTS].decode("utf-8")
    _need(text.count(raisa_policy.G2_PREAMBLE) == 1, "bounded_g2_closeout_preamble")
    text = text.replace(raisa_policy.G2_PREAMBLE, raisa_policy.G2_CLOSED_PREAMBLE, 1)
    lines = text.splitlines(keepends=True)
    positions = [i for i, line in enumerate(lines) if line.startswith("| Active programme gate |")]
    _need(len(positions) == 1, "bounded_g2_closeout_instruction_row")
    ending = "\r\n" if lines[positions[0]].endswith("\r\n") else "\n"
    lines[positions[0]] = "| Active programme gate | G2 accepted and closed; G3 implementation requires separate reviewed admission. Runtime, providers and protected integration remain closed. |" + ending
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
        GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
        OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
        AGENTS: "".join(lines).encode(), G2_CLOSEOUT_SCOPE: raw}


def _load_closeout_helper(source, read):
    """One additional closed-kind-only attested stdlib-only import; no discovery."""
    import importlib.util
    path = source / G2_CLOSEOUT_HELPER
    raw = read(path, G2_CLOSEOUT_HELPER_SHA256)
    spec = importlib.util.spec_from_file_location("_g2_closeout_complete_v3", path)
    _need(spec is not None and spec.loader is not None, "bounded_g2_closeout_helper")
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def _load_g2_closeout_inputs(context, target, source, evidence_root, scratch, q, read, snapshots):
    _keys(q, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
        "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
        "prior_policy_sha256", "prior_acceptance_path", "prior_acceptance_sha256", "proof_sha256",
        "installed_controller", "complete_source_sha256"}, "bounded_g2_closeout_binding_schema")
    _need(q["schema_version"] == G2_CLOSEOUT_BINDING_VERSION and q["operation_kind"] == G2_CLOSEOUT_KIND,
          "bounded_g2_closeout_binding_version")
    _need(type(q["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", q["operation_id"]),
          "bounded_g2_closeout_operation_id")
    _need(q["phase"] in {"development", "pre-push", "post-push"}, "bounded_g2_closeout_phase")
    _need(all(type(q[k]) is str and re.fullmatch(r"[0-9a-f]{40}", q[k]) for k in
        ("base_commit", "base_tree", "candidate_tree", "expected_head", "expected_index_tree")),
        "bounded_g2_closeout_git_binding")
    source_pins = _digest_map(q["source_sha256"], G2_CLOSEOUT_SOURCE_PATHS, "bounded_g2_closeout_source_paths")
    _need(source_pins[G2_CLOSEOUT_HELPER] == G2_CLOSEOUT_HELPER_SHA256
          and source_pins["orchestration_harness/trusted_git.py"] ==
          "4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527",
          "bounded_g2_closeout_source_changed")
    for path, digest in source_pins.items():
        raw = read(source / path, digest)
        _need(trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + path) == raw,
              "bounded_g2_closeout_source_not_installed")
    helper = _load_closeout_helper(source, read)
    _validate_installed_controller(q["installed_controller"])
    _batch_publication(target, q["installed_controller"], q["base_commit"])
    for path, digest in q["installed_controller"]["source_sha256"].items():
        _need(source_pins[path] == digest and _sha(trusted_git.run_git_bytes(target, "cat-file", "blob",
            q["installed_controller"]["commit"] + ":" + path)) == digest,
            "bounded_g2_closeout_controller_disagreement")
    pins = _digest_map(q["payload_sha256"], G2_CLOSEOUT_INPUT_PATHS, "bounded_g2_closeout_payload_paths")
    payloads = {p: read(target / p, digest) for p, digest in sorted(pins.items())}
    before = {p: trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p)
              for p in G2_CLOSEOUT_BEFORE_PATHS}
    _need(_digest_map(q["prior_policy_sha256"], G2_CLOSEOUT_BEFORE_PATHS,
                     "bounded_g2_closeout_prior_policy") == {p: _sha(raw) for p, raw in before.items()},
          "bounded_g2_closeout_preimage")
    _need(trusted_git.run_git_bytes(target, "ls-tree", "-z", q["base_commit"], "--", G2_CLOSEOUT_SCOPE) == b"",
          "bounded_g2_closeout_already_consumed")
    for p in G2_CLOSEOUT_INPUT_PATHS - G2_CLOSEOUT_PATHS:
        _need(trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p) == payloads[p],
              "bounded_g2_closeout_unowned_changed")
    proof_pins = q["proof_sha256"]
    _need(type(proof_pins) is dict and 0 < len(proof_pins) <= 258, "bounded_g2_closeout_proof_paths")
    # The trusted caller's exact binding declares ordinary data paths before any read.
    proof = {}
    _need(len({p.casefold() for p in proof_pins if type(p) is str}) == len(proof_pins),
          "bounded_g2_closeout_proof_path")
    for p, digest in proof_pins.items():
        helper._literal_path(p)
        _closeout_digest(digest)
        _need(p.startswith("orchestration/programme/g2-closeout-evidence/"),
              "bounded_g2_closeout_proof_path")
        proof[p] = read(target / p, digest)
    # External prior judgment follows actual CI adoption. It cannot be an
    # earlier CI payload which binds the policy containing that same map.
    approval_path = q["prior_acceptance_path"]
    _need(type(approval_path) is str and Path(approval_path).is_absolute(),
          "bounded_g2_closeout_approval_unbound")
    _closeout_digest(q["prior_acceptance_sha256"])
    approval = _json(read(Path(approval_path), q["prior_acceptance_sha256"]))
    _validate_g2_closeout_approval(approval)
    _need(approval["prior_policy_sha256"] == q["prior_policy_sha256"], "bounded_g2_closeout_prior_policy")
    seal = _validate_g2_ci_installed_policy(before)
    _need(proof_pins == seal["manifest"]["proof_sha256"]
          and approval["complete_selection"] == seal["manifest"]["complete_selection"]
          and approval["trusted_context"] == seal["manifest"]["trusted_context"],
          "bounded_g2_closeout_ci_proof_readback")
    ci = _validate_g2_ci_publication(approval["ci_adoption"])
    _need(ci["manifest_sha256"] == seal["manifest_sha256"], "bounded_g2_closeout_ci_adoption_unbound")
    _validate_g2_ci_publication_review(ci, _json(read(Path(ci["review_path"]), ci["review_sha256"])))
    _batch_publication(target, ci["publication"], q["base_commit"])
    for p, pair in seal["manifest"]["changes"].items():
        raw = read(target / p, pair["after_sha256"])
        _need(raw == trusted_git.run_git_bytes(target, "cat-file", "blob", ci["publication"]["commit"] + ":" + p)
              and raw == trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p),
              "bounded_g2_closeout_ci_payload_readback")
    for ref in seal["manifest"]["caller"].values():
        if type(ref) is dict:
            raw = read(target / ref["path"], ref["sha256"])
            _need(raw == trusted_git.run_git_bytes(target, "cat-file", "blob", ci["publication"]["commit"] + ":" + ref["path"])
                  and raw == trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + ref["path"]),
                  "bounded_g2_closeout_ci_caller_readback")
    _validate_g2_ci_caller_bytes(seal["manifest"], read(target / seal["manifest"]["caller"]["workflow"]["path"],
        seal["manifest"]["caller"]["workflow"]["sha256"]))
    for p, digest in approval["evidence_sha256"].items():
        _need(proof_pins.get(p) == digest, "bounded_g2_closeout_evidence_unbound")
    # Authenticate the complete graph and bounded source allowlist before the
    # unchanged complete-v3 loader can follow any reference. No discovery.
    for key in ("complete_selection", "trusted_context"):
        ref = approval[key]
        _need(proof_pins.get(ref["path"]) == ref["sha256"], "bounded_g2_closeout_complete_unbound")
    wrapper = _json(proof[approval["complete_selection"]["path"]])
    _need(type(wrapper.get("artifacts")) is list and wrapper["artifacts"],
          "bounded_g2_closeout_complete_unbound")
    _need(all(type(row) is dict and proof_pins.get(row.get("path")) == row.get("sha256")
              for row in wrapper["artifacts"]), "bounded_g2_closeout_complete_unbound")
    selected = [row for row in wrapper["artifacts"] if row.get("id") == wrapper.get("bounded_selection")]
    _need(len(selected) == 1, "bounded_g2_closeout_complete_unbound")
    bounded = helper.validate_selection(_json(proof[selected[0]["path"]]))
    selected_pins = {row["path"]: row["sha256"] for row in bounded["files"]}
    _need(type(q["complete_source_sha256"]) is dict and q["complete_source_sha256"] == selected_pins,
          "bounded_g2_closeout_complete_sources_unbound")
    for p, digest in selected_pins.items():
        helper._literal_path(p)
        _need(p not in proof_pins and p not in G2_CLOSEOUT_PATHS,
              "bounded_g2_closeout_proof_source_collision")
        read(target / p, digest)
    try:
        trusted = helper.load_complete_context(approval["trusted_context"]["path"],
            sha256=approval["trusted_context"]["sha256"], repo_root=target)
        _need(trusted["context"] == approval["complete_context"],
              "bounded_g2_closeout_trusted_context")
        _validate_g2_closeout_trusted_roles(approval, trusted)
        complete = helper.load_complete_selection(approval["complete_selection"]["path"],
            selection_sha256=approval["complete_selection"]["sha256"], trusted_context=trusted, repo_root=target)
    except helper.SourceStateError as error:
        raise BoundedG1BError("bounded_g2_closeout_complete_" + str(error)) from error
    _need({cid for ids in approval["required_ci_map"].values() for cid in ids} ==
          {row["id"] for row in wrapper["required_checks"]}, "bounded_g2_closeout_ci_duties")
    _need(complete["coverage"]["status"] == "authenticated_accepted_complete_evidence",
          "bounded_g2_closeout_complete_not_accepted")
    publication = approval["product_publication"]
    _batch_publication(target, publication, q["base_commit"])
    for p, pair in G2_SIX_REPAIR_PINS.items():
        _need(_sha(payloads[p]) == pair["after_sha256"] and _sha(trusted_git.run_git_bytes(target,
            "cat-file", "blob", publication["commit"] + ":" + p)) == pair["after_sha256"],
            "bounded_g2_closeout_product_not_installed")
    scope = _json(payloads[G2_CLOSEOUT_SCOPE])
    _need(scope["prior_acceptance"] == approval and scope["transition_base_commit"] == q["base_commit"],
          "bounded_g2_closeout_scope_disagreement")
    expected = build_g2_closeout_transition(before, scope)
    _need(all(payloads[p] == raw for p, raw in expected.items()), "bounded_g2_closeout_policy_delta")
    attested = G2_CLOSEOUT_INPUT_PATHS - G2_CLOSEOUT_PATHS if q["phase"] == "development" else G2_CLOSEOUT_INPUT_PATHS
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=q["expected_head"], expected_index_tree=q["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", q["base_commit"] + "^{tree}") == q["base_tree"],
          "bounded_g2_closeout_base_tree")
    if q["phase"] == "development":
        _need(q["expected_head"] == q["base_commit"] and q["expected_index_tree"] in
              {q["base_tree"], q["candidate_tree"]}, "bounded_g2_closeout_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", q["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([x for x in headers if x.startswith("parent ")] == ["parent " + q["base_commit"]]
              and [x for x in headers if x.startswith("tree ")] == ["tree " + q["candidate_tree"]]
              and q["expected_index_tree"] == q["candidate_tree"], "bounded_g2_closeout_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(q, before, payloads, proof, observation)


def _validate_g2_closeout_loaded_policy(inputs):
    after = {p: inputs.payloads[p] for p in G2_CLOSEOUT_PATHS}
    expected = build_g2_closeout_transition(inputs.before, _json(after[G2_CLOSEOUT_SCOPE]))
    _need(after == expected, "bounded_g2_closeout_policy_delta")
    try:
        configuration = raisa_policy.validate_recovery_configuration(
            documents={Path(p).name: inputs.payloads[p] for p in CONFIGURATION_PATHS},
            expected_sha256={Path(p).name: inputs.binding["payload_sha256"][p] for p in CONFIGURATION_PATHS},
            agents_text=after[AGENTS].decode("utf-8"), state=_json(after[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    return after, configuration


# Fixed V21 seven-path maintenance installer; old V20 builders and latches stay historical.
G2_CLOSEOUT_ENABLE_KIND = "enable_g2_closeout_control"
G2_CLOSEOUT_ENABLE_BINDING_VERSION = "ariadne.g2_closeout_enable_binding.v21"
G2_CLOSEOUT_ENABLE_SCOPE_VERSION = "ariadne.g2_closeout_enable_scope.v21"
G2_CLOSEOUT_ENABLE_PATHS = G2_BATCH_CODE_PATHS | G2_BATCH_CONTROL_PATHS | {G2_CLOSEOUT_HELPER}
G2_CLOSEOUT_HELPER_PREIMAGE_SHA256 = "deda2e86f7a6cfc1f8da56e45dc420c896a24749324e326cfc54e576e11528de"
G2_CLOSEOUT_ENABLE_INPUT_PATHS = G2_CATALOGUE_POLICY_PATHS | SOURCE_PATHS | CONTROLLER_PATHS | {G2_CLOSEOUT_HELPER}
G2_CLOSEOUT_V20_PUBLICATION = {
    "commit": "b5a1b76c578ccc9df9dbd8d27f1f933a06ef4211",
    "parent": "7d9edaa404d912b53316fe868cad4de0bbc8bf60",
    "tree": "474fd174067e079d97ddf447933730475132e6c8",
}
G2_CLOSEOUT_V20_SOURCE = {
    "orchestration_harness/bounded_g1b.py": "ca77be8c6ac915b489cf027206d169801fe5715f80d52cd7087f06cc961d4c87",
    "orchestration_harness/raisa_policy.py": "2575d02773ce740910cc30725041ee8e43ff430cb0b8a0ea4b0e0c7907ba20f8",
    "tests/test_bounded_g1b.py": "1516efa540a571bcc2a673737faf52751903c1c6b3d61887ae17de5b91f972d8",
    "orchestration_harness/configuration_core.py": "f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5",
    "orchestration_harness/programme_admission.py": "ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181",
}
G2_CLOSEOUT_V20_POLICY = {
    STATE: "0905831ca51d16b14e7ae396737ad5b743102b69522a41b360b3d47513060874",
    G2_SCOPE: "f30f74b6ae079743a47b6485069d63b675517fff47831014fa82dea069b3969c",
    OVERLAY: "2b23f225682d3387188ad0321936dc27c22a1c282c10c084c2c2ffe8eb83f91d",
    AGENTS: "97d6ea223508d53ee704a0cc3ceec383e2eea9f3db764376b538e8341bee886e",
    GATES: "115a651a0b13156a591045638d1833a9a71347e7b1f7e694767eac49d2abc341",
}
G2_CLOSEOUT_V20_REVIEW_PINS = {
    "commit": "e14cfd2529fd691ff0dcaf40fdf6ed4cb3a9a292068e615e3ac258db92ab7186",
    "push": "29ee5e98bef25266fc0fcb26e83c5a86485e2a8d7f07dbd0ad86750fe0d7f400",
}
G2_CLOSEOUT_ENABLE_LIMITS = (
    "fixed seven maintenance files only; product publication must precede installation",
    "G2 remains active; prior scopes, latches and consumed grants remain historical",
    "no closeout acceptance, G3, runtime, provider, protected or deployment authority",
)
OPERATION_PATHS[G2_CLOSEOUT_ENABLE_KIND] = G2_CLOSEOUT_ENABLE_PATHS


def _closeout_enable_before(before):
    _keys(before, G2_CLOSEOUT_BEFORE_PATHS, "bounded_g2_closeout_enable_before_paths")
    _need(all(type(raw) is bytes and _sha(raw) == G2_CLOSEOUT_V20_POLICY[p]
              for p, raw in before.items()), "bounded_g2_closeout_enable_preimage")
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    prior = _json(before[G2_SCOPE])
    _need(state["programme_mode"] == "recovery" and state["current_gate"] == "G2"
          and state["current_gate_status"] == "active" and state["active_profile"] == G2_PROFILE
          and state["g2"]["status"] == "active" and state["g2"]["completion_accepted"] is False
          and "acceptance" not in state["g2"] and state["feature_work_eligible"] is False
          and state["product_work_eligible"] is False
          and state["g2"]["scope_sha256"] == _sha(before[G2_SCOPE])
          and state["g2"]["current_operation"] == prior["current_operation"]
          and prior["schema_version"] == G2_SIX_SCOPE_VERSION
          and prior["repair_subject_sha256"] == G2_SIX_SUBJECT_SHA256,
          "bounded_g2_closeout_enable_predecessor")
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G2"]["exit_checks"] == list(G2_CRITERIA)
          and by_id["G2"]["status"] == "active" and by_id["G3"]["status"] == "blocked_by_G2"
          and gates["programme"]["current_gate"] == "G2" and overlay["active_profile"] == G2_PROFILE
          and overlay["profiles"][G2_PROFILE] == raisa_policy.g2_six_file_repair_profile(),
          "bounded_g2_closeout_enable_gate_predecessor")
    return state, overlay, prior


def build_g2_closeout_enable_scope(before, recorded_at, product_publication, controller_sources, ci_adoption):
    """Pure installer scope. Authored publication is not native publication proof."""
    _, _, prior = _closeout_enable_before(before)
    try:
        aware = type(recorded_at) is str and datetime.fromisoformat(recorded_at).tzinfo is not None
    except ValueError:
        aware = False
    _need(aware, "bounded_g1b_timestamp_invalid")
    _closeout_publication(product_publication)
    _need(product_publication["parent"] == G2_CLOSEOUT_V20_PUBLICATION["commit"]
          and product_publication["tree"] == "553497967c1aa51369e6bcef05eaf817e8ce123a"
          and product_publication["commit"] != product_publication["parent"],
          "bounded_g2_closeout_enable_product_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS, "bounded_g2_closeout_enable_sources")
    _need(all(sources[p] == G2_CLOSEOUT_V20_SOURCE[p] for p in CONTROLLER_PATHS - G2_BATCH_CODE_PATHS),
          "bounded_g2_closeout_enable_unchanged_controller")
    _need(all(sources[p] != G2_CLOSEOUT_V20_SOURCE[p] for p in G2_BATCH_CODE_PATHS),
          "bounded_g2_closeout_enable_source_successor")
    _validate_g2_ci_seal(ci_adoption)
    scope = copy.deepcopy(prior)
    scope.update(schema_version=G2_CLOSEOUT_ENABLE_SCOPE_VERSION, recorded_at=recorded_at,
        transition_base_commit=product_publication["commit"], controller_source_sha256=sources,
        enable_operation=G2_CLOSEOUT_ENABLE_KIND, repair_operation=G2_CLOSEOUT_KIND,
        allowed_paths=sorted(G2_CLOSEOUT_PATHS | set(ci_adoption["manifest"]["changes"])),
        maximum_changed_files=max(5, len(ci_adoption["manifest"]["changes"])),
        allowed_additions=sorted({G2_CLOSEOUT_SCOPE} | {p for p, pair in ci_adoption["manifest"]["changes"].items()
            if pair["before_sha256"] is None}), allowed_effects=sorted(EFFECTS),
        ci_adoption=copy.deepcopy(ci_adoption),
        forbidden_effects=raisa_policy.g2_closeout_preparation_profile()["forbidden_effects"],
        preserved_six_file_scope=copy.deepcopy(prior),
        installed_V20_publication=copy.deepcopy(G2_CLOSEOUT_V20_PUBLICATION),
        product_publication=copy.deepcopy(product_publication),
        maintenance_paths=sorted(G2_CLOSEOUT_ENABLE_PATHS),
        maintenance_effects=sorted(EFFECTS),
        closeout_helper={"path": G2_CLOSEOUT_HELPER, "before_sha256": G2_CLOSEOUT_HELPER_PREIMAGE_SHA256,
            "after_sha256": G2_CLOSEOUT_HELPER_SHA256, "new_kind_only_import": True}, g2_complete=False,
        g3_implementation_authorized=False, claim_limits=list(G2_CLOSEOUT_ENABLE_LIMITS))
    scope["current_operation"] = {
        **copy.deepcopy(prior["current_operation"]),
        "operation_id": "g2-closeout-control-preparation", "status": "active",
        "completion_accepted": False,
        "supersedes": {"operation_id": prior["current_operation"]["operation_id"],
            "scope_path": G2_SCOPE, "scope_commit": product_publication["commit"],
            "scope_sha256": G2_CLOSEOUT_V20_POLICY[G2_SCOPE], "historical_latch_preserved": True,
            "predecessor_completion_accepted": False}}
    return scope


def build_g2_closeout_enable_transition(before, scope):
    state, overlay, _ = _closeout_enable_before(before)
    expected = build_g2_closeout_enable_scope(before, scope.get("recorded_at"),
        scope.get("product_publication"), scope.get("controller_source_sha256"), scope.get("ci_adoption"))
    _need(_canonical(scope) == _canonical(expected), "bounded_g2_closeout_enable_scope")
    raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(raw), current_operation=copy.deepcopy(scope["current_operation"]))
    state["task_selection"].update(allowed_task_kinds=[G2_CLOSEOUT_CI_KIND, G2_CLOSEOUT_KIND], next_eligible_now=False,
        next_eligibility_condition="G2_closeout_requires_all12_complete_v3_and_final_independent_review")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_closeout_preparation_profile(scope["allowed_paths"])
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
        OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(), G2_SCOPE: raw}


def _validate_g2_ci_reseal_manifest_delta(old, new):
    """Only the quoted workflow afterimage and its caller digest may differ."""
    _validate_g2_ci_manifest(old)
    _validate_g2_ci_manifest(new)
    _need(_sha(_canonical(old)) == G2_CI_RESEAL_OLD_MANIFEST_SHA256,
          "bounded_g2_ci_reseal_old_manifest")
    _need(_sha(_canonical(new)) == G2_CI_RESEAL_NEW_MANIFEST_SHA256,
          "bounded_g2_ci_reseal_new_manifest")
    workflow = ".github/workflows/python-security.yml"
    _need(old["changes"][workflow]["after_sha256"] == G2_CI_RESEAL_OLD_WORKFLOW_SHA256
          and old["caller"]["workflow"]["sha256"] == G2_CI_RESEAL_OLD_WORKFLOW_SHA256,
          "bounded_g2_ci_reseal_old_workflow")
    expected = copy.deepcopy(old)
    expected["changes"][workflow]["after_sha256"] = G2_CI_RESEAL_NEW_WORKFLOW_SHA256
    expected["caller"]["workflow"]["sha256"] = G2_CI_RESEAL_NEW_WORKFLOW_SHA256
    _need(_canonical(new) == _canonical(expected), "bounded_g2_ci_reseal_manifest_delta")


def build_g2_ci_reseal_scope(before, recorded_at, controller_sources, ci_adoption):
    """Exact prospective V21 scope successor; no CI payload or G2 gate transition."""
    _keys(before, G2_CLOSEOUT_BEFORE_PATHS, "bounded_g2_ci_reseal_before_paths")
    _need(all(_sha(before[p]) == G2_CI_RESEAL_BEFORE[p] for p in before),
          "bounded_g2_ci_reseal_preimage")
    _validate_g2_ci_installed_policy(before)
    prior = _json(before[G2_SCOPE])
    _need(prior["controller_source_sha256"] == G2_CI_RESEAL_INSTALLED_CONTROLLER["source_sha256"],
          "bounded_g2_ci_reseal_controller_preimage")
    try:
        aware = type(recorded_at) is str and datetime.fromisoformat(recorded_at).tzinfo is not None
    except ValueError:
        aware = False
    _need(aware, "bounded_g1b_timestamp_invalid")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS, "bounded_g2_ci_reseal_sources")
    _need(all(sources[p] == G2_CI_RESEAL_INSTALLED_CONTROLLER["source_sha256"][p]
              for p in CONTROLLER_PATHS - G2_CI_RESEAL_CODE_PATHS)
          and all(sources[p] != G2_CI_RESEAL_INSTALLED_CONTROLLER["source_sha256"][p]
                  for p in G2_CI_RESEAL_CODE_PATHS), "bounded_g2_ci_reseal_source_successor")
    seal = _validate_g2_ci_seal(ci_adoption)
    _validate_g2_ci_reseal_manifest_delta(prior["ci_adoption"]["manifest"], seal["manifest"])
    scope = copy.deepcopy(prior)
    scope.update(recorded_at=recorded_at, controller_source_sha256=sources,
                 ci_adoption=copy.deepcopy(seal))
    return scope


def build_g2_ci_reseal_transition(before, scope):
    prior_state = _json(before[STATE])
    expected_scope = build_g2_ci_reseal_scope(before, scope.get("recorded_at"),
        scope.get("controller_source_sha256"), scope.get("ci_adoption"))
    _need(_canonical(scope) == _canonical(expected_scope), "bounded_g2_ci_reseal_scope")
    scope_raw = _canonical(scope) + b"\n"
    state = copy.deepcopy(prior_state)
    state["observed_at"] = scope["recorded_at"]
    state["g2"]["scope_sha256"] = _sha(scope_raw)
    state_raw = (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode()
    after = {**before, STATE: state_raw, G2_SCOPE: scope_raw}
    _validate_g2_ci_installed_policy(after)
    return {STATE: state_raw, G2_SCOPE: scope_raw}


def _closeout_enable_changes(q):
    _keys(q["repair_sha256"], G2_CLOSEOUT_ENABLE_PATHS, "bounded_g2_closeout_enable_paths")
    for p, row in q["repair_sha256"].items():
        _keys(row, {"before_sha256", "after_sha256"}, "bounded_g2_closeout_enable_pair")
        _closeout_digest(row["before_sha256"])
        _closeout_digest(row["after_sha256"])
        expected = (G2_CLOSEOUT_V20_SOURCE[p] if p in G2_BATCH_CODE_PATHS
                    else G2_CLOSEOUT_HELPER_PREIMAGE_SHA256 if p == G2_CLOSEOUT_HELPER
                    else G2_CLOSEOUT_V20_POLICY[p])
        _need(row["before_sha256"] == expected and row["before_sha256"] != row["after_sha256"],
              "bounded_g2_closeout_enable_preimage")
        if p == G2_CLOSEOUT_HELPER:
            _need(row["after_sha256"] == G2_CLOSEOUT_HELPER_SHA256,
                  "bounded_g2_closeout_enable_helper")
        if p in G2_BATCH_CODE_PATHS:
            _need(row["after_sha256"] == q["source_sha256"][p],
                  "bounded_g2_closeout_enable_executing_source")
    return q["repair_sha256"]


def _load_g2_closeout_enable_inputs(context, target, source, evidence_root, scratch, q, read, snapshots):
    _keys(q, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
        "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
        "installed_controller", "repair_sha256", "product_publication", "publication_review_paths",
        "product_publication_review_path", "product_publication_review_sha256"},
        "bounded_g2_closeout_enable_binding_schema")
    _need(q["schema_version"] == G2_CLOSEOUT_ENABLE_BINDING_VERSION
          and q["operation_kind"] == G2_CLOSEOUT_ENABLE_KIND,
          "bounded_g2_closeout_enable_binding_version")
    _need(type(q["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", q["operation_id"]),
          "bounded_g1b_operation_id")
    _need(q["phase"] in {"development", "pre-push", "post-push"}, "bounded_g1b_phase")
    _need(all(type(q[k]) is str and re.fullmatch(r"[0-9a-f]{40}", q[k]) for k in
        ("base_commit", "base_tree", "expected_head", "expected_index_tree", "candidate_tree")),
        "bounded_g2_closeout_enable_git_binding")
    sources = _digest_map(q["source_sha256"], SOURCE_PATHS | CONTROLLER_PATHS,
                          "bounded_g2_closeout_enable_source_paths")
    _need(sources["orchestration_harness/trusted_git.py"] ==
          "4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527",
          "bounded_g2_closeout_enable_trusted_git")
    changes = _closeout_enable_changes(q)
    _need(q["installed_controller"] == {**G2_CLOSEOUT_V20_PUBLICATION, "source_sha256": G2_CLOSEOUT_V20_SOURCE},
          "bounded_g2_closeout_enable_controller")
    _batch_publication(target, q["installed_controller"], q["base_commit"])
    for p, digest in sources.items():
        raw = read(source / p, digest)
        previous = trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p)
        if p in G2_BATCH_CODE_PATHS:
            _need(_sha(previous) == G2_CLOSEOUT_V20_SOURCE[p], "bounded_g2_closeout_enable_source_preimage")
        else:
            _need(previous == raw, "bounded_g2_closeout_enable_unchanged_source")
        if p in CONTROLLER_PATHS:
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_CLOSEOUT_V20_PUBLICATION["commit"] + ":" + p)) == G2_CLOSEOUT_V20_SOURCE[p],
                "bounded_g2_closeout_enable_controller")
    publication = _closeout_publication(q["product_publication"])
    _need(publication["commit"] == q["base_commit"] and publication["tree"] == q["base_tree"]
          and publication["parent"] == G2_CLOSEOUT_V20_PUBLICATION["commit"],
          "bounded_g2_closeout_enable_product_base")
    _batch_publication(target, publication, q["base_commit"])
    for p, row in G2_SIX_REPAIR_PINS.items():
        _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob",
            q["base_commit"] + ":" + p)) == row["after_sha256"],
            "bounded_g2_closeout_enable_product_not_published")
    _keys(q["publication_review_paths"], {"commit", "push"}, "bounded_g2_closeout_enable_review_paths")
    reviews = {}
    for kind, pin in G2_CLOSEOUT_V20_REVIEW_PINS.items():
        path = q["publication_review_paths"][kind]
        _need(type(path) is str and Path(path).is_absolute(), "bounded_g2_closeout_enable_review_path")
        row = _json(read(Path(path), pin))
        _need(row.get("reviewer_agent") == "/root/g2_admission_review" and row.get("independent") is True
              and row.get("implementation_authorship") is False and row.get("blocking_findings") == []
              and row.get("verdict") == "PASS_ISOLATED_V20_MAINTENANCE_" + kind.upper() + "_EFFECT"
              and all(row.get(k) == v for k, v in G2_CLOSEOUT_V20_PUBLICATION.items()),
              "bounded_g2_closeout_enable_publication_review")
        reviews[kind] = row
    _closeout_digest(q["product_publication_review_sha256"])
    product_path = q["product_publication_review_path"]
    _need(type(product_path) is str and Path(product_path).is_absolute(), "bounded_g2_closeout_enable_review_path")
    review = _json(read(Path(product_path), q["product_publication_review_sha256"]))
    _need(review.get("reviewer_agent") == "/root/g2_admission_review" and review.get("independent") is True
          and review.get("implementation_authorship") is False and review.get("blocking_findings") == []
          and review.get("schema_version") == "emr4.isolated_six_product_push_effect_review.v1"
          and review.get("verdict") == "PASS_ISOLATED_SIX_PRODUCT_PUSH_EFFECT"
          and review.get("protected_refs_unchanged") is True and review.get("normal_nonforced_push") is True
          and review.get("same_attempt_remote_readback_verified") is True
          and review.get("index_sha256") == "27b9d88a270e51f9a09fa1b16e3f0dd5b076bb73e7f062c934f6fc444c08bbfd"
          and type(review.get("result_sha256")) is str
          and re.fullmatch(r"[0-9a-f]{64}", review["result_sha256"])
          and review.get("remote_after") == {"refs/heads/codex/raisa-ariadne-recovery-g0": publication["commit"],
              "refs/heads/master": "2e34bdad732fdab32fbf778280b3d3c70d66d602",
              "refs/heads/handoff/current": "2e34bdad732fdab32fbf778280b3d3c70d66d602"}
          and all(review.get(k) == v for k, v in publication.items()),
          "bounded_g2_closeout_enable_product_review")
    pins = _digest_map(q["payload_sha256"], G2_CLOSEOUT_ENABLE_INPUT_PATHS,
                       "bounded_g2_closeout_enable_payload_paths")
    payloads = {p: read(target / p, digest) for p, digest in sorted(pins.items())}
    before = {p: trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p)
              for p in G2_CLOSEOUT_BEFORE_PATHS}
    _closeout_enable_before(before)
    for p in G2_CLOSEOUT_ENABLE_INPUT_PATHS - G2_CLOSEOUT_ENABLE_PATHS:
        _need(trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + p) == payloads[p],
              "bounded_g2_closeout_enable_unowned_changed")
    _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob",
        q["base_commit"] + ":" + G2_CLOSEOUT_HELPER)) == G2_CLOSEOUT_HELPER_PREIMAGE_SHA256,
        "bounded_g2_closeout_enable_helper_preimage")
    for p, row in changes.items():
        _need(_sha(payloads[p]) == row["after_sha256"], "bounded_g2_closeout_enable_afterimage")
    for p in G2_BATCH_CODE_PATHS:
        _need(pins[p] == sources[p], "bounded_g2_closeout_enable_executing_source")
    scope = _json(payloads[G2_SCOPE])
    _need(scope["transition_base_commit"] == q["base_commit"] and scope["product_publication"] == publication
          and scope["controller_source_sha256"] == {p: sources[p] for p in CONTROLLER_PATHS},
          "bounded_g2_closeout_enable_scope_binding")
    seal = _validate_g2_ci_seal(scope["ci_adoption"])
    _validate_g2_ci_scope_review(seal, _json(read(Path(seal["review_path"]), seal["review_sha256"])))
    expected = build_g2_closeout_enable_transition(before, scope)
    _need(all(payloads[p] == raw for p, raw in expected.items()), "bounded_g2_closeout_enable_policy_delta")
    attested = G2_CLOSEOUT_ENABLE_INPUT_PATHS - G2_CLOSEOUT_ENABLE_PATHS if q["phase"] == "development" else G2_CLOSEOUT_ENABLE_INPUT_PATHS
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=q["expected_head"], expected_index_tree=q["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", q["base_commit"] + "^{tree}") == q["base_tree"],
          "bounded_g1b_base_tree_changed")
    if q["phase"] == "development":
        _need(q["expected_head"] == q["base_commit"] and q["expected_index_tree"] in
              {q["base_tree"], q["candidate_tree"]}, "bounded_g1b_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", q["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([x for x in headers if x.startswith("parent ")] == ["parent " + q["base_commit"]]
              and [x for x in headers if x.startswith("tree ")] == ["tree " + q["candidate_tree"]]
              and q["expected_index_tree"] == q["candidate_tree"], "bounded_g1b_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(q, before, payloads, reviews, observation)


def _validate_g2_closeout_enable_loaded_policy(inputs):
    expected = build_g2_closeout_enable_transition(inputs.before, _json(inputs.payloads[G2_SCOPE]))
    _need(all(inputs.payloads[p] == raw for p, raw in expected.items()), "bounded_g2_closeout_enable_policy_delta")
    try:
        configuration = raisa_policy.validate_recovery_configuration(
            documents={Path(p).name: inputs.payloads[p] for p in CONFIGURATION_PATHS},
            expected_sha256={Path(p).name: inputs.binding["payload_sha256"][p] for p in CONFIGURATION_PATHS},
            agents_text=inputs.payloads[AGENTS].decode("utf-8"), state=_json(inputs.payloads[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    return {p: inputs.payloads[p] for p in G2_TRANSITION_PATHS}, configuration


def _g2_ci_reseal_changes(q):
    _keys(q["repair_sha256"], G2_CI_RESEAL_PATHS, "bounded_g2_ci_reseal_paths")
    for path, pair in q["repair_sha256"].items():
        _keys(pair, {"before_sha256", "after_sha256"}, "bounded_g2_ci_reseal_pair")
        _closeout_digest(pair["after_sha256"])
        _need(pair["before_sha256"] == G2_CI_RESEAL_BEFORE[path]
              and pair["after_sha256"] != pair["before_sha256"],
              "bounded_g2_ci_reseal_preimage")
        if path in G2_CI_RESEAL_CODE_PATHS:
            _need(pair["after_sha256"] == q["source_sha256"][path],
                  "bounded_g2_ci_reseal_executing_source")
    return q["repair_sha256"]


def _validate_g2_ci_reseal_scope_sources(scope, sources):
    """Recorded controller identity must equal the authenticated executing source."""
    _need(type(scope) is dict and scope.get("controller_source_sha256") ==
          {path: sources[path] for path in CONTROLLER_PATHS},
          "bounded_g2_ci_reseal_scope_sources")


def _load_g2_ci_reseal_inputs(context, target, source, evidence_root, scratch, q, read, snapshots):
    _keys(q, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
        "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
        "installed_controller", "repair_sha256", "ci_adoption_seal_path", "ci_adoption_seal_sha256"},
        "bounded_g2_ci_reseal_binding_schema")
    _need(q["schema_version"] == G2_CI_RESEAL_BINDING_VERSION
          and q["operation_kind"] == G2_CI_RESEAL_KIND,
          "bounded_g2_ci_reseal_binding_version")
    _need(type(q["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", q["operation_id"])
          and q["phase"] in {"development", "pre-push", "post-push"}, "bounded_g2_ci_reseal_phase")
    _need(q["base_commit"] == G2_CI_RESEAL_BASE["commit"]
          and q["base_tree"] == G2_CI_RESEAL_BASE["tree"]
          and all(type(q[k]) is str and re.fullmatch(r"[0-9a-f]{40}", q[k]) for k in
                  ("expected_head", "expected_index_tree", "candidate_tree")),
          "bounded_g2_ci_reseal_base")
    _need(q["installed_controller"] == G2_CI_RESEAL_INSTALLED_CONTROLLER,
          "bounded_g2_ci_reseal_installed_controller")
    _validate_installed_controller(q["installed_controller"])
    _batch_publication(target, q["installed_controller"], q["base_commit"])
    sources = _digest_map(q["source_sha256"], SOURCE_PATHS | CONTROLLER_PATHS,
                          "bounded_g2_ci_reseal_source_paths")
    _need(sources["orchestration_harness/trusted_git.py"] ==
          "4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527",
          "bounded_g2_ci_reseal_trusted_git")
    changes = _g2_ci_reseal_changes(q)
    for path, digest in sources.items():
        raw = read(source / path, digest)
        previous = trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + path)
        if path in G2_CI_RESEAL_CODE_PATHS:
            _need(_sha(previous) == G2_CI_RESEAL_BEFORE[path], "bounded_g2_ci_reseal_source_preimage")
        else:
            _need(previous == raw, "bounded_g2_ci_reseal_unchanged_source")
    before = {path: trusted_git.run_git_bytes(target, "cat-file", "blob", q["base_commit"] + ":" + path)
              for path in G2_CLOSEOUT_BEFORE_PATHS}
    _need(all(_sha(before[path]) == G2_CI_RESEAL_BEFORE[path] for path in before),
          "bounded_g2_ci_reseal_preimage")
    old_seal = _validate_g2_ci_installed_policy(before)
    old_review = _json(read(Path(old_seal["review_path"]), old_seal["review_sha256"]))
    _validate_g2_ci_scope_review(old_seal, old_review)
    seal_path = Path(q["ci_adoption_seal_path"])
    _need(seal_path.is_absolute() and seal_path != target and not seal_path.is_relative_to(target),
          "bounded_g2_ci_reseal_seal_path")
    _closeout_digest(q["ci_adoption_seal_sha256"])
    seal = _json(read(seal_path, q["ci_adoption_seal_sha256"]))
    _validate_g2_ci_seal(seal)
    _validate_g2_ci_reseal_manifest_delta(old_seal["manifest"], seal["manifest"])
    new_review = _json(read(Path(seal["review_path"]), seal["review_sha256"]))
    _validate_g2_ci_scope_review(seal, new_review)
    pins = _digest_map(q["payload_sha256"], G2_CLOSEOUT_ENABLE_INPUT_PATHS,
                       "bounded_g2_ci_reseal_payload_paths")
    payloads = {path: read(target / path, digest) for path, digest in sorted(pins.items())}
    for path in G2_CLOSEOUT_ENABLE_INPUT_PATHS - G2_CI_RESEAL_PATHS:
        _need(payloads[path] == trusted_git.run_git_bytes(target, "cat-file", "blob",
              q["base_commit"] + ":" + path), "bounded_g2_ci_reseal_unowned_changed")
    for path, pair in changes.items():
        _need(_sha(payloads[path]) == pair["after_sha256"], "bounded_g2_ci_reseal_afterimage")
    scope = _json(payloads[G2_SCOPE])
    _validate_g2_ci_reseal_scope_sources(scope, sources)
    _need(_canonical(scope["ci_adoption"]) == _canonical(seal),
          "bounded_g2_ci_reseal_seal_binding")
    expected = build_g2_ci_reseal_transition(before, scope)
    _need(all(payloads[path] == raw for path, raw in expected.items()),
          "bounded_g2_ci_reseal_policy_delta")
    attested = G2_CLOSEOUT_ENABLE_INPUT_PATHS - G2_CI_RESEAL_PATHS if q["phase"] == "development" else G2_CLOSEOUT_ENABLE_INPUT_PATHS
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=q["expected_head"], expected_index_tree=q["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", q["base_commit"] + "^{tree}") == q["base_tree"],
          "bounded_g2_ci_reseal_base_tree")
    if q["phase"] == "development":
        _need(q["expected_head"] == q["base_commit"] and q["expected_index_tree"] in
              {q["base_tree"], q["candidate_tree"]}, "bounded_g2_ci_reseal_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", q["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + q["base_commit"]]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + q["candidate_tree"]]
              and q["expected_index_tree"] == q["candidate_tree"],
              "bounded_g2_ci_reseal_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(q, before, payloads,
        {"old_scope_review": old_review, "new_scope_review": new_review}, observation)


def _validate_g2_ci_reseal_loaded_policy(inputs):
    expected = build_g2_ci_reseal_transition(inputs.before, _json(inputs.payloads[G2_SCOPE]))
    _need(all(inputs.payloads[path] == raw for path, raw in expected.items()),
          "bounded_g2_ci_reseal_policy_delta")
    try:
        configuration = raisa_policy.validate_recovery_configuration(
            documents={Path(path).name: inputs.payloads[path] for path in CONFIGURATION_PATHS},
            expected_sha256={Path(path).name: inputs.binding["payload_sha256"][path] for path in CONFIGURATION_PATHS},
            agents_text=inputs.payloads[AGENTS].decode("utf-8"), state=_json(inputs.payloads[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    return {path: inputs.payloads[path] for path in (STATE, G2_SCOPE)}, configuration



def operation_effects(kind: str) -> frozenset[str]:
    if kind == G2_CI_RESEAL_KIND:
        return EFFECTS
    if kind in {"repair_g2_migration", "repair_g2_migration_downgrade_guard",
                "repair_g2_appointment_concurrency"}:
        return G2_MIGRATION_EFFECTS
    if kind in {"repair_g2_batch", "repair_g2_audio_privacy", "repair_g2_patient_binding",
                "repair_g2_consultation_atomicity", "repair_g2_clinical_authority"}:
        return G2_BATCH_EFFECTS
    if kind in {"repair_g2_production_profile", "repair_g2_transport_repair", "repair_g2_six_file_repair"}:
        return G2_BATCH_EFFECTS
    if kind in {"repair_g2_dependency_repair", "repair_g2_pyjwt_repair"}:
        return G2_DEPENDENCY_EFFECTS
    if kind == "repair_g2_ci_migration":
        return G2_CIM_EFFECTS
    if kind == "repair_g2_tenant_migration":
        return G2_TENANT_EFFECTS
    if kind == "repair_g2_tenant_relationships":
        return G2_RELATIONSHIP_EFFECTS
    if kind == "repair_g2_ci_completeness":
        return G2_COMPLETENESS_EFFECTS
    if kind == "repair_g2_ci_selection":
        return G2_CI_EFFECTS
    return frozenset({"repository_read"}) if kind == "assess_g1e" else EFFECTS


def operation_paths(kind: str, binding: dict | None = None) -> frozenset[str]:
    _need(type(kind) is str and kind in OPERATION_PATHS, "bounded_g1b_operation_kind")
    if kind in {"repair_g2_batch", "repair_g2_migration", "repair_g2_audio_privacy",
                "repair_g2_patient_binding", "repair_g2_consultation_atomicity", "repair_g2_clinical_authority",
                 "repair_g2_migration_downgrade_guard", "repair_g2_appointment_concurrency",
                 "repair_g2_production_profile", "repair_g2_dependency_repair", "repair_g2_pyjwt_repair", "repair_g2_transport_repair", "repair_g2_six_file_repair",
                   "repair_g2_ci_selection", "repair_g2_tenant_migration",
                    "repair_g2_tenant_relationships", "repair_g2_ci_completeness"}:
        _need(type(binding) is dict and binding.get("operation_kind") == kind,
              "bounded_g2_batch_binding_required")
        return frozenset(_batch_changes(binding))
    if kind == G2_CLOSEOUT_CI_KIND:
        _need(type(binding) is dict and binding.get("operation_kind") == kind, "bounded_g2_ci_binding_required")
        return frozenset(_validate_g2_ci_manifest(binding.get("ci_manifest"))["changes"])
    return OPERATION_PATHS[kind]


def _operation(kind: str, binding: dict | None = None) -> dict:
    paths = operation_paths(kind, binding)
    if kind == G2_CI_RESEAL_KIND:
        return {"paths": paths, "input_paths": G2_CLOSEOUT_ENABLE_INPUT_PATHS,
                "transition_paths": frozenset({STATE, G2_SCOPE}), "scope_path": G2_SCOPE,
                "transition": False, "ci_reseal": True, "profile": G2_PROFILE, "gate": "G2",
                "limits": G2_CI_RESEAL_LIMITS}
    if kind == G2_CLOSEOUT_CI_KIND:
        return {"paths": paths, "input_paths": G2_CATALOGUE_POLICY_PATHS | SOURCE_PATHS | CONTROLLER_PATHS | paths,
                "transition_paths": G2_TRANSITION_PATHS, "scope_path": G2_SCOPE, "transition": False,
                "ci_adoption": True, "profile": G2_PROFILE, "gate": "G2", "limits": G2_CLOSEOUT_LIMITS}
    if kind == G2_CLOSEOUT_ENABLE_KIND:
        return {"paths": paths, "input_paths": G2_CLOSEOUT_ENABLE_INPUT_PATHS,
                "transition_paths": G2_TRANSITION_PATHS, "scope_path": G2_SCOPE,
                "transition": True, "closeout_enable": True, "profile": G2_PROFILE,
                "gate": "G2", "limits": G2_CLOSEOUT_ENABLE_LIMITS}
    if kind == G2_CLOSEOUT_KIND:
        return {"paths": paths, "input_paths": G2_CLOSEOUT_INPUT_PATHS,
                "transition_paths": G2_CLOSEOUT_PATHS, "scope_path": G2_CLOSEOUT_SCOPE,
                "transition": True, "closeout": True, "profile": raisa_policy.G2_CLOSED_PROFILE,
                "gate": "G2", "limits": G2_CLOSEOUT_LIMITS}
    if kind in G2_BATCH_KINDS:
        return {"paths": paths, "input_paths": batch_input_paths(binding),
                "transition_paths": G2_TRANSITION_PATHS, "scope_path": G2_SCOPE,
                "transition": kind in G2_MAINTENANCE_KINDS, "batch": True,
                "profile": G2_PROFILE, "gate": "G2",
                  "limits": G2_SIX_LIMITS if binding.get("schema_version") == G2_SIX_BINDING_VERSION else G2_TRANSPORT_LIMITS if binding.get("schema_version") == G2_TRANSPORT_BINDING_VERSION else G2_PYJWT_LIMITS if binding.get("schema_version") == G2_PYJWT_BINDING_VERSION
                  else G2_COMPLETENESS_LIMITS if binding.get("schema_version") == G2_COMPLETENESS_BINDING_VERSION
                  else G2_RELATIONSHIP_LIMITS if binding.get("schema_version") == G2_RELATIONSHIP_BINDING_VERSION
                  else G2_TENANT_LIMITS if binding.get("schema_version") == G2_TENANT_BINDING_VERSION
                  else G2_CIM_LIMITS if binding.get("schema_version") == G2_CIM_BINDING_VERSION
                 else G2_CI_LIMITS if binding.get("schema_version") == G2_CI_BINDING_VERSION
                 else G2_DEPENDENCY_LIMITS if binding.get("schema_version") == G2_DEPENDENCY_BINDING_VERSION
                 else G2_PRODUCTION_PROFILE_LIMITS if binding.get("schema_version") == G2_PRODUCTION_PROFILE_BINDING_VERSION
                else G2_APPOINTMENT_LIMITS if binding.get("schema_version") == G2_APPOINTMENT_BINDING_VERSION
                else G2_MIGRATION_GUARD_LIMITS if binding.get("schema_version") == G2_MIGRATION_GUARD_BINDING_VERSION
                else G2_CLINICAL_LIMITS if binding.get("schema_version") == G2_CLINICAL_BINDING_VERSION
                else G2_ATOMICITY_LIMITS if binding.get("schema_version") == G2_ATOMICITY_BINDING_VERSION
                else G2_PATIENT_LIMITS if binding.get("schema_version") == G2_PATIENT_BINDING_VERSION
                else G2_AUDIO_LIMITS if binding.get("schema_version") == G2_AUDIO_BINDING_VERSION
                else G2_BATCH_LIMITS}
    if kind in {"accept_g1e", "repair_g2_fixture"}:
        return {
            "paths": paths, "successor": True, "transition": kind == "accept_g1e",
            "input_paths": G2_INPUT_PATHS, "transition_paths": G2_TRANSITION_PATHS,
            "scope_path": G2_SCOPE, "baseline_pins": G1E_BASELINE_PINS,
            "baseline_directory": "g1e-baseline", "evidence_pins": G1E_EVIDENCE_PINS,
            "profile": G2_PROFILE, "gate": "G2", "accepted_publication": G1E_PUBLICATION,
            "accepted_pins": G1E_SOURCE_PINS, "component_reason": "bounded_g2", "limits": G2_LIMITS,
        }
    if kind in {"accept_g1d", "assess_g1e"}:
        return {
            "paths": paths, "successor": True, "transition": kind == "accept_g1d", "assessment": kind == "assess_g1e",
            "input_paths": G1E_INPUT_PATHS, "transition_paths": G1E_TRANSITION_PATHS,
            "scope_path": G1E_SCOPE, "baseline_pins": G1D_BASELINE_PINS,
            "baseline_directory": "g1d-baseline", "evidence_pins": G1D_EVIDENCE_PINS,
            "profile": G1E_PROFILE, "gate": "G1E", "accepted_publication": PROVENANCE_PUBLICATION,
            "accepted_pins": PROVENANCE_PINS, "component_reason": "bounded_g1e", "limits": G1E_LIMITS,
        }
    if kind in {"accept_g1c", "implement_g1d"}:
        return {
            "paths": paths, "successor": True, "transition": kind == "accept_g1c",
            "input_paths": G1D_INPUT_PATHS, "transition_paths": G1D_TRANSITION_PATHS,
            "scope_path": G1D_SCOPE, "baseline_pins": G1C_BASELINE_PINS,
            "baseline_directory": "g1c-baseline", "evidence_pins": G1C_EVIDENCE_PINS,
            "profile": G1D_PROFILE, "gate": "G1D", "accepted_publication": GOVERNOR_PUBLICATION,
            "accepted_pins": GOVERNOR_PINS, "component_reason": "bounded_g1d",
            "limits": (("G1C component acceptance awaits reviewed transition publication",)
                       if kind == "accept_g1c" else ("G1C component accepted",)) + G1D_LIMITS,
        }
    successor = kind in {"accept_g1b", "implement_g1c"}
    return {
        "paths": paths, "successor": successor, "transition": kind in {"accept_journal", "accept_g1b"},
        "input_paths": G1C_INPUT_PATHS if successor else INPUT_PATHS,
        "transition_paths": G1C_TRANSITION_PATHS if successor else TRANSITION_PATHS,
        "scope_path": G1C_SCOPE if successor else SCOPE_PATH,
        "baseline_pins": G1B_BASELINE_PINS if successor else BASELINE_PINS,
        "baseline_directory": "g1b-baseline" if successor else "baseline",
        "evidence_pins": G1B_EVIDENCE_PINS if successor else EVIDENCE_PINS,
        "profile": G1C_PROFILE if successor else PROFILE,
        "gate": "G1C" if successor else "G1B",
        "accepted_publication": PERSISTENCE_PUBLICATION, "accepted_pins": PERSISTENCE_PINS,
        "component_reason": "bounded_g1c",
        "limits": (("G1B component acceptance awaits reviewed transition publication",) + G1C_LIMITS
                   if kind == "accept_g1b" else ("G1B component accepted",) + G1C_LIMITS if successor else LIMITS),
    }


class BoundedG1BError(ValueError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise BoundedG1BError(reason)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _keys(value: object, expected: set[str] | frozenset[str], reason: str) -> dict:
    _need(type(value) is dict and set(value) == expected, reason)
    return value


def _pairs(rows):
    result = {}
    for key, value in rows:
        _need(type(key) is str and key not in result, "bounded_g1b_duplicate_or_invalid_key")
        result[key] = value
    return result


def _constant(value):
    raise BoundedG1BError("bounded_g1b_nonfinite_json")


def _canonical(value: object) -> bytes:
    seen = set()
    remaining = 50000

    def visit(item: object, depth: int) -> None:
        nonlocal remaining
        remaining -= 1
        _need(remaining >= 0 and depth <= 64, "bounded_g1b_structure_bound")
        if type(item) in (dict, list):
            _need(id(item) not in seen, "bounded_g1b_shared_or_cyclic_container")
            seen.add(id(item))
            if type(item) is dict:
                _need(all(type(key) is str for key in item), "bounded_g1b_invalid_key")
                children = item.values()
            else:
                children = item
            for child in children:
                visit(child, depth + 1)
        else:
            _need(type(item) in (str, int, float, bool, type(None)), "bounded_g1b_non_json_value")

    visit(value, 0)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _json(raw: bytes) -> dict:
    _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "bounded_g1b_payload_size")
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    _need(type(value) is dict, "bounded_g1b_object_required")
    _canonical(value)
    return value


class _Yaml(yaml.SafeLoader):
    pass


def _yaml_mapping(loader, node, deep=False):
    return _pairs((loader.construct_object(key, deep=deep), loader.construct_object(value, deep=deep))
                  for key, value in node.value)


_Yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)


def _document(raw: bytes, path: str) -> dict:
    if path.endswith(".json"):
        return _json(raw)
    _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "bounded_g1b_payload_size")
    value = yaml.load(raw, Loader=_Yaml)
    _need(type(value) is dict, "bounded_g1b_object_required")
    # Also reject YAML NaN, date objects and cyclic/non-JSON structures.
    _canonical(value)
    return value


def recognises_bounded_request(manifest: object) -> bool:
    if type(manifest) is not dict:
        return False
    version = manifest.get("schema_version")
    kind = manifest.get("operation_kind")
    task = manifest.get("task_class")
    return ((type(version) is str and version.startswith("ariadne.bounded_g1b_"))
            or (type(kind) is str and kind in OPERATION_PATHS)
            or (type(task) is str and task in {TASK_CLASS, G1C_TASK, G1D_TASK, G1E_TASK, G2_TASK, G2_BATCH_TASK}))


def build_completion_scope(recorded_at: str, transition_base: str) -> dict:
    return {
        "schema_version": SCOPE_VERSION,
        "recorded_at": recorded_at,
        "transition_base_commit": transition_base,
        "accepted_component": "G1B.2_pure_journal_and_replay",
        "implementation_review": {
            "reviewer": "/root/journal_independent_review",
            "subject_sha256": EVIDENCE_PINS["admission/review-subject.json"],
            "transcription_sha256": EVIDENCE_PINS["admission/independent-review-transcription.md"],
            "verdict": "PASS_BOUNDED_IMPLEMENTATION_ONLY",
            "original_operational_acceptance": False,
        },
        "publication": {"commit": JOURNAL_COMMIT, "parent": JOURNAL_PARENT, "tree": JOURNAL_TREE,
                        "commit_receipt_sha256": EVIDENCE_PINS["publication/commit-receipt.json"],
                        "push_receipt_sha256": EVIDENCE_PINS["publication/push-receipt.json"]},
        "kernel_sha256": dict(KERNEL_PINS),
        "criteria": list(CRITERIA),
        "evidence_sha256": dict(EVIDENCE_PINS),
        "current_operation": {"operation_id": "g1b-persistence-recovery-completion", "profile": PROFILE,
                              "task_class": TASK_CLASS, "status": "active", "completion_accepted": False},
        "completion_paths": sorted(COMPLETION_PATHS),
        "allowed_effects": sorted(EFFECTS),
        "forbidden_effects": sorted(FORBIDDEN),
        "claim_limits": list(LIMITS),
        "g1b_complete": False, "g1c_eligible": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False,
    }


def _validate_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None,
          "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None,
          "bounded_g1b_transition_base_invalid")
    _need(_canonical(scope) == _canonical(build_completion_scope(stamp, base)), "bounded_g1b_acceptance_scope_invalid")


def build_g1b_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Derive the sole allowed delta from already authenticated predecessor bytes."""
    _keys(before, set(BASELINE_PINS), "bounded_g1b_predecessor_paths")
    for path, digest in BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest,
              "bounded_g1b_predecessor_changed")
    _validate_scope(scope)
    state = _document(before[STATE], STATE)
    gates = _document(before[GATES], GATES)
    overlay = _document(before[OVERLAY], OVERLAY)
    _need(state["active_profile"] == OLD_PROFILE and state["current_gate"] == "G1B.2",
          "bounded_g1b_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True,
          "bounded_g1b_repair_only_required")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1B", active_correction="G1B", active_profile=PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1b"].update(status="active_completion", next_action=TASK_CLASS)
    state["g1b"]["subgates"]["G1B.2"].update(status="passed", implementation_started=True,
                                                implementation_authorized=False)
    state["g1b"]["completion"] = {"scope_path": SCOPE_PATH, "scope_sha256": _sha(scope_raw),
                                    "current_operation": copy.deepcopy(scope["current_operation"])}
    state["task_selection"].update(allowed_task_kinds=[TASK_CLASS], next_eligible_tranche="G1B",
                                   next_eligibility_condition="bounded_G1B_completion_profile_active")
    gates["programme"].update(current_gate="G1B", next_eligible_tranche="G1B",
                                prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]), "bounded_g1b_duplicate_gate")
    _need(by_id["G1B.2"]["exit_checks"] == list(CRITERIA), "bounded_g1b_criteria_changed")
    by_id["G1B"]["status"] = "active_completion"
    by_id["G1B"]["next_gate"] = "G1C"
    by_id["G1B.2"]["status"] = "passed"
    overlay["active_profile"] = PROFILE
    _need(PROFILE not in overlay["profiles"], "bounded_g1b_predecessor_already_active")
    overlay["profiles"][PROFILE] = {
        "profile_kind": "bounded_G1B_completion", "expected_programme_mode": "recovery",
        "expected_current_gate": "G1B", "expected_gate_status": "active", "active_correction": "G1B",
        "programme_gate": "G1B", "admitted_task_classes": [TASK_CLASS],
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "allowed_paths": sorted(COMPLETION_PATHS), "autonomous_task_selection": False,
        "feature_work_eligible": False, "product_work_eligible": False,
        "provider_calls_eligible": False, "deployment_eligible": False,
        "protected_ref_movement_eligible": False, "g1c_eligible": False,
        "scope_behavior": "bounded_g1b_completion", "scope_file": SCOPE_PATH,
        "closed_entrypoints": ["worker_dispatch", "provider_invocation", "clockwork_tick_mutation",
                               "clockwork_closeout_mutation", "integration", "protected_ref_operation", "deployment"],
    }
    text = before[AGENTS].decode("utf-8")
    _need(text.count(OLD_PREAMBLE) == 1 and text.startswith("# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n"),
          "bounded_g1b_predecessor_preamble")
    text = text.replace(OLD_PREAMBLE, NEW_PREAMBLE, 1)
    old_gate = "| Active programme gate | G1B.2 pure journal/replay; G1B.1 closeout accepted. G1B.2 closeout and G1C remain pending. |"
    new_gate = "| Active programme gate | G1B completion; the pure G1B.2 journal is accepted for composition. Persistence, recovery, stale-lease protection and derived narrative remain to be completed. G1C remains closed. |"
    _need(text.count(old_gate) == 1, "bounded_g1b_baton_gate_missing")
    text = text.replace(old_gate, new_gate, 1)
    old_next = "| Next dependency | Verify relevant current controls, accept the published G1B.2 journal through the required controller transition, then complete the remaining G1B guarantees. |"
    new_next = "| Next dependency | Implement and verify the bounded G1B completion task in orchestration/programme/g1b-completion-scope.json; its current operation supersedes the preserved historical latch. |"
    _need(text.count(old_next) == 1, "bounded_g1b_baton_next_missing")
    text = text.replace(old_next, new_next, 1)
    return {
        STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
        GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
        OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
        AGENTS: text.encode(), SCOPE_PATH: scope_raw,
    }


def validate_g1b_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, TRANSITION_PATHS, "bounded_g1b_transition_paths")
    _keys(evidence, set(EVIDENCE_PINS), "bounded_g1b_evidence_paths")
    for path, digest in EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest,
              "bounded_g1b_evidence_changed")
    expected = build_g1b_acceptance_transition(before, _json(after[SCOPE_PATH]))
    for path in TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1b_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1b_agents_delta_invalid")
    # The digest in state refers to the canonical scope bytes, not an equivalent
    # but differently encoded candidate file.
    _need(after[SCOPE_PATH] == expected[SCOPE_PATH], "bounded_g1b_scope_encoding_invalid")


def build_governor_scope(recorded_at: str, transition_base: str) -> dict:
    return {
        "schema_version": "ariadne.g1c_governor_scope.v1", "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "accepted_component": "G1B_persisted_versioned_journal",
        "accepted_publication": dict(PERSISTENCE_PUBLICATION), "accepted_source_sha256": dict(PERSISTENCE_PINS),
        "kernel_sha256": dict(KERNEL_PINS), "criteria": list(G1B_CRITERIA),
        "evidence_sha256": dict(G1B_EVIDENCE_PINS),
        "preserved_predecessor_scope": {"path": SCOPE_PATH, "sha256": G1B_BASELINE_PINS[SCOPE_PATH]},
        "current_operation": {
            "operation_id": "g1c-recovery-governor", "profile": G1C_PROFILE, "task_class": G1C_TASK,
            "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g1b-persistence-recovery-completion", "scope_path": SCOPE_PATH,
                           "scope_sha256": G1B_BASELINE_PINS[SCOPE_PATH], "historical_latch_preserved": True},
        },
        "implementation_paths": sorted(GOVERNOR_PATHS), "governor_criteria": list(G1C_CRITERIA),
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "budget_semantics": {
            "cost_policy_path": COST, "cost_policy_sha256": COST_PIN,
            "accounting_mode": "subscription_usage_window", "monetary_budget_enforcement": "inactive",
            "estimated_cost_reporting": "advisory_only", "estimated_cost_or_local_cap_triggers_fallback": False,
            "recovery_envelope_requires": ["finite_usage_and_token_reservations", "finite_operation_and_total_attempts",
                "finite_operation_and_envelope_deadlines", "fresh_account_pool_window_unit_bound_usage",
                "atomic_reservation_wip_and_journal_head", "retain_unresolved_reservations_until_verified_settlement"],
            "global_defaults_changed": False,
        },
        "versioned_persistence_change_permitted": True, "automatic_v1_migration_permitted": False,
        "g1b_component_accepted": True, "g1c_complete": False, "g1d_eligible": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False,
        "claim_limits": list(G1C_LIMITS),
    }


def _validate_governor_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None,
          "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None,
          "bounded_g1b_transition_base_invalid")
    _need(_canonical(scope) == _canonical(build_governor_scope(stamp, base)), "bounded_g1c_scope_invalid")


def build_g1c_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Accept the immutable G1B component and enable only the G1C implementation."""
    _keys(before, set(G1B_BASELINE_PINS), "bounded_g1c_predecessor_paths")
    for path, digest in G1B_BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest, "bounded_g1c_predecessor_changed")
    _validate_governor_scope(scope)
    state = _document(before[STATE], STATE)
    gates = _document(before[GATES], GATES)
    overlay = _document(before[OVERLAY], OVERLAY)
    _need(state["active_profile"] == PROFILE and state["current_gate"] == "G1B"
          and state["g1b"]["status"] == "active_completion" and "g1c" not in state,
          "bounded_g1c_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True, "bounded_g1b_repair_only_required")
    _need(state["g1b"]["completion"]["scope_sha256"] == _sha(before[SCOPE_PATH])
          and state["g1b"]["completion"]["current_operation"] == _json(before[SCOPE_PATH])["current_operation"],
          "bounded_g1c_predecessor_operation_changed")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1C", active_correction="G1C", active_profile=G1C_PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1b"].update(status="passed", next_action="G1C_governor_implementation")
    # Preserve the previous completion object verbatim as historical authority.
    state["g1b"]["acceptance"] = {"scope_path": G1C_SCOPE, "scope_sha256": _sha(scope_raw),
        "accepted_component_commit": PERSISTENCE_PUBLICATION["commit"], "criteria": list(G1B_CRITERIA)}
    state["g1c"] = {"status": "active", "scope_path": G1C_SCOPE, "scope_sha256": _sha(scope_raw),
                     "current_operation": copy.deepcopy(scope["current_operation"]), "completion_accepted": False}
    state["task_selection"].update(allowed_task_kinds=[G1C_TASK], next_eligible_tranche="G1C",
                                   next_eligibility_condition="bounded_G1C_governor_profile_active")
    gates["programme"].update(current_gate="G1C", next_eligible_tranche="G1C", prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G1B"]["exit_checks"] == list(G1B_CRITERIA)
          and by_id["G1C"]["exit_checks"] == list(G1C_CRITERIA) and by_id["G1C"]["status"] == "blocked_by_G1B"
          and by_id["G1D"]["status"] == "blocked_by_G1C", "bounded_g1c_gate_predecessor_invalid")
    by_id["G1B"]["status"] = "passed"
    by_id["G1C"]["status"] = "active"
    _need(overlay["active_profile"] == PROFILE and G1C_PROFILE not in overlay["profiles"], "bounded_g1c_profile_already_active")
    overlay["active_profile"] = G1C_PROFILE
    overlay["profiles"][G1C_PROFILE] = {
        "profile_kind": "bounded_G1C_governor", "expected_programme_mode": "recovery",
        "expected_current_gate": "G1C", "expected_gate_status": "active", "active_correction": "G1C",
        "programme_gate": "G1C", "admitted_task_classes": [G1C_TASK],
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "allowed_paths": sorted(GOVERNOR_PATHS), "autonomous_task_selection": False,
        "feature_work_eligible": False, "product_work_eligible": False, "provider_calls_eligible": False,
        "deployment_eligible": False, "protected_ref_movement_eligible": False, "g1d_eligible": False,
        "scope_behavior": "bounded_g1c_governor", "scope_file": G1C_SCOPE,
        "recovery_envelope_limits_required": True, "global_execution_defaults_unchanged": True,
        "closed_entrypoints": ["worker_dispatch", "provider_invocation", "clockwork_tick_mutation",
                               "clockwork_closeout_mutation", "integration", "protected_ref_operation", "deployment"],
    }
    text = before[AGENTS].decode("utf-8")
    replacements = {
        NEW_PREAMBLE: G1C_PREAMBLE,
        "| Active programme gate | G1B completion; the pure G1B.2 journal is accepted for composition. Persistence, recovery, stale-lease protection and derived narrative remain to be completed. G1C remains closed. |":
        "| Active programme gate | G1C governor; the bounded G1B persistence component is accepted. G1C implementation is eligible; operational multi-task control and G1D remain unaccepted. |",
        "| Next dependency | Implement and verify the bounded G1B completion task in orchestration/programme/g1b-completion-scope.json; its current operation supersedes the preserved historical latch. |":
        "| Next dependency | Integrate and verify the bounded G1C governor task in orchestration/programme/g1c-governor-scope.json; its current operation explicitly supersedes the preserved G1B operation. |",
    }
    for old, new in replacements.items():
        _need(text.count(old) == 1, "bounded_g1c_agents_predecessor_changed")
        text = text.replace(old, new, 1)
    return {STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
            GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            AGENTS: text.encode(), G1C_SCOPE: scope_raw}


def validate_g1c_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, G1C_TRANSITION_PATHS, "bounded_g1c_transition_paths")
    _keys(evidence, set(G1B_EVIDENCE_PINS), "bounded_g1c_evidence_paths")
    for path, digest in G1B_EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest, "bounded_g1c_evidence_changed")
    review = _json(evidence["g1b-evidence/implementation-review.json"])
    tests = _json(evidence["g1b-evidence/windows-test-2.stdout.json"])
    readback = _json(evidence["g1b-evidence/fresh-readback.json"])
    _need(review["verdict"] == "G1B_PERSISTENCE_IMPLEMENTATION_PASS"
          and review["source_sha256"] == PERSISTENCE_PINS["orchestration_harness/clockwork_persistence.py"]
          and review["test_sha256"] == PERSISTENCE_PINS["tests/test_clockwork_persistence.py"]
          and review["windows_result_sha256"] == G1B_EVIDENCE_PINS["g1b-evidence/windows-test-2.stdout.json"]
          and tests["status"] == "pass" and tests["tests_run"] == 15 and tests["guard_violations"] == []
          and tests["native_process_death_boundaries"] == ["after_commit", "before_commit"]
          and all(readback[key] == value for key, value in PERSISTENCE_PUBLICATION.items()),
          "bounded_g1c_component_evidence_invalid")
    expected = build_g1c_acceptance_transition(before, _json(after[G1C_SCOPE]))
    for path in G1C_TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1c_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1c_agents_delta_invalid")
    _need(after[G1C_SCOPE] == expected[G1C_SCOPE], "bounded_g1c_scope_encoding_invalid")


def build_provenance_scope(recorded_at: str, transition_base: str) -> dict:
    return {
        "schema_version": "ariadne.g1d_provenance_scope.v1", "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "accepted_component": "G1C_bounded_recovery_governor",
        "accepted_publication": dict(GOVERNOR_PUBLICATION), "accepted_source_sha256": dict(GOVERNOR_PINS),
        "criteria": list(G1C_CRITERIA), "evidence_sha256": dict(G1C_EVIDENCE_PINS),
        "preserved_predecessor_scope": {"path": G1C_SCOPE, "sha256": G1C_BASELINE_PINS[G1C_SCOPE]},
        "current_operation": {
            "operation_id": "g1d-provenance-and-independent-verification", "profile": G1D_PROFILE,
            "task_class": G1D_TASK, "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g1c-recovery-governor", "scope_path": G1C_SCOPE,
                           "scope_sha256": G1C_BASELINE_PINS[G1C_SCOPE], "historical_latch_preserved": True},
        },
        "implementation_paths": sorted(PROVENANCE_PATHS), "provenance_criteria": list(G1D_CRITERIA),
        "dependency_sha256": dict(PROVENANCE_DEPENDENCY_PINS),
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "verification_boundary": {
            "execution_profile": "reviewed_local_authored_programs", "live_model_context_accepted": False,
            "trusted_controller_owns": ["assignment_and_risk_classification", "reviewed_source_allowlist",
                "context_assembly", "assignment_to_capture_directory_binding", "durable_independent_anchor_retention"],
            "routine_requires_independent_deterministic_recomputation": True,
            "control_and_publication_risk_floor": "dual_review",
            "red_context": "fresh_candidate_only_without_blue_or_previous_review_artifacts",
            "worker_declarations_establish_independence": False,
            "replay_grants_execution_integration_or_usage_settlement_authority": False,
            "global_policy_and_existing_execution_defaults_changed": False,
        },
        "g1b_component_accepted": True, "g1c_component_accepted": True, "g1d_complete": False,
        "g1e_eligible": False, "operational_multi_task_control_accepted": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False,
        "claim_limits": list(G1D_LIMITS),
    }


def _validate_provenance_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None, "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None, "bounded_g1b_transition_base_invalid")
    _need(_canonical(scope) == _canonical(build_provenance_scope(stamp, base)), "bounded_g1d_scope_invalid")


def build_g1d_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Accept the published G1C component and enable only bounded G1D implementation."""
    _keys(before, set(G1C_BASELINE_PINS), "bounded_g1d_predecessor_paths")
    for path, digest in G1C_BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest, "bounded_g1d_predecessor_changed")
    _validate_provenance_scope(scope)
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    _need(state["active_profile"] == G1C_PROFILE and state["current_gate"] == "G1C"
          and state["g1b"]["status"] == "passed" and state["g1c"]["status"] == "active"
          and state["g1c"]["completion_accepted"] is False and "g1d" not in state,
          "bounded_g1d_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True, "bounded_g1b_repair_only_required")
    _need(state["g1c"]["scope_sha256"] == _sha(before[G1C_SCOPE])
          and state["g1c"]["current_operation"] == _json(before[G1C_SCOPE])["current_operation"],
          "bounded_g1d_predecessor_operation_changed")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1D", active_correction="G1D", active_profile=G1D_PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1c"].update(status="passed", completion_accepted=True)
    # Earlier scope/current_operation objects remain verbatim historical records.
    state["g1c"]["acceptance"] = {"scope_path": G1D_SCOPE, "scope_sha256": _sha(scope_raw),
        "accepted_component_commit": GOVERNOR_PUBLICATION["commit"], "criteria": list(G1C_CRITERIA)}
    state["g1d"] = {"status": "active", "scope_path": G1D_SCOPE, "scope_sha256": _sha(scope_raw),
        "current_operation": copy.deepcopy(scope["current_operation"]), "completion_accepted": False}
    state["task_selection"].update(allowed_task_kinds=[G1D_TASK], next_eligible_tranche="G1D",
                                   next_eligibility_condition="bounded_G1D_provenance_profile_active")
    gates["programme"].update(current_gate="G1D", next_eligible_tranche="G1D", prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G1C"]["exit_checks"] == list(G1C_CRITERIA)
          and by_id["G1D"]["exit_checks"] == list(G1D_CRITERIA) and by_id["G1C"]["status"] == "active"
          and by_id["G1D"]["status"] == "blocked_by_G1C" and by_id["G1E"]["status"] == "blocked_by_G1D",
          "bounded_g1d_gate_predecessor_invalid")
    by_id["G1C"]["status"], by_id["G1D"]["status"] = "passed", "active"
    _need(overlay["active_profile"] == G1C_PROFILE and G1D_PROFILE not in overlay["profiles"],
          "bounded_g1d_profile_already_active")
    overlay["active_profile"] = G1D_PROFILE
    overlay["profiles"][G1D_PROFILE] = {
        "profile_kind": "bounded_G1D_provenance", "expected_programme_mode": "recovery",
        "expected_current_gate": "G1D", "expected_gate_status": "active", "active_correction": "G1D",
        "programme_gate": "G1D", "admitted_task_classes": [G1D_TASK],
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "allowed_paths": sorted(PROVENANCE_PATHS), "autonomous_task_selection": False,
        "feature_work_eligible": False, "product_work_eligible": False, "provider_calls_eligible": False,
        "deployment_eligible": False, "protected_ref_movement_eligible": False, "g1e_eligible": False,
        "scope_behavior": "bounded_g1d_provenance", "scope_file": G1D_SCOPE,
        "reviewed_local_authored_verification_only": True, "global_execution_defaults_unchanged": True,
        "closed_entrypoints": ["worker_dispatch", "provider_invocation", "clockwork_tick_mutation",
                               "clockwork_closeout_mutation", "integration", "protected_ref_operation", "deployment"],
    }
    text = before[AGENTS].decode("utf-8")
    replacements = {
        G1C_PREAMBLE: G1D_PREAMBLE,
        "| Active programme gate | G1C governor; the bounded G1B persistence component is accepted. G1C implementation is eligible; operational multi-task control and G1D remain unaccepted. |":
        "| Active programme gate | G1D provenance; the bounded G1C governor component is accepted. G1D implementation is eligible; operational multi-task control and G1E remain unaccepted. |",
        "| Next dependency | Integrate and verify the bounded G1C governor task in orchestration/programme/g1c-governor-scope.json; its current operation explicitly supersedes the preserved G1B operation. |":
        "| Next dependency | Integrate and verify the bounded G1D provenance task in orchestration/programme/g1d-provenance-scope.json; its current operation explicitly supersedes the preserved G1C operation. |",
    }
    for old, new in replacements.items():
        _need(text.count(old) == 1, "bounded_g1d_agents_predecessor_changed")
        text = text.replace(old, new, 1)
    return {STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
            GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            AGENTS: text.encode(), G1D_SCOPE: scope_raw}


def validate_g1d_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, G1D_TRANSITION_PATHS, "bounded_g1d_transition_paths")
    _keys(evidence, set(G1C_EVIDENCE_PINS), "bounded_g1d_evidence_paths")
    for path, digest in G1C_EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest, "bounded_g1d_evidence_changed")
    review = _json(evidence["g1c-evidence/implementation-review-windows.json"])
    operation = _json(evidence["g1c-evidence/operation-review.json"])
    tests = _json(evidence["g1c-evidence/windows-governor-1.stdout.json"])
    persistence = _json(evidence["g1c-evidence/windows-persistence-1.stdout.json"])
    readback = _json(evidence["g1c-evidence/fresh-readback.json"])
    _need(review["verdict"] == "G1C_GOVERNOR_CODE_LOCAL_AND_WINDOWS_EVIDENCE_PASS"
          and review["source_sha256"] == GOVERNOR_PINS
          and operation["six_g1c_criteria_supported_for_bounded_component_acceptance"] is True
          and set(operation["criteria_evidence"]) == set(G1C_CRITERIA)
          and operation["implementation_review_sha256"] == G1C_EVIDENCE_PINS["g1c-evidence/implementation-review-windows.json"]
          and tests["status"] == "PASS" and tests["tests"] == 32 and tests["observation_guard_violations"] == []
          and tests["failures"] == tests["errors"] == tests["provider_calls"] == tests["external_worker_dispatches"] == 0
          and persistence["status"] == "pass" and persistence["tests_run"] == 15 and persistence["guard_violations"] == []
          and persistence["native_process_death_boundaries"] == ["after_commit", "before_commit"]
          and all(readback[key] == value for key, value in GOVERNOR_PUBLICATION.items())
          and readback["remote"][RECOVERY_REF] == GOVERNOR_PUBLICATION["commit"],
          "bounded_g1d_component_evidence_invalid")
    expected = build_g1d_acceptance_transition(before, _json(after[G1D_SCOPE]))
    for path in G1D_TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1d_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1d_agents_delta_invalid")
    _need(after[G1D_SCOPE] == expected[G1D_SCOPE], "bounded_g1d_scope_encoding_invalid")


def _validate_installed_controller(value: object) -> dict:
    result = _keys(value, {"commit", "parent", "tree", "source_sha256"}, "bounded_g1e_controller_schema")
    _need(all(type(result[k]) is str and re.fullmatch(r"[0-9a-f]{40}", result[k])
              for k in ("commit", "parent", "tree")), "bounded_g1e_controller_identity")
    _digest_map(result["source_sha256"], CONTROLLER_PATHS, "bounded_g1e_controller_source_paths")
    return result


def build_configuration_scope(recorded_at: str, transition_base: str, installed_controller: dict) -> dict:
    controller = _validate_installed_controller(installed_controller)
    _need(controller["commit"] == transition_base, "bounded_g1e_controller_must_precede_activation")
    return {
        "schema_version": "ariadne.g1e_configuration_core_scope.v1", "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "accepted_component": "G1D_reviewed_local_provenance",
        "accepted_publication": dict(PROVENANCE_PUBLICATION), "accepted_source_sha256": dict(PROVENANCE_PINS),
        "criteria": list(G1D_CRITERIA), "evidence_sha256": dict(G1D_EVIDENCE_PINS),
        "preserved_predecessor_scope": {"path": G1D_SCOPE, "sha256": G1D_BASELINE_PINS[G1D_SCOPE]},
        "current_operation": {
            "operation_id": "g1e-configuration-and-core-assessment", "profile": G1E_PROFILE,
            "task_class": G1E_TASK, "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g1d-provenance-and-independent-verification",
                "scope_path": G1D_SCOPE, "scope_sha256": G1D_BASELINE_PINS[G1D_SCOPE],
                "historical_latch_preserved": True},
        },
        "installed_controller_publication": copy.deepcopy(controller),
        "installed_component_paths": sorted(CONTROLLER_PATHS),
        "configuration_paths": sorted(CONFIGURATION_PATHS), "configuration_criteria": list(G1E_CRITERIA),
        "assessment_operation": "assess_g1e", "assessment_entrypoint": "recovery_preflight",
        "assessment_phase": "assessment", "assessment_allowed_paths": [], "allowed_effects": ["repository_read"],
        "activation_publication_paths": sorted(G1E_TRANSITION_PATHS), "activation_effects": sorted(EFFECTS),
        "forbidden_effects": raisa_policy.configuration_profile()["forbidden_effects"],
        "configuration_boundary": {
            "declared_policy_files": 10, "caller_authenticates_pins_and_source": True,
            "document_hashes_authorize_themselves": False, "reference_traversal": False,
            "historical_defaults_activate_effects": False, "assessment_grants_publication_or_execution": False,
            "existing_component_is_republished_by_assessment": False,
        },
        "g1b_component_accepted": True, "g1c_component_accepted": True, "g1d_component_accepted": True,
        "g1e_complete": False, "g2_eligible": False, "operational_multi_task_control_accepted": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False, "claim_limits": list(G1E_LIMITS),
    }


def _validate_configuration_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None, "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None, "bounded_g1b_transition_base_invalid")
    expected = build_configuration_scope(stamp, base, scope.get("installed_controller_publication"))
    _need(_canonical(scope) == _canonical(expected), "bounded_g1e_scope_invalid")


def build_g1e_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Accept the published G1D component and enable only installed-core assessment."""
    _keys(before, set(G1D_BASELINE_PINS), "bounded_g1e_predecessor_paths")
    for path, digest in G1D_BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest, "bounded_g1e_predecessor_changed")
    _validate_configuration_scope(scope)
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    _need(state["active_profile"] == G1D_PROFILE and state["current_gate"] == "G1D"
          and state["g1c"]["status"] == "passed" and state["g1d"]["status"] == "active"
          and state["g1d"]["completion_accepted"] is False and "g1e" not in state,
          "bounded_g1e_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True, "bounded_g1b_repair_only_required")
    _need(state["g1d"]["scope_sha256"] == _sha(before[G1D_SCOPE])
          and state["g1d"]["current_operation"] == _json(before[G1D_SCOPE])["current_operation"],
          "bounded_g1e_predecessor_operation_changed")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1E", active_correction="G1E", active_profile=G1E_PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1d"].update(status="passed", completion_accepted=True)
    state["g1d"]["acceptance"] = {"scope_path": G1E_SCOPE, "scope_sha256": _sha(scope_raw),
        "accepted_component_commit": PROVENANCE_PUBLICATION["commit"], "criteria": list(G1D_CRITERIA)}
    state["g1e"] = {"status": "active", "scope_path": G1E_SCOPE, "scope_sha256": _sha(scope_raw),
        "current_operation": copy.deepcopy(scope["current_operation"]), "completion_accepted": False}
    state["task_selection"].update(allowed_task_kinds=[G1E_TASK], next_eligible_tranche="G1E",
        next_eligibility_condition="bounded_G1E_installed_configuration_assessment_active")
    gates["programme"].update(current_gate="G1E", next_eligible_tranche="G1E", prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G1D"]["exit_checks"] == list(G1D_CRITERIA)
          and by_id["G1E"]["exit_checks"] == list(G1E_CRITERIA) and by_id["G1D"]["status"] == "active"
          and by_id["G1E"]["status"] == "blocked_by_G1D" and by_id["G2"]["status"] == "blocked_by_G1",
          "bounded_g1e_gate_predecessor_invalid")
    by_id["G1D"]["status"], by_id["G1E"]["status"] = "passed", "active"
    _need(overlay["active_profile"] == G1D_PROFILE and G1E_PROFILE not in overlay["profiles"],
          "bounded_g1e_profile_already_active")
    overlay["active_profile"] = G1E_PROFILE
    overlay["profiles"][G1E_PROFILE] = raisa_policy.configuration_profile()
    text = before[AGENTS].decode("utf-8")
    replacements = {
        G1D_PREAMBLE: G1E_PREAMBLE,
        "| Active programme gate | G1D provenance; the bounded G1C governor component is accepted. G1D implementation is eligible; operational multi-task control and G1E remain unaccepted. |":
        "| Active programme gate | G1E configuration/core assessment; the bounded G1D provenance component is accepted. The installed controller is eligible for read-only assessment; operational multi-task control and G2 remain unaccepted. |",
        "| Next dependency | Integrate and verify the bounded G1D provenance task in orchestration/programme/g1d-provenance-scope.json; its current operation explicitly supersedes the preserved G1C operation. |":
        "| Next dependency | Verify the installed configuration/core component using orchestration/programme/g1e-configuration-core-scope.json; its read-only assessment explicitly supersedes the preserved G1D operation. |",
    }
    for old, new in replacements.items():
        _need(text.count(old) == 1, "bounded_g1e_agents_predecessor_changed")
        text = text.replace(old, new, 1)
    return {STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
            GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            AGENTS: text.encode(), G1E_SCOPE: scope_raw}


def validate_g1e_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, G1E_TRANSITION_PATHS, "bounded_g1e_transition_paths")
    _keys(evidence, set(G1D_EVIDENCE_PINS), "bounded_g1e_evidence_paths")
    for path, digest in G1D_EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest, "bounded_g1e_evidence_changed")
    review = _json(evidence["g1d-evidence/implementation-review.json"])
    operation = _json(evidence["g1d-evidence/operation-review.json"])
    tests = _json(evidence["g1d-evidence/windows-test-2.stdout.json"])
    validation = _json(evidence["g1d-evidence/windows-validation-v2.json"])
    readback = _json(evidence["g1d-evidence/fresh-readback.json"])
    source = _json(evidence["g1d-evidence/source-manifest-v3.json"])
    _need(review["verdict"] == "G1D_PROVENANCE_CODE_LOCAL_AND_WINDOWS_EVIDENCE_PASS"
          and review["source_sha256"] == PROVENANCE_PINS and set(review["criteria_evidence"]) == set(G1D_CRITERIA)
          and operation["verdict"] == "RECOVERY_PUBLICATION_OPERATION_PASS"
          and operation["implementation_review_sha256"] == G1D_EVIDENCE_PINS["g1d-evidence/implementation-review.json"]
          and operation["owned_paths"] == 3 and operation["candidate_tree"] == PROVENANCE_PUBLICATION["tree"]
          and tests["status"] == "pass" and tests["tests_run"] == 19 and tests["guard_violations"] == []
          and tests["failures"] == tests["errors"] == tests["skips"] == tests["provider_calls"] == 0
          and tests["local_execution_profile_only"] is True and tests["live_repository_tested"] is False
          and len(tests["native_processes"]) == 13 and len(tests["saved_evidence_sha256"]) == 14
          and validation["status"] == "external_windows_capsule_pass" and validation["tests_run"] == 19
          and validation["failures"] == validation["errors"] == 0 and validation["guard_violations"] == []
          and validation["repository_mutated"] is False and validation["g1d_accepted"] is False
          and validation["runner_sha256"] == review["runner_sha256"]
          and tests["source_manifest_sha256"] == validation["source_manifest_sha256"] == review["source_manifest_sha256"]
          == G1D_EVIDENCE_PINS["g1d-evidence/source-manifest-v3.json"]
          and all(source[path] == digest for path, digest in PROVENANCE_PINS.items())
          and all(readback[key] == value for key, value in PROVENANCE_PUBLICATION.items())
          and readback["remote"][RECOVERY_REF] == PROVENANCE_PUBLICATION["commit"],
          "bounded_g1e_component_evidence_invalid")
    expected = build_g1e_acceptance_transition(before, _json(after[G1E_SCOPE]))
    for path in G1E_TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1e_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1e_agents_delta_invalid")
    _need(after[G1E_SCOPE] == expected[G1E_SCOPE], "bounded_g1e_scope_encoding_invalid")


def build_g2_repair_scope(recorded_at: str, transition_base: str, installed_controller: dict) -> dict:
    controller = _validate_installed_controller(installed_controller)
    _need(controller["commit"] == transition_base, "bounded_g2_controller_must_precede_activation")
    _need(controller["source_sha256"]["orchestration_harness/configuration_core.py"]
          == G1E_SOURCE_PINS["orchestration_harness/configuration_core.py"], "bounded_g2_preserved_core_changed")
    return {
        "schema_version": "ariadne.g2_baseline_repair_scope.v1", "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "accepted_component": "G1E_configuration_and_core",
        "accepted_publication": dict(G1E_PUBLICATION), "accepted_source_sha256": dict(G1E_SOURCE_PINS),
        "accepted_activation": dict(G1E_ACTIVATION), "criteria": list(G1E_CRITERIA),
        "evidence_sha256": dict(G1E_EVIDENCE_PINS),
        "preserved_predecessor_scope": {"path": G1E_SCOPE, "sha256": G1E_BASELINE_PINS[G1E_SCOPE]},
        "current_operation": {
            "operation_id": "g2-confirmation-family-fixture-repair", "profile": G2_PROFILE,
            "task_class": G2_TASK, "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g1e-configuration-and-core-assessment",
                "scope_path": G1E_SCOPE, "scope_sha256": G1E_BASELINE_PINS[G1E_SCOPE],
                "historical_latch_preserved": True},
        },
        "installed_controller_publication": copy.deepcopy(controller),
        "installed_component_paths": sorted(CONTROLLER_PATHS),
        "repair": {"path": G2_FIXTURE, "before_sha256": G2_FIXTURE_BEFORE,
                   "original_reviewed_after_sha256": G2_ORIGINAL_FIXTURE_AFTER,
                   "after_sha256": G2_FIXTURE_AFTER, "runtime_acceptance": False},
        "repair_sha256": copy.deepcopy(G2_REPAIR_PINS),
        "cold_import_prerequisite": "Delay the excluded typed-plan import until its existing default-off product-context functions are invoked; no clinical or provider semantics changed",
        "allowed_paths": sorted(G2_REPAIR_PINS), "allowed_effects": sorted(EFFECTS),
        "forbidden_effects": raisa_policy.g2_repair_profile()["forbidden_effects"],
        "owner_test_runtime_exception": raisa_policy.g2_test_exception(),
        "g2_exit_requirements": list(G2_CRITERIA), "g1e_complete": True, "g2_complete": False,
        "global_gate": "red_repair_only", "feature_work_eligible": False,
        "execution_authorized": False, "operational_multi_task_control_accepted": False,
        "existing_clockwork_writers_activated": False, "claim_limits": list(G2_LIMITS),
    }


def _validate_g2_repair_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None, "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None, "bounded_g1b_transition_base_invalid")
    expected = build_g2_repair_scope(stamp, base, scope.get("installed_controller_publication"))
    _need(_canonical(scope) == _canonical(expected), "bounded_g2_scope_invalid")


def build_g2_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Record accepted G1E evidence and open the exact first G2 repair only."""
    _keys(before, set(G1E_BASELINE_PINS), "bounded_g2_predecessor_paths")
    for path, digest in G1E_BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest, "bounded_g2_predecessor_changed")
    _validate_g2_repair_scope(scope)
    state, gates, overlay = (_document(before[p], p) for p in (STATE, GATES, OVERLAY))
    _need(state["active_profile"] == G1E_PROFILE and state["current_gate"] == "G1E"
          and all(state[key]["status"] == "passed" for key in ("g1b", "g1c", "g1d"))
          and state["g1e"]["status"] == "active" and state["g1e"]["completion_accepted"] is False
          and "g2" not in state, "bounded_g2_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True, "bounded_g1b_repair_only_required")
    _need(state["g1e"]["scope_sha256"] == _sha(before[G1E_SCOPE])
          and state["g1e"]["current_operation"] == _json(before[G1E_SCOPE])["current_operation"],
          "bounded_g2_predecessor_operation_changed")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G2", active_correction="G2", active_profile=G2_PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1e"].update(status="passed", completion_accepted=True)
    state["g1e"]["acceptance"] = {"scope_path": G2_SCOPE, "scope_sha256": _sha(scope_raw),
        "accepted_component_commit": G1E_PUBLICATION["commit"], "criteria": list(G1E_CRITERIA),
        "assessment_sha256": G1E_EVIDENCE_PINS["g1e-evidence/assessment.stdout.json"]}
    state["g2"] = {"status": "active", "scope_path": G2_SCOPE, "scope_sha256": _sha(scope_raw),
        "current_operation": copy.deepcopy(scope["current_operation"]), "completion_accepted": False}
    state["task_selection"].update(allowed_task_kinds=[G2_TASK], next_eligible_tranche="G2",
        next_eligibility_condition="bounded_G2_baseline_repair_active")
    gates["programme"].update(current_gate="G2", next_eligible_tranche="G2", prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G1E"]["exit_checks"] == list(G1E_CRITERIA)
          and by_id["G2"]["exit_checks"] == list(G2_CRITERIA) and by_id["G1E"]["status"] == "active"
          and by_id["G2"]["status"] == "blocked_by_G1", "bounded_g2_gate_predecessor_invalid")
    by_id["G1E"]["status"], by_id["G2"]["status"] = "passed", "active"
    _need(overlay["active_profile"] == G1E_PROFILE and G2_PROFILE not in overlay["profiles"],
          "bounded_g2_profile_already_active")
    overlay["active_profile"] = G2_PROFILE
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_repair_profile()
    text = before[AGENTS].decode("utf-8")
    old_runtime = "- Real patient/clinical data, live external model/identity/clinical providers and product runtime effects are closed during this recovery work. Do not start application, database or browser runtimes merely to satisfy a historical test fixture."
    exception = raisa_policy.g2_test_exception()
    replacements = {
        G1E_PREAMBLE: G2_PREAMBLE,
        "| Active programme gate | G1E configuration/core assessment; the bounded G1D provenance component is accepted. The installed controller is eligible for read-only assessment; operational multi-task control and G2 remain unaccepted. |":
        "| Active programme gate | G2 baseline repair; the G1E configuration/core criteria are accepted. Only the exact active repair and separately reviewed isolated synthetic tests are eligible; global CI, G2 completion and feature development remain unaccepted. |",
        "| Next dependency | Verify the installed configuration/core component using orchestration/programme/g1e-configuration-core-scope.json; its read-only assessment explicitly supersedes the preserved G1D operation. |":
        "| Next dependency | Integrate and verify the exact confirmation-family fixture repair in orchestration/programme/g2-baseline-repair-scope.json, then continue current stop-ship repairs under standing authority. |",
        old_runtime: old_runtime + "\n- Yuri expressly authorised the isolated G2 application/PostgreSQL test-only exception: contract SHA-256 `" + exception["contract_sha256"] + "`, owner approval SHA-256 `" + exception["owner_approval_sha256"] + "`. This covers independently scoped and reviewed batches with synthetic data, a new disposable database, no public application listener, and test-process network access only to that database on loopback. Each launch requires the reviewed executable/import/endpoint/cleanup binding and the contract's finite budgets. Real data, existing environments, providers, protected evidence and all other closures remain excluded. The general closed-surfaces policy is preserved; admission alone grants no runtime execution authority.",
    }
    for old, new in replacements.items():
        _need(text.count(old) == 1, "bounded_g2_agents_predecessor_changed")
        text = text.replace(old, new, 1)
    return {STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
            GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            AGENTS: text.encode(), G2_SCOPE: scope_raw}


def validate_g2_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                      evidence: dict[str, bytes]) -> None:
    _keys(after, G2_TRANSITION_PATHS, "bounded_g2_transition_paths")
    _keys(evidence, set(G1E_EVIDENCE_PINS), "bounded_g2_evidence_paths")
    for path, digest in G1E_EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest, "bounded_g2_evidence_changed")
    review = _json(evidence["g1e-evidence/criteria-review.json"])
    assessment = _json(evidence["g1e-evidence/assessment.stdout.json"])
    binding = _json(evidence["g1e-evidence/assessment-binding.json"])
    readback = _json(evidence["g1e-evidence/fresh-readback.json"])
    approval = _json(evidence["g1e-evidence/owner-runtime-approval.json"])
    contract = _json(evidence["g1e-evidence/isolated-test-contract.json"])
    refinement = _json(evidence["g1e-evidence/fixture-refinement-independent-review.json"])
    cold_import = _json(evidence["g1e-evidence/cold-import-independent-review.json"])
    _need(review["verdict"] == "G1E_CONFIGURATION_CORE_CRITERIA_PASS"
          and set(review["criteria"]) == set(G1E_CRITERIA)
          and all(value.startswith("PASS:") for value in review["criteria"].values())
          and review["installed_controller_commit"] == G1E_PUBLICATION["commit"]
          and review["activation_commit"] == G1E_ACTIVATION["commit"]
          and review["assessment_sha256"] == G1E_EVIDENCE_PINS["g1e-evidence/assessment.stdout.json"]
          and review["assessment_binding_sha256"] == assessment["binding_sha256"]
          == G1E_EVIDENCE_PINS["g1e-evidence/assessment-binding.json"]
          and assessment["status"] == "assessment_pass" and assessment["assessment_passed"] is True
          and assessment["execution_authorized"] is False and assessment["policy_eligible"] is False
          and assessment["reason_codes"] == assessment["failed_checks"] == []
          and assessment["configuration_document_count"] == review["configuration_documents"] == 10
          and assessment["configuration_sha256"] == review["configuration_sha256"]
          == "5018a1040498890d595f1f1f3429c331020152fa11e874e76a5aa09fa0125453"
          and binding["operation_kind"] == "assess_g1e" and binding["phase"] == "assessment"
          and binding["base_commit"] == binding["expected_head"] == binding["activation_commit"] == G1E_ACTIVATION["commit"]
          and binding["base_tree"] == binding["expected_index_tree"] == binding["candidate_tree"] == G1E_ACTIVATION["tree"]
          and binding["installed_controller"] == {**G1E_PUBLICATION, "source_sha256": G1E_SOURCE_PINS}
          and all(readback[key] == value for key, value in G1E_ACTIVATION.items())
          and readback["remote"][RECOVERY_REF] == G1E_ACTIVATION["commit"],
          "bounded_g2_g1e_evidence_invalid")
    _need(approval["approved"] is True and approval["owner_response_verbatim"] == "Yes"
          and approval["contract_sha256"] == G1E_EVIDENCE_PINS["g1e-evidence/isolated-test-contract.json"]
          and contract["first_candidate"]["path"] == G2_FIXTURE
          and contract["first_candidate"]["before_sha256"] == G2_FIXTURE_BEFORE
          and contract["first_candidate"]["after_sha256"] == G2_ORIGINAL_FIXTURE_AFTER
          and refinement["verdict"] == "BERNIE_ARGUMENT_REFINEMENT_STATIC_PASS"
          and refinement["original_candidate_sha256"] == G2_ORIGINAL_FIXTURE_AFTER
          and refinement["candidate_sha256"] == G2_FIXTURE_AFTER
          and refinement["source_review_sha256"] == G1E_EVIDENCE_PINS["g1e-evidence/fixture-refinement-source.json"]
          and refinement["assertions_preserved"] == 16 and refinement["test_methods"] == 4
          and refinement["runtime_authority_unchanged"] is True
          and refinement["module_repaired_or_runtime_accepted"] is False,
          "bounded_g2_owner_exception_invalid")
    _need(cold_import["verdict"] == "LAZY_TYPED_PLAN_IMPORT_STATIC_PASS"
          and cold_import["source_review_sha256"] == G1E_EVIDENCE_PINS["g1e-evidence/cold-import-source-review.json"]
          and cold_import["path"] == G2_COLD_IMPORT
          and cold_import["before_sha256"] == G2_REPAIR_PINS[G2_COLD_IMPORT]["before_sha256"]
          and cold_import["candidate_sha256"] == G2_REPAIR_PINS[G2_COLD_IMPORT]["after_sha256"]
          and cold_import["remaining_ast_identical"] is True
          and cold_import["excluded_script_read_copied_or_imported"] is False
          and cold_import["application_runtime_tested"] is False and cold_import["runtime_feature_activated"] is False,
          "bounded_g2_cold_import_review_invalid")
    expected = build_g2_acceptance_transition(before, _json(after[G2_SCOPE]))
    for path in G2_TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g2_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g2_agents_delta_invalid")
    _need(after[G2_SCOPE] == expected[G2_SCOPE], "bounded_g2_scope_encoding_invalid")


@dataclass(frozen=True, slots=True)
class BoundedG1BContext:
    target_root: Path
    source_root: Path
    evidence_root: Path
    scratch_root: Path
    binding_path: Path
    expected_binding_sha256: str


@dataclass(frozen=True, slots=True)
class BoundedG1BInputs:
    binding: dict[str, Any]
    before: dict[str, bytes]
    payloads: dict[str, bytes]
    evidence: dict[str, bytes]
    index_observation: dict[str, Any]


@dataclass(frozen=True, slots=True)
class BoundedG1BDecision:
    policy_admitted: bool
    reason_codes: tuple[str, ...]
    entrypoint: str
    phase: str
    operation_id: str | None = None
    candidate_tree: str | None = None
    binding_sha256: str | None = None
    observation_sha256: str | None = None
    execution_authorized: bool = False
    claim_limits: tuple[str, ...] = LIMITS
    current_gate: str | None = None
    active_profile: str | None = None
    assessment_passed: bool = False
    configuration_sha256: str | None = None


def _digest_map(value: object, paths: frozenset[str], reason: str) -> dict:
    result = _keys(value, paths, reason)
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in result.values()), reason)
    return result


def build_g2_batch_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    sources = _digest_map(controller_sources, CONTROLLER_PATHS, "bounded_g2_batch_controller_paths")
    _need(type(recorded_at) is str and datetime.fromisoformat(recorded_at).tzinfo is not None,
          "bounded_g2_batch_timestamp")
    _need(type(transition_base) is str and re.fullmatch(r"[0-9a-f]{40}", transition_base),
          "bounded_g2_batch_transition_base")
    _need(all(sources[p] == G2_INITIAL_CONTROLLER["source_sha256"][p]
              for p in CONTROLLER_PATHS - G2_BATCH_CODE_PATHS),
          "bounded_g2_batch_unchanged_controller_component")
    return {
        "schema_version": G2_BATCH_SCOPE_VERSION, "recorded_at": recorded_at,
        "transition_base_commit": transition_base,
        "initial_activation": copy.deepcopy(G2_INITIAL_ACTIVATION),
        "initial_scope": {"path": G2_SCOPE, "sha256": G2_INITIAL_POLICY_PINS[G2_SCOPE]},
        "initial_source_repair": copy.deepcopy(G2_INITIAL_REPAIR),
        "controller_source_sha256": dict(sources),
        "current_operation": {
            "operation_id": "g2-reviewed-baseline-repair", "profile": G2_PROFILE,
            "task_class": G2_BATCH_TASK, "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g2-confirmation-family-fixture-repair",
                           "scope_path": G2_SCOPE, "scope_commit": G2_INITIAL_ACTIVATION["commit"],
                           "scope_sha256": G2_INITIAL_POLICY_PINS[G2_SCOPE],
                           "historical_latch_preserved": True},
        },
        "allowed_paths": sorted(G2_BATCH_PATHS), "maximum_changed_files": 6,
        "candidate_authority": "independently_reviewed_exact_operation_binding",
        "allowed_effects": sorted(G2_BATCH_EFFECTS),
        "forbidden_effects": raisa_policy.g2_batch_profile()["forbidden_effects"],
        "owner_test_runtime_exception": raisa_policy.g2_test_exception(),
        "g2_exit_requirements": list(G2_CRITERIA), "g1e_complete": True, "g2_complete": False,
        "global_gate": "red_repair_only", "feature_work_eligible": False,
        "operational_multi_task_control_accepted": False, "execution_authorized": False,
        "existing_clockwork_writers_activated": False, "claim_limits": list(G2_BATCH_LIMITS),
    }


def build_g2_catalogue_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    scope = build_g2_batch_scope(recorded_at, transition_base, controller_sources)
    _need(len(G2_CATALOGUE_PATHS) == 148
          and _sha(_canonical(sorted(G2_CATALOGUE_PATHS))) == raisa_policy.G2_CATALOGUE_PATH_SET_SHA256,
          "bounded_g2_catalogue_membership_changed")
    scope.update(schema_version=G2_CATALOGUE_SCOPE_VERSION, allowed_paths=sorted(G2_CATALOGUE_PATHS),
                 source_catalogue={"source_binding_sha256": raisa_policy.G2_CATALOGUE_SOURCE_BINDING_SHA256,
                                   "path_set_sha256": raisa_policy.G2_CATALOGUE_PATH_SET_SHA256,
                                   "path_count": 148},
                 prior_batch_activation={"commit": G2_CATALOGUE_PREDECESSOR["commit"],
                                         "scope_sha256": G2_CATALOGUE_PREDECESSOR_POLICY[G2_SCOPE]})
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-reviewed-baseline-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_CATALOGUE_PREDECESSOR["commit"],
        "scope_sha256": G2_CATALOGUE_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def build_g2_migration_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """A separate migration lane; no extension of the historical catalogue."""
    scope = build_g2_batch_scope(recorded_at, transition_base, controller_sources)
    scope.update(
        schema_version=G2_MIGRATION_SCOPE_VERSION,
        enable_operation="enable_g2_migration", repair_operation="repair_g2_migration",
        allowed_paths=sorted(G2_MIGRATION_PATHS), maximum_changed_files=2,
        allowed_additions=[G2_MIGRATION_ADDITION],
        allowed_effects=sorted(G2_MIGRATION_EFFECTS),
        forbidden_effects=raisa_policy.g2_migration_profile()["forbidden_effects"],
        migration_supported_paths=raisa_policy.g2_migration_contract(),
        prior_catalogue_activation={"commit": G2_MIGRATION_PREDECESSOR["commit"],
                                    "scope_sha256": G2_MIGRATION_PREDECESSOR_POLICY[G2_SCOPE]},
    )
    scope["current_operation"]["operation_id"] = "g2-migration-preservation-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-reviewed-baseline-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_MIGRATION_PREDECESSOR["commit"],
        "scope_sha256": G2_MIGRATION_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def build_g2_instructions_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Recognize one published instruction policy without broadening G2."""
    scope = build_g2_migration_scope(recorded_at, transition_base, controller_sources)
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v)
              for v in G2_INSTRUCTIONS_PUBLICATION.values()), "bounded_g2_instructions_publication_unbound")
    _need(controller_sources["orchestration_harness/raisa_policy.py"] ==
          G2_INSTRUCTIONS_PREDECESSOR["source_sha256"]["orchestration_harness/raisa_policy.py"],
          "bounded_g2_instructions_profile_changed")
    scope.update(schema_version=G2_INSTRUCTIONS_SCOPE_VERSION, enable_operation="align_g2_instructions",
        current_instruction_policy={"path": AGENTS, "sha256": G2_INSTRUCTIONS_SHA256,
            "previous_sha256": G2_INITIAL_POLICY_PINS[AGENTS],
            "publication": copy.deepcopy(G2_INSTRUCTIONS_PUBLICATION)},
        prior_migration_activation={"commit": G2_INSTRUCTIONS_PREDECESSOR["commit"],
                                   "scope_sha256": G2_INSTRUCTIONS_PREDECESSOR_POLICY[G2_SCOPE]})
    return scope


def build_g2_audio_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Activate only the reviewed audio privacy source paths; runtime stays closed."""
    scope = build_g2_migration_scope(recorded_at, transition_base, controller_sources)
    _need(len(G2_AUDIO_PATHS) == 4 and G2_AUDIO_ADDITION in G2_AUDIO_PATHS,
          "bounded_g2_audio_paths_changed")
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v)
              for publication in (G2_AUDIO_TRUSTED_GIT_PUBLICATION, G2_AUDIO_INSTRUCTIONS_PUBLICATION)
              for v in publication.values()),
          "bounded_g2_audio_publication_unbound")
    _digest_map(G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256,
                frozenset(G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256),
                "bounded_g2_audio_trusted_git_sources")
    scope.update(
        schema_version=G2_AUDIO_SCOPE_VERSION,
        enable_operation="enable_g2_audio_privacy",
        repair_operation="repair_g2_audio_privacy",
        allowed_paths=sorted(G2_AUDIO_PATHS),
        maximum_changed_files=4,
        allowed_additions=[G2_AUDIO_ADDITION],
        allowed_effects=sorted(G2_AUDIO_EFFECTS),
        forbidden_effects=raisa_policy.g2_audio_privacy_profile()["forbidden_effects"],
        current_instruction_policy={"path": AGENTS, "sha256": G2_AUDIO_INSTRUCTIONS_SHA256,
            "previous_sha256": G2_INSTRUCTIONS_SHA256,
            "publication": copy.deepcopy(G2_AUDIO_INSTRUCTIONS_PUBLICATION)},
        prior_migration_activation={"commit": G2_INSTRUCTIONS_PREDECESSOR["commit"],
                                    "scope_sha256": G2_INSTRUCTIONS_PREDECESSOR_POLICY[G2_SCOPE]},
        prior_instruction_alignment={"commit": G2_AUDIO_PREDECESSOR["commit"],
                                     "scope_sha256": G2_AUDIO_PREDECESSOR_POLICY[G2_SCOPE]},
        trusted_git_successor={**copy.deepcopy(G2_AUDIO_TRUSTED_GIT_PUBLICATION),
                               "source_sha256": copy.deepcopy(G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256)},
        claim_limits=list(G2_AUDIO_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-audio-privacy-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-migration-preservation-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_AUDIO_PREDECESSOR["commit"],
        "scope_sha256": G2_AUDIO_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def build_g2_patient_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Activate only the reviewed no-implicit-patient repair; runtime stays closed."""
    scope = build_g2_audio_scope(recorded_at, transition_base, controller_sources)
    _need(len(G2_PATIENT_PATHS) == 4 and G2_PATIENT_ADDITION in G2_PATIENT_PATHS,
          "bounded_g2_patient_paths_changed")
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v)
              for v in G2_AUDIO_REPAIR_PUBLICATION.values()),
          "bounded_g2_patient_audio_publication_unbound")
    _digest_map(G2_AUDIO_REPAIR_SOURCE_SHA256, frozenset(G2_AUDIO_REPAIR_SOURCE_SHA256),
                "bounded_g2_patient_audio_sources")
    scope.update(
        schema_version=G2_PATIENT_SCOPE_VERSION,
        enable_operation="enable_g2_patient_binding",
        repair_operation="repair_g2_patient_binding",
        allowed_paths=sorted(G2_PATIENT_PATHS),
        maximum_changed_files=4,
        allowed_additions=[G2_PATIENT_ADDITION],
        allowed_effects=sorted(G2_PATIENT_EFFECTS),
        forbidden_effects=raisa_policy.g2_patient_binding_profile()["forbidden_effects"],
        prior_audio_activation={"commit": G2_PATIENT_PREDECESSOR["commit"],
                                "scope_sha256": G2_PATIENT_PREDECESSOR_POLICY[G2_SCOPE]},
        published_audio_repair={**copy.deepcopy(G2_AUDIO_REPAIR_PUBLICATION),
                                "source_sha256": copy.deepcopy(G2_AUDIO_REPAIR_SOURCE_SHA256)},
        claim_limits=list(G2_PATIENT_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-patient-binding-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-audio-privacy-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_PATIENT_PREDECESSOR["commit"],
        "scope_sha256": G2_PATIENT_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def build_g2_atomicity_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Activate only the reviewed consultation transaction repair; runtime stays separate."""
    scope = build_g2_patient_scope(recorded_at, transition_base, controller_sources)
    _need(len(G2_ATOMICITY_PATHS) == 4 and G2_ATOMICITY_ADDITION in G2_ATOMICITY_PATHS,
          "bounded_g2_atomicity_paths_changed")
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v)
              for v in G2_PATIENT_REPAIR_PUBLICATION.values()),
          "bounded_g2_atomicity_patient_publication_unbound")
    _digest_map(G2_PATIENT_REPAIR_SOURCE_SHA256, frozenset(G2_PATIENT_REPAIR_SOURCE_SHA256),
                "bounded_g2_atomicity_patient_sources")
    scope.update(
        schema_version=G2_ATOMICITY_SCOPE_VERSION,
        enable_operation="enable_g2_consultation_atomicity",
        repair_operation="repair_g2_consultation_atomicity",
        allowed_paths=sorted(G2_ATOMICITY_PATHS),
        maximum_changed_files=4,
        allowed_additions=[G2_ATOMICITY_ADDITION],
        allowed_effects=sorted(G2_ATOMICITY_EFFECTS),
        forbidden_effects=raisa_policy.g2_consultation_atomicity_profile()["forbidden_effects"],
        prior_patient_activation={"commit": G2_ATOMICITY_PREDECESSOR["commit"],
                                "scope_sha256": G2_ATOMICITY_PREDECESSOR_POLICY[G2_SCOPE]},
        published_patient_repair={**copy.deepcopy(G2_PATIENT_REPAIR_PUBLICATION),
                                "source_sha256": copy.deepcopy(G2_PATIENT_REPAIR_SOURCE_SHA256)},
        claim_limits=list(G2_ATOMICITY_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-consultation-atomicity-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-patient-binding-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_ATOMICITY_PREDECESSOR["commit"],
        "scope_sha256": G2_ATOMICITY_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope

def build_g2_clinical_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Bind semantic V8 source revision 4; never grant live authority."""
    scope = build_g2_atomicity_scope(recorded_at, transition_base, controller_sources)
    contract = raisa_policy.g2_clinical_authority_contract()
    _need(contract.get("semantic_version") == "v8"
          and contract.get("source_revision") == G2_CLINICAL_SOURCE_REVISION,
          "bounded_g2_clinical_source_revision")
    _need(len(G2_CLINICAL_PATHS) == 6, "bounded_g2_clinical_paths_changed")
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{40}", v)
              for v in G2_ATOMICITY_REPAIR_PUBLICATION.values()),
          "bounded_g2_clinical_atomicity_publication_unbound")
    _digest_map(G2_ATOMICITY_REPAIR_SOURCE_SHA256, G2_CLINICAL_PATHS,
                "bounded_g2_clinical_atomicity_sources")
    scope.update(
        schema_version=G2_CLINICAL_SCOPE_VERSION,
        enable_operation="enable_g2_clinical_authority",
        repair_operation="repair_g2_clinical_authority",
        allowed_paths=sorted(G2_CLINICAL_PATHS),
        maximum_changed_files=6,
        allowed_additions=[],
        allowed_effects=sorted(G2_CLINICAL_EFFECTS),
        forbidden_effects=raisa_policy.g2_clinical_authority_profile()["forbidden_effects"],
        prior_atomicity_activation={"commit": G2_CLINICAL_PREDECESSOR["commit"],
                                     "scope_sha256": G2_CLINICAL_PREDECESSOR_POLICY[G2_SCOPE]},
        published_atomicity_repair={**copy.deepcopy(G2_ATOMICITY_REPAIR_PUBLICATION),
                                    "source_sha256": copy.deepcopy(G2_ATOMICITY_REPAIR_SOURCE_SHA256)},
        clinical_authority_contract=contract,
        claim_limits=list(G2_CLINICAL_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-clinical-authority-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-consultation-atomicity-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_CLINICAL_PREDECESSOR["commit"],
        "scope_sha256": G2_CLINICAL_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def build_g2_migration_guard_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """A distinct V9 successor from accepted clinical publication; no replay."""
    _need(transition_base == G2_MIGRATION_GUARD_PREDECESSOR["commit"],
          "bounded_g2_migration_guard_transition_base")
    scope = build_g2_clinical_scope(recorded_at, transition_base, controller_sources)
    _need(all(controller_sources[path] == G2_MIGRATION_GUARD_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_MIGRATION_GUARD_CODE_PATHS),
          "bounded_g2_migration_guard_unchanged_controller_component")
    scope["prior_instruction_policy"] = copy.deepcopy(scope["current_instruction_policy"])
    scope.update(
        schema_version=G2_MIGRATION_GUARD_SCOPE_VERSION,
        enable_operation="enable_g2_migration_downgrade_guard",
        repair_operation="repair_g2_migration_downgrade_guard",
        allowed_paths=sorted(G2_MIGRATION_PATHS), maximum_changed_files=2, allowed_additions=[],
        allowed_effects=sorted(G2_MIGRATION_EFFECTS),
        forbidden_effects=raisa_policy.g2_migration_profile()["forbidden_effects"],
        migration_supported_paths=raisa_policy.g2_migration_contract(),
        repair_preimage_sha256=copy.deepcopy(G2_MIGRATION_GUARD_REPAIR_PINS),
        current_instruction_policy={"path": AGENTS, "sha256": G2_MIGRATION_GUARD_INSTRUCTIONS_SHA256,
            "previous_sha256": G2_MIGRATION_GUARD_PREDECESSOR_POLICY[AGENTS],
            "authority": "accepted_meeting_insertion_owned_by_exact_maintenance_candidate"},
        published_clinical_repair={key: G2_MIGRATION_GUARD_PREDECESSOR[key]
                                   for key in ("commit", "parent", "tree")},
        prior_migration_acceptance=copy.deepcopy(G2_MIGRATION_GUARD_PRIOR_ACCEPTANCE),
        prior_clinical_publication_acceptance=copy.deepcopy(G2_MIGRATION_GUARD_CLINICAL_ACCEPTANCE),
        claim_limits=list(G2_MIGRATION_GUARD_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-migration-downgrade-guard-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-clinical-authority-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_MIGRATION_GUARD_PREDECESSOR["commit"],
        "scope_sha256": G2_MIGRATION_GUARD_PREDECESSOR_POLICY[G2_SCOPE], "historical_latch_preserved": True}
    return scope


def _g2_appointment_profile() -> dict:
    """Return the exact V10 profile recognized by the real configuration validator."""
    return raisa_policy.g2_appointment_concurrency_profile()


def build_g2_appointment_scope(recorded_at: str, transition_base: str, controller_sources: dict) -> dict:
    """Select one exact seven-file successor without replaying the consumed V9 batch."""
    _need(transition_base == G2_APPOINTMENT_PREDECESSOR["commit"],
          "bounded_g2_appointment_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_appointment_controller_paths")
    historical_sources = copy.deepcopy(sources)
    historical_sources["orchestration_harness/raisa_policy.py"] = (
        G2_APPOINTMENT_PREDECESSOR["source_sha256"]["orchestration_harness/raisa_policy.py"])
    scope = build_g2_migration_guard_scope(
        recorded_at, G2_MIGRATION_GUARD_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_APPOINTMENT_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_APPOINTMENT_CODE_PATHS),
          "bounded_g2_appointment_unchanged_controller_component")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope["prior_instruction_policy"] = copy.deepcopy(scope["current_instruction_policy"])
    scope.update(
        schema_version=G2_APPOINTMENT_SCOPE_VERSION,
        enable_operation="enable_g2_appointment_concurrency",
        repair_operation="repair_g2_appointment_concurrency",
        allowed_paths=sorted(G2_APPOINTMENT_PATHS), maximum_changed_files=7,
        allowed_additions=sorted(G2_APPOINTMENT_ADDITIONS),
        allowed_effects=sorted(G2_MIGRATION_EFFECTS),
        forbidden_effects=_g2_appointment_profile()["forbidden_effects"],
        appointment_concurrency_invariant=copy.deepcopy(G2_APPOINTMENT_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_APPOINTMENT_REPAIR_PINS),
        current_instruction_policy={
            "path": AGENTS, "sha256": G2_APPOINTMENT_INSTRUCTIONS_SHA256,
            "previous_sha256": G2_APPOINTMENT_PREDECESSOR_POLICY[AGENTS],
            "authority": "owner_requested_worker_allocation_parallel_delivery_identity_relay_and_compaction_rehydration_update",
        },
        published_migration_guard_repair={
            **{key: G2_APPOINTMENT_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_APPOINTMENT_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_APPOINTMENT_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-appointment-concurrency-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-migration-downgrade-guard-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_APPOINTMENT_PREDECESSOR["commit"],
        "scope_sha256": G2_APPOINTMENT_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_production_profile() -> dict:
    """Return the exact V11 controller profile recognized by the real validator."""
    return raisa_policy.g2_production_profile()


def build_g2_production_profile_scope(recorded_at: str, transition_base: str,
                                       controller_sources: dict) -> dict:
    """Select the exact four-file serving-containment successor."""
    _need(transition_base == G2_PRODUCTION_PROFILE_PREDECESSOR["commit"],
          "bounded_g2_production_profile_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_production_profile_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_PRODUCTION_PROFILE_CODE_PATHS:
        historical_sources[path] = G2_PRODUCTION_PROFILE_PREDECESSOR["source_sha256"][path]
    scope = build_g2_appointment_scope(
        recorded_at, G2_APPOINTMENT_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_PRODUCTION_PROFILE_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_PRODUCTION_PROFILE_CODE_PATHS),
          "bounded_g2_production_profile_unchanged_controller_component")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_PRODUCTION_PROFILE_SCOPE_VERSION,
        enable_operation="enable_g2_production_profile",
        repair_operation="repair_g2_production_profile",
        allowed_paths=sorted(G2_PRODUCTION_PROFILE_PATHS), maximum_changed_files=4,
        allowed_additions=sorted(G2_PRODUCTION_PROFILE_ADDITIONS),
        allowed_effects=sorted(G2_BATCH_EFFECTS),
        forbidden_effects=_g2_production_profile()["forbidden_effects"],
        production_profile_invariant=copy.deepcopy(G2_PRODUCTION_PROFILE_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_PRODUCTION_PROFILE_REPAIR_PINS),
        published_appointment_product_repair={
            **{key: G2_PRODUCTION_PROFILE_PREDECESSOR[key]
               for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_PRODUCTION_PROFILE_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_PRODUCTION_PROFILE_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-production-profile-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-appointment-concurrency-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_PRODUCTION_PROFILE_PREDECESSOR["commit"],
        "scope_sha256": G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_dependency_profile() -> dict:
    """Return the exact V12 profile recognized by the canonical validator."""
    return raisa_policy.g2_dependency_repair_profile()


def build_g2_dependency_scope(recorded_at: str, transition_base: str,
                              controller_sources: dict) -> dict:
    """Select the exact requirements change and one new compatibility test."""
    _need(transition_base == G2_DEPENDENCY_PREDECESSOR["commit"],
          "bounded_g2_dependency_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_dependency_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_DEPENDENCY_CODE_PATHS:
        historical_sources[path] = G2_DEPENDENCY_PREDECESSOR["source_sha256"][path]
    scope = build_g2_production_profile_scope(
        recorded_at, G2_PRODUCTION_PROFILE_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_DEPENDENCY_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_DEPENDENCY_CODE_PATHS),
          "bounded_g2_dependency_unchanged_controller_component")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_DEPENDENCY_SCOPE_VERSION,
        enable_operation="enable_g2_dependency_repair",
        repair_operation="repair_g2_dependency_repair",
        allowed_paths=sorted(G2_DEPENDENCY_PATHS), maximum_changed_files=2,
        allowed_additions=sorted(G2_DEPENDENCY_ADDITIONS),
        allowed_effects=sorted(G2_DEPENDENCY_EFFECTS),
        forbidden_effects=_g2_dependency_profile()["forbidden_effects"],
        dependency_invariant=copy.deepcopy(G2_DEPENDENCY_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_DEPENDENCY_REPAIR_PINS),
        published_production_profile_repair={
            **{key: G2_DEPENDENCY_PREDECESSOR[key]
               for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_DEPENDENCY_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_DEPENDENCY_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-dependency-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-production-profile-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_DEPENDENCY_PREDECESSOR["commit"],
        "scope_sha256": G2_DEPENDENCY_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_ci_profile() -> dict:
    """Return the exact V13 profile recognized by the canonical validator."""
    return raisa_policy.g2_ci_selection_profile()


def build_g2_ci_scope(recorded_at: str, transition_base: str,
                      controller_sources: dict) -> dict:
    """Select exactly seven ordinary verification files after dependency repair."""
    _need(transition_base == G2_CI_PREDECESSOR["commit"],
          "bounded_g2_ci_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_ci_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_CI_CODE_PATHS:
        historical_sources[path] = G2_CI_PREDECESSOR["source_sha256"][path]
    scope = build_g2_dependency_scope(
        recorded_at, G2_DEPENDENCY_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_CI_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_CI_CODE_PATHS),
          "bounded_g2_ci_unchanged_controller_component")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_CI_SCOPE_VERSION,
        enable_operation="enable_g2_ci_selection",
        repair_operation="repair_g2_ci_selection",
        allowed_paths=sorted(G2_CI_PATHS), maximum_changed_files=7,
        allowed_additions=[],
        allowed_effects=sorted(G2_CI_EFFECTS),
        forbidden_effects=_g2_ci_profile()["forbidden_effects"],
        ci_selection_invariant=copy.deepcopy(G2_CI_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_CI_REPAIR_PINS),
        published_dependency_repair={
            **{key: G2_CI_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_CI_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_CI_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-ci-selection-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-dependency-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_CI_PREDECESSOR["commit"],
        "scope_sha256": G2_CI_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_cim_profile() -> dict:
    """Return the exact V14 profile; database execution remains separately bound."""
    return raisa_policy.g2_ci_migration_profile()


def build_g2_cim_scope(recorded_at: str, transition_base: str,
                       controller_sources: dict) -> dict:
    """Select the two migration-helper files after accepted CI selection repair."""
    _need(transition_base == G2_CIM_PREDECESSOR["commit"],
          "bounded_g2_cim_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_cim_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_CIM_CODE_PATHS:
        historical_sources[path] = G2_CIM_PREDECESSOR["source_sha256"][path]
    scope = build_g2_ci_scope(
        recorded_at, G2_CI_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_CIM_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_CIM_CODE_PATHS),
          "bounded_g2_cim_unchanged_controller_component")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_CIM_SCOPE_VERSION,
        enable_operation="enable_g2_ci_migration",
        repair_operation="repair_g2_ci_migration",
        allowed_paths=sorted(G2_CIM_PATHS), maximum_changed_files=2,
        allowed_additions=[],
        allowed_effects=sorted(G2_CIM_EFFECTS),
        forbidden_effects=_g2_cim_profile()["forbidden_effects"],
        ci_migration_invariant=copy.deepcopy(G2_CIM_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_CIM_REPAIR_PINS),
        published_ci_selection_repair={
            **{key: G2_CIM_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_CIM_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_CIM_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-ci-migration-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-ci-selection-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_CIM_PREDECESSOR["commit"],
        "scope_sha256": G2_CIM_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_tenant_profile() -> dict:
    """Return only the exact V15 two-addition profile."""
    return raisa_policy.g2_tenant_migration_profile()


def build_g2_tenant_scope(recorded_at: str, transition_base: str,
                          controller_sources: dict) -> dict:
    """Select the two new tenant migration files after accepted CI-B publication."""
    _need(transition_base == G2_TENANT_PREDECESSOR["commit"],
          "bounded_g2_tenant_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_tenant_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_TENANT_CODE_PATHS:
        historical_sources[path] = G2_TENANT_PREDECESSOR["source_sha256"][path]
    scope = build_g2_cim_scope(
        recorded_at, G2_CIM_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_TENANT_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_TENANT_CODE_PATHS),
          "bounded_g2_tenant_unchanged_controller_component")
    scope["historical_ci_migration_invariant"] = scope.pop("ci_migration_invariant")
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_TENANT_SCOPE_VERSION,
        enable_operation="enable_g2_tenant_migration",
        repair_operation="repair_g2_tenant_migration",
        allowed_paths=sorted(G2_TENANT_PATHS), maximum_changed_files=2,
        allowed_additions=sorted(G2_TENANT_PATHS),
        allowed_effects=sorted(G2_TENANT_EFFECTS),
        forbidden_effects=_g2_tenant_profile()["forbidden_effects"],
        tenant_migration_invariant=copy.deepcopy(G2_TENANT_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_TENANT_REPAIR_PINS),
        published_ci_migration_repair={
            **{key: G2_TENANT_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_TENANT_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_TENANT_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-tenant-migration-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-ci-migration-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_TENANT_PREDECESSOR["commit"],
        "scope_sha256": G2_TENANT_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_relationship_profile() -> dict:
    """Return only the fixed V16 three-addition migration profile."""
    return raisa_policy.g2_tenant_relationship_profile()


def build_g2_relationship_scope(recorded_at: str, transition_base: str,
                                controller_sources: dict) -> dict:
    """Select three reviewed new files after accepted tenant publication."""
    _need(transition_base == G2_RELATIONSHIP_PREDECESSOR["commit"],
          "bounded_g2_relationship_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_relationship_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_RELATIONSHIP_CODE_PATHS:
        historical_sources[path] = G2_RELATIONSHIP_PREDECESSOR["source_sha256"][path]
    scope = build_g2_tenant_scope(
        recorded_at, G2_TENANT_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_RELATIONSHIP_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_RELATIONSHIP_CODE_PATHS),
          "bounded_g2_relationship_unchanged_controller_component")
    scope["historical_tenant_migration_invariant"] = scope.pop("tenant_migration_invariant")
    scope["historical_tenant_operation"] = copy.deepcopy(scope["current_operation"])
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_RELATIONSHIP_SCOPE_VERSION,
        enable_operation="enable_g2_tenant_relationships",
        repair_operation="repair_g2_tenant_relationships",
        allowed_paths=sorted(G2_RELATIONSHIP_PATHS), maximum_changed_files=3,
        allowed_additions=sorted(G2_RELATIONSHIP_PATHS),
        allowed_effects=sorted(G2_RELATIONSHIP_EFFECTS),
        forbidden_effects=_g2_relationship_profile()["forbidden_effects"],
        tenant_relationship_invariant=copy.deepcopy(G2_RELATIONSHIP_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_RELATIONSHIP_REPAIR_PINS),
        published_tenant_migration_repair={
            **{key: G2_RELATIONSHIP_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_RELATIONSHIP_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_RELATIONSHIP_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-tenant-relationship-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-tenant-migration-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_RELATIONSHIP_PREDECESSOR["commit"],
        "scope_sha256": G2_RELATIONSHIP_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope


def _g2_completeness_profile() -> dict:
    """Return only the fixed V17 three-update CI profile."""
    return raisa_policy.g2_ci_completeness_profile()


def build_g2_completeness_scope(recorded_at: str, transition_base: str,
                                controller_sources: dict) -> dict:
    """Select three existing guard files after accepted relationship publication."""
    _need(transition_base == G2_COMPLETENESS_PREDECESSOR["commit"],
          "bounded_g2_completeness_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_completeness_controller_paths")
    historical_sources = copy.deepcopy(sources)
    for path in G2_COMPLETENESS_CODE_PATHS:
        historical_sources[path] = G2_COMPLETENESS_PREDECESSOR["source_sha256"][path]
    scope = build_g2_relationship_scope(
        recorded_at, G2_RELATIONSHIP_PREDECESSOR["commit"], historical_sources)
    _need(all(sources[path] == G2_COMPLETENESS_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_COMPLETENESS_CODE_PATHS),
          "bounded_g2_completeness_unchanged_controller_component")
    scope["historical_relationship_invariant"] = scope.pop("tenant_relationship_invariant")
    scope["historical_relationship_operation"] = copy.deepcopy(scope["current_operation"])
    scope["controller_source_sha256"] = copy.deepcopy(sources)
    scope["transition_base_commit"] = transition_base
    scope.update(
        schema_version=G2_COMPLETENESS_SCOPE_VERSION,
        enable_operation="enable_g2_ci_completeness",
        repair_operation="repair_g2_ci_completeness",
        allowed_paths=sorted(G2_COMPLETENESS_PATHS), maximum_changed_files=3,
        allowed_additions=[],
        allowed_effects=sorted(G2_COMPLETENESS_EFFECTS),
        forbidden_effects=_g2_completeness_profile()["forbidden_effects"],
        ci_completeness_invariant=copy.deepcopy(G2_COMPLETENESS_INVARIANT),
        repair_preimage_sha256=copy.deepcopy(G2_COMPLETENESS_REPAIR_PINS),
        published_relationship_repair={
            **{key: G2_COMPLETENESS_PREDECESSOR[key] for key in ("commit", "parent", "tree")},
            "acceptance": copy.deepcopy(G2_COMPLETENESS_PUBLICATION_ACCEPTANCE),
        },
        claim_limits=list(G2_COMPLETENESS_LIMITS),
    )
    scope["current_operation"]["operation_id"] = "g2-ci-completeness-repair"
    scope["current_operation"]["supersedes"] = {
        "operation_id": "g2-tenant-relationship-repair", "scope_path": G2_SCOPE,
        "scope_commit": G2_COMPLETENESS_PREDECESSOR["commit"],
        "scope_sha256": G2_COMPLETENESS_PREDECESSOR_POLICY[G2_SCOPE],
        "historical_latch_preserved": True,
    }
    return scope



def build_g2_pyjwt_scope(recorded_at: str, transition_base: str,
                         controller_sources: dict) -> dict:
    """Exact successor from current CI-incomplete bytes; no history reconstruction."""
    _need(type(recorded_at) is str, "bounded_g2_pyjwt_timestamp")
    try:
        stamp = datetime.fromisoformat(recorded_at)
    except ValueError:
        raise BoundedG1BError("bounded_g2_pyjwt_timestamp") from None
    _need(stamp.tzinfo is not None and stamp.utcoffset() is not None,
          "bounded_g2_pyjwt_timestamp")
    _need(transition_base == G2_PYJWT_PREDECESSOR["commit"],
          "bounded_g2_pyjwt_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_pyjwt_controller_paths")
    _need(all(sources[path] == G2_PYJWT_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_DEPENDENCY_CODE_PATHS),
          "bounded_g2_pyjwt_unchanged_controller_component")
    prior = copy.deepcopy(G2_PYJWT_PRIOR_CI_SCOPE)
    _need(_sha(_canonical(prior) + b"\n") == G2_PYJWT_PREDECESSOR_POLICY[G2_SCOPE],
          "bounded_g2_pyjwt_preserved_ci_scope")
    scope = copy.deepcopy(prior)
    scope.update(schema_version=G2_PYJWT_SCOPE_VERSION, recorded_at=recorded_at,
        transition_base_commit=transition_base, controller_source_sha256=sources,
        enable_operation="enable_g2_pyjwt_repair", repair_operation="repair_g2_pyjwt_repair",
        allowed_paths=sorted(G2_DEPENDENCY_PATHS), maximum_changed_files=2,
        allowed_additions=[], allowed_effects=sorted(G2_DEPENDENCY_EFFECTS),
        forbidden_effects=raisa_policy.g2_pyjwt_repair_profile()["forbidden_effects"],
        dependency_invariant={"root_change": {"package": "PyJWT", "before": "2.13.0", "after": "2.15.1"},
            "all_other_24_roots_unchanged": True, "cryptography": "50.0.1",
            "candidate_sha256": copy.deepcopy(G2_PYJWT_CANDIDATE_PINS),
            "compatibility_acceptance": copy.deepcopy(G2_PYJWT_COMPATIBILITY_ACCEPTANCE),
            "metadata_audit_is_not_runtime_or_g2_acceptance": True},
        repair_preimage_sha256=copy.deepcopy(G2_PYJWT_REPAIR_PINS),
        preserved_incomplete_ci_scope=prior, claim_limits=list(G2_PYJWT_LIMITS))
    scope["current_operation"] = {
        **copy.deepcopy(prior["current_operation"]),
        "operation_id": "g2-pyjwt2151-repair",
        "completion_accepted": False, "status": "active",
        "supersedes": {"operation_id": prior["current_operation"]["operation_id"],
            "scope_path": G2_SCOPE, "scope_commit": transition_base,
            "scope_sha256": G2_PYJWT_PREDECESSOR_POLICY[G2_SCOPE],
            "historical_latch_preserved": True, "predecessor_completion_accepted": False}}
    return scope

def build_g2_pyjwt_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Use existing three-record G2 transition; preserve all other state/overlay."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_pyjwt_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_PYJWT_PREDECESSOR_POLICY[path],
              "bounded_g2_pyjwt_prior_policy_changed")
    _need(scope.get("schema_version") == G2_PYJWT_SCOPE_VERSION, "bounded_g2_pyjwt_scope_version")
    _validate_g2_batch_scope(scope)
    state, overlay = _json(before[STATE]), _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_pyjwt2151_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_pyjwt_repair_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}

def _g2_transport_prior_scope() -> dict:
    # Reconstruct only the already fixed ordinary V18 scope with its historical
    # builder. This performs no filesystem load and creates no acceptance.
    prior = build_g2_pyjwt_scope("2026-10-01T02:31:54.5397521Z",
                               G2_PYJWT_PREDECESSOR["commit"],
                               G2_TRANSPORT_PREDECESSOR["source_sha256"])
    _need(_sha(_canonical(prior) + b"\n") == G2_TRANSPORT_PREDECESSOR_POLICY[G2_SCOPE],
          "bounded_g2_transport_prior_scope_changed")
    return prior


def build_g2_transport_scope(recorded_at: str, transition_base: str,
                             controller_sources: dict) -> dict:
    """Fixed transport successor; preserve prior state and consumed authorities."""
    _need(type(recorded_at) is str, "bounded_g2_transport_timestamp")
    try:
        stamp = datetime.fromisoformat(recorded_at)
    except ValueError:
        raise BoundedG1BError("bounded_g2_transport_timestamp") from None
    _need(stamp.tzinfo is not None and stamp.utcoffset() is not None,
          "bounded_g2_transport_timestamp")
    _need(transition_base == G2_TRANSPORT_PREDECESSOR["commit"],
          "bounded_g2_transport_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_transport_controller_paths")
    _need(all(sources[path] == G2_TRANSPORT_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_BATCH_CODE_PATHS),
          "bounded_g2_transport_unchanged_controller_component")
    prior = _g2_transport_prior_scope()
    scope = copy.deepcopy(prior)
    scope.update(schema_version=G2_TRANSPORT_SCOPE_VERSION, recorded_at=recorded_at,
        transition_base_commit=transition_base, controller_source_sha256=sources,
        enable_operation="enable_g2_transport_repair", repair_operation="repair_g2_transport_repair",
        allowed_paths=sorted(G2_TRANSPORT_PATHS), maximum_changed_files=2,
        allowed_additions=sorted(G2_TRANSPORT_ADDITIONS), allowed_effects=sorted(G2_BATCH_EFFECTS),
        forbidden_effects=raisa_policy.g2_transport_repair_profile()["forbidden_effects"],
        repair_preimage_sha256=copy.deepcopy(G2_TRANSPORT_REPAIR_PINS),
        preserved_incomplete_pyjwt_scope=prior, claim_limits=list(G2_TRANSPORT_LIMITS),
        current_owner_directive={"owner": "Yuri", "record_path": G2_TRANSPORT_OWNER_RECORD,
            "sha256": G2_TRANSPORT_OWNER_SHA256, "historical_authority_rewritten": False},
        transport_invariant={"no_hosted_browser_bearer_storage": True,
            "malformed_or_missing_hosting_policy_fails_closed": True,
            "all_provider_transports_require_reviewed_gate": True,
            "existing_uncommitted_changes_preserved_in_reviewed_afterimage": True,
            "admission_grants_runtime_authority": False})
    scope["current_operation"] = {
        **copy.deepcopy(prior["current_operation"]),
        "operation_id": "g2-taskpane-transport-repair",
        "completion_accepted": False, "status": "active",
        "supersedes": {"operation_id": prior["current_operation"]["operation_id"],
            "scope_path": G2_SCOPE, "scope_commit": G2_TRANSPORT_HISTORICAL_V18_SCOPE_COMMIT,
            "scope_sha256": G2_TRANSPORT_PREDECESSOR_POLICY[G2_SCOPE],
            "historical_latch_preserved": True, "predecessor_completion_accepted": False}}
    return scope


def build_g2_transport_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Three exact control afterimages; no gate, historical latch or grant change."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_transport_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_TRANSPORT_PREDECESSOR_POLICY[path],
              "bounded_g2_transport_prior_policy_changed")
    _need(scope.get("schema_version") == G2_TRANSPORT_SCOPE_VERSION, "bounded_g2_transport_scope_version")
    _validate_g2_batch_scope(scope)
    state, overlay = _json(before[STATE]), _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_taskpane_transport_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_transport_repair_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def _g2_six_file_prior_scope() -> dict:
    prior = build_g2_transport_scope(G2_SIX_PRIOR_RECORDED_AT,
        G2_TRANSPORT_PREDECESSOR["commit"], G2_SIX_PREDECESSOR["source_sha256"])
    _need(_sha(_canonical(prior) + b"\n") == G2_SIX_PREDECESSOR_POLICY[G2_SCOPE],
          "bounded_g2_six_file_prior_scope_changed")
    return prior


def build_g2_six_file_scope(recorded_at: str, transition_base: str,
                            controller_sources: dict) -> dict:
    _need(type(recorded_at) is str, "bounded_g2_six_file_timestamp")
    try:
        stamp = datetime.fromisoformat(recorded_at)
    except ValueError:
        raise BoundedG1BError("bounded_g2_six_file_timestamp") from None
    _need(stamp.tzinfo is not None and stamp.utcoffset() is not None,
          "bounded_g2_six_file_timestamp")
    _need(transition_base == G2_SIX_PREDECESSOR["commit"], "bounded_g2_six_file_transition_base")
    sources = _digest_map(controller_sources, CONTROLLER_PATHS,
                          "bounded_g2_six_file_controller_paths")
    _need(all(sources[path] == G2_SIX_PREDECESSOR["source_sha256"][path]
              for path in CONTROLLER_PATHS - G2_BATCH_CODE_PATHS),
          "bounded_g2_six_file_unchanged_controller_component")
    prior = _g2_six_file_prior_scope()
    scope = copy.deepcopy(prior)
    scope.update(schema_version=G2_SIX_SCOPE_VERSION, recorded_at=recorded_at,
        transition_base_commit=transition_base, controller_source_sha256=sources,
        enable_operation="enable_g2_six_file_repair", repair_operation="repair_g2_six_file_repair",
        allowed_paths=sorted(G2_SIX_PATHS), maximum_changed_files=6, allowed_additions=[],
        allowed_effects=sorted(G2_BATCH_EFFECTS),
        forbidden_effects=raisa_policy.g2_six_file_repair_profile()["forbidden_effects"],
        repair_subject_sha256=G2_SIX_SUBJECT_SHA256,
        repair_sha256=copy.deepcopy(G2_SIX_REPAIR_PINS),
        repair_preimage_sha256={p: row["before_sha256"] for p, row in G2_SIX_REPAIR_PINS.items()},
        preserved_transport_scope=prior, claim_limits=list(G2_SIX_LIMITS),
        predecessor_publication_review_sha256=copy.deepcopy(G2_SIX_PUBLICATION_REVIEW_PINS))
    scope["current_operation"] = {
        **copy.deepcopy(prior["current_operation"]),
        "operation_id": "g2-six-file-confirmation-and-checker-repair",
        "completion_accepted": False, "status": "active",
        "supersedes": {"operation_id": prior["current_operation"]["operation_id"],
            "scope_path": G2_SCOPE, "scope_commit": G2_SIX_PREDECESSOR["commit"],
            "scope_sha256": G2_SIX_PREDECESSOR_POLICY[G2_SCOPE],
            "historical_latch_preserved": True, "predecessor_completion_accepted": False}}
    return scope


def build_g2_six_file_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_six_file_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_SIX_PREDECESSOR_POLICY[path],
              "bounded_g2_six_file_prior_policy_changed")
    _need(scope.get("schema_version") == G2_SIX_SCOPE_VERSION, "bounded_g2_six_file_scope_version")
    _validate_g2_batch_scope(scope)
    state, overlay = _json(before[STATE]), _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_six_file_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_six_file_repair_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def _validate_g2_batch_scope(scope: dict) -> None:
    builder = (build_g2_six_file_scope if scope.get("schema_version") == G2_SIX_SCOPE_VERSION else build_g2_transport_scope if scope.get("schema_version") == G2_TRANSPORT_SCOPE_VERSION else build_g2_pyjwt_scope if scope.get("schema_version") == G2_PYJWT_SCOPE_VERSION
               else build_g2_completeness_scope if scope.get("schema_version") == G2_COMPLETENESS_SCOPE_VERSION
               else build_g2_relationship_scope if scope.get("schema_version") == G2_RELATIONSHIP_SCOPE_VERSION
               else build_g2_tenant_scope if scope.get("schema_version") == G2_TENANT_SCOPE_VERSION
               else build_g2_cim_scope if scope.get("schema_version") == G2_CIM_SCOPE_VERSION
               else build_g2_ci_scope if scope.get("schema_version") == G2_CI_SCOPE_VERSION
               else build_g2_dependency_scope
               if scope.get("schema_version") == G2_DEPENDENCY_SCOPE_VERSION
               else build_g2_production_profile_scope
               if scope.get("schema_version") == G2_PRODUCTION_PROFILE_SCOPE_VERSION
               else build_g2_appointment_scope if scope.get("schema_version") == G2_APPOINTMENT_SCOPE_VERSION
               else build_g2_migration_guard_scope if scope.get("schema_version") == G2_MIGRATION_GUARD_SCOPE_VERSION
               else build_g2_clinical_scope if scope.get("schema_version") == G2_CLINICAL_SCOPE_VERSION
               else build_g2_atomicity_scope if scope.get("schema_version") == G2_ATOMICITY_SCOPE_VERSION
               else build_g2_patient_scope if scope.get("schema_version") == G2_PATIENT_SCOPE_VERSION
               else build_g2_audio_scope if scope.get("schema_version") == G2_AUDIO_SCOPE_VERSION
               else build_g2_instructions_scope if scope.get("schema_version") == G2_INSTRUCTIONS_SCOPE_VERSION
               else build_g2_migration_scope if scope.get("schema_version") == G2_MIGRATION_SCOPE_VERSION
               else build_g2_catalogue_scope if scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION
               else build_g2_batch_scope)
    expected = builder(scope.get("recorded_at"), scope.get("transition_base_commit"),
                       scope.get("controller_source_sha256"))
    _need(_canonical(scope) == _canonical(expected), "bounded_g2_batch_scope_invalid")


def build_g2_batch_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Change the active G2 lane, leaving historical acceptance and gates intact."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_batch_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_INITIAL_POLICY_PINS[path],
              "bounded_g2_batch_initial_policy_changed")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(allowed_task_kinds=[G2_BATCH_TASK],
                                   next_eligibility_condition="bounded_G2_reviewed_repair_batches_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_batch_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_catalogue_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Extend the installed batch lane; preserve every historical gate decision."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_catalogue_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_CATALOGUE_PREDECESSOR_POLICY[path],
              "bounded_g2_catalogue_prior_policy_changed")
    _need(scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION, "bounded_g2_catalogue_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_catalogue_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(), G2_SCOPE: scope_raw}


def build_g2_migration_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Bind the owner-supported migration paths without accepting or rewriting G2."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_migration_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_MIGRATION_PREDECESSOR_POLICY[path],
              "bounded_g2_migration_prior_policy_changed")
    _need(scope.get("schema_version") == G2_MIGRATION_SCOPE_VERSION, "bounded_g2_migration_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_migration_preservation_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_migration_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(), G2_SCOPE: scope_raw}


def build_g2_instructions_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Update only scope consistency; the migration profile and gates stay fixed."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_instructions_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_INSTRUCTIONS_PREDECESSOR_POLICY[path],
              "bounded_g2_instructions_prior_policy_changed")
    _need(scope.get("schema_version") == G2_INSTRUCTIONS_SCOPE_VERSION, "bounded_g2_instructions_scope_version")
    _validate_g2_batch_scope(scope)
    scope_raw = _canonical(scope) + b"\n"
    state = _json(before[STATE])
    state["observed_at"] = scope["recorded_at"]
    state["g2"]["scope_sha256"] = _sha(scope_raw)
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: before[OVERLAY], G2_SCOPE: scope_raw}


def build_g2_audio_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate the exact audio source scope without accepting G2 or runtime."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_audio_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_AUDIO_PREDECESSOR_POLICY[path],
              "bounded_g2_audio_prior_policy_changed")
    _need(scope.get("schema_version") == G2_AUDIO_SCOPE_VERSION, "bounded_g2_audio_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_audio_privacy_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_audio_privacy_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_patient_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate exact patient binding without accepting G2 or runtime."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_patient_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_PATIENT_PREDECESSOR_POLICY[path],
              "bounded_g2_patient_prior_policy_changed")
    _need(scope.get("schema_version") == G2_PATIENT_SCOPE_VERSION, "bounded_g2_patient_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_patient_binding_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_patient_binding_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_atomicity_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate atomic consultation persistence without accepting G2 or runtime."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_atomicity_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_ATOMICITY_PREDECESSOR_POLICY[path],
              "bounded_g2_atomicity_prior_policy_changed")
    _need(scope.get("schema_version") == G2_ATOMICITY_SCOPE_VERSION, "bounded_g2_atomicity_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_consultation_atomicity_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_consultation_atomicity_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}

def build_g2_clinical_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate only the owner-scoped clinical repair; preserve historical gates."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_clinical_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_CLINICAL_PREDECESSOR_POLICY[path],
              "bounded_g2_clinical_prior_policy_changed")
    _need(scope.get("schema_version") == G2_CLINICAL_SCOPE_VERSION, "bounded_g2_clinical_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_clinical_authority_repair_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_clinical_authority_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_migration_guard_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Preserve accepted historical state; replace only the active repair lane."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_migration_guard_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_MIGRATION_GUARD_PREDECESSOR_POLICY[path],
              "bounded_g2_migration_guard_prior_policy_changed")
    _need(scope.get("schema_version") == G2_MIGRATION_GUARD_SCOPE_VERSION,
          "bounded_g2_migration_guard_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_migration_downgrade_guard_active")
    overlay["profiles"][G2_PROFILE] = raisa_policy.g2_migration_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_appointment_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Replace only the active G2 lane; preserve gates and consumed V9 history."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_appointment_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes and _sha(before[path]) == G2_APPOINTMENT_PREDECESSOR_POLICY[path],
              "bounded_g2_appointment_prior_policy_changed")
    _need(scope.get("schema_version") == G2_APPOINTMENT_SCOPE_VERSION,
          "bounded_g2_appointment_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw), current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_appointment_concurrency_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_appointment_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_production_profile_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Replace the active G2 lane without changing AGENTS, gates or consumed history."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_production_profile_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY[path],
              "bounded_g2_production_profile_prior_policy_changed")
    _need(scope.get("schema_version") == G2_PRODUCTION_PROFILE_SCOPE_VERSION,
          "bounded_g2_production_profile_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(
        next_eligibility_condition="bounded_G2_production_profile_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_production_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_dependency_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Replace the active G2 lane while retaining gates and consumed history."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_dependency_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_DEPENDENCY_PREDECESSOR_POLICY[path],
              "bounded_g2_dependency_prior_policy_changed")
    _need(scope.get("schema_version") == G2_DEPENDENCY_SCOPE_VERSION,
          "bounded_g2_dependency_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_dependency_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_dependency_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_ci_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate only CI selection; retain accepted history and G2 closures."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_ci_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_CI_PREDECESSOR_POLICY[path],
              "bounded_g2_ci_prior_policy_changed")
    _need(scope.get("schema_version") == G2_CI_SCOPE_VERSION,
          "bounded_g2_ci_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_ci_selection_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_ci_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def _batch_publication(target: Path, publication: dict, base: str) -> None:
    headers = trusted_git.run_git(target, "cat-file", "commit", publication["commit"]).split("\n\n", 1)[0].splitlines()
    _need([line for line in headers if line.startswith("parent ")] == ["parent " + publication["parent"]]
          and [line for line in headers if line.startswith("tree ")] == ["tree " + publication["tree"]],
          "bounded_g2_batch_publication_invalid")
    trusted_git.run_git(target, "merge-base", "--is-ancestor", publication["commit"], base)


def _validate_g2_audio_trusted_git_publication(target: Path, base: str) -> None:
    _batch_publication(target, G2_AUDIO_TRUSTED_GIT_PUBLICATION, base)
    for path, digest in G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256.items():
        raw = trusted_git.run_git_bytes(
            target, "cat-file", "blob", G2_AUDIO_TRUSTED_GIT_PUBLICATION["commit"] + ":" + path)
        _need(_sha(raw) == digest, "bounded_g2_audio_trusted_git_publication_bytes_changed")


def _validate_g2_audio_instructions_publication(target: Path, base: str) -> None:
    _batch_publication(target, G2_AUDIO_INSTRUCTIONS_PUBLICATION, base)
    for commit, digest in (
        (G2_AUDIO_INSTRUCTIONS_PUBLICATION["parent"], G2_INSTRUCTIONS_SHA256),
        (G2_AUDIO_INSTRUCTIONS_PUBLICATION["commit"], G2_AUDIO_INSTRUCTIONS_SHA256),
    ):
        raw = trusted_git.run_git_bytes(target, "cat-file", "blob", commit + ":" + AGENTS)
        _need(_sha(raw) == digest, "bounded_g2_audio_instructions_publication_bytes_changed")


def _validate_g2_patient_audio_publication(target: Path, base: str) -> None:
    _batch_publication(target, G2_AUDIO_REPAIR_PUBLICATION, base)
    for path, digest in G2_AUDIO_REPAIR_SOURCE_SHA256.items():
        raw = trusted_git.run_git_bytes(
            target, "cat-file", "blob", G2_AUDIO_REPAIR_PUBLICATION["commit"] + ":" + path)
        _need(_sha(raw) == digest, "bounded_g2_patient_audio_publication_bytes_changed")


def _validate_g2_atomicity_patient_publication(target: Path, base: str) -> None:
    _batch_publication(target, G2_PATIENT_REPAIR_PUBLICATION, base)
    for path, digest in G2_PATIENT_REPAIR_SOURCE_SHA256.items():
        raw = trusted_git.run_git_bytes(
            target, "cat-file", "blob", G2_PATIENT_REPAIR_PUBLICATION["commit"] + ":" + path)
        _need(_sha(raw) == digest, "bounded_g2_atomicity_patient_publication_bytes_changed")

def _validate_g2_clinical_atomicity_publication(target: Path, base: str) -> None:
    _batch_publication(target, G2_ATOMICITY_REPAIR_PUBLICATION, base)
    for path, digest in G2_ATOMICITY_REPAIR_SOURCE_SHA256.items():
        raw = trusted_git.run_git_bytes(
            target, "cat-file", "blob", G2_ATOMICITY_REPAIR_PUBLICATION["commit"] + ":" + path)
        _need(_sha(raw) == digest, "bounded_g2_clinical_atomicity_publication_bytes_changed")


def _load_g2_batch_inputs(context, target, source, evidence_root, scratch, binding, read, snapshots):
    """The caller digest authenticates the binding before any selected input read."""
    _keys(binding, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
                    "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
                    "activation_commit", "installed_controller", "repair_sha256"},
          "bounded_g2_batch_binding_schema")
    six_file = binding["schema_version"] == G2_SIX_BINDING_VERSION
    transport = binding["schema_version"] == G2_TRANSPORT_BINDING_VERSION
    catalogue = binding["schema_version"] == G2_CATALOGUE_BINDING_VERSION
    instructions = binding["schema_version"] == G2_INSTRUCTIONS_BINDING_VERSION
    migration = instructions or binding["schema_version"] == G2_MIGRATION_BINDING_VERSION
    audio = binding["schema_version"] == G2_AUDIO_BINDING_VERSION
    patient = binding["schema_version"] == G2_PATIENT_BINDING_VERSION
    atomicity = binding["schema_version"] == G2_ATOMICITY_BINDING_VERSION
    clinical = binding["schema_version"] == G2_CLINICAL_BINDING_VERSION
    guard = binding["schema_version"] == G2_MIGRATION_GUARD_BINDING_VERSION
    appointment = binding["schema_version"] == G2_APPOINTMENT_BINDING_VERSION
    production = binding["schema_version"] == G2_PRODUCTION_PROFILE_BINDING_VERSION
    pyjwt = binding["schema_version"] == G2_PYJWT_BINDING_VERSION
    dependency = pyjwt or binding["schema_version"] == G2_DEPENDENCY_BINDING_VERSION
    ci = binding["schema_version"] == G2_CI_BINDING_VERSION
    cim = binding["schema_version"] == G2_CIM_BINDING_VERSION
    tenant = binding["schema_version"] == G2_TENANT_BINDING_VERSION
    relationship = binding["schema_version"] == G2_RELATIONSHIP_BINDING_VERSION
    completeness = binding["schema_version"] == G2_COMPLETENESS_BINDING_VERSION
    post_audio = six_file or transport or audio or patient or atomicity or clinical or guard or appointment or production or dependency or ci or cim or tenant or relationship or completeness
    version_kinds = {
        G2_BATCH_BINDING_VERSION: {"enable_g2_batches", "repair_g2_batch"},
        G2_CATALOGUE_BINDING_VERSION: {"extend_g2_catalogue", "repair_g2_batch"},
        G2_MIGRATION_BINDING_VERSION: {"enable_g2_migration", "repair_g2_migration"},
        G2_INSTRUCTIONS_BINDING_VERSION: {"align_g2_instructions", "repair_g2_migration"},
        G2_AUDIO_BINDING_VERSION: {"enable_g2_audio_privacy", "repair_g2_audio_privacy"},
        G2_PATIENT_BINDING_VERSION: {"enable_g2_patient_binding", "repair_g2_patient_binding"},
        G2_ATOMICITY_BINDING_VERSION: {"enable_g2_consultation_atomicity", "repair_g2_consultation_atomicity"},
        G2_CLINICAL_BINDING_VERSION: {"enable_g2_clinical_authority", "repair_g2_clinical_authority"},
        G2_MIGRATION_GUARD_BINDING_VERSION: {"enable_g2_migration_downgrade_guard", "repair_g2_migration_downgrade_guard"},
        G2_APPOINTMENT_BINDING_VERSION: {"enable_g2_appointment_concurrency", "repair_g2_appointment_concurrency"},
        G2_PRODUCTION_PROFILE_BINDING_VERSION: {"enable_g2_production_profile", "repair_g2_production_profile"},
        G2_DEPENDENCY_BINDING_VERSION: {"enable_g2_dependency_repair", "repair_g2_dependency_repair"},
        G2_CI_BINDING_VERSION: {"enable_g2_ci_selection", "repair_g2_ci_selection"},
        G2_CIM_BINDING_VERSION: {"enable_g2_ci_migration", "repair_g2_ci_migration"},
        G2_TENANT_BINDING_VERSION: {"enable_g2_tenant_migration", "repair_g2_tenant_migration"},
        G2_RELATIONSHIP_BINDING_VERSION: {"enable_g2_tenant_relationships", "repair_g2_tenant_relationships"},
        G2_COMPLETENESS_BINDING_VERSION: {"enable_g2_ci_completeness", "repair_g2_ci_completeness"},
        G2_PYJWT_BINDING_VERSION: {"enable_g2_pyjwt_repair", "repair_g2_pyjwt_repair"},
        G2_TRANSPORT_BINDING_VERSION: {"enable_g2_transport_repair", "repair_g2_transport_repair"},
        G2_SIX_BINDING_VERSION: {"enable_g2_six_file_repair", "repair_g2_six_file_repair"},
    }
    _need(binding["operation_kind"] in version_kinds.get(binding["schema_version"], set()),
          "bounded_g2_batch_binding_version")
    changes = _batch_changes(binding)
    input_paths = batch_input_paths(binding)
    maintenance = binding["operation_kind"] in G2_MAINTENANCE_KINDS
    if six_file and maintenance:
        _need(binding["base_commit"] == G2_SIX_PREDECESSOR["commit"],
              "bounded_g2_six_file_transition_base")
    if transport and maintenance:
        _need(binding["base_commit"] == G2_TRANSPORT_PREDECESSOR["commit"],
              "bounded_g2_transport_transition_base")
    if guard and maintenance:
        _need(binding["base_commit"] == G2_MIGRATION_GUARD_PREDECESSOR["commit"],
              "bounded_g2_migration_guard_transition_base")
    if appointment and maintenance:
        _need(binding["base_commit"] == G2_APPOINTMENT_PREDECESSOR["commit"],
              "bounded_g2_appointment_transition_base")
    if production and maintenance:
        _need(binding["base_commit"] == G2_PRODUCTION_PROFILE_PREDECESSOR["commit"],
              "bounded_g2_production_profile_transition_base")
    if cim and maintenance:
        _need(binding["base_commit"] == G2_CIM_PREDECESSOR["commit"],
              "bounded_g2_cim_transition_base")
    if tenant and maintenance:
        _need(binding["base_commit"] == G2_TENANT_PREDECESSOR["commit"],
              "bounded_g2_tenant_transition_base")
    if relationship and maintenance:
        _need(binding["base_commit"] == G2_RELATIONSHIP_PREDECESSOR["commit"],
              "bounded_g2_relationship_transition_base")
    if completeness and maintenance:
        _need(binding["base_commit"] == G2_COMPLETENESS_PREDECESSOR["commit"],
              "bounded_g2_completeness_transition_base")
    if ci and maintenance:
        _need(binding["base_commit"] == G2_CI_PREDECESSOR["commit"],
              "bounded_g2_ci_transition_base")
    if dependency and maintenance:
        _need(binding["base_commit"] == (G2_PYJWT_PREDECESSOR if pyjwt else G2_DEPENDENCY_PREDECESSOR)["commit"],
              "bounded_g2_dependency_transition_base")
    _need(type(binding["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", binding["operation_id"]),
          "bounded_g2_batch_operation_id")
    _need(binding["phase"] in {"development", "pre-push", "post-push"}, "bounded_g2_batch_phase")
    _need(all(type(binding[k]) is str and re.fullmatch(r"[0-9a-f]{40}", binding[k])
              for k in ("base_commit", "base_tree", "expected_head", "expected_index_tree", "candidate_tree")),
          "bounded_g2_batch_git_binding")
    source_pins = _digest_map(binding["source_sha256"], SOURCE_PATHS, "bounded_g2_batch_source_paths")
    payload_pins = _digest_map(binding["payload_sha256"], input_paths, "bounded_g2_batch_payload_paths")
    expected_git_source = (G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256["orchestration_harness/trusted_git.py"]
                           if post_audio else
                           "5f8bfd44b63282e205a22bef1b81d0b8b5271572ba47c5b5df7371c0f638874f")
    _need(source_pins["orchestration_harness/trusted_git.py"] == expected_git_source,
          "bounded_g1b_git_source_changed")
    source_payloads = {path: read(source / path, digest) for path, digest in source_pins.items()}
    payloads = {path: read(target / path, digest) for path, digest in sorted(payload_pins.items())}
    scope = _json(payloads[G2_SCOPE])
    _need((scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION) == catalogue,
          "bounded_g2_catalogue_scope_binding_mismatch")
    _need((scope.get("schema_version") in {G2_MIGRATION_SCOPE_VERSION, G2_INSTRUCTIONS_SCOPE_VERSION}) == migration,
          "bounded_g2_migration_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_INSTRUCTIONS_SCOPE_VERSION) == instructions,
          "bounded_g2_instructions_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_AUDIO_SCOPE_VERSION) == audio,
          "bounded_g2_audio_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_PATIENT_SCOPE_VERSION) == patient,
          "bounded_g2_patient_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_ATOMICITY_SCOPE_VERSION) == atomicity,
          "bounded_g2_atomicity_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_CLINICAL_SCOPE_VERSION) == clinical,
          "bounded_g2_clinical_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_MIGRATION_GUARD_SCOPE_VERSION) == guard,
          "bounded_g2_migration_guard_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_APPOINTMENT_SCOPE_VERSION) == appointment,
          "bounded_g2_appointment_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_PRODUCTION_PROFILE_SCOPE_VERSION) == production,
          "bounded_g2_production_profile_scope_binding_mismatch")
    _need((scope.get("schema_version") == (G2_PYJWT_SCOPE_VERSION if pyjwt else G2_DEPENDENCY_SCOPE_VERSION)) == dependency,
          "bounded_g2_dependency_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_CI_SCOPE_VERSION) == ci,
          "bounded_g2_ci_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_CIM_SCOPE_VERSION) == cim,
          "bounded_g2_cim_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_TENANT_SCOPE_VERSION) == tenant,
          "bounded_g2_tenant_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_RELATIONSHIP_SCOPE_VERSION) == relationship,
          "bounded_g2_relationship_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_COMPLETENESS_SCOPE_VERSION) == completeness,
          "bounded_g2_completeness_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_TRANSPORT_SCOPE_VERSION) == transport,
          "bounded_g2_transport_scope_binding_mismatch")
    _need((scope.get("schema_version") == G2_SIX_SCOPE_VERSION) == six_file,
          "bounded_g2_six_file_scope_binding_mismatch")
    _validate_g2_batch_scope(scope)
    frozen = {**FROZEN_PINS, COST: COST_PIN, SCOPE_PATH: G1B_BASELINE_PINS[SCOPE_PATH],
              G1C_SCOPE: G1C_BASELINE_PINS[G1C_SCOPE], G1D_SCOPE: G1D_BASELINE_PINS[G1D_SCOPE],
              G1E_SCOPE: G1E_BASELINE_PINS[G1E_SCOPE], **GOVERNOR_PINS, **PROVENANCE_DEPENDENCY_PINS,
              **PROVENANCE_PINS, **CONFIGURATION_LEAF_PINS,
                 AGENTS: (G2_SIX_PREDECESSOR_POLICY[AGENTS] if six_file else G2_TRANSPORT_PREDECESSOR_POLICY[AGENTS] if transport else G2_PRODUCTION_PROFILE_INSTRUCTIONS_SHA256 if production or dependency or ci or cim or tenant or relationship or completeness
                       else G2_APPOINTMENT_INSTRUCTIONS_SHA256 if appointment
                       else G2_MIGRATION_GUARD_INSTRUCTIONS_SHA256 if guard
                       else G2_AUDIO_INSTRUCTIONS_SHA256 if post_audio else
                       G2_INSTRUCTIONS_SHA256 if instructions else G2_INITIAL_POLICY_PINS[AGENTS]),
              GATES: G2_INITIAL_POLICY_PINS[GATES]}
    _need(all(_sha(payloads[path]) == digest for path, digest in frozen.items()),
          "bounded_g2_batch_frozen_input_changed")
    evidence = {path: read(evidence_root / path, digest) for path, digest in G1E_EVIDENCE_PINS.items()}
    base = binding["base_commit"]
    initial_policy = {}
    for publication, pins in (
        (G1E_PUBLICATION, G1E_SOURCE_PINS), (G1E_ACTIVATION, G1E_BASELINE_PINS),
        (G2_INITIAL_CONTROLLER, G2_INITIAL_CONTROLLER["source_sha256"]),
        (G2_INITIAL_ACTIVATION, G2_INITIAL_POLICY_PINS),
        (G2_INITIAL_REPAIR, {p: row["after_sha256"] for p, row in G2_REPAIR_PINS.items()}),
    ):
        _batch_publication(target, publication, base)
        for path, digest in pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", publication["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_batch_historical_bytes_changed")
            if publication is G2_INITIAL_ACTIVATION:
                initial_policy[path] = raw
    legacy_before = {path: read(source / "g1e-baseline" / path, digest)
                     for path, digest in G1E_BASELINE_PINS.items()}
    validate_g2_acceptance_transition(legacy_before, initial_policy, evidence)
    if migration or post_audio:
        owner_path = raisa_policy.G2_MIGRATION_OWNER_RECORD
        evidence[owner_path] = read(evidence_root / owner_path, raisa_policy.G2_MIGRATION_OWNER_SHA256)
    if clinical or guard or appointment or production or dependency or ci or cim or tenant or relationship or completeness:
        owner_path = raisa_policy.G2_CLINICAL_OWNER_RECORD
        evidence[owner_path] = read(evidence_root / owner_path, raisa_policy.G2_CLINICAL_OWNER_SHA256)
    if transport or six_file:
        evidence[G2_TRANSPORT_OWNER_RECORD] = read(evidence_root / G2_TRANSPORT_OWNER_RECORD,
                                                  G2_TRANSPORT_OWNER_SHA256)
    prior_policy = initial_policy
    if catalogue or migration or post_audio:
        _batch_publication(target, G2_CATALOGUE_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_CATALOGUE_PREDECESSOR_POLICY,
                             **G2_CATALOGUE_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_CATALOGUE_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_catalogue_predecessor_bytes_changed")
            if path in G2_CATALOGUE_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if migration or post_audio:
        _batch_publication(target, G2_MIGRATION_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_MIGRATION_PREDECESSOR_POLICY,
                             **G2_MIGRATION_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_MIGRATION_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_migration_predecessor_bytes_changed")
            if path in G2_MIGRATION_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if instructions or post_audio:
        _batch_publication(target, G2_INSTRUCTIONS_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_INSTRUCTIONS_PREDECESSOR_POLICY,
                             **G2_INSTRUCTIONS_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_INSTRUCTIONS_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_instructions_predecessor_bytes_changed")
            if path in G2_INSTRUCTIONS_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        _batch_publication(target, G2_INSTRUCTIONS_PUBLICATION, base)
        for commit, digest in ((G2_INSTRUCTIONS_PUBLICATION["parent"], G2_INITIAL_POLICY_PINS[AGENTS]),
                               (G2_INSTRUCTIONS_PUBLICATION["commit"], G2_INSTRUCTIONS_SHA256)):
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", commit + ":" + AGENTS)
            _need(_sha(raw) == digest, "bounded_g2_instructions_publication_bytes_changed")
    if post_audio:
        _batch_publication(target, G2_AUDIO_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_AUDIO_PREDECESSOR_POLICY,
                             **G2_AUDIO_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_AUDIO_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_audio_predecessor_bytes_changed")
            if path in G2_AUDIO_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        _validate_g2_audio_trusted_git_publication(target, base)
        _validate_g2_audio_instructions_publication(target, base)
    if patient or atomicity or clinical or guard or appointment or production or dependency:
        _batch_publication(target, G2_PATIENT_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_PATIENT_PREDECESSOR_POLICY,
                             **G2_PATIENT_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_PATIENT_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_patient_predecessor_bytes_changed")
            if path in G2_PATIENT_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        _validate_g2_patient_audio_publication(target, base)
    if atomicity or clinical or guard or appointment or production or dependency:
        _batch_publication(target, G2_ATOMICITY_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_ATOMICITY_PREDECESSOR_POLICY,
                             **G2_ATOMICITY_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_ATOMICITY_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_atomicity_predecessor_bytes_changed")
            if path in G2_ATOMICITY_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        _validate_g2_atomicity_patient_publication(target, base)
    if clinical or guard or appointment or production or dependency:
        _batch_publication(target, G2_CLINICAL_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_CLINICAL_PREDECESSOR_POLICY,
                             **G2_CLINICAL_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_CLINICAL_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_clinical_predecessor_bytes_changed")
            if path in G2_CLINICAL_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        _validate_g2_clinical_atomicity_publication(target, base)
    if guard or appointment or production or dependency or ci or cim or tenant or relationship or completeness:
        _batch_publication(target, G2_MIGRATION_GUARD_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_MIGRATION_GUARD_PREDECESSOR_POLICY,
                             **G2_MIGRATION_GUARD_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_MIGRATION_GUARD_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_migration_guard_predecessor_bytes_changed")
            if path in G2_MIGRATION_GUARD_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if appointment or production or dependency or ci or cim or tenant or relationship or completeness:
        _batch_publication(target, G2_APPOINTMENT_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_APPOINTMENT_PREDECESSOR_POLICY,
                             **G2_APPOINTMENT_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_APPOINTMENT_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_appointment_predecessor_bytes_changed")
            if path in G2_APPOINTMENT_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if production or dependency or ci or cim or tenant or relationship or completeness:
        _batch_publication(target, G2_PRODUCTION_PROFILE_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {
            **G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY,
            **G2_PRODUCTION_PROFILE_PREDECESSOR["source_sha256"],
            **{path: digest for path, digest in G2_PRODUCTION_PROFILE_REPAIR_PINS.items()
               if digest is not None},
        }
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_PRODUCTION_PROFILE_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest,
                  "bounded_g2_production_profile_predecessor_bytes_changed")
            if path in G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if dependency or ci or cim or tenant or relationship or completeness:
        _batch_publication(target, G2_DEPENDENCY_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {
            **G2_DEPENDENCY_PREDECESSOR_POLICY,
            **G2_DEPENDENCY_PREDECESSOR["source_sha256"],
            **{path: digest for path, digest in G2_DEPENDENCY_REPAIR_PINS.items()
               if digest is not None},
        }
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_DEPENDENCY_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_dependency_predecessor_bytes_changed")
            if path in G2_DEPENDENCY_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if ci or cim or tenant or relationship or completeness:
        _batch_publication(target, G2_CI_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {**G2_CI_PREDECESSOR_POLICY,
                            **G2_CI_PREDECESSOR["source_sha256"],
                            **G2_CI_REPAIR_PINS}
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_CI_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_ci_predecessor_bytes_changed")
            if path in G2_CI_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if cim or tenant or relationship or completeness:
        _batch_publication(target, G2_CIM_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {**G2_CIM_PREDECESSOR_POLICY,
                            **G2_CIM_PREDECESSOR["source_sha256"],
                            **G2_CIM_REPAIR_PINS}
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_CIM_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_cim_predecessor_bytes_changed")
            if path in G2_CIM_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if tenant or relationship or completeness:
        _batch_publication(target, G2_TENANT_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {**G2_TENANT_PREDECESSOR_POLICY,
                            **G2_TENANT_PREDECESSOR["source_sha256"]}
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_TENANT_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_tenant_predecessor_bytes_changed")
            if path in G2_TENANT_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if relationship or completeness:
        _batch_publication(target, G2_RELATIONSHIP_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {**G2_RELATIONSHIP_PREDECESSOR_POLICY,
                            **G2_RELATIONSHIP_PREDECESSOR["source_sha256"],
                            **G2_RELATIONSHIP_PRESERVED_TENANT_PINS}
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_RELATIONSHIP_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_relationship_predecessor_bytes_changed")
            if path in G2_RELATIONSHIP_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if completeness:
        _batch_publication(target, G2_COMPLETENESS_PREDECESSOR, base)
        prior_policy = {}
        predecessor_pins = {**G2_COMPLETENESS_PREDECESSOR_POLICY,
                            **G2_COMPLETENESS_PREDECESSOR["source_sha256"],
                            **G2_COMPLETENESS_PRESERVED_RELATIONSHIP_PINS,
                            **G2_COMPLETENESS_REPAIR_PINS}
        for path, digest in predecessor_pins.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_COMPLETENESS_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_completeness_predecessor_bytes_changed")
            if path in G2_COMPLETENESS_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if pyjwt:
        _batch_publication(target, G2_PYJWT_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_PYJWT_PREDECESSOR_POLICY,
                             **G2_PYJWT_PREDECESSOR["source_sha256"],
                             **G2_PYJWT_REPAIR_PINS}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_PYJWT_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_pyjwt_predecessor_bytes_changed")
            if path in G2_PYJWT_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if transport or six_file:
        _batch_publication(target, G2_TRANSPORT_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_TRANSPORT_PREDECESSOR_POLICY,
                             **G2_TRANSPORT_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_TRANSPORT_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_transport_predecessor_bytes_changed")
            if path in G2_TRANSPORT_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    if six_file:
        _batch_publication(target, G2_SIX_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_SIX_PREDECESSOR_POLICY,
                             **G2_SIX_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob",
                G2_SIX_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_six_file_predecessor_bytes_changed")
            if path in G2_SIX_PREDECESSOR_POLICY:
                prior_policy[path] = raw
        for path, digest in G2_SIX_PUBLICATION_REVIEW_PINS.items():
            raw = read(evidence_root / path, digest)
            evidence[path] = raw
            review = _json(raw)
            verdict = ("PASS_ISOLATED_TRANSPORT_COMMIT_EFFECT" if "commit-effect" in path
                       else "PASS_ISOLATED_TRANSPORT_PUSH_EFFECT")
            _need(review.get("verdict") == verdict
                  and review.get("reviewer_agent") == "/root/g2_admission_review"
                  and review.get("independent") is True
                  and review.get("implementation_authorship") is False
                  and review.get("blocking_findings") == []
                  and all(review.get(key) == G2_SIX_PREDECESSOR[key]
                          for key in ("commit", "parent", "tree")),
                  "bounded_g2_six_file_predecessor_review_invalid")
    base_payloads = {}
    for path in sorted(input_paths):
        if path in changes and changes[path]["before_sha256"] is None:
            # Only the fixed reviewed additions reach this branch. Empty bytes
            # are present blobs; absence requires a successful literal-path query.
            _need(trusted_git.run_git_bytes(target, "ls-tree", "-z", base, "--", path) == b"",
                   "bounded_g2_relationship_addition_already_exists" if relationship
                   else "bounded_g2_tenant_addition_already_exists" if tenant
                   else "bounded_g2_dependency_addition_already_exists" if dependency
                  else "bounded_g2_production_profile_addition_already_exists" if production
                  else "bounded_g2_appointment_addition_already_exists" if appointment
                  else "bounded_g2_atomicity_addition_already_exists" if atomicity
                  else "bounded_g2_patient_addition_already_exists" if patient
                  else "bounded_g2_audio_addition_already_exists" if audio
                  else "bounded_g2_migration_addition_already_exists")
            base_payloads[path] = None
        else:
            base_payloads[path] = trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path)
    for path, raw in base_payloads.items():
        if path in changes:
            _need((None if raw is None else _sha(raw)) == changes[path]["before_sha256"],
                  "bounded_g2_batch_preimage_changed")
            _need(_sha(payloads[path]) == changes[path]["after_sha256"], "bounded_g2_batch_candidate_changed")
        else:
            _need(raw == payloads[path], "bounded_g2_batch_unowned_input_changed")
    controller = binding["installed_controller"]
    _validate_installed_controller(controller)
    _batch_publication(target, controller, base)
    if maintenance:
        expected_controller = (G2_SIX_PREDECESSOR if six_file else G2_TRANSPORT_PREDECESSOR if transport else G2_COMPLETENESS_PREDECESSOR if completeness
                                else G2_RELATIONSHIP_PREDECESSOR if relationship
                               else G2_TENANT_PREDECESSOR if tenant
                               else G2_CIM_PREDECESSOR if cim
                               else G2_CI_PREDECESSOR if ci
                               else (G2_PYJWT_PREDECESSOR if pyjwt else G2_DEPENDENCY_PREDECESSOR) if dependency
                               else G2_PRODUCTION_PROFILE_PREDECESSOR if production
                               else G2_APPOINTMENT_PREDECESSOR if appointment
                               else G2_MIGRATION_GUARD_PREDECESSOR if guard else G2_CLINICAL_PREDECESSOR if clinical
                               else G2_ATOMICITY_PREDECESSOR if atomicity
                               else G2_PATIENT_PREDECESSOR if patient else G2_AUDIO_PREDECESSOR if audio
                               else G2_INSTRUCTIONS_PREDECESSOR if instructions
                               else G2_MIGRATION_PREDECESSOR if migration else G2_CATALOGUE_PREDECESSOR if catalogue
                               else G2_INITIAL_CONTROLLER)
        expected_activation = (expected_controller["commit"] if catalogue or migration or post_audio
                               else G2_INITIAL_ACTIVATION["commit"])
        _need(controller == expected_controller and binding["activation_commit"] == expected_activation,
              "bounded_g2_batch_maintenance_predecessor")
        _need(scope["transition_base_commit"] == base, "bounded_g2_batch_maintenance_base")
        prior_pins = (G2_SIX_PREDECESSOR_POLICY if six_file else G2_TRANSPORT_PREDECESSOR_POLICY if transport else G2_COMPLETENESS_PREDECESSOR_POLICY if completeness
                       else G2_RELATIONSHIP_PREDECESSOR_POLICY if relationship
                      else G2_TENANT_PREDECESSOR_POLICY if tenant
                      else G2_CIM_PREDECESSOR_POLICY if cim
                      else G2_CI_PREDECESSOR_POLICY if ci
                      else (G2_PYJWT_PREDECESSOR_POLICY if pyjwt else G2_DEPENDENCY_PREDECESSOR_POLICY) if dependency
                      else G2_PRODUCTION_PROFILE_PREDECESSOR_POLICY if production
                      else G2_APPOINTMENT_PREDECESSOR_POLICY if appointment
                      else G2_MIGRATION_GUARD_PREDECESSOR_POLICY if guard
                      else {**G2_CLINICAL_PREDECESSOR_POLICY, AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256} if clinical
                      else {**G2_ATOMICITY_PREDECESSOR_POLICY, AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256} if atomicity
                      else {**G2_PATIENT_PREDECESSOR_POLICY, AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256} if patient
                      else {**G2_AUDIO_PREDECESSOR_POLICY, AGENTS: G2_AUDIO_INSTRUCTIONS_SHA256} if audio
                      else {**G2_INSTRUCTIONS_PREDECESSOR_POLICY, AGENTS: G2_INSTRUCTIONS_SHA256} if instructions
                      else G2_MIGRATION_PREDECESSOR_POLICY if migration else G2_CATALOGUE_PREDECESSOR_POLICY if catalogue
                      else G2_INITIAL_POLICY_PINS)
        for path, digest in prior_pins.items():
            _need(_sha(base_payloads[path]) == digest, "bounded_g2_batch_maintenance_policy_changed")
        if not catalogue and not migration and not post_audio:
            for path, row in G2_REPAIR_PINS.items():
                _need(_sha(base_payloads[path]) == row["after_sha256"], "bounded_g2_batch_first_repair_changed")
    else:
        activation = binding["activation_commit"]
        _need(type(activation) is str and activation == controller["commit"], "bounded_g2_batch_activation_binding")
        _need(controller["parent"] == scope["transition_base_commit"], "bounded_g2_batch_activation_parent")
        _need(controller["source_sha256"] == scope["controller_source_sha256"],
              "bounded_g2_batch_controller_disagreement")
        for path in G2_TRANSITION_PATHS:
            _need(trusted_git.run_git_bytes(target, "cat-file", "blob", activation + ":" + path) == payloads[path],
                  "bounded_g2_batch_activation_not_committed")
    for path in SOURCE_PATHS | CONTROLLER_PATHS:
        if path not in source_payloads:
            source_payloads[path] = read(source / path, scope["controller_source_sha256"][path])
        raw = source_payloads[path]
        _need(payloads.get(path, raw) == raw, "bounded_g2_batch_loaded_source_disagreement")
        if path in CONTROLLER_PATHS:
            _need(_sha(raw) == scope["controller_source_sha256"][path], "bounded_g2_batch_prospective_controller_changed")
            installed_raw = trusted_git.run_git_bytes(target, "cat-file", "blob", controller["commit"] + ":" + path)
            _need(_sha(installed_raw) == controller["source_sha256"][path], "bounded_g2_batch_installed_controller_changed")
            if maintenance:
                _need(_sha(base_payloads[path]) == controller["source_sha256"][path],
                      "bounded_g2_batch_prior_controller_not_installed")
        if not maintenance or path not in changes:
            _need(trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path) == raw,
                  "bounded_g2_batch_source_not_installed")
    attested = input_paths - set(changes) if binding["phase"] == "development" else input_paths
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=binding["expected_head"], expected_index_tree=binding["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", base + "^{tree}") == binding["base_tree"],
          "bounded_g2_batch_base_tree_changed")
    if binding["phase"] == "development":
        _need(binding["expected_head"] == base and binding["expected_index_tree"] in
              {binding["base_tree"], binding["candidate_tree"]}, "bounded_g2_batch_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", binding["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + base]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + binding["candidate_tree"]]
              and binding["expected_index_tree"] == binding["candidate_tree"], "bounded_g2_batch_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(binding, prior_policy, payloads, evidence, observation)


def build_g2_cim_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate only CI migration-helper repair; retain accepted history and G2 closures."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_cim_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_CIM_PREDECESSOR_POLICY[path],
              "bounded_g2_cim_prior_policy_changed")
    _need(scope.get("schema_version") == G2_CIM_SCOPE_VERSION,
          "bounded_g2_cim_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_ci_migration_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_cim_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_tenant_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate exactly the two tenant additions; preserve G2 and runtime closure."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_tenant_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_TENANT_PREDECESSOR_POLICY[path],
              "bounded_g2_tenant_prior_policy_changed")
    _need(scope.get("schema_version") == G2_TENANT_SCOPE_VERSION,
          "bounded_g2_tenant_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_tenant_migration_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_tenant_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_relationship_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate only the three relationship additions; retain all G2 closures."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_relationship_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_RELATIONSHIP_PREDECESSOR_POLICY[path],
              "bounded_g2_relationship_prior_policy_changed")
    _need(scope.get("schema_version") == G2_RELATIONSHIP_SCOPE_VERSION,
          "bounded_g2_relationship_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_tenant_relationship_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_relationship_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def build_g2_completeness_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Activate only three existing guard updates; retain every G2 closure."""
    _keys(before, G2_BATCH_CONTROL_PATHS, "bounded_g2_completeness_transition_paths")
    for path in G2_BATCH_CONTROL_PATHS:
        _need(type(before[path]) is bytes
              and _sha(before[path]) == G2_COMPLETENESS_PREDECESSOR_POLICY[path],
              "bounded_g2_completeness_prior_policy_changed")
    _need(scope.get("schema_version") == G2_COMPLETENESS_SCOPE_VERSION,
          "bounded_g2_completeness_scope_version")
    _validate_g2_batch_scope(scope)
    state = _json(before[STATE])
    overlay = _document(before[OVERLAY], OVERLAY)
    scope_raw = _canonical(scope) + b"\n"
    state["observed_at"] = scope["recorded_at"]
    state["g2"].update(scope_sha256=_sha(scope_raw),
                       current_operation=_json(_canonical(scope["current_operation"])))
    state["task_selection"].update(next_eligibility_condition="bounded_G2_ci_completeness_repair_active")
    overlay["profiles"][G2_PROFILE] = _g2_completeness_profile()
    return {STATE: (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            G2_SCOPE: scope_raw}


def _validate_g2_batch_loaded_policy(inputs):
    scope = _json(inputs.payloads[G2_SCOPE])
    builder = (build_g2_six_file_transition if scope.get("schema_version") == G2_SIX_SCOPE_VERSION else build_g2_transport_transition if scope.get("schema_version") == G2_TRANSPORT_SCOPE_VERSION else build_g2_pyjwt_transition if scope.get("schema_version") == G2_PYJWT_SCOPE_VERSION
               else build_g2_completeness_transition if scope.get("schema_version") == G2_COMPLETENESS_SCOPE_VERSION
               else build_g2_relationship_transition if scope.get("schema_version") == G2_RELATIONSHIP_SCOPE_VERSION
               else build_g2_tenant_transition if scope.get("schema_version") == G2_TENANT_SCOPE_VERSION
               else build_g2_cim_transition if scope.get("schema_version") == G2_CIM_SCOPE_VERSION
               else build_g2_ci_transition if scope.get("schema_version") == G2_CI_SCOPE_VERSION
               else build_g2_dependency_transition
               if scope.get("schema_version") == G2_DEPENDENCY_SCOPE_VERSION
               else build_g2_production_profile_transition
               if scope.get("schema_version") == G2_PRODUCTION_PROFILE_SCOPE_VERSION
               else build_g2_appointment_transition if scope.get("schema_version") == G2_APPOINTMENT_SCOPE_VERSION
               else build_g2_migration_guard_transition if scope.get("schema_version") == G2_MIGRATION_GUARD_SCOPE_VERSION
               else build_g2_clinical_transition if scope.get("schema_version") == G2_CLINICAL_SCOPE_VERSION
               else build_g2_atomicity_transition if scope.get("schema_version") == G2_ATOMICITY_SCOPE_VERSION
               else build_g2_patient_transition if scope.get("schema_version") == G2_PATIENT_SCOPE_VERSION
               else build_g2_audio_transition if scope.get("schema_version") == G2_AUDIO_SCOPE_VERSION
               else build_g2_instructions_transition if scope.get("schema_version") == G2_INSTRUCTIONS_SCOPE_VERSION
               else build_g2_migration_transition if scope.get("schema_version") == G2_MIGRATION_SCOPE_VERSION
               else build_g2_catalogue_transition if scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION
               else build_g2_batch_transition)
    expected = builder({p: inputs.before[p] for p in G2_BATCH_CONTROL_PATHS}, scope)
    _need(all(inputs.payloads[p] == raw for p, raw in expected.items()), "bounded_g2_batch_policy_delta_invalid")
    after = {p: inputs.payloads[p] for p in G2_TRANSITION_PATHS}
    try:
        configuration = raisa_policy.validate_recovery_configuration(
            documents={Path(p).name: inputs.payloads[p] for p in CONFIGURATION_PATHS},
            expected_sha256={Path(p).name: inputs.binding["payload_sha256"][p] for p in CONFIGURATION_PATHS},
            agents_text=after[AGENTS].decode("utf-8"), state=_json(after[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    return after, configuration


def load_bounded_g1b_inputs(context: BoundedG1BContext) -> BoundedG1BInputs:
    """Read authenticated ordinary inputs; expected digest is caller authority."""
    _need(type(context) is BoundedG1BContext, "bounded_g1b_context_required")
    for path in (context.target_root, context.source_root, context.evidence_root,
                 context.scratch_root, context.binding_path):
        trusted_git._validate_path_components(path.absolute())
    target, source, evidence_root, scratch = (p.resolve(strict=True) for p in
        (context.target_root, context.source_root, context.evidence_root, context.scratch_root))
    _need(all(p != target and not p.is_relative_to(target) and not target.is_relative_to(p)
              for p in (source, evidence_root, scratch)), "bounded_g1b_external_roots_required")
    administration = trusted_git._physical_git_administration(target)
    _need(all(a != b and not a.is_relative_to(b) and not b.is_relative_to(a)
              for a in (source, evidence_root, scratch)
              for b in (administration["gitdir"], administration["commondir"])),
          "bounded_g1b_roots_overlap_git_administration")
    _need(scratch != source and not scratch.is_relative_to(source) and not source.is_relative_to(scratch),
          "bounded_g1b_scratch_overlaps_source")
    _need(Path(__file__).resolve() == source / "orchestration_harness/bounded_g1b.py"
          and Path(trusted_git.__file__).resolve() == source / "orchestration_harness/trusted_git.py"
          and Path(configuration_core.__file__).resolve() == source / "orchestration_harness/configuration_core.py"
          and Path(raisa_policy.__file__).resolve() == source / "orchestration_harness/raisa_policy.py",
          "bounded_g1b_source_not_isolated")
    binding_path = context.binding_path.resolve(strict=True)
    _need(binding_path != target and not binding_path.is_relative_to(target),
          "bounded_g1b_binding_inside_target")
    _need(all(not binding_path.is_relative_to(p) for p in
              (administration["gitdir"], administration["commondir"])), "bounded_g1b_binding_inside_git")
    snapshots = {}

    def read(path: Path, expected: str) -> bytes:
        snapshot = trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024)
        _need(_sha(snapshot[1]) == expected, "bounded_g1b_input_digest_changed")
        snapshots[path] = snapshot
        return snapshot[1]

    binding = _json(read(binding_path, context.expected_binding_sha256))
    if binding.get("operation_kind") == G2_CI_RESEAL_KIND:
        return _load_g2_ci_reseal_inputs(context, target, source, evidence_root, scratch,
                                         binding, read, snapshots)
    if binding.get("operation_kind") == G2_CLOSEOUT_CI_KIND:
        return _load_g2_ci_adoption_inputs(context, target, source, evidence_root, scratch, binding, read, snapshots)
    if binding.get("operation_kind") == G2_CLOSEOUT_ENABLE_KIND:
        return _load_g2_closeout_enable_inputs(context, target, source, evidence_root, scratch,
                                              binding, read, snapshots)
    if binding.get("operation_kind") == G2_CLOSEOUT_KIND:
        return _load_g2_closeout_inputs(context, target, source, evidence_root, scratch,
                                       binding, read, snapshots)
    if type(binding.get("operation_kind")) is str and binding["operation_kind"] in G2_BATCH_KINDS:
        return _load_g2_batch_inputs(context, target, source, evidence_root, scratch,
                                     binding, read, snapshots)
    _keys(binding, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
                    "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
                    "activation_commit", "installed_controller"},
          "bounded_g1b_binding_schema")
    _need(binding["schema_version"] == BINDING_VERSION, "bounded_g1b_binding_version")
    operation = _operation(binding["operation_kind"])
    _need(type(binding["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", binding["operation_id"]),
          "bounded_g1b_operation_id")
    _need(binding["phase"] in ({"assessment"} if operation.get("assessment")
                              else {"development", "pre-push", "post-push"}), "bounded_g1b_phase")
    if operation["gate"] in {"G1E", "G2"}:
        _validate_installed_controller(binding["installed_controller"])
    else:
        _need(binding["installed_controller"] is None, "bounded_g1e_unexpected_installed_controller")
    _need(all(type(binding[k]) is str and re.fullmatch(r"[0-9a-f]{40}", binding[k])
              for k in ("base_commit", "base_tree", "expected_head", "expected_index_tree", "candidate_tree")),
          "bounded_g1b_git_binding")
    source_pins = _digest_map(binding["source_sha256"], SOURCE_PATHS, "bounded_g1b_source_paths")
    payload_pins = _digest_map(binding["payload_sha256"], operation["input_paths"], "bounded_g1b_payload_paths")
    source_payloads = {path: read(source / path, digest) for path, digest in source_pins.items()}
    _need(source_pins["orchestration_harness/trusted_git.py"] ==
          "5f8bfd44b63282e205a22bef1b81d0b8b5271572ba47c5b5df7371c0f638874f", "bounded_g1b_git_source_changed")
    before = {path: read(source / operation["baseline_directory"] / path, digest)
              for path, digest in operation["baseline_pins"].items()}
    payloads = {path: read(target / path, payload_pins[path]) for path in sorted(operation["input_paths"])}
    frozen_pins = dict(FROZEN_PINS)
    if operation["successor"]:
        frozen_pins.update({COST: COST_PIN, SCOPE_PATH: G1B_BASELINE_PINS[SCOPE_PATH]})
    if operation["gate"] in {"G1D", "G1E", "G2"}:
        frozen_pins.update({G1C_SCOPE: G1C_BASELINE_PINS[G1C_SCOPE], **GOVERNOR_PINS, **PROVENANCE_DEPENDENCY_PINS})
    if operation["gate"] in {"G1E", "G2"}:
        frozen_pins.update({G1D_SCOPE: G1D_BASELINE_PINS[G1D_SCOPE], **PROVENANCE_PINS, **CONFIGURATION_LEAF_PINS})
    if operation["gate"] == "G2":
        frozen_pins[G1E_SCOPE] = G1E_BASELINE_PINS[G1E_SCOPE]
    for path, digest in frozen_pins.items():
        _need(_sha(payloads[path]) == digest, "bounded_g1b_frozen_input_changed")
    evidence = {path: read(evidence_root / path, digest) for path, digest in operation["evidence_pins"].items()}
    base = binding["base_commit"]
    if operation["successor"]:
        publication = operation["accepted_publication"]
        accepted = publication["commit"]
        headers = trusted_git.run_git(target, "cat-file", "commit", accepted).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] ==
              ["parent " + publication["parent"]]
              and [line for line in headers if line.startswith("tree ")] ==
              ["tree " + publication["tree"]], operation["component_reason"] + "_component_publication_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", accepted, base)
        for path, digest in operation["accepted_pins"].items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", accepted + ":" + path)) == digest,
                  operation["component_reason"] + "_accepted_component_changed")
    if operation["gate"] == "G2":
        accepted_activation = G1E_ACTIVATION["commit"]
        headers = trusted_git.run_git(target, "cat-file", "commit", accepted_activation).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + G1E_ACTIVATION["parent"]]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + G1E_ACTIVATION["tree"]],
              "bounded_g2_accepted_activation_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", accepted_activation, base)
        for path, digest in G1E_BASELINE_PINS.items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", accepted_activation + ":" + path)) == digest,
                  "bounded_g2_assessed_authority_changed")
        for path, pins in G2_REPAIR_PINS.items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path)) == pins["before_sha256"],
                  "bounded_g2_fixture_predecessor_changed")
            expected = pins["before_sha256"] if operation["transition"] else pins["after_sha256"]
            _need(_sha(payloads[path]) == expected, "bounded_g2_fixture_candidate_changed")
    if operation["gate"] in {"G1E", "G2"}:
        controller = binding["installed_controller"]
        installed = controller["commit"]
        headers = trusted_git.run_git(target, "cat-file", "commit", installed).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + controller["parent"]]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + controller["tree"]],
              "bounded_g1e_controller_publication_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", installed, base)
        if operation["transition"]:
            _need(installed == base, "bounded_g1e_controller_must_precede_activation")
        for path, digest in controller["source_sha256"].items():
            _need(_sha(payloads[path]) == digest, "bounded_g1e_installed_controller_changed")
            if path in source_pins:
                _need(source_pins[path] == digest, "bounded_g1e_loaded_controller_disagreement")
            else:
                source_payloads[path] = read(source / path, digest)
        for path, raw in source_payloads.items():
            for commit in sorted({installed, base}):
                _need(trusted_git.run_git_bytes(target, "cat-file", "blob", commit + ":" + path) == raw,
                      "bounded_g1e_controller_source_not_installed")
    if operation["transition"]:
        _need(binding["activation_commit"] is None, "bounded_g1b_premature_activation")
        for path, digest in operation["baseline_pins"].items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path)) == digest,
                  "bounded_g1b_actual_predecessor_changed")
        _need(trusted_git.run_git_bytes(target, "ls-tree", "-z", base, "--", operation["scope_path"]) == b"",
              "bounded_g1b_predecessor_already_active")
    else:
        activation = binding["activation_commit"]
        _need(type(activation) is str and re.fullmatch(r"[0-9a-f]{40}", activation),
              "bounded_g1b_activation_binding_required")
        scope = _json(payloads[operation["scope_path"]])
        headers = trusted_git.run_git(target, "cat-file", "commit", activation).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] ==
              ["parent " + scope["transition_base_commit"]], "bounded_g1b_activation_parent_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", activation, base)
        for path in operation["transition_paths"]:
            for commit in (activation, base):
                _need(trusted_git.run_git_bytes(target, "cat-file", "blob", commit + ":" + path) == payloads[path],
                      "bounded_g1b_activation_not_committed")
    attested = operation["input_paths"]
    if binding["phase"] == "development":
        attested = attested - operation["paths"]
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=binding["expected_head"], expected_index_tree=binding["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", binding["base_commit"] + "^{tree}") == binding["base_tree"],
          "bounded_g1b_base_tree_changed")
    if operation.get("assessment"):
        _need(binding["expected_head"] == binding["base_commit"] == binding["activation_commit"]
              and binding["expected_index_tree"] == binding["base_tree"] == binding["candidate_tree"],
              "bounded_g1e_assessment_current_binding")
    elif binding["phase"] == "development":
        _need(binding["expected_head"] == binding["base_commit"] and binding["expected_index_tree"]
              in {binding["base_tree"], binding["candidate_tree"]}, "bounded_g1b_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", binding["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + binding["base_commit"]]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + binding["candidate_tree"]]
              and binding["expected_index_tree"] == binding["candidate_tree"], "bounded_g1b_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(binding, before, payloads, evidence, observation)


def _validate_loaded_policy(inputs: BoundedG1BInputs) -> tuple[dict[str, bytes], configuration_core.ValidatedConfiguration | None]:
    operation = _operation(inputs.binding["operation_kind"], inputs.binding)
    if operation.get("ci_reseal"):
        return _validate_g2_ci_reseal_loaded_policy(inputs)
    if operation.get("ci_adoption"):
        return _validate_g2_ci_loaded_policy(inputs)
    if operation.get("closeout_enable"):
        return _validate_g2_closeout_enable_loaded_policy(inputs)
    if operation.get("closeout"):
        return _validate_g2_closeout_loaded_policy(inputs)
    if operation.get("batch"):
        return _validate_g2_batch_loaded_policy(inputs)
    after = {path: inputs.payloads[path] for path in operation["transition_paths"]}
    validator = {"G1B": validate_g1b_acceptance_transition, "G1C": validate_g1c_acceptance_transition,
                 "G1D": validate_g1d_acceptance_transition, "G1E": validate_g1e_acceptance_transition,
                 "G2": validate_g2_acceptance_transition}[operation["gate"]]
    validator(inputs.before, after, inputs.evidence)
    try:
        raisa_policy.validate_precedence(
            _document(inputs.payloads[PROJECT], PROJECT),
            _document(inputs.payloads[CONTINUATION], CONTINUATION),
            after[AGENTS].decode("utf-8"), _json(after[STATE]),
        )
        configuration = None
        if operation["gate"] in {"G1E", "G2"}:
            scope = _json(after[operation["scope_path"]])
            _need(_canonical(scope["installed_controller_publication"]) == _canonical(inputs.binding["installed_controller"]),
                  "bounded_g1e_controller_binding_disagreement")
            configuration = raisa_policy.validate_recovery_configuration(
                documents={Path(path).name: inputs.payloads[path] for path in CONFIGURATION_PATHS},
                expected_sha256={Path(path).name: inputs.binding["payload_sha256"][path] for path in CONFIGURATION_PATHS},
                agents_text=after[AGENTS].decode("utf-8"), state=_json(after[STATE]))
    except (raisa_policy.RaisaPolicyError, configuration_core.ConfigurationError) as error:
        raise BoundedG1BError(error.reason_code) from error
    if operation["transition"]:
        _need(_json(after[operation["scope_path"]])["transition_base_commit"] == inputs.binding["base_commit"],
              "bounded_g1b_transition_base_mismatch")
    return after, configuration


def build_bounded_g1b_manifest(context: BoundedG1BContext) -> dict:
    inputs = load_bounded_g1b_inputs(context)
    _validate_loaded_policy(inputs)
    q = inputs.binding
    return {"schema_version": REQUEST_VERSION, "operation_id": q["operation_id"],
            "operation_kind": q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
            "candidate_tree": q["candidate_tree"], "allowed_paths": sorted(operation_paths(q["operation_kind"], q)),
            "intended_side_effect_classes": sorted(operation_effects(q["operation_kind"]))}


def evaluate_bounded_g1b_operation(*, context: BoundedG1BContext | None, manifest: object,
                                  entrypoint: str, phase: str, target_root: Path | None = None,
                                  source_root: Path | None = None) -> BoundedG1BDecision:
    try:
        _need(type(context) is BoundedG1BContext, "bounded_g1b_context_required")
        if type(manifest) is dict and manifest.get("operation_kind") == "assess_g1e":
            _need(entrypoint == "recovery_preflight" and phase == "assessment", "bounded_g1e_assessment_entrypoint_closed")
        _need(target_root is None or target_root.absolute() == context.target_root.absolute(),
              "bounded_g1b_caller_target_mismatch")
        _need(source_root is None or source_root.absolute() == context.source_root.absolute(),
              "bounded_g1b_caller_source_mismatch")
        _need(entrypoint in {"recovery_preflight", "task_branch_commit", "task_branch_push"},
              "bounded_g1b_entrypoint_closed")
        _need(phase in {"development", "pre-push", "post-push", "assessment"}, "bounded_g1b_phase")
        _need(entrypoint != "task_branch_commit" or phase == "development", "bounded_g1b_commit_phase")
        _need(entrypoint != "task_branch_push" or phase in {"pre-push", "post-push"}, "bounded_g1b_push_phase")
        _keys(manifest, {"schema_version", "operation_id", "operation_kind", "binding_sha256", "candidate_tree",
                         "allowed_paths", "intended_side_effect_classes"}, "bounded_g1b_manifest_schema")
        _need(manifest["schema_version"] == REQUEST_VERSION, "bounded_g1b_manifest_version")
        inputs = load_bounded_g1b_inputs(context)
        q = inputs.binding
        _need(q["phase"] == phase, "bounded_g1b_phase_disagreement")
        expected = {"schema_version": REQUEST_VERSION, "operation_id": q["operation_id"],
                    "operation_kind": q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
                    "candidate_tree": q["candidate_tree"], "allowed_paths": sorted(operation_paths(q["operation_kind"], q)),
                    "intended_side_effect_classes": sorted(operation_effects(q["operation_kind"]))}
        _need(_canonical(manifest) == _canonical(expected), "bounded_g1b_manifest_binding_mismatch")
        _after, configuration = _validate_loaded_policy(inputs)
        operation = _operation(q["operation_kind"], q)
        if operation.get("assessment"):
            _need(entrypoint == "recovery_preflight" and phase == "assessment", "bounded_g1e_assessment_entrypoint_closed")
            _need(configuration is not None, "bounded_g1e_configuration_required")
            return BoundedG1BDecision(False, (), entrypoint, phase, q["operation_id"], q["candidate_tree"],
                context.expected_binding_sha256, inputs.index_observation["observation_sha256"],
                claim_limits=operation["limits"], current_gate=operation["gate"], active_profile=operation["profile"],
                assessment_passed=True, configuration_sha256=configuration.canonical_sha256)
        return BoundedG1BDecision(True, (), entrypoint, phase, q["operation_id"], q["candidate_tree"],
                                 context.expected_binding_sha256, inputs.index_observation["observation_sha256"],
                                 claim_limits=operation["limits"], current_gate=operation["gate"],
                                 active_profile=operation["profile"])
    except (BoundedG1BError, trusted_git.TrustedGitError) as error:
        return BoundedG1BDecision(False, (error.reason_code,), entrypoint, phase)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, yaml.YAMLError):
        return BoundedG1BDecision(False, ("bounded_g1b_invalid_input",), entrypoint, phase)


def bounded_g1b_report(*, context: BoundedG1BContext | None, manifest: object,
                       entrypoint: str, phase: str, target_root: Path | None = None) -> dict:
    decision = evaluate_bounded_g1b_operation(context=context, manifest=manifest, entrypoint=entrypoint,
                                             phase=phase, target_root=target_root)
    return {"schema_version": "raisa-ariadne.bounded-g1b-preflight.v1",
            "status": "assessment_pass" if decision.assessment_passed else "policy_eligible" if decision.policy_admitted else "blocked", "read_only": True,
            "phase": phase, "requested_entrypoint": entrypoint, "programme_mode": "recovery",
            "current_gate": decision.current_gate, "active_profile": decision.active_profile,
            "feature_work_eligible": False, "global_gate": "g2_accepted_closed" if decision.policy_admitted and decision.active_profile == raisa_policy.G2_CLOSED_PROFILE else "red_repair_only", "execution_authorized": False,
            "reason_codes": list(decision.reason_codes), "failed_checks": list(decision.reason_codes),
            "candidate_tree": decision.candidate_tree, "binding_sha256": decision.binding_sha256,
            "observation_sha256": decision.observation_sha256, "claim_limits": list(decision.claim_limits),
            "policy_eligible": decision.policy_admitted, "assessment_passed": decision.assessment_passed,
            "configuration_sha256": decision.configuration_sha256,
            "configuration_document_count": 10 if decision.assessment_passed else None, "checks": []}
