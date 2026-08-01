from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "bernie-reception-one-word-desktop-authenticated-dialog-check-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-word-desktop-authenticated-dialog-check-threat-model-delta.md"
)
CANONICAL_MANIFEST = ROOT / "EMR4 Sidebar" / "manifest.xml"
CHECK_MANIFEST = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-online-authenticated-dialog-check"
    / "manifest.xml"
)
WEBPACK = ROOT / "EMR4 Sidebar" / "webpack.config.js"
TASKPANE = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-desktop-authenticated-dialog-check"
    / "desktop-acceptance-evidence.json"
)
RESIDUE = EVIDENCE.with_name("final-residue-evidence.json")
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
AGENTS = ROOT / "AGENTS.md"

NS = {
    "office": "http://schemas.microsoft.com/office/appforoffice/1.1",
    "ov": "http://schemas.microsoft.com/office/taskpaneappversionoverrides",
    "bt": "http://schemas.microsoft.com/office/officeappbasictypes/1.0",
}


def _manifest(path: Path):
    return ElementTree.parse(path).getroot()


def test_desktop_plan_preserves_the_closed_provider_free_contract():
    text = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for required in (
        "new blank document",
        "do not inspect",
        "authored-synthetic",
        "no provider",
        "no backend",
        "no document",
        "remove the sideload",
        "127.0.0.1",
        "word online remains platform-blocked",
    ):
        assert required in text


def test_disposable_manifest_is_distinct_and_loopback_only():
    canonical = _manifest(CANONICAL_MANIFEST)
    check = _manifest(CHECK_MANIFEST)
    assert check.find("office:Id", NS).text != canonical.find("office:Id", NS).text

    urls = [
        check.find("office:DefaultSettings/office:SourceLocation", NS).attrib["DefaultValue"],
        check.find(
            "ov:VersionOverrides/ov:Resources/bt:Urls/bt:Url[@id='Commands.Url']",
            NS,
        ).attrib["DefaultValue"],
        check.find(
            "ov:VersionOverrides/ov:Resources/bt:Urls/bt:Url[@id='Taskpane.Url']",
            NS,
        ).attrib["DefaultValue"],
    ]
    for value in urls:
        parsed = urlparse(value)
        assert parsed.scheme == "https"
        assert parsed.hostname == "localhost"
        assert parsed.port == 3000
    assert parse_qs(urlparse(urls[-1]).query) == {
        "reception_one_companion_demo": ["true"]
    }


def test_development_server_is_bound_to_ipv4_loopback():
    source = WEBPACK.read_text(encoding="utf-8")
    assert 'host: "127.0.0.1"' in source


def test_companion_mode_is_not_overwritten_by_the_normal_login_branch():
    source = TASKPANE.read_text(encoding="utf-8")
    on_ready_start = source.index("Office.onReady(")
    resume_start = source.index(
        "// \u2500\u2500 Resume session or show login",
        on_ready_start,
    )
    resume_end = source.index("\n});", resume_start)
    resume_branch = source[resume_start:resume_end]
    assert "if (isReceptionOneCompanionDemoEnabled()) {" in resume_branch
    assert 'showView("view-app");' in resume_branch
    assert "configureReceptionOneCompanion();" in resume_branch
    assert "} else if (token) {" in resume_branch


def test_desktop_evidence_is_zero_authority_and_cleanup_complete():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    residue = json.loads(RESIDUE.read_text(encoding="utf-8"))
    assert evidence["result"] == (
        "reception_one_word_desktop_supervised_dialog_check_pass"
    )
    assert evidence["host"]["new_blank_document_only"] is True
    assert evidence["host"]["document_body_read_count"] == 0
    assert evidence["host"]["document_body_write_count"] == 0
    assert evidence["exchange"]["request_count"] == 1
    assert evidence["exchange"]["proofreader_disposition"] == "admit"
    assert evidence["exchange"]["native_diary_result_count"] == 3
    assert evidence["exchange"]["request_text_returned_to_word"] is False
    assert evidence["exchange"]["appointment_detail_returned_to_word"] is False
    assert set(evidence["zero_authority_counts"].values()) == {0}
    assert evidence["sensitive_exclusions"]["raw_request_retained"] is False
    assert evidence["sensitive_exclusions"]["credential_retained"] is False
    assert residue["result"] == "pass"
    assert residue["checks"]["office_addin_debugging_stopped"] is True
    assert all(
        value is False
        for key, value in residue["checks"].items()
        if key != "office_addin_debugging_stopped"
    )


def test_continuity_compass_and_handover_bind_the_desktop_result():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    node = nodes["reception-one-word-desktop-authenticated-dialog-check"]
    assert graph["graph_revision"] >= 170
    assert node["status"] == "accepted"
    assert compass["map_revision"] >= 151
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
    assert "Word desktop dialog check acceptance" in AGENTS.read_text(
        encoding="utf-8"
    )
