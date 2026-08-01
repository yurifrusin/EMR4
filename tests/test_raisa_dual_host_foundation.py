import json
import shutil
import subprocess
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
PUBLISHED = ROOT / "docs" / "taskpane"
RUNTIME = SOURCE / "office-host-runtime.js"
SCHEMA = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-dual-host-foundation"
    / "office-host-runtime-profile.schema.json"
)
INVENTORY = SCHEMA.with_name("feature-inventory.json")
PLAN = ROOT / "docs" / "raisa-dual-host-foundation-plan.md"
THREAT = (
    ROOT / "docs" / "security" / "raisa-dual-host-foundation-threat-model-delta.md"
)
TASKPANE = SOURCE / "taskpane.js"
HTML = SOURCE / "taskpane.html"
WEBPACK = ROOT / "EMR4 Sidebar" / "webpack.config.js"
SYNC = ROOT / "sync_taskpane.py"
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
RENDERED_COMPASS = ROOT / "docs" / "ariadne-compass-current.md"
AGENTS = ROOT / "AGENTS.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _node_profiles() -> dict:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the Office host runtime contract.")
    script = r"""
const runtime = require(process.argv[1]);
let calls = 0;
const fn = () => { calls += 1; };
function environment(options = {}) {
  const includeDialog = options.dialog !== false;
  const includeDevicePermission = options.devicePermission !== false;
  const includeMedia = options.media !== false;
  const includeWord = options.word !== false;
  const includeCrypto = options.crypto !== false;
  return {
    office: {
      context: {
        ui: includeDialog ? { displayDialogAsync: fn } : {},
        document: { customXmlParts: {} },
        devicePermission: includeDevicePermission
          ? { requestPermissionsAsync: fn }
          : {},
      },
      actions: { associate: fn },
      DevicePermission: includeDevicePermission ? { microphone: "microphone" } : {},
    },
    word: includeWord ? { run: fn } : {},
    navigator: includeMedia
      ? { mediaDevices: { getUserMedia: fn } }
      : {},
    mediaRecorder: includeMedia ? function MediaRecorder() {} : undefined,
    crypto: includeCrypto ? { randomUUID: fn } : {},
  };
}
const desktop = runtime.createOfficeHostProfile(
  { host: "Word", platform: "PC" },
  environment()
);
const web = runtime.createOfficeHostProfile(
  { host: "Word", platform: "OfficeOnline" },
  environment()
);
const webWithoutDevicePermission = runtime.createOfficeHostProfile(
  { host: "Word", platform: "OfficeOnline" },
  environment({ devicePermission: false })
);
const mobile = runtime.createOfficeHostProfile(
  { host: "Word", platform: "iOS" },
  environment({ media: false })
);
const unknown = runtime.createOfficeHostProfile(
  { host: "Excel", platform: "Linux" },
  environment({ dialog: false, word: false, media: false, crypto: false })
);
process.stdout.write(JSON.stringify({
  calls,
  frozen: {
    profile: Object.isFrozen(desktop),
    capabilities: Object.isFrozen(desktop.capabilities),
    features: Object.isFrozen(desktop.features),
    feature: Object.isFrozen(desktop.features["clinician_one.workspace"]),
    authority: Object.isFrozen(desktop.authority),
  },
  profiles: {
    desktop,
    web,
    web_without_device_permission: webWithoutDevicePermission,
    mobile,
    unknown,
  },
}));
"""
    completed = subprocess.run(
        [node, "-e", script, str(RUNTIME)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_profile_schema_is_closed_and_all_host_fixtures_validate():
    schema = json.loads(_read(SCHEMA))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    observed = _node_profiles()

    assert schema["additionalProperties"] is False
    assert observed["calls"] == 0
    assert set(observed["frozen"].values()) == {True}
    for profile in observed["profiles"].values():
        validator.validate(profile)
        assert set(profile["authority"].values()) == {False}


def test_desktop_and_web_profiles_share_contract_without_sharing_permission_strategy():
    profiles = _node_profiles()["profiles"]
    desktop = profiles["desktop"]
    web = profiles["web"]

    assert desktop["host_kind"] == "desktop"
    assert desktop["platform"] == "desktop_windows"
    assert desktop["microphone_permission_strategy"] == "browser_media_prompt"
    assert web["host_kind"] == "web"
    assert web["platform"] == "word_online"
    assert web["microphone_permission_strategy"] == (
        "office_device_permission_then_browser_media"
    )

    for profile in (desktop, web):
        assert profile["features"]["clinician_one.workspace"]["status"] == "host_ready"
        assert (
            profile["features"]["clinician_one.scribe_capture"]["status"]
            == "host_ready"
        )
        assert profile["features"]["reception_one.dialog"]["status"] == "host_ready"
        assert (
            profile["features"]["reception_one.companion"]["status"]
            == "host_ready"
        )
        for feature in profile["features"].values():
            assert feature["decision_basis"] == "host_capability_only"
            assert feature["authorization"] == (
                "product_authorization_not_evaluated"
            )


def test_web_scribe_and_unknown_hosts_fail_closed_with_exact_reasons():
    profiles = _node_profiles()["profiles"]
    web = profiles["web_without_device_permission"]
    unknown = profiles["unknown"]

    assert web["features"]["clinician_one.workspace"]["status"] == "host_ready"
    assert web["features"]["clinician_one.scribe_capture"] == {
        "status": "host_blocked",
        "missing_capabilities": ["office_device_permission"],
        "decision_basis": "host_capability_only",
        "authorization": "product_authorization_not_evaluated",
    }
    assert web["features"]["reception_one.companion"]["status"] == "host_ready"
    assert unknown["host"] == "unknown"
    assert unknown["platform"] == "unknown"
    for feature in unknown["features"].values():
        assert feature["status"] == "host_blocked"
        assert "word_host" in feature["missing_capabilities"]


def test_host_profile_constructor_has_no_sensitive_or_operational_calls():
    source = _read(RUNTIME)
    for prohibited in (
        "fetch(",
        ".getUserMedia(",
        ".displayDialogAsync(",
        ".randomUUID(",
        ".run(",
        "localStorage",
        "sessionStorage",
        "document.body",
        "XMLHttpRequest",
        "WebSocket",
    ):
        assert prohibited not in source


def test_runtime_loads_before_taskpane_and_is_published_from_office_on_ready():
    webpack = _read(WEBPACK)
    taskpane = _read(TASKPANE)

    assert webpack.index('"./src/taskpane/office-host-runtime.js"') < webpack.index(
        '"./src/taskpane/taskpane.js"'
    )
    on_ready = taskpane[taskpane.index("Office.onReady(info => {") :]
    assert on_ready.index("configureOfficeHostRuntime(info);") < on_ready.index(
        "if (info.host !== Office.HostType.Word) return;"
    )
    configure = taskpane[
        taskpane.index("function configureOfficeHostRuntime")
        : taskpane.index("function updateSyncDebug")
    ]
    assert "window.emr4HostRuntimeProfile = officeHostRuntimeProfile" in configure
    assert 'features["clinician_one.scribe_capture"]' in configure
    assert "Audio capture is unavailable in this Word host." in configure


def test_build_and_sync_paths_include_the_shared_runtime_without_hidden_rewrite():
    webpack = _read(WEBPACK)
    sync = _read(SYNC)
    assert '"./src/taskpane/office-host-runtime.js"' in webpack
    assert '"./src/taskpane/clinician-one-document-context.js"' in webpack
    assert '"office-host-runtime.js",' in sync
    assert '"hosting-policy.js",' in sync
    assert 'shutil.copy2(SRC / "taskpane.js", DEST / "taskpane.js")' in sync
    assert "copied + patched taskpane.js" not in sync

    for name in (
        "taskpane.html",
        "taskpane.css",
        "taskpane.js",
        "office-host-runtime.js",
        "hosting-policy.js",
    ):
        assert _read(SOURCE / name) == _read(PUBLISHED / name)


def test_inventory_preserves_integrated_reception_one_and_closed_patient_gates():
    inventory = json.loads(_read(INVENTORY))
    integrated = inventory["integrated_reception_domain"]
    assert integrated["invariant"] == (
        "one_backend_owned_reception_truth_with_role_scoped_surfaces"
    )
    assert integrated["future_online_booking_surface"].endswith(
        "booking_contract_only"
    )
    assert integrated["future_arrival_surface"].startswith("rayleen_")
    assert integrated["third_party_primary_reception_product"] == "not_selected"
    assert integrated["current_external_patient_authority"] is False
    assert integrated["current_online_booking_authority"] is False
    assert integrated["current_rayleen_authority"] is False
    assert integrated["current_arrival_write_authority"] is False
    delivery = inventory["delivery_direction"]
    assert delivery["primary_model"] == (
        "cloud_first_practice_management_as_a_service"
    )
    assert delivery["future_local_model_role"].startswith("optional_subordinate_")
    assert delivery["parallel_clinical_or_reception_truth_permitted"] is False
    assert delivery["current_cloud_resource_authority"] is False

    features = {item["feature_id"]: item for item in inventory["features"]}
    assert {
        "clinician.patient_file_context",
        "clinician.consultation_start_and_bounded_note_read",
        "clinician.background_analysis",
        "clinician.scribe_capture",
        "clinician.scribe_submission",
        "clinician.review_and_finalise",
        "reception.ordinary_diary_launch",
        "reception.contextual_launch",
        "reception.compact_companion",
    } == set(features)


def test_plan_and_threat_model_keep_candidate_brand_and_api_spine_gates_closed():
    combined = f"{_read(PLAN)}\n{_read(THREAT)}".lower()
    for phrase in (
        "candidate master brand",
        "one reception domain",
        "role-scoped surfaces",
        "third-party booking",
        "rayleen",
        "cloud-first",
        "subordinate edge",
        "no provider call",
        "no online-booking client",
        "no document",
        "no microphone capture",
        "graphql remains read-only",
        "product_authorization_not_evaluated",
        "protected holdouts",
        "public rename",
    ):
        assert phrase in combined


def test_continuity_compass_and_handover_bind_the_dual_host_foundation():
    graph = json.loads(_read(GRAPH))
    compass = json.loads(_read(COMPASS))
    nodes = {node["id"]: node for node in graph["nodes"]}
    node = nodes["raisa-dual-host-foundation"]

    assert graph["graph_revision"] >= 172
    assert node["status"] == "accepted"
    assert any(
        relationship["node_id"]
        == "reception-one-word-desktop-authenticated-dialog-check"
        and relationship["relation"] == "builds_on"
        for relationship in node["relationships"]
    )
    assert compass["map_revision"] >= 153
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
    assert "Raisa Candidate Dual-host Foundation" in _read(RENDERED_COMPASS)
    handover = _read(AGENTS)
    assert "raisa_dual_host_foundation_pass" in handover
    assert "Rayleen" in handover
