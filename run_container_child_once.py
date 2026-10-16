"""Prospective finite two-slot interactive voice child. No admission.

The trusted native entry must supply exact frozen external binding and
independent-review pins, after durable coordinator grant consumption. A client
request or in-process assignment cannot supply launch authority. This file
neither imports a model nor runs Docker when imported.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import secrets
import stat
import subprocess
import threading
import time
import wave


IMAGE_ID = "sha256:192e420d4057bc851bb8db5af2495c35281fca92e56a76cec7f32cf8d3a6e1f9"
DOCKER_PATH = Path("C:/Program Files/Docker/Docker/resources/bin/docker.exe")
MIGRATION_ROOT = Path("C:/Users/there/EMR4-migration")
TOOLS_ROOT = Path("C:/Users/there/EMR4-tools")
CAPSULE_ROOT = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-offline-voice-child-qualification-source-v5/voicecapsule")
OUTPUT_ROOT = Path("C:/Users/there/EMR4-tools/stage1-offline-voice-container-child-v1")
CAPSULE_MANIFEST_SHA256 = "29cd4d946438a5d60a2bccc2d17ac12277b1a5d26d6b71f81ab8b819449ec87c"
CHILD_SCRIPT_SHA256 = "7889826df90b724eb1e43fc1ef7cc25d62db99342bd4e32a82ab6f5c6a52bd43"
STAGE1_ROOT = MIGRATION_ROOT / "20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2"
SOURCE_ROOT = STAGE1_ROOT / "stage1-voice-external-binding-source-v2"
RUNNER_PATH = SOURCE_ROOT / "run_container_child_once.py"
RUNNER_BYTES = 30852  # Frozen body size; no self-referential body digest.
LAUNCH_BINDING_PATH = SOURCE_ROOT / "interactive-voice-binding-v2.json"
LAUNCH_REVIEW_PATH = SOURCE_ROOT / "independent-voice-binding-review-v2.json"
NATIVE08_EFFECT_REVIEW_SHA256 = "818f7069444cdbed12c5baf1608bb4ccfa44b936b5db7e33182fad7af1b3b1c2"
# Factual dependency pin retained for the old inert upper adapter. This is
# never sufficient for launch; Q/R and durable consumption are still required.
CHILD_EFFECT_REVIEW_SHA256 = NATIVE08_EFFECT_REVIEW_SHA256
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
MAX_WAV = 512 * 1024
MAX_STDOUT = 4096
MAX_STDERR = 4096
CHILD_SECONDS = 45
OUTER_SECONDS = 300
LABEL = "org.emr4.stage1.voice-child-owner"
COMMAND = ["/opt/g2-tools/bin/python", "-I", "-B", "/capsule/container_child.py"]
_RUN_LOCK = threading.Lock()
_INTERACTIVE_USED_SLOTS: set[str] = set()
TMPFS = {
    "/tmp": "rw,noexec,nosuid,nodev,size=16777216,uid=10001,gid=10001,mode=0700",
    "/run/voice": "rw,exec,nosuid,nodev,size=134217728,uid=10001,gid=10001,mode=0700",
    # The accepted staff base image declares a PostgreSQL VOLUME. A dummy
    # read-only tmpfs prevents Docker allocating an automatic managed volume.
    "/var/lib/postgresql/data": "ro,noexec,nosuid,nodev,size=1048576,mode=0000",
}


class ChildUnavailable(RuntimeError):
    """No result or no proven cleanup. Never includes audio or transcript."""


@dataclass(frozen=True, repr=False)
class TrustedLaunchAuthority:
    """Values pinned by the reviewed native entry, never parsed from HTTP."""

    binding_path: Path
    binding_sha256: str
    review_path: Path
    review_sha256: str
    durable_consumption_confirmed: bool
    durable_consumption_grant_sha256: str
    durable_consumption_slot: str


@dataclass(frozen=True, repr=False)
class ExecutionBinding:
    docker_executable: Path
    docker_sha256: str
    capsule_root: Path
    owned_output_root: Path
    stage1_profile_sha256: str
    source_review_sha256: str
    execution_review_sha256: str
    finite_grant_sha256: str
    mode: str  # interactive-voice only; qualification uses frozen v5 runner
    child_effect_review_sha256: str | None = None
    interactive_slot: str | None = None  # finite patient/staff grant slots

    def ready(self, launch_authority: TrustedLaunchAuthority | None = None) -> bool:
        # The prior qualification runner and consumed grant are separate.
        try:
            return self._ready_checked(launch_authority)
        except (OSError, ValueError, KeyError, TypeError, ChildUnavailable,
                UnicodeError):
            return False

    def _ready_checked(self, launch_authority: TrustedLaunchAuthority | None) -> bool:
        common = (self.mode == "interactive-voice"
                  and self.docker_executable == DOCKER_PATH
                  and self.capsule_root == CAPSULE_ROOT
                  and self.owned_output_root == OUTPUT_ROOT
                  and not _reparse(self.docker_executable)
                  and not _reparse(self.capsule_root)
                  and not _reparse(self.owned_output_root)
                  and self.interactive_slot in ("patient", "staff"))
        if not common:
            return False
        return _reviewed_launch_matches(self, launch_authority)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _reparse(path: Path) -> bool:
    mode = path.stat(follow_symlinks=False)
    return bool(getattr(mode, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or path.is_symlink()


def _literal_directory_chain(approved_root: Path, selected: Path) -> None:
    """Lstat only declared path components; do not resolve a junction target."""
    try:
        parts = selected.relative_to(approved_root).parts
    except ValueError as exc:
        raise ChildUnavailable("VOICE_PATH_OUTSIDE_APPROVED_ROOT") from exc
    current = approved_root
    for segment in (None, *parts):
        if segment is not None:
            current = current / segment
        details = current.stat(follow_symlinks=False)
        if _reparse(current) or not stat.S_ISDIR(details.st_mode):
            raise ChildUnavailable("VOICE_DIRECTORY_REPARSE_OR_INVALID")


def _checked_pinned_bytes(path: Path, expected_sha256: str, maximum: int,
                          exact_bytes: int | None = None) -> bytes:
    if (not isinstance(path, Path) or not path.is_absolute()
            or ".." in path.parts or not path.is_relative_to(STAGE1_ROOT)
            or type(expected_sha256) is not str
            or SHA256_PATTERN.fullmatch(expected_sha256) is None
            or type(maximum) is not int or not 1 <= maximum <= 65536
            or (exact_bytes is not None and
                (type(exact_bytes) is not int or not 1 <= exact_bytes <= maximum))):
        raise ValueError("VOICE_LAUNCH_PIN_INVALID")
    _literal_directory_chain(MIGRATION_ROOT, path.parent)
    before = path.stat(follow_symlinks=False)
    if (_reparse(path) or not stat.S_ISREG(before.st_mode)
            or not 1 <= before.st_size <= maximum or not before.st_ino
            or (exact_bytes is not None and before.st_size != exact_bytes)):
        raise ValueError("VOICE_LAUNCH_PIN_INVALID")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode)
                or getattr(opened, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
                or (opened.st_dev, opened.st_ino) !=
                   (before.st_dev, before.st_ino)
                or not 1 <= opened.st_size <= maximum
                or (exact_bytes is not None and opened.st_size != exact_bytes)):
            raise ValueError("VOICE_LAUNCH_PIN_INVALID")
        raw = stream.read(maximum + 1)
        after_handle = os.fstat(stream.fileno())
    after_path = path.stat(follow_symlinks=False)
    _literal_directory_chain(MIGRATION_ROOT, path.parent)
    if (_reparse(path) or not stat.S_ISREG(after_path.st_mode)
            or len(raw) > maximum or len(raw) != after_handle.st_size
            or (exact_bytes is not None and len(raw) != exact_bytes)
            or (after_handle.st_dev, after_handle.st_ino) !=
               (before.st_dev, before.st_ino)
            or (after_path.st_dev, after_path.st_ino) !=
               (before.st_dev, before.st_ino)
            or after_path.st_size != len(raw)
            or hashlib.sha256(raw).hexdigest() != expected_sha256):
        raise ValueError("VOICE_LAUNCH_PIN_DRIFT")
    return raw


def _pinned_launch_json(path: Path, expected_sha256: str) -> dict:
    if not isinstance(path, Path) or path not in (
            LAUNCH_BINDING_PATH, LAUNCH_REVIEW_PATH):
        raise ValueError("VOICE_LAUNCH_PATH_UNREVIEWED")
    raw = _checked_pinned_bytes(path, expected_sha256, 16384)

    def unique_object(pairs):
        row = {}
        for key, value in pairs:
            if key in row:
                raise ValueError("VOICE_LAUNCH_DUPLICATE_KEY")
            row[key] = value
        return row

    result = json.loads(raw, object_pairs_hook=unique_object)
    if type(result) is not dict:
        raise ValueError("VOICE_LAUNCH_SCHEMA_INVALID")
    return result


def _reviewed_launch_matches(binding: ExecutionBinding,
                             launch: TrustedLaunchAuthority | None) -> bool:
    # The native entry alone supplies these expected digests and records its
    # durable grant consumption before invoking run_once. This validator
    # checks their exact relationship; it cannot authenticate an HTTP caller.
    if (type(launch) is not TrustedLaunchAuthority
            or launch.durable_consumption_confirmed is not True
            or launch.durable_consumption_grant_sha256 != binding.finite_grant_sha256
            or launch.durable_consumption_slot != binding.interactive_slot
            or launch.binding_path == launch.review_path):
        return False
    q = _pinned_launch_json(launch.binding_path, launch.binding_sha256)
    r = _pinned_launch_json(launch.review_path, launch.review_sha256)
    required_q = {
        "schema", "operative", "mode", "attempts", "automatic_retry", "slots",
        "runner_path", "runner_sha256", "docker_executable", "docker_sha256",
        "image_id", "capsule_root", "capsule_manifest_sha256",
        "child_script_sha256", "owned_output_root", "stage1_profile_sha256",
        "child_effect_review_sha256", "durable_consumption_required",
    }
    if set(q) != required_q:
        return False
    digests = (
        "runner_sha256", "docker_sha256", "stage1_profile_sha256",
        "child_effect_review_sha256",
    )
    if any(type(q[key]) is not str or SHA256_PATTERN.fullmatch(q[key]) is None
           for key in digests):
        return False
    if any(type(value) is not str or SHA256_PATTERN.fullmatch(value) is None
           for value in (binding.source_review_sha256,
                         binding.execution_review_sha256,
                         binding.finite_grant_sha256)):
        return False
    if (type(q["runner_path"]) is not str
            or Path(q["runner_path"]) != RUNNER_PATH
            or ".." in Path(q["runner_path"]).parts):
        return False
    _checked_pinned_bytes(RUNNER_PATH, q["runner_sha256"],
                          RUNNER_BYTES, RUNNER_BYTES)
    if (q["schema"] != "emr4.stage1_interactive_voice_external_binding.v1"
            or q["operative"] is not True
            or q["mode"] != "interactive-voice"
            or type(q["attempts"]) is not int or q["attempts"] != 2
            or q["automatic_retry"] is not False
            or q["slots"] != ["patient", "staff"]
            or q["durable_consumption_required"] is not True
            or type(q["docker_executable"]) is not str
            or Path(q["docker_executable"]) != DOCKER_PATH
            or q["docker_sha256"] != binding.docker_sha256
            or q["image_id"] != IMAGE_ID
            or type(q["capsule_root"]) is not str
            or Path(q["capsule_root"]) != CAPSULE_ROOT
            or q["capsule_manifest_sha256"] != CAPSULE_MANIFEST_SHA256
            or q["child_script_sha256"] != CHILD_SCRIPT_SHA256
            or type(q["owned_output_root"]) is not str
            or Path(q["owned_output_root"]) != OUTPUT_ROOT
            or q["stage1_profile_sha256"] != binding.stage1_profile_sha256
            or q["child_effect_review_sha256"] != NATIVE08_EFFECT_REVIEW_SHA256
            or binding.child_effect_review_sha256 != NATIVE08_EFFECT_REVIEW_SHA256):
        return False
    if (type(r.get("independent")) is not bool
            or type(r.get("implementation_authorship")) is not bool
            or type(r.get("attempts")) is not int
            or type(r.get("durable_consumption_required")) is not bool):
        return False
    return r == {
        "schema": "emr4.stage1_interactive_voice_external_binding_review.v1",
        "verdict": "PASS_STAGE1_INTERACTIVE_VOICE_EXTERNAL_BINDING",
        "independent": True,
        "implementation_authorship": False,
        "blocking_findings": [],
        "binding_sha256": launch.binding_sha256,
        "runner_sha256": q["runner_sha256"],
        "source_review_sha256": binding.source_review_sha256,
        "execution_review_sha256": binding.execution_review_sha256,
        "finite_grant_sha256": binding.finite_grant_sha256,
        "child_effect_review_sha256": NATIVE08_EFFECT_REVIEW_SHA256,
        "mode": "interactive-voice",
        "attempts": 2,
        "slots": ["patient", "staff"],
        "durable_consumption_required": True,
    }


def _exact_capsule_tree(root: Path, expected_files: set[str]) -> None:
    """Inspect only declared owned directories; never descend into extras."""
    tree: dict[PurePosixPath, dict[str, str]] = {PurePosixPath("."): {}}
    for item in expected_files:
        rel = PurePosixPath(item)
        if (rel.is_absolute() or not rel.parts or any(part in (".", "..") for part in rel.parts)
                or "\\" in item or item.startswith("/")):
            raise ChildUnavailable("VOICE_CAPSULE_INVALID")
        parent = PurePosixPath(".")
        for part in rel.parts[:-1]:
            tree.setdefault(parent, {})[part] = "directory"
            parent = parent / part
            tree.setdefault(parent, {})
        tree.setdefault(parent, {})[rel.parts[-1]] = "file"
    for relative, children in tree.items():
        directory = root.joinpath(*relative.parts)
        if _reparse(directory):
            raise ChildUnavailable("VOICE_CAPSULE_REPARSE")
        with os.scandir(directory) as entries:
            found = {entry.name: entry for entry in entries}
        if set(found) != set(children):
            raise ChildUnavailable("VOICE_CAPSULE_EXTRA_OR_MISSING_ENTRY")
        for name, expected_kind in children.items():
            entry = found[name]
            details = entry.stat(follow_symlinks=False)
            if (entry.is_symlink()
                    or getattr(details, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
                raise ChildUnavailable("VOICE_CAPSULE_REPARSE")
            if expected_kind == "file" and not stat.S_ISREG(details.st_mode):
                raise ChildUnavailable("VOICE_CAPSULE_INVALID")
            if expected_kind == "directory" and not stat.S_ISDIR(details.st_mode):
                raise ChildUnavailable("VOICE_CAPSULE_INVALID")


def validate_wav(raw: bytes) -> None:
    if (not isinstance(raw, bytes) or not 44 <= len(raw) <= MAX_WAV
            or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE"
            or int.from_bytes(raw[4:8], "little") + 8 != len(raw)):
        raise ChildUnavailable("VOICE_WAV_INVALID")
    try:
        with wave.open(io.BytesIO(raw), "rb") as source:
            if (source.getnchannels() != 1 or source.getsampwidth() != 2
                    or source.getframerate() != 16000 or source.getcomptype() != "NONE"
                    or not 1 <= source.getnframes() <= 192000
                    or len(source.readframes(192001)) != source.getnframes() * 2):
                raise ChildUnavailable("VOICE_WAV_INVALID")
    except (wave.Error, EOFError) as exc:
        raise ChildUnavailable("VOICE_WAV_INVALID") from exc


def verify_capsule(root: Path) -> None:
    if _reparse(root) or not root.is_dir():
        raise ChildUnavailable("VOICE_CAPSULE_INVALID")
    for name in ("capsule-manifest.json", "container_child.py"):
        declared = root / name
        if _reparse(declared) or not stat.S_ISREG(declared.stat(follow_symlinks=False).st_mode):
            raise ChildUnavailable("VOICE_CAPSULE_REPARSE_OR_INVALID")
    if (sha(root / "capsule-manifest.json") != CAPSULE_MANIFEST_SHA256
            or CHILD_SCRIPT_SHA256 is None):
        raise ChildUnavailable("VOICE_CAPSULE_INVALID")
    document = json.loads((root / "capsule-manifest.json").read_text(encoding="utf-8"))
    rows = document.get("files")
    if document.get("schema") != "emr4.stage1_voice_capsule.v1" or not isinstance(rows, list) or len(rows) != 19:
        raise ChildUnavailable("VOICE_CAPSULE_INVALID")
    expected_files = {row["path"] for row in rows}
    if len(expected_files) != 19:
        raise ChildUnavailable("VOICE_CAPSULE_INVALID")
    expected_files.update(("capsule-manifest.json", "container_child.py"))
    _exact_capsule_tree(root, expected_files)
    if sha(root / "container_child.py") != CHILD_SCRIPT_SHA256:
        raise ChildUnavailable("VOICE_CAPSULE_INVALID")
    names = set()
    for row in rows:
        name = row["path"]
        if (not isinstance(name, str) or name in names or name.startswith("/")
                or "\\" in name or ".." in Path(name).parts):
            raise ChildUnavailable("VOICE_CAPSULE_INVALID")
        names.add(name)
        source = root / name
        if (_reparse(source)
                or not stat.S_ISREG(source.stat(follow_symlinks=False).st_mode)
                or source.stat(follow_symlinks=False).st_size != row["bytes"]
                or sha(source) != row["sha256"]):
            raise ChildUnavailable("VOICE_CAPSULE_INVALID")


def _call(docker: Path, args: list[str], env: dict[str, str], seconds: int = 15) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(docker), *args], input=b"", stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, timeout=seconds, check=False,
                          shell=False, env=env)


def _inspect(docker: Path, cid: str, env: dict[str, str]) -> dict:
    result = _call(docker, ["inspect", cid], env)
    if result.returncode or len(result.stdout) > 64 * 1024:
        raise ChildUnavailable("VOICE_INSPECT_UNAVAILABLE")
    rows = json.loads(result.stdout)
    if not isinstance(rows, list) or len(rows) != 1:
        raise ChildUnavailable("VOICE_INSPECT_UNAVAILABLE")
    return rows[0]


def _check_created(row: dict, cid: str, owner: str, capsule: Path) -> None:
    config, host = row["Config"], row["HostConfig"]
    mounts = row["Mounts"]
    host_mounts = host["Mounts"]
    expected_mount = str(capsule)
    if (row["Id"] != cid or row["Name"] != "/stage1-voice-" + owner
            or row["Image"] != IMAGE_ID
            or row["State"]["Status"] != "created"
            or config["Labels"].get(LABEL) != owner
            or config["User"] != "10001:10001"
            or config["WorkingDir"] != "/tmp"
            or config["Entrypoint"] != [COMMAND[0]]
            or config["Cmd"] != COMMAND[1:]
            or config["OpenStdin"] is not True
            or config["Tty"] is not False
            or host["NetworkMode"] != "none"
            or host["ReadonlyRootfs"] is not True
            or host["Privileged"] is not False
            or "ALL" not in host["CapDrop"]
            or "no-new-privileges" not in host["SecurityOpt"]
            or host["Memory"] != 1024 * 1024 * 1024
            or host["NanoCpus"] != 1_000_000_000
            or host["PidsLimit"] != 128
            or host["PortBindings"] not in (None, {})
            or host["Devices"] not in (None, [])
            or host["AutoRemove"] is not False
            or host["LogConfig"]["Type"] != "none"
            or host["RestartPolicy"]["Name"] not in ("no", "")
            or host["Binds"] not in (None, [])
            or host["VolumesFrom"] not in (None, [])
            or len(host_mounts) != 1 or host_mounts[0]["Type"] != "bind"
            or host_mounts[0]["Target"] != "/capsule"
            or host_mounts[0]["ReadOnly"] is not True
            or host_mounts[0]["Source"].replace("\\", "/").casefold() != expected_mount.replace("\\", "/").casefold()
            or len(mounts) != 4
            or {item["Destination"] for item in mounts} != {"/capsule", *TMPFS}
            or any(item["Type"] == "volume" for item in mounts)
            or any(item["Type"] != ("bind" if item["Destination"] == "/capsule" else "tmpfs") for item in mounts)
            or any(item["RW"] for item in mounts if item["Destination"] == "/capsule")
            or host["Tmpfs"] != TMPFS):
        raise ChildUnavailable("VOICE_CONTAINER_CONTAINMENT_UNPROVEN")


def _stream(docker: Path, cid: str, raw: bytes, env: dict[str, str]) -> bytes:
    process = subprocess.Popen([str(docker), "start", "--attach", "--interactive", cid],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=False, env=env)
    chunks: list[bytes] = []
    overflow = threading.Event()
    writer_errors: list[str] = []

    def feed():
        try:
            process.stdin.write(raw)
            process.stdin.close()
        except OSError:
            writer_errors.append("WRITE_FAILED")

    def drain(stream, limit, collect):
        seen = 0
        while True:
            block = stream.read(512)
            if not block:
                return
            seen += len(block)
            if seen > limit:
                overflow.set()
                try:
                    process.kill()
                except OSError:
                    pass
                return
            if collect:
                chunks.append(block)

    readers = [threading.Thread(target=drain, args=(process.stdout, MAX_STDOUT, True), daemon=True),
               threading.Thread(target=drain, args=(process.stderr, MAX_STDERR, False), daemon=True)]
    writer = threading.Thread(target=feed, daemon=True)
    for reader in readers:
        reader.start()
    writer.start()
    try:
        deadline = time.monotonic() + CHILD_SECONDS
        while process.poll() is None and time.monotonic() < deadline and not overflow.is_set():
            time.sleep(0.05)
        timed_out = time.monotonic() >= deadline
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        writer.join(timeout=2)
        for reader in readers:
            reader.join(timeout=2)
        if (timed_out or process.returncode != 0 or overflow.is_set()
                or writer.is_alive() or writer_errors
                or any(reader.is_alive() for reader in readers)):
            raise ChildUnavailable("VOICE_CHILD_FAILED")
        return b"".join(chunks)
    except (OSError, subprocess.TimeoutExpired) as exc:
        process.kill()
        raise ChildUnavailable("VOICE_CHILD_FAILED") from exc
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)


def run_once(raw: bytes, binding: ExecutionBinding, *,
             launch_authority: TrustedLaunchAuthority | None = None) -> str:
    """One effect only, after a trusted entry supplies reviewed launch pins."""
    if not _RUN_LOCK.acquire(blocking=False):
        raise ChildUnavailable("VOICE_CHILD_ALREADY_ACTIVE")
    try:
        return _run_once_locked(raw, binding, launch_authority)
    finally:
        _RUN_LOCK.release()


def _run_once_locked(raw: bytes, binding: ExecutionBinding,
                     launch_authority: TrustedLaunchAuthority | None) -> str:
    validate_wav(raw)
    if type(binding) is not ExecutionBinding or not binding.ready(launch_authority):
        raise ChildUnavailable("VOICE_EXECUTION_NOT_ADMITTED")
    # _RUN_LOCK covers this process-wide claim. Reconstructing a binding
    # cannot reuse either slot under the reviewed finite two-slot grant.
    if binding.interactive_slot in _INTERACTIVE_USED_SLOTS:
        raise ChildUnavailable("VOICE_INTERACTIVE_SLOT_CONSUMED")
    _INTERACTIVE_USED_SLOTS.add(binding.interactive_slot)
    deadline = time.monotonic() + OUTER_SECONDS
    _literal_directory_chain(MIGRATION_ROOT, binding.capsule_root)
    verify_capsule(binding.capsule_root)
    _literal_directory_chain(TOOLS_ROOT, binding.owned_output_root)
    if (_reparse(binding.docker_executable)
            or sha(binding.docker_executable) != binding.docker_sha256):
        raise ChildUnavailable("VOICE_BINDING_INVALID")
    owner = secrets.token_hex(16)
    name = "stage1-voice-" + owner
    intent = binding.owned_output_root / (name + ".intent.json")
    docker_config = binding.owned_output_root / "empty-docker-config"
    _literal_directory_chain(TOOLS_ROOT, docker_config)
    if tuple(docker_config.iterdir()):
        raise ChildUnavailable("VOICE_DOCKER_CONFIG_UNTRUSTED")
    # Recheck both owned write roots immediately before the first open. No
    # resolve() call may turn a same-path junction into apparent identity.
    _literal_directory_chain(TOOLS_ROOT, binding.owned_output_root)
    _literal_directory_chain(TOOLS_ROOT, docker_config)
    # The trusted entry freezes Q/R; check again before the first effect.
    if not _reviewed_launch_matches(binding, launch_authority):
        raise ChildUnavailable("VOICE_EXECUTION_NOT_ADMITTED")
    system_root = os.environ.get("SystemRoot")
    if not system_root:
        raise ChildUnavailable("VOICE_SYSTEM_ROOT_UNAVAILABLE")
    env = {"SystemRoot": system_root,
           "PATH": os.pathsep.join((str(binding.docker_executable.parent),
                                    str(Path(system_root) / "System32"))),
           "DOCKER_HOST": "npipe:////./pipe/docker_engine",
           "DOCKER_CONFIG": str(docker_config),
           "DOCKER_BUILDKIT": "0"}
    with intent.open("x", encoding="utf-8") as output:
        json.dump({"owner": owner, "image": IMAGE_ID, "mode": binding.mode,
                   "status": "attempt_started"}, output, sort_keys=True)
    docker = binding.docker_executable
    cid = None
    cleaned = False
    result_verified = False
    try:
        command = ["create", "--pull=never", "--interactive", "--name", name,
                   "--label", LABEL + "=" + owner, "--network=none", "--read-only",
                   "--log-driver=none",
                   "--cap-drop=ALL", "--security-opt=no-new-privileges",
                   "--cpus=1", "--memory=1024m", "--pids-limit=128",
                   "--user=10001:10001", "--workdir=/tmp",
                   "--entrypoint=" + COMMAND[0]]
        for target, options in TMPFS.items():
            command += ["--tmpfs", target + ":" + options]
        command += ["--mount", "type=bind,source=" + str(binding.capsule_root)
                    + ",target=/capsule,readonly", IMAGE_ID, *COMMAND[1:]]
        _literal_directory_chain(MIGRATION_ROOT, binding.capsule_root)
        _literal_directory_chain(TOOLS_ROOT, binding.owned_output_root)
        _literal_directory_chain(TOOLS_ROOT, docker_config)
        result = _call(docker, command, env, seconds=30)
        if result.returncode or len(result.stdout) > 128:
            raise ChildUnavailable("VOICE_CREATE_UNCERTAIN")
        cid = result.stdout.decode("ascii").strip()
        if len(cid) != 64 or any(char not in "0123456789abcdef" for char in cid):
            raise ChildUnavailable("VOICE_CREATE_UNCERTAIN")
        _check_created(_inspect(docker, cid, env), cid, owner, binding.capsule_root)
        payload = _stream(docker, cid, raw, env)
        row = _inspect(docker, cid, env)
        if row["State"]["Status"] != "exited" or row["State"]["ExitCode"] != 0:
            raise ChildUnavailable("VOICE_CHILD_FAILED")
        if time.monotonic() > deadline:
            raise ChildUnavailable("VOICE_OUTER_LIMIT")
        result_data = json.loads(payload)
        transcript = result_data.get("text") if isinstance(result_data, dict) else None
        if not isinstance(transcript, str) or len(transcript) > 500:
            raise ChildUnavailable("VOICE_RESULT_INVALID")
        result_verified = True
        return transcript.strip()
    finally:
        # On uncertain create, look up only the exact name and matching owner.
        if cid is None:
            found = _call(docker, ["ps", "-aq", "--no-trunc", "--filter", "name=^/" + name + "$",
                                   "--filter", "label=" + LABEL + "=" + owner], env)
            possible = found.stdout.decode("ascii", errors="ignore").strip()
            if len(possible) == 64 and all(c in "0123456789abcdef" for c in possible):
                cid = possible
            # A lost create response can complete after an empty snapshot.
            # Keep the intent unresolved; an empty ps is never cleanup proof.
        if cid is not None:
            try:
                row = _inspect(docker, cid, env)
                if (row["Id"] != cid or row["Name"] != "/" + name
                        or row["Config"]["Labels"].get(LABEL) != owner):
                    raise ChildUnavailable("VOICE_OWNERSHIP_UNPROVEN")
                removed = _call(docker, ["rm", "-f", cid], env, seconds=15)
                if removed.returncode:
                    raise ChildUnavailable("VOICE_CLEANUP_UNPROVEN")
                absent = _call(docker, ["inspect", cid], env)
                cleaned = absent.returncode != 0
            except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
                cleaned = False
        if not cleaned:
            _literal_directory_chain(TOOLS_ROOT, binding.owned_output_root)
            with (binding.owned_output_root / (name + ".uncertain.json")).open("x", encoding="utf-8") as output:
                json.dump({"owner": owner, "cleanup_verified": False,
                           "result_verified": False, "status": "unresolved_attempt"},
                          output, sort_keys=True)
            raise ChildUnavailable("VOICE_CLEANUP_UNPROVEN")
        _literal_directory_chain(TOOLS_ROOT, binding.owned_output_root)
        with (binding.owned_output_root / (name + ".result.json")).open("x", encoding="utf-8") as output:
            json.dump({"owner": owner, "cleanup_verified": True,
                       "result_verified": result_verified}, output, sort_keys=True)


def synthetic_silence_wav() -> bytes:
    """Future one-shot nonpatient qualification input, generated in memory."""
    output = io.BytesIO()
    with wave.open(output, "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(16000)
        target.writeframes(b"\0" * 32000)
    return output.getvalue()
