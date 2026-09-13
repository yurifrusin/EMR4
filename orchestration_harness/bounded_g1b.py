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
OPERATION_PATHS.update(enable_g2_batches=G2_BATCH_MAINTENANCE_PATHS,
                       extend_g2_catalogue=G2_BATCH_MAINTENANCE_PATHS,
                       repair_g2_batch=G2_BATCH_PATHS)


def _batch_changes(binding: dict) -> dict:
    kind = binding.get("operation_kind")
    rows = binding.get("repair_sha256")
    _need(kind in G2_BATCH_KINDS and type(rows) is dict and 1 <= len(rows) <= 6,
          "bounded_g2_batch_changes_invalid")
    maintenance = kind in {"enable_g2_batches", "extend_g2_catalogue"}
    catalogue = binding.get("schema_version") == G2_CATALOGUE_BINDING_VERSION
    allowed = G2_BATCH_MAINTENANCE_PATHS if maintenance else G2_CATALOGUE_PATHS if catalogue else G2_BATCH_PATHS
    _need(set(rows) <= allowed and (not maintenance or set(rows) == allowed),
          "bounded_g2_batch_path_not_allowed")
    for row in rows.values():
        _keys(row, {"before_sha256", "after_sha256"}, "bounded_g2_batch_change_schema")
        _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in row.values())
              and row["before_sha256"] != row["after_sha256"], "bounded_g2_batch_change_digest")
    return rows


def batch_input_paths(binding: dict) -> frozenset[str]:
    """Catalogue authority is metadata; only fixed policy and selected files open."""
    changes = _batch_changes(binding)
    if binding.get("schema_version") == G2_CATALOGUE_BINDING_VERSION:
        return G2_CATALOGUE_POLICY_PATHS | frozenset(changes)
    return G2_BATCH_INPUT_PATHS


def operation_effects(kind: str) -> frozenset[str]:
    if kind == "repair_g2_batch":
        return G2_BATCH_EFFECTS
    return frozenset({"repository_read"}) if kind == "assess_g1e" else EFFECTS


def operation_paths(kind: str, binding: dict | None = None) -> frozenset[str]:
    _need(type(kind) is str and kind in OPERATION_PATHS, "bounded_g1b_operation_kind")
    if kind == "repair_g2_batch":
        _need(type(binding) is dict and binding.get("operation_kind") == kind,
              "bounded_g2_batch_binding_required")
        return frozenset(_batch_changes(binding))
    return OPERATION_PATHS[kind]


def _operation(kind: str, binding: dict | None = None) -> dict:
    paths = operation_paths(kind, binding)
    if kind in G2_BATCH_KINDS:
        return {"paths": paths, "input_paths": batch_input_paths(binding),
                "transition_paths": G2_TRANSITION_PATHS, "scope_path": G2_SCOPE,
                "transition": kind in {"enable_g2_batches", "extend_g2_catalogue"}, "batch": True,
                "profile": G2_PROFILE, "gate": "G2", "limits": G2_BATCH_LIMITS}
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


