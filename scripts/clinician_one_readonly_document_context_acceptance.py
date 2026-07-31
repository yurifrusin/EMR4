from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
PUBLISHED = ROOT / "docs" / "taskpane"
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "clinician-one-readonly-document-context"
)
MODULE = SOURCE / "clinician-one-document-context.js"
HOST_RUNTIME = SOURCE / "office-host-runtime.js"
REQUEST_SCHEMA = CONTINUITY / "document-context-request.schema.json"
RESPONSE_SCHEMA = CONTINUITY / "document-context-response.schema.json"
OUTPUT = CONTINUITY / "adapter-evidence.json"


NODE_SCRIPT = r"""
const documentContext = require(process.argv[1]);
const hostRuntime = require(process.argv[2]);

function profile(platform) {
  return hostRuntime.createOfficeHostProfile(
    { host: "Word", platform },
    {
      office: { context: {}, actions: {} },
      word: { run: () => {} },
      navigator: {},
      crypto: {},
    }
  );
}
function request(suffix) {
  return documentContext.createLocalFixtureRequest(
    `clinician-context-${suffix}`
  );
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
  const desktopRequest = request("acceptance-desktop-001");
  const desktop = await desktopAdapter.read(desktopRequest, profile("PC"));
  const replay = await desktopAdapter.read(desktopRequest, profile("PC"));

  let webReads = 0;
  const webRequest = request("acceptance-web-001");
  const web = await documentContext
    .createClinicianDocumentContextAdapter({
      readSelectionText: async () => {
        webReads += 1;
        return "Synthetic web selection.";
      },
    })
    .read(webRequest, profile("OfficeOnline"));

  process.stdout.write(JSON.stringify({
    requests: { desktopRequest, webRequest },
    responses: { desktop, web, replay },
    readCounts: { desktopReads, webReads },
  }));
})().catch(error => {
  process.stderr.write(String(error && error.stack ? error.stack : error));
  process.exit(1);
});
"""


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def main() -> int:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js is required.")
    completed = subprocess.run(
        [node, "-e", NODE_SCRIPT, str(MODULE), str(HOST_RUNTIME)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(completed.stdout)
    request_schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    response_schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(request_schema)
    jsonschema.Draft202012Validator.check_schema(response_schema)
    for request in observed["requests"].values():
        jsonschema.validate(request, request_schema)
    for response in observed["responses"].values():
        jsonschema.validate(response, response_schema)

    desktop = observed["responses"]["desktop"]
    web = observed["responses"]["web"]
    replay = observed["responses"]["replay"]
    if desktop["status"] != "admitted" or web["status"] != "admitted":
        raise SystemExit("Desktop or web context frame was not admitted.")
    if replay["reason_code"] != "already_consumed":
        raise SystemExit("Single-use replay did not fail closed.")
    if observed["readCounts"] != {"desktopReads": 1, "webReads": 1}:
        raise SystemExit("Unexpected document-read count.")
    if MODULE.read_bytes() != (
        PUBLISHED / "clinician-one-document-context.js"
    ).read_bytes():
        raise SystemExit("Source and published adapters differ.")

    cases = {}
    for name, response in (("desktop", desktop), ("web", web)):
        frame = response.pop("context_frame")
        selection_text = frame.pop("text")
        cases[name] = {
            "status": response["status"],
            "disposition": response["disposition"],
            "host_kind": frame["host_kind"],
            "platform": frame["platform"],
            "source_label": frame["source_label"],
            "character_count": frame["character_count"],
            "line_count": frame["line_count"],
            "selection_sha256": _sha256_bytes(selection_text.encode("utf-8")),
            "truncated": frame["truncated"],
            "authority": frame["authority"],
            "audit": response["audit"],
        }

    evidence = {
        "schema_version": (
            "raisa.clinician-one-readonly-document-context-evidence.v1"
        ),
        "result": "clinician_one_readonly_document_context_adapter_pass",
        "evidence_mode": "authored_synthetic_dependency_injected_fixture",
        "adapter_sha256": _sha256_bytes(MODULE.read_bytes()),
        "source_published_adapter_equal": True,
        "cases": cases,
        "single_use": {
            "first_document_read_count": desktop["audit"][
                "document_read_count"
            ],
            "replay_status": replay["status"],
            "replay_reason_code": replay["reason_code"],
            "replay_document_read_count": replay["audit"][
                "document_read_count"
            ],
            "total_desktop_reader_invocations": observed["readCounts"][
                "desktopReads"
            ],
        },
        "durable_exclusions": {
            "raw_selection_text": False,
            "raw_office_error": False,
            "document_body": False,
            "patient_context": False,
            "provider_material": False,
            "credentials": False,
        },
        "candid_limit": (
            "Dependency-injected desktop and web fixtures do not prove real "
            "Word selection semantics, authenticated Word Online, Office "
            "identity, role authorization, clinical-data safety or "
            "production fitness."
        ),
    }
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": evidence["result"], "output": str(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
