import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "prepare_raisa_office_web_dev_context.py"
DEPLOY = REPO_ROOT / "deploy" / "raisa-office-web-dev"
DIARY_HTML = REPO_ROOT / "docs" / "diary" / "diary.html"
DIARY_JS = REPO_ROOT / "docs" / "diary" / "diary.js"
CONTINUITY = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-cloud-run-public-https-dev-host-readiness"
)


def load_module():
    spec = importlib.util.spec_from_file_location("raisa_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_origin_validation_is_exact():
    module = load_module()
    assert (
        module.validate_origin("http://127.0.0.1:18080")
        == "http://127.0.0.1:18080"
    )
    assert (
        module.validate_origin(
            "https://raisa-office-web-dev-123456789012.australia-southeast1.run.app"
        )
        == "https://raisa-office-web-dev-123456789012.australia-southeast1.run.app"
    )
    for unsafe in (
        "https://example.com",
        "http://localhost:18080",
        "https://raisa-office-web-dev.example.run.app/path",
        "https://raisa-office-web-dev.example.run.app?secret=value",
    ):
        with pytest.raises(ValueError):
            module.validate_origin(unsafe)


def test_closed_context_is_deterministic_after_production_build():
    subprocess.run(
        ["npm.cmd", "run", "build"],
        cwd=REPO_ROOT / "EMR4 Sidebar",
        check=True,
        capture_output=True,
        text=True,
    )
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        first = root / "first"
        second = root / "second"
        origin = "http://127.0.0.1:18080"
        result_a = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(first), "--origin", origin],
            check=True,
            capture_output=True,
            text=True,
        )
        result_b = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(second), "--origin", origin],
            check=True,
            capture_output=True,
            text=True,
        )
        parsed_a = json.loads(result_a.stdout)
        parsed_b = json.loads(result_b.stdout)
        assert parsed_a["content_manifest_sha256"] == parsed_b["content_manifest_sha256"]
        files_a = {
            path.relative_to(first).as_posix(): path.read_bytes()
            for path in first.rglob("*")
            if path.is_file()
        }
        files_b = {
            path.relative_to(second).as_posix(): path.read_bytes()
            for path in second.rglob("*")
            if path.is_file()
        }
        assert files_a == files_b
        assert not any(path.endswith(".map") for path in files_a)
        assert not any(".git" in path or ".env" in path for path in files_a)
        manifest = json.loads(files_a["public/content-manifest.json"])
        assert manifest["authority"] == {
            "backend": False,
            "command": False,
            "credential": False,
            "document_write": False,
            "microphone": False,
            "production": False,
            "provider": False,
        }
        xml = files_a["manifest.xml"].decode()
        assert "<Permissions>ReadDocument</Permissions>" in xml
        assert "__RAISA_PUBLIC_ORIGIN__" not in xml


def test_static_server_and_container_preserve_zero_authority_posture():
    server = (DEPLOY / "server.mjs").read_text(encoding="utf-8")
    dockerfile = (DEPLOY / "Dockerfile").read_text(encoding="utf-8")
    template = (DEPLOY / "manifest-template.xml").read_text(encoding="utf-8")
    assert 'request.method !== "GET" && request.method !== "HEAD"' in server
    assert 'path === "/health"' in server
    assert 'path === "/healthz"' in server
    assert 'path === "/hosting-policy.js"' in server
    assert 'allowedFiles.has(path)' in server
    assert "Content-Security-Policy" in server
    assert "no-store" in server
    assert "console.log" not in server
    assert "/api/v1" not in server
    assert "node:24-bookworm-slim@sha256:" in dockerfile
    assert "USER 65532:65532" in dockerfile
    assert "npm install" not in dockerfile
    assert "<Permissions>ReadDocument</Permissions>" in template
    assert "ReadWriteDocument" not in template


def test_hosted_diary_admits_only_the_zero_authority_companion_capabilities():
    html = DIARY_HTML.read_text(encoding="utf-8")
    source = DIARY_JS.read_text(encoding="utf-8")
    assert '<script src="../hosting-policy.js?v=1"></script>' in html
    hosted_gate = source[
        source.index("const HOSTED_SYNTHETIC_CAPABILITY_ALLOWLIST")
        : source.index("function isApprovedNgrokHostname")
    ]
    assert '"reception_one_companion_demo"' in hosted_gate
    assert '"smoke"' in hosted_gate
    for prohibited_capability in (
        "bernie_dev_review",
        "bernie_confirm_adapter",
        "product_context_acceptance",
        "product_context_live_local",
        "slot_preview",
    ):
        assert prohibited_capability not in hosted_gate
    for zero_authority in (
        "provider_authority",
        "backend_authority",
        "credential_authority",
        "microphone_authority",
        "command_authority",
        "document_write_authority",
        "production_authority",
    ):
        assert zero_authority in hosted_gate
    capability_gate = source[
        source.index("function isLocalHarnessCapabilityEnabled")
        : source.index("function secureClientIdentifier")
    ]
    assert "HOSTED_SYNTHETIC_CAPABILITY_ALLOWLIST.has(param)" in capability_gate
    assert "isHostedSyntheticOnlyModeEnabled()" in capability_gate


def test_closeout_is_revision_bound_and_external_state_remains_closed():
    graph = json.loads(
        (
            REPO_ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
        ).read_text(encoding="utf-8")
    )
    compass = json.loads(
        (
            REPO_ROOT / "orchestration" / "continuity" / "emr4-compass.json"
        ).read_text(encoding="utf-8")
    )
    # This historical node stays accepted as later Continuity/Compass
    # descendants append; the top-level revisions must advance together.
    assert graph["graph_revision"] >= 180
    assert compass["map_revision"] >= 161
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-cloud-run-public-https-dev-host-readiness"
    )
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "clinician-one-word-desktop-selection-check",
            "relation": "builds_on",
        }
    ]
    evidence = json.loads(
        (CONTINUITY / "local-container-browser-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence["result"] == "pass"
    assert evidence["authority"]["external_cloud_mutations"] == 0
    assert evidence["browser"]["observed_emr_backend_requests"] == 0
    assert evidence["browser"]["observed_vertex_or_other_provider_requests"] == 0
    residue = json.loads(
        (CONTINUITY / "final-residue-evidence.json").read_text(encoding="utf-8")
    )
    assert residue["result"] == "pass"
    assert residue["owned_containers"] == 0
    assert residue["external_cloud_resources_created_or_changed"] == 0
