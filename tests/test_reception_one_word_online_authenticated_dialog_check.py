from pathlib import Path
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "bernie-reception-one-word-online-authenticated-dialog-check-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-word-online-authenticated-dialog-check-threat-model-delta.md"
)
CANONICAL_MANIFEST = ROOT / "EMR4 Sidebar" / "manifest.xml"
CHECK_MANIFEST = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-online-authenticated-dialog-check"
    / "manifest.xml"
)
TASKPANE_SOURCE = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"
TASKPANE_PUBLISHED = ROOT / "docs" / "taskpane" / "taskpane.js"

NS = {
    "office": "http://schemas.microsoft.com/office/appforoffice/1.1",
    "ov": "http://schemas.microsoft.com/office/taskpaneappversionoverrides",
    "bt": "http://schemas.microsoft.com/office/officeappbasictypes/1.0",
}


def _manifest_urls(path: Path) -> tuple[str, str]:
    root = ElementTree.parse(path).getroot()
    default = root.find(
        "office:DefaultSettings/office:SourceLocation",
        NS,
    ).attrib["DefaultValue"]
    taskpane = root.find(
        "ov:VersionOverrides/ov:Resources/bt:Urls/"
        "bt:Url[@id='Taskpane.Url']",
        NS,
    ).attrib["DefaultValue"]
    return default, taskpane


def _manifest_identity(path: Path) -> tuple[str, str]:
    root = ElementTree.parse(path).getroot()
    return (
        root.find("office:Id", NS).text,
        root.find("office:Version", NS).text,
    )


def test_plan_and_threat_model_keep_live_host_check_provider_free():
    text = PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")
    for required in (
        "authored-synthetic",
        "new blank word online document",
        "do not inspect",
        "same HTTPS loopback origin",
        "no provider",
        "no backend",
        "no document URL",
        "stop for user intervention",
    ):
        assert required.lower() in text.lower()


def test_task_specific_manifest_enables_only_the_loopback_companion():
    canonical_default, canonical_taskpane = _manifest_urls(CANONICAL_MANIFEST)
    check_default, check_taskpane = _manifest_urls(CHECK_MANIFEST)

    assert canonical_default == "https://localhost:3000/taskpane.html"
    assert canonical_taskpane == "https://localhost:3000/taskpane.html"
    assert check_default == check_taskpane

    parsed = urlparse(check_default)
    assert parsed.scheme == "https"
    assert parsed.hostname == "localhost"
    assert parsed.port == 3000
    assert parsed.path == "/taskpane.html"
    assert parse_qs(parsed.query) == {"reception_one_companion_demo": ["true"]}

    canonical_id, canonical_version = _manifest_identity(CANONICAL_MANIFEST)
    check_id, check_version = _manifest_identity(CHECK_MANIFEST)
    assert check_id != canonical_id
    assert check_version != canonical_version


def test_real_companion_dialog_is_forced_into_authored_synthetic_smoke_mode():
    source = TASKPANE_SOURCE.read_text(encoding="utf-8")
    resolver = source[
        source.index("function diaryDialogUrl("):
        source.index("function companionStatus(")
    ]
    assert 'url.searchParams.set("reception_one_companion_demo", "true")' in resolver
    assert 'url.searchParams.set("smoke", "true")' in resolver
    for forbidden in (
        "request_text",
        "correlation_id",
        "request_id",
        "token",
        "patient_id",
        "appointment_id",
    ):
        assert forbidden not in resolver


def test_source_and_published_taskpane_remain_byte_identical():
    assert TASKPANE_SOURCE.read_bytes() == TASKPANE_PUBLISHED.read_bytes()
