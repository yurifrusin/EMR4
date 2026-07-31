import json
import shutil
import subprocess
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
PUBLISHED = ROOT / "docs" / "taskpane"
MODULE = SOURCE / "clinician-one-document-context.js"
HOST_RUNTIME = SOURCE / "office-host-runtime.js"
TASKPANE = SOURCE / "taskpane.js"
HTML = SOURCE / "taskpane.html"
WEBPACK = ROOT / "EMR4 Sidebar" / "webpack.config.js"
SYNC = ROOT / "sync_taskpane.py"
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "clinician-one-readonly-document-context"
)
REQUEST_SCHEMA = CONTINUITY / "document-context-request.schema.json"
RESPONSE_SCHEMA = CONTINUITY / "document-context-response.schema.json"
PLAN = ROOT / "docs" / "raisa-clinician-one-readonly-document-context-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-clinician-one-readonly-document-context-threat-model-delta.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
RENDERED_COMPASS = ROOT / "docs" / "ariadne-compass-current.md"
AGENTS = ROOT / "AGENTS.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_node_matrix() -> dict:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the document-context contract.")
    script = r"""
const documentContext = require(process.argv[1]);
const hostRuntime = require(process.argv[2]);

function hostEnvironment() {
  return {
    office: { context: {}, actions: {} },
    word: { run: () => {} },
    navigator: {},
    crypto: {},
  };
}
function profile(platform, host = "Word") {
  return hostRuntime.createOfficeHostProfile(
    { host, platform },
    hostEnvironment()
  );
}
function request(suffix) {
  return documentContext.createLocalFixtureRequest(
    `clinician-context-${suffix}`
  );
}
function isDeeplyFrozen(value) {
  if (!value || typeof value !== "object") return true;
  return Object.isFrozen(value)
    && Object.values(value).every(isDeeplyFrozen);
}

(async () => {
  let desktopReads = 0;
  const desktopAdapter =
    documentContext.createClinicianDocumentContextAdapter({
      readSelectionText: async () => {
        desktopReads += 1;
        return "Synthetic cough review\r\nNo patient identifiers.";
      },
    });
  const desktopRequest = request("desktop-case-001");
  const desktop = await desktopAdapter.read(
    desktopRequest,
    profile("PC")
  );
  const replay = await desktopAdapter.read(
    desktopRequest,
    profile("PC")
  );

  let webReads = 0;
  const webAdapter = documentContext.createClinicianDocumentContextAdapter({
    readSelectionText: async () => {
      webReads += 1;
      return "Synthetic web selection.";
    },
  });
  const webRequest = request("web-case-001");
  const web = await webAdapter.read(webRequest, profile("OfficeOnline"));

  let blockedReads = 0;
  const blockedAdapter =
    documentContext.createClinicianDocumentContextAdapter({
      readSelectionText: async () => {
        blockedReads += 1;
        return "must not be read";
      },
    });
  const mobile = await blockedAdapter.read(
    request("mobile-case-001"),
    profile("iOS")
  );
  const unknown = await blockedAdapter.read(
    request("unknown-case-001"),
    profile("mystery")
  );
  const hostNotReady = await blockedAdapter.read(
    request("not-ready-case-001"),
    profile("PC", "Excel")
  );

  const invalidRequest = {
    ...JSON.parse(JSON.stringify(request("invalid-case-001"))),
    unexpected: true,
  };
  const invalid = await blockedAdapter.read(invalidRequest, profile("PC"));
  const deniedRequest = JSON.parse(
    JSON.stringify(request("denied-case-001"))
  );
  deniedRequest.grant.provider_invocation = true;
  const denied = await blockedAdapter.read(deniedRequest, profile("PC"));

  async function contentCase(suffix, text, throws = false) {
    const adapter =
      documentContext.createClinicianDocumentContextAdapter({
        readSelectionText: async () => {
          if (throws) throw new Error("sensitive host error");
          return text;
        },
      });
    return adapter.read(request(suffix), profile("PC"));
  }
  const empty = await contentCase("empty-case-001", " \r\n ");
  const tooLarge = await contentCase(
    "large-case-001",
    "x".repeat(documentContext.MAXIMUM_CHARACTERS + 1)
  );
  const tooManyLines = await contentCase(
    "lines-case-001",
    Array(documentContext.MAXIMUM_LINES + 1).fill("x").join("\n")
  );
  const readError = await contentCase(
    "read-error-case-001",
    "",
    true
  );

  const wordCalls = {
    run: 0,
    getSelection: 0,
    load: [],
    sync: 0,
  };
  const wordRuntime = {
    run: async callback => {
      wordCalls.run += 1;
      return callback({
        document: {
          getSelection: () => {
            wordCalls.getSelection += 1;
            return {
              text: "Synthetic direct selection.",
              load: field => wordCalls.load.push(field),
            };
          },
        },
        sync: async () => { wordCalls.sync += 1; },
      });
    },
  };
  const directText =
    await documentContext.createWordSelectionReader(wordRuntime)();

  process.stdout.write(JSON.stringify({
    requests: { desktopRequest, webRequest },
    responses: {
      desktop,
      web,
      replay,
      mobile,
      unknown,
      hostNotReady,
      invalid,
      denied,
      empty,
      tooLarge,
      tooManyLines,
      readError,
    },
    counts: { desktopReads, webReads, blockedReads },
    frozen: {
      request: isDeeplyFrozen(desktopRequest),
      desktop: isDeeplyFrozen(desktop),
      blocked: isDeeplyFrozen(replay),
    },
    wordReader: { directText, wordCalls },
  }));
})().catch(error => {
  process.stderr.write(String(error && error.stack ? error.stack : error));
  process.exit(1);
});
"""
    completed = subprocess.run(
        [node, "-e", script, str(MODULE), str(HOST_RUNTIME)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


@pytest.fixture(scope="module")
def matrix() -> dict:
    return _run_node_matrix()


def test_schemas_are_closed_valid_and_accept_the_positive_matrix(matrix):
    request_schema = json.loads(_read(REQUEST_SCHEMA))
    response_schema = json.loads(_read(RESPONSE_SCHEMA))
    jsonschema.Draft202012Validator.check_schema(request_schema)
    jsonschema.Draft202012Validator.check_schema(response_schema)

    for request in matrix["requests"].values():
        jsonschema.validate(request, request_schema)
    for response in matrix["responses"].values():
        jsonschema.validate(response, response_schema)


def test_desktop_and_web_emit_exact_non_authoritative_frames(matrix):
    desktop = matrix["responses"]["desktop"]
    web = matrix["responses"]["web"]

    assert desktop["status"] == "admitted"
    assert desktop["reason_code"] is None
    assert desktop["context_frame"]["host_kind"] == "desktop"
    assert desktop["context_frame"]["platform"] == "desktop_windows"
    assert desktop["context_frame"]["text"] == (
        "Synthetic cough review\nNo patient identifiers."
    )
    assert desktop["context_frame"]["line_count"] == 2
    assert web["status"] == "admitted"
    assert web["context_frame"]["host_kind"] == "web"
    assert web["context_frame"]["platform"] == "word_online"

    for response in (desktop, web):
        frame = response["context_frame"]
        assert frame["frame_type"] == "current_consult_note"
        assert frame["authority_label"] == "staff_selected"
        assert frame["source_scope"] == "active_document_selection"
        assert frame["data_classification"] == "authored_synthetic"
        assert frame["truncated"] is False
        assert all(value is False for value in frame["authority"].values())
        assert response["audit"] == {
            "document_read_count": 1,
            "document_write_count": 0,
            "provider_call_count": 0,
            "network_call_count": 0,
            "command_count": 0,
            "write_count": 0,
            "raw_text_persisted": False,
            "raw_text_logged": False,
        }


def test_single_use_replay_and_unsupported_hosts_fail_before_another_read(matrix):
    assert matrix["counts"] == {
        "desktopReads": 1,
        "webReads": 1,
        "blockedReads": 0,
    }
    expected = {
        "replay": "already_consumed",
        "mobile": "host_not_supported",
        "unknown": "host_not_supported",
        "hostNotReady": "host_not_ready",
        "invalid": "invalid_request",
        "denied": "grant_denied",
    }
    for key, reason in expected.items():
        response = matrix["responses"][key]
        assert response["status"] == "blocked"
        assert response["disposition"] == "edge_aborted"
        assert response["reason_code"] == reason
        assert response["context_frame"] is None
        assert response["audit"]["document_read_count"] == 0


def test_content_limits_and_read_error_fail_closed_without_raw_error(matrix):
    expected = {
        "empty": "selection_empty",
        "tooLarge": "selection_too_large",
        "tooManyLines": "selection_too_many_lines",
        "readError": "selection_read_failed",
    }
    for key, reason in expected.items():
        response = matrix["responses"][key]
        assert response["status"] == "blocked"
        assert response["reason_code"] == reason
        assert response["context_frame"] is None
        assert response["audit"]["document_read_count"] == 1
        assert "sensitive host error" not in json.dumps(response)


def test_requests_and_responses_are_deeply_immutable(matrix):
    assert matrix["frozen"] == {
        "request": True,
        "desktop": True,
        "blocked": True,
    }


def test_word_reader_accesses_only_the_current_selection_text(matrix):
    reader = matrix["wordReader"]
    assert reader["directText"] == "Synthetic direct selection."
    assert reader["wordCalls"] == {
        "run": 1,
        "getSelection": 1,
        "load": ["text"],
        "sync": 1,
    }


def test_adapter_source_has_no_network_storage_provider_body_or_write_path():
    source = _read(MODULE)
    required = (
        "context.document.getSelection()",
        'selection.load("text")',
        "current_consult_note",
        "local_authored_synthetic_fixture",
        "already_consumed",
    )
    for phrase in required:
        assert phrase in source

    prohibited = (
        "document.body",
        ".paragraphs",
        "customXmlParts",
        "insertText",
        "insertParagraph",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "localStorage",
        "sessionStorage",
        "getUserMedia",
        "MediaRecorder",
        "console.",
        "/analyze-consultation",
        "/scribe-consultation",
    )
    for phrase in prohibited:
        assert phrase not in source


def test_plan_and_threat_model_preserve_api_spine_and_clinical_gates():
    combined = f"{_read(PLAN)}\n{_read(THREAT)}".lower()
    for phrase in (
        "current_consult_note",
        "staff_selected",
        "active_document_selection",
        "explicit click",
        "single-use",
        "never reads `context.document.body`",
        "graphql remains read-only",
        "no rest command",
        "no provider",
        "no document write",
        "authored_synthetic",
        "authenticated word online execution remains unproven",
    ):
        assert phrase in combined


def test_taskpane_wiring_is_default_off_attested_and_counts_only():
    html = _read(HTML)
    taskpane = _read(TASKPANE)
    assert (
        'id="clinician-one-document-context" class="clinician-one-context hidden"'
        in html
    )
    assert 'id="clinician-one-synthetic-attestation"' in html
    assert 'id="btn-clinician-one-read-selection"' in html
    assert "task-created synthetic document" in html

    assert 'get("clinician_one_context_demo") === "true"' in taskpane
    assert "isClinicianOneDocumentContextDemoEnabled()" in taskpane
    assert "configureClinicianOneDocumentContext();" in taskpane
    assert "runtime.createWordSelectionReader(window.Word)" in taskpane
    handler = taskpane[
        taskpane.index("async function readClinicianOneDocumentContext")
        : taskpane.index("function configureClinicianOneDocumentContext")
    ]
    assert "frame.character_count" in handler
    assert "frame.line_count" in handler
    assert "frame.source_label" in handler
    assert "frame.host_kind" in handler
    assert "frame.text" not in handler
    assert "console." not in handler


def test_module_loads_between_host_profile_and_taskpane_in_both_copies():
    source_html = _read(HTML)
    published_html = _read(PUBLISHED / "taskpane.html")
    webpack = _read(WEBPACK)
    assert (
        webpack.index('"./src/taskpane/office-host-runtime.js"')
        < webpack.index('"./src/taskpane/clinician-one-document-context.js"')
        < webpack.index('"./src/taskpane/taskpane.js"')
    )
    assert source_html == published_html
    assert _read(MODULE) == _read(
        PUBLISHED / "clinician-one-document-context.js"
    )
    assert _read(TASKPANE) == _read(PUBLISHED / "taskpane.js")


def test_build_and_sync_paths_publish_the_adapter():
    webpack = _read(WEBPACK)
    sync = _read(SYNC)
    assert '"./src/taskpane/clinician-one-document-context.js"' in webpack
    assert 'taskpane: [' in webpack
    assert '"clinician-one-document-context.js",' in sync


def test_continuity_compass_and_handover_bind_the_accepted_adapter():
    graph = json.loads(_read(GRAPH))
    compass = json.loads(_read(COMPASS))
    nodes = {node["id"]: node for node in graph["nodes"]}
    node = nodes["clinician-one-readonly-document-context"]

    assert graph["graph_revision"] >= 174
    assert node["status"] == "accepted"
    assert {
        item["contract_id"]: item["status"]
        for item in node["contract_evidence"]
    } == {
        "combined-patient-practitioner-time-duration-intent": "satisfied",
        "committed-reschedule-availability-reconciliation": "satisfied",
    }
    assert compass["map_revision"] >= 155
    assert compass["source_graph_revision"] >= 174
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
    assert compass["current_position"]["node_id"] == compass["journey"][-1]["node_id"]
    assert "Clinician One Read-only Document Context" in _read(
        RENDERED_COMPASS
    )
    handover = _read(AGENTS)
    assert "clinician_one_readonly_document_context_adapter_pass" in handover
