from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-clinician-one-word-desktop-selection-check-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-clinician-one-word-desktop-selection-check-threat-model-delta.md"
)
CANONICAL_MANIFEST = ROOT / "EMR4 Sidebar" / "manifest.xml"
PREVIOUS_MANIFEST = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-online-authenticated-dialog-check"
    / "manifest.xml"
)
MANIFEST = (
    ROOT
    / "orchestration"
    / "continuity"
    / "clinician-one-word-desktop-selection-check"
    / "manifest.xml"
)
ADAPTER = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "clinician-one-document-context.js"
TASKPANE = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"
EVIDENCE = MANIFEST.with_name("desktop-selection-evidence.json")
RESIDUE = MANIFEST.with_name("final-residue-evidence.json")
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


def test_plan_and_threat_model_freeze_the_real_host_boundary():
    text = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for required in (
        "new unsaved blank document",
        "authored-synthetic",
        "read only the exact current",
        "readDocument".lower(),
        "do not inspect",
        "provider-free",
        "backend or database",
        "don't save",
        "user confirmation",
        "127.0.0.1",
    ):
        assert required in text


def test_disposable_manifest_is_distinct_read_only_and_loopback():
    canonical = _manifest(CANONICAL_MANIFEST)
    previous = _manifest(PREVIOUS_MANIFEST)
    check = _manifest(MANIFEST)
    ids = {
        canonical.find("office:Id", NS).text,
        previous.find("office:Id", NS).text,
        check.find("office:Id", NS).text,
    }
    assert len(ids) == 3
    assert check.find("office:Permissions", NS).text == "ReadDocument"

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
        "clinician_one_context_demo": ["true"]
    }


def test_accepted_adapter_still_reads_only_current_selection():
    adapter = ADAPTER.read_text(encoding="utf-8")
    assert "context.document.getSelection()" in adapter
    assert 'selection.load("text")' in adapter
    for forbidden in (
        "context.document.body",
        ".insertText(",
        ".insertHtml(",
        "getFileAsync",
        "getSelectedDataAsync",
        "fetch(",
        "MediaRecorder",
        "localStorage",
        "sessionStorage",
    ):
        assert forbidden not in adapter
    taskpane = TASKPANE.read_text(encoding="utf-8")
    assert "frame.text" not in taskpane
    assert "clinician_one_context_demo" in taskpane


def test_real_host_evidence_is_sanitized_and_zero_authority():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["result"] == "clinician_one_word_desktop_selection_check_pass"
    assert evidence["evidence_mode"] == "installed_word_desktop_authored_synthetic"
    assert evidence["host"]["application"] == "Microsoft Word desktop"
    assert evidence["host"]["new_unsaved_blank_document_only"] is True
    assert evidence["host"]["existing_document_inspected"] is False
    assert evidence["selection"]["request_count"] == 1
    assert evidence["selection"]["status"] == "admitted"
    assert evidence["selection"]["source_label"] == "word_current_selection"
    assert evidence["selection"]["host_kind"] == "desktop"
    assert evidence["selection"]["raw_text_retained"] is False
    assert evidence["selection"]["raw_text_rendered"] is False
    assert evidence["selection"]["truncated"] is False
    assert evidence["selection"]["character_count"] > 0
    assert evidence["selection"]["line_count"] == 3
    assert evidence["selection"]["visible_fixture_line_count"] == 2
    assert evidence["selection"]["word_terminal_paragraph_marker_observed"] is True
    assert evidence["selection"]["selection_sha256"].startswith("sha256:")
    assert set(evidence["zero_authority_counts"].values()) == {0}
    serialized = json.dumps(evidence).lower()
    for forbidden in ("access_token", "refresh_token", "patient_name", "document_id"):
        assert forbidden not in serialized


def test_cleanup_and_continuity_close_the_descendant():
    residue = json.loads(RESIDUE.read_text(encoding="utf-8"))
    assert residue["result"] == "pass"
    assert all(value is False for value in residue["residue"].values())
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    assert graph["graph_revision"] >= 175
    assert compass["source_graph_revision"] == graph["graph_revision"]
    journey_ids = [item["node_id"] for item in compass["journey"]]
    assert "clinician-one-word-desktop-selection-check" in journey_ids
    assert compass["current_position"]["node_id"] == journey_ids[-1]
    handover = AGENTS.read_text(encoding="utf-8")
    assert "clinician_one_word_desktop_selection_check_pass" in handover
