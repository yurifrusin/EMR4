from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = ROOT / "orchestration" / "continuity" / "raisa-dual-host-foundation"
RUNTIME = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "office-host-runtime.js"
PUBLISHED_RUNTIME = ROOT / "docs" / "taskpane" / "office-host-runtime.js"
SCHEMA = CONTINUITY / "office-host-runtime-profile.schema.json"
OUTPUT = CONTINUITY / "host-profile-matrix-evidence.json"


NODE_SCRIPT = r"""
const runtime = require(process.argv[1]);
let calls = 0;
const fn = () => { calls += 1; };
function environment(options = {}) {
  const devicePermission = options.devicePermission !== false;
  const media = options.media !== false;
  return {
    office: {
      context: {
        ui: { displayDialogAsync: fn },
        document: { customXmlParts: {} },
        devicePermission: devicePermission
          ? { requestPermissionsAsync: fn }
          : {},
      },
      actions: { associate: fn },
      DevicePermission: devicePermission ? { microphone: "microphone" } : {},
    },
    word: { run: fn },
    navigator: media ? { mediaDevices: { getUserMedia: fn } } : {},
    mediaRecorder: media ? function MediaRecorder() {} : undefined,
    crypto: { randomUUID: fn },
  };
}
const fixtures = {
  word_desktop_windows: runtime.createOfficeHostProfile(
    { host: "Word", platform: "PC" },
    environment()
  ),
  word_online: runtime.createOfficeHostProfile(
    { host: "Word", platform: "OfficeOnline" },
    environment()
  ),
  word_online_without_device_permission: runtime.createOfficeHostProfile(
    { host: "Word", platform: "OfficeOnline" },
    environment({ devicePermission: false })
  ),
  word_mobile_without_media: runtime.createOfficeHostProfile(
    { host: "Word", platform: "iOS" },
    environment({ media: false })
  ),
};
process.stdout.write(JSON.stringify({
  calls,
  deeply_frozen: Object.values(fixtures).every(profile =>
    Object.isFrozen(profile) &&
    Object.isFrozen(profile.capabilities) &&
    Object.isFrozen(profile.features) &&
    Object.isFrozen(profile.authority)
  ),
  fixtures,
}));
"""


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def main() -> int:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js is required.")
    completed = subprocess.run(
        [node, "-e", NODE_SCRIPT, str(RUNTIME)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(completed.stdout)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    for profile in observed["fixtures"].values():
        validator.validate(profile)

    if observed["calls"] != 0:
        raise SystemExit("Host profiling invoked a capability.")
    if not observed["deeply_frozen"]:
        raise SystemExit("Host profiles are not deeply frozen.")
    if RUNTIME.read_bytes() != PUBLISHED_RUNTIME.read_bytes():
        raise SystemExit("Source and published host runtimes differ.")

    evidence = {
        "schema_version": "raisa.dual-host-foundation-evidence.v1",
        "result": "raisa_dual_host_foundation_pass",
        "evidence_mode": "authored_synthetic_deterministic_fixture",
        "runtime_sha256": _sha256(RUNTIME),
        "source_published_runtime_equal": True,
        "capability_invocation_count": observed["calls"],
        "profiles_deeply_frozen": observed["deeply_frozen"],
        "profiles": observed["fixtures"],
        "authority_counts": {
            "document_read": 0,
            "document_write": 0,
            "microphone_capture": 0,
            "network_access": 0,
            "provider_invocation": 0,
            "patient_context_read": 0,
            "clinical_context_read": 0,
            "command": 0,
            "write": 0,
        },
        "candid_limit": (
            "This is deterministic host-capability fixture evidence. It does "
            "not prove authenticated Word Online, microphone behavior, scribe "
            "correctness, backend/provider authorization, public branding, "
            "production, deployment or release."
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