def _validate_g2_batch_scope(scope: dict) -> None:
    builder = (build_g2_catalogue_scope if scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION
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


def _batch_publication(target: Path, publication: dict, base: str) -> None:
    headers = trusted_git.run_git(target, "cat-file", "commit", publication["commit"]).split("\n\n", 1)[0].splitlines()
    _need([line for line in headers if line.startswith("parent ")] == ["parent " + publication["parent"]]
          and [line for line in headers if line.startswith("tree ")] == ["tree " + publication["tree"]],
          "bounded_g2_batch_publication_invalid")
    trusted_git.run_git(target, "merge-base", "--is-ancestor", publication["commit"], base)


def _load_g2_batch_inputs(context, target, source, evidence_root, scratch, binding, read, snapshots):
    """The caller digest authenticates the binding before any selected input read."""
    _keys(binding, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
                    "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
                    "activation_commit", "installed_controller", "repair_sha256"},
          "bounded_g2_batch_binding_schema")
    catalogue = binding["schema_version"] == G2_CATALOGUE_BINDING_VERSION
    _need(binding["schema_version"] in {G2_BATCH_BINDING_VERSION, G2_CATALOGUE_BINDING_VERSION}
          and (binding["operation_kind"] != "extend_g2_catalogue" or catalogue)
          and (binding["operation_kind"] != "enable_g2_batches" or not catalogue),
          "bounded_g2_batch_binding_version")
    changes = _batch_changes(binding)
    input_paths = batch_input_paths(binding)
    maintenance = binding["operation_kind"] in {"enable_g2_batches", "extend_g2_catalogue"}
    _need(type(binding["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", binding["operation_id"]),
          "bounded_g2_batch_operation_id")
    _need(binding["phase"] in {"development", "pre-push", "post-push"}, "bounded_g2_batch_phase")
    _need(all(type(binding[k]) is str and re.fullmatch(r"[0-9a-f]{40}", binding[k])
              for k in ("base_commit", "base_tree", "expected_head", "expected_index_tree", "candidate_tree")),
          "bounded_g2_batch_git_binding")
    source_pins = _digest_map(binding["source_sha256"], SOURCE_PATHS, "bounded_g2_batch_source_paths")
    payload_pins = _digest_map(binding["payload_sha256"], input_paths, "bounded_g2_batch_payload_paths")
    _need(source_pins["orchestration_harness/trusted_git.py"] ==
          "5f8bfd44b63282e205a22bef1b81d0b8b5271572ba47c5b5df7371c0f638874f", "bounded_g1b_git_source_changed")
    source_payloads = {path: read(source / path, digest) for path, digest in source_pins.items()}
    payloads = {path: read(target / path, digest) for path, digest in sorted(payload_pins.items())}
    scope = _json(payloads[G2_SCOPE])
    _need((scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION) == catalogue,
          "bounded_g2_catalogue_scope_binding_mismatch")
    _validate_g2_batch_scope(scope)
    frozen = {**FROZEN_PINS, COST: COST_PIN, SCOPE_PATH: G1B_BASELINE_PINS[SCOPE_PATH],
              G1C_SCOPE: G1C_BASELINE_PINS[G1C_SCOPE], G1D_SCOPE: G1D_BASELINE_PINS[G1D_SCOPE],
              G1E_SCOPE: G1E_BASELINE_PINS[G1E_SCOPE], **GOVERNOR_PINS, **PROVENANCE_DEPENDENCY_PINS,
              **PROVENANCE_PINS, **CONFIGURATION_LEAF_PINS,
              AGENTS: G2_INITIAL_POLICY_PINS[AGENTS], GATES: G2_INITIAL_POLICY_PINS[GATES]}
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
    prior_policy = initial_policy
    if catalogue:
        _batch_publication(target, G2_CATALOGUE_PREDECESSOR, base)
        prior_policy = {}
        for path, digest in {**G2_CATALOGUE_PREDECESSOR_POLICY,
                             **G2_CATALOGUE_PREDECESSOR["source_sha256"]}.items():
            raw = trusted_git.run_git_bytes(target, "cat-file", "blob", G2_CATALOGUE_PREDECESSOR["commit"] + ":" + path)
            _need(_sha(raw) == digest, "bounded_g2_catalogue_predecessor_bytes_changed")
            if path in G2_CATALOGUE_PREDECESSOR_POLICY:
                prior_policy[path] = raw
    base_payloads = {path: trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path)
                     for path in sorted(input_paths)}
    for path, raw in base_payloads.items():
        if path in changes:
            _need(_sha(raw) == changes[path]["before_sha256"], "bounded_g2_batch_preimage_changed")
            _need(_sha(payloads[path]) == changes[path]["after_sha256"], "bounded_g2_batch_candidate_changed")
        else:
            _need(raw == payloads[path], "bounded_g2_batch_unowned_input_changed")
    controller = binding["installed_controller"]
    _validate_installed_controller(controller)
    _batch_publication(target, controller, base)
    if maintenance:
        expected_controller = G2_CATALOGUE_PREDECESSOR if catalogue else G2_INITIAL_CONTROLLER
        expected_activation = expected_controller["commit"] if catalogue else G2_INITIAL_ACTIVATION["commit"]
        _need(controller == expected_controller and binding["activation_commit"] == expected_activation,
              "bounded_g2_batch_maintenance_predecessor")
        _need(scope["transition_base_commit"] == base, "bounded_g2_batch_maintenance_base")
        prior_pins = G2_CATALOGUE_PREDECESSOR_POLICY if catalogue else G2_INITIAL_POLICY_PINS
        for path, digest in prior_pins.items():
            _need(_sha(base_payloads[path]) == digest, "bounded_g2_batch_maintenance_policy_changed")
        if not catalogue:
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
        if not maintenance or path not in G2_BATCH_CODE_PATHS:
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


def _validate_g2_batch_loaded_policy(inputs):
    scope = _json(inputs.payloads[G2_SCOPE])
    builder = (build_g2_catalogue_transition if scope.get("schema_version") == G2_CATALOGUE_SCOPE_VERSION
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
            "feature_work_eligible": False, "global_gate": "red_repair_only", "execution_authorized": False,
            "reason_codes": list(decision.reason_codes), "failed_checks": list(decision.reason_codes),
            "candidate_tree": decision.candidate_tree, "binding_sha256": decision.binding_sha256,
            "observation_sha256": decision.observation_sha256, "claim_limits": list(decision.claim_limits),
            "policy_eligible": decision.policy_admitted, "assessment_passed": decision.assessment_passed,
            "configuration_sha256": decision.configuration_sha256,
            "configuration_document_count": 10 if decision.assessment_passed else None, "checks": []}
