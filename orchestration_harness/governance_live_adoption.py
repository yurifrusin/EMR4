"""Single-owner live publication for Ariadne repository governance."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, NoReturn

from orchestration_harness import transactional_closeout as tc
from orchestration_harness.governance_writer_guard import POINTER_VERSION
from scripts import ariadne_compass


CONTRACT_VERSION = "ariadne.governance_live_adoption_contract.v1"
INTENT_VERSION = "ariadne.governance_live_adoption_intent.v1"
INVENTORY_VERSION = "ariadne.governance_writer_inventory.v1"
GENERATION_VERSION = "ariadne.governance_live_generation.v1"
OWNERSHIP_VERSION = "ariadne.governance_live_ownership.v1"
TRANSACTION_VERSION = "ariadne.governance_live_transaction.v1"
COMMAND_VERSION = "ariadne.governance_command_manifest.v1"
WRITER = "clockwork"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CANONICAL_KEYS = (
    "continuity",
    "compass",
    "compass_markdown",
    "active_latch",
    "error_register",
    "pattern_report",
    "current_baton",
)
METADATA_NAMES = (
    "command-manifest.json",
    "transaction.json",
    "ownership.json",
)
DERIVED_KEYS = {
    "source_commit",
    "source_head",
    "graph_revision",
    "map_revision",
    "register_revision",
    "incident_population",
    "latest_incident_id",
    "transaction_id",
    "generation_id",
    "lease_id",
    "output_path",
    "bundle_sha256",
}


class AdoptionRejection(ValueError):
    """A live-adoption condition failed before the pointer commit."""


class CommittedAdoption(RuntimeError):
    """An injected exception occurred after a complete pointer commit."""


def _reject(rule: str) -> NoReturn:
    raise AdoptionRejection(rule)


def _exact(value: object, keys: set[str], rule: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject(rule)
    return value


def _json_text(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_json(value: object) -> str:
    return _hash_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
    )


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AdoptionRejection("json_read") from error
    if not isinstance(value, dict):
        _reject("json_object")
    return value


def _safe_path(raw: object, rule: str) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        _reject(rule)
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or raw.startswith("docs/branding/"):
        _reject(rule)
    return raw


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_all_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value), set())
    return set()


def _git(repo_root: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
    except subprocess.CalledProcessError as error:
        raise AdoptionRejection("git_read") from error


def _git_bytes(repo_root: Path, source: str, relative: str) -> bytes:
    if not HEX40.fullmatch(source):
        _reject("git_source")
    try:
        return subprocess.run(
            ["git", "show", f"{source}:{relative}"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as error:
        raise AdoptionRejection("git_file_read") from error


def validate_contract(value: object) -> dict[str, Any]:
    keys = {
        "schema_version",
        "operation_id",
        "required_ancestor",
        "accepted_rehearsal_source",
        "protected_commit",
        "canonical_paths",
        "clockwork_root",
        "writer_inventory",
        "legacy_writer_classes",
        "commands",
        "selected_command_ids",
        "baton_acceptance_paths",
    }
    row = _exact(value, keys, "contract_keys")
    if row["schema_version"] != CONTRACT_VERSION:
        _reject("contract_version")
    for field in ("required_ancestor", "accepted_rehearsal_source", "protected_commit"):
        if not isinstance(row[field], str) or not HEX40.fullmatch(row[field]):
            _reject("contract_oid")
    canonical = _exact(row["canonical_paths"], set(CANONICAL_KEYS), "canonical_paths")
    paths = [*canonical.values(), row["clockwork_root"], row["writer_inventory"], *row["baton_acceptance_paths"]]
    for raw in paths:
        _safe_path(raw, "contract_path")
    if len(set(canonical.values())) != len(CANONICAL_KEYS):
        _reject("canonical_path_duplicate")
    expected_classes = [
        "bespoke_continuity_updater",
        "manual_baton_editor",
        "manual_latch_editor",
        "manual_register_fixture_editor",
    ]
    if row["legacy_writer_classes"] != expected_classes:
        _reject("legacy_writer_classes")
    if not isinstance(row["commands"], list) or not row["commands"]:
        _reject("commands")
    command_ids: list[str] = []
    for raw in row["commands"]:
        command = _exact(
            raw,
            {"command_id", "executable", "arguments", "completion_contract"},
            "command_keys",
        )
        operands = [command["executable"], *command["arguments"]]
        if (
            command["completion_contract"] != "final_exit_code_zero_required"
            or not isinstance(command["arguments"], list)
            or not all(isinstance(item, str) and item for item in operands)
            or any(any(mark in item for mark in "*?[]") for item in operands)
        ):
            _reject("command_contract")
        command_ids.append(command["command_id"])
    if len(command_ids) != len(set(command_ids)) or row["selected_command_ids"] != command_ids:
        _reject("command_selection")
    if not isinstance(row["baton_acceptance_paths"], list) or not row["baton_acceptance_paths"]:
        _reject("baton_acceptance_paths")
    return row


def validate_intent(value: object, contract: dict[str, Any]) -> dict[str, Any]:
    row = _exact(value, {"schema_version", "transaction_manifest", "command_ids"}, "intent_keys")
    if row["schema_version"] != INTENT_VERSION or row["command_ids"] != contract["selected_command_ids"]:
        _reject("intent_version_or_commands")
    if _all_keys(row) & DERIVED_KEYS:
        _reject("caller_authored_derived_binding")
    try:
        manifest = tc.validate_manifest(row["transaction_manifest"])
    except ValueError as error:
        raise AdoptionRejection("transaction_manifest") from error
    if (
        manifest["operation_id"] != contract["operation_id"]
        or manifest["broker"] != {"enabled": False, "posture": "provider_free_shadow"}
    ):
        _reject("intent_authority")
    return {
        "schema_version": row["schema_version"],
        "transaction_manifest": manifest,
        "command_ids": list(row["command_ids"]),
    }


def validate_writer_inventory(repo_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    inventory = _exact(
        _load(repo_root / contract["writer_inventory"]),
        {
            "schema_version",
            "operation_id",
            "historical_updater_glob",
            "historical_updater_count",
            "sorted_path_list_sha256",
            "shared_compass_guard_count",
            "explicit_entry_guard_paths",
            "canonical_authority_paths",
            "legacy_writer_classes",
        },
        "inventory_keys",
    )
    if inventory["schema_version"] != INVENTORY_VERSION or inventory["operation_id"] != contract["operation_id"]:
        _reject("inventory_version")
    paths = sorted(
        f"scripts/{path.name}"
        for path in (repo_root / "scripts").glob("*continuity_update.py")
        if path.is_file()
    )
    digest = _hash_bytes((("\n".join(paths)) + "\n").encode("utf-8"))
    shared = [path for path in paths if "ariadne_compass" in (repo_root / path).read_text(encoding="utf-8")]
    explicit = sorted(set(paths) - set(shared))
    if (
        len(paths) != inventory["historical_updater_count"]
        or digest != inventory["sorted_path_list_sha256"]
        or len(shared) != inventory["shared_compass_guard_count"]
        or explicit != inventory["explicit_entry_guard_paths"]
        or inventory["canonical_authority_paths"] != contract["canonical_paths"]
        or inventory["legacy_writer_classes"] != contract["legacy_writer_classes"]
    ):
        _reject("writer_inventory_drift")
    guard_token = "refuse_retired_legacy_writer"
    if guard_token not in (repo_root / "scripts/ariadne_compass.py").read_text(encoding="utf-8"):
        _reject("shared_guard_missing")
    if any(guard_token not in (repo_root / path).read_text(encoding="utf-8") for path in explicit):
        _reject("explicit_guard_missing")
    return inventory


def _assert_git_state(
    repo_root: Path, contract: dict[str, Any], expected_source: str | None = None
) -> str:
    source = _git(repo_root, "rev-parse", "HEAD")
    if not HEX40.fullmatch(source) or (expected_source is not None and source != expected_source):
        _reject("source_head")
    protected = {
        _git(repo_root, "rev-parse", ref)
        for ref in ("master", "handoff/current", "origin/master", "origin/handoff/current")
    }
    if protected != {contract["protected_commit"]}:
        _reject("protected_refs")
    _git(repo_root, "merge-base", "--is-ancestor", contract["required_ancestor"], source)
    _git(repo_root, "merge-base", "--is-ancestor", contract["accepted_rehearsal_source"], source)
    return source


def _canonical_bytes(repo_root: Path, contract: dict[str, Any]) -> dict[str, bytes]:
    root = repo_root.resolve()
    result: dict[str, bytes] = {}
    for key, relative in contract["canonical_paths"].items():
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            _reject("canonical_escape")
        if not path.is_file():
            _reject("canonical_missing")
        result[key] = path.read_bytes()
    return result


def _source_bytes(
    repo_root: Path, contract: dict[str, Any], source: str
) -> dict[str, bytes]:
    return {
        key: _git_bytes(repo_root, source, relative)
        for key, relative in contract["canonical_paths"].items()
    }


def _replace_table_row(text: str, label: str, value: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(matches) != 1:
        _reject("baton_row")
    return text.replace(matches[0], f"| {label} | {value} |", 1)


def _render_agents(
    current: str,
    contract: dict[str, Any],
    manifest: dict[str, Any],
    graph: dict[str, Any],
    compass: dict[str, Any],
    source: str,
) -> str:
    title = manifest["title"]
    result = (
        f"At Continuity {graph['graph_revision']} / Compass {compass['map_revision']}, {title} is accepted at exact reviewed source `{source}`. "
        "All ten repository-governance surfaces have one clockwork owner, zero have dual ownership, four legacy writer classes are retired, and the exact previous Git generation remains byte-recoverable. The first live tick uses one validated intent and no bespoke updater."
    )
    successor = manifest["next_operation"]
    next_value = (
        f"Proceed under standing authority with `{successor['operation_id']}`: {successor['objective']} "
        "It is provider-free and read-only; occupied DeepSeek/HMR, ordinary-practice enablement, product/data/runtime/deployment/release/Pages and protected-ref movement remain closed. Preserve `docs/branding/`; stage explicit paths only."
    )
    current = _replace_table_row(current, "Current result", result)
    current = _replace_table_row(current, "Next implementation", next_value)
    old_prefix = "| Current shadow clockwork relation |"
    old = [line for line in current.splitlines() if line.startswith(old_prefix)]
    if len(old) != 1:
        _reject("clockwork_relation_row")
    relation = (
        f"| Current clockwork relation | The task branch has one live repository-governance clockwork owner at exact reviewed source `{source}`. "
        "The accepted mirror safety floor `d03cc6386fdf3e2714881089514380d93824e160` remains an ancestor; four historical writer classes are retired without deleting their evidence, and exact Git-backed rollback remains available. This opens no product, provider, deployment or protected-ref authority. |"
    )
    current = current.replace(old[0], relation, 1)
    label = "Ariadne provider-free clockwork live canonical adoption and retirement acceptance"
    paths = ", ".join(f"`{path}`" for path in contract["baton_acceptance_paths"])
    acceptance = f"| {label} | {paths} |"
    existing = [line for line in current.splitlines() if line.startswith(f"| {label} |")]
    if existing:
        if len(existing) != 1:
            _reject("baton_acceptance_row")
        current = current.replace(existing[0], acceptance, 1)
    else:
        marker = "| Current result |"
        index = current.find(marker)
        if index < 0:
            _reject("baton_acceptance_insert")
        current = current[:index] + acceptance + "\n" + current[index:]
    return current


def build_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    contract = validate_contract(contract_value)
    intent = validate_intent(intent_value, contract)
    validate_writer_inventory(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    current = _canonical_bytes(repo_root, contract)
    previous = _source_bytes(repo_root, contract, source)
    if current != previous:
        _reject("canonical_not_at_source")
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    latch = json.loads(current["active_latch"].decode("utf-8"))
    register = json.loads(current["error_register"].decode("utf-8"))
    try:
        prepared = tc.prepare_transaction(
            intent["transaction_manifest"],
            repo_root=repo_root,
            graph=graph,
            compass=compass,
            active_latch=latch,
        )
    except ValueError as error:
        raise AdoptionRejection("transaction_prepare") from error
    report = ariadne_compass.build_compass_report(
        prepared["projections"]["compass"],
        prepared["projections"]["graph"],
        repo_root=repo_root,
        require_evidence_files=False,
    )
    if report["status"] != "passed":
        raise AdoptionRejection("full_compass:" + ",".join(report["reasons"]))
    manifest = intent["transaction_manifest"]
    canonical = {
        "continuity": _json_text(prepared["projections"]["graph"]).encode("utf-8"),
        "compass": _json_text(prepared["projections"]["compass"]).encode("utf-8"),
        "compass_markdown": ariadne_compass.render_markdown(report).encode("utf-8"),
        "active_latch": _json_text(prepared["projections"]["latch"]).encode("utf-8"),
        "error_register": current["error_register"],
        "pattern_report": current["pattern_report"],
        "current_baton": _render_agents(
            current["current_baton"].decode("utf-8"),
            contract,
            manifest,
            prepared["projections"]["graph"],
            prepared["projections"]["compass"],
            source,
        ).encode("utf-8"),
    }
    selected = [
        command
        for command in contract["commands"]
        if command["command_id"] in intent["command_ids"]
    ]
    command_manifest = {
        "schema_version": COMMAND_VERSION,
        "commands": selected,
    }
    previous_sha256s = {key: _hash_bytes(value) for key, value in previous.items()}
    canonical_sha256s = {key: _hash_bytes(value) for key, value in canonical.items()}
    ownership = {
        "schema_version": OWNERSHIP_VERSION,
        "phase": "clockwork_active",
        "surface_owners": {
            **{key: WRITER for key in CANONICAL_KEYS},
            "command_manifest": WRITER,
            "transaction": WRITER,
            "ownership": WRITER,
        },
        "legacy_writers": {
            name: "retired" for name in contract["legacy_writer_classes"]
        },
    }
    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": contract["operation_id"],
        "transaction_id": prepared["transaction_id"],
        "source_commit": source,
        "previous_source_commit": source,
        "previous_canonical_sha256s": previous_sha256s,
        "projection_sha256s": prepared["projection_sha256s"],
        "journal": prepared["journal"],
        "publication_mode": "lease_bound_pointer_last_live_materialization",
        "event_kind": "clean_closeout",
        "register_bytes_preserved": canonical["error_register"] == previous["error_register"],
        "pattern_bytes_preserved": canonical["pattern_report"] == previous["pattern_report"],
    }
    metadata = {
        "command-manifest.json": _json_text(command_manifest).encode("utf-8"),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": _json_text(ownership).encode("utf-8"),
    }
    metadata_sha256s = {key: _hash_bytes(value) for key, value in metadata.items()}
    bundle_sha256 = _hash_json(
        {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
    )
    generation_id = "gen-" + bundle_sha256
    previous_bundle_sha256 = _hash_json(previous_sha256s)
    generation_manifest = {
        "schema_version": GENERATION_VERSION,
        "generation_id": generation_id,
        "bundle_sha256": bundle_sha256,
        "source_commit": source,
        "previous_generation": {
            "generation_id": "git-" + source,
            "source_commit": source,
            "bundle_sha256": previous_bundle_sha256,
            "canonical_sha256s": previous_sha256s,
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
    }
    pointer = {
        "schema_version": POINTER_VERSION,
        "phase": "clockwork_active",
        "selected_generation_id": generation_id,
        "selected_bundle_sha256": bundle_sha256,
        "previous_generation_id": "git-" + source,
        "previous_source_commit": source,
        "lease_sequence": 1,
        "writer": WRITER,
    }
    result = {
        "schema_version": "ariadne.governance_live_prepared_generation.v1",
        "contract": contract,
        "source_commit": source,
        "canonical": canonical,
        "metadata": metadata,
        "generation_manifest": generation_manifest,
        "pointer": pointer,
    }
    validate_prepared_generation(repo_root, result)
    return result


def validate_prepared_generation(repo_root: Path, value: object) -> dict[str, Any]:
    row = _exact(
        value,
        {
            "schema_version",
            "contract",
            "source_commit",
            "canonical",
            "metadata",
            "generation_manifest",
            "pointer",
        },
        "prepared_keys",
    )
    if row["schema_version"] != "ariadne.governance_live_prepared_generation.v1":
        _reject("prepared_version")
    contract = validate_contract(row["contract"])
    if set(row["canonical"]) != set(CANONICAL_KEYS) or set(row["metadata"]) != set(METADATA_NAMES):
        _reject("prepared_files")
    generation = row["generation_manifest"]
    pointer = row["pointer"]
    if (
        generation["schema_version"] != GENERATION_VERSION
        or pointer["schema_version"] != POINTER_VERSION
        or pointer["phase"] != "clockwork_active"
        or pointer["writer"] != WRITER
        or pointer["selected_generation_id"] != generation["generation_id"]
        or pointer["selected_bundle_sha256"] != generation["bundle_sha256"]
        or not HEX40.fullmatch(row["source_commit"])
        or not generation["generation_id"].startswith("gen-")
        or not HEX64.fullmatch(generation["bundle_sha256"])
    ):
        _reject("prepared_identity")
    canonical_sha256s = {key: _hash_bytes(value) for key, value in row["canonical"].items()}
    metadata_sha256s = {key: _hash_bytes(value) for key, value in row["metadata"].items()}
    if (
        canonical_sha256s != generation["canonical_sha256s"]
        or metadata_sha256s != generation["metadata_sha256s"]
        or generation["bundle_sha256"]
        != _hash_json({"canonical": canonical_sha256s, "metadata": metadata_sha256s})
    ):
        _reject("prepared_digest")
    graph = json.loads(row["canonical"]["continuity"].decode("utf-8"))
    compass = json.loads(row["canonical"]["compass"].decode("utf-8"))
    latch = json.loads(row["canonical"]["active_latch"].decode("utf-8"))
    ownership = json.loads(row["metadata"]["ownership.json"].decode("utf-8"))
    if (
        graph["nodes"][-1]["id"] != contract["operation_id"]
        or compass["current_position"]["node_id"] != contract["operation_id"]
        or latch["operation_id"]
        != _load(repo_root / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/closeout-intent.json")["transaction_manifest"]["next_operation"]["operation_id"]
        or set(ownership["surface_owners"].values()) != {WRITER}
        or len(ownership["surface_owners"]) != 10
        or set(ownership["legacy_writers"].values()) != {"retired"}
    ):
        _reject("prepared_semantics")
    if row["canonical"]["error_register"] != _git_bytes(
        repo_root, row["source_commit"], contract["canonical_paths"]["error_register"]
    ):
        _reject("register_not_preserved")
    if row["canonical"]["pattern_report"] != _git_bytes(
        repo_root, row["source_commit"], contract["canonical_paths"]["pattern_report"]
    ):
        _reject("pattern_not_preserved")
    return row


def _write_temp(target: Path, value: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_bytes(value)
    if temporary.read_bytes() != value:
        _reject("temporary_reread")
    return temporary


def _replace_bytes(target: Path, value: bytes) -> None:
    temporary = _write_temp(target, value)
    os.replace(temporary, target)


def publish_live_generation(
    repo_root: Path,
    prepared: dict[str, Any],
    *,
    writer_id: str,
    fail_at: str | None = None,
) -> dict[str, Any]:
    prepared = validate_prepared_generation(repo_root, prepared)
    contract = prepared["contract"]
    if writer_id != WRITER:
        _reject("writer_not_clockwork")
    _assert_git_state(repo_root, contract, prepared["source_commit"])
    root = repo_root / contract["clockwork_root"]
    pointer_path = root / "current.json"
    if pointer_path.is_file():
        current = _load(pointer_path)
        if (
            current.get("phase") == "clockwork_active"
            and current.get("selected_generation_id")
            == prepared["generation_manifest"]["generation_id"]
        ):
            return validate_live_state(repo_root, contract)
        if current.get("phase") != "rolled_back":
            _reject("clockwork_already_initialized")
        prepared = dict(prepared)
        prepared["pointer"] = {
            **prepared["pointer"],
            "lease_sequence": current["lease_sequence"] + 1,
        }
    root.mkdir(parents=True, exist_ok=True)
    lease_path = root / "writer.lock"
    try:
        descriptor = os.open(lease_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as error:
        raise AdoptionRejection("lease_occupied") from error
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as lease:
        lease.write(
            _json_text(
                {
                    "schema_version": "ariadne.governance_live_lease.v1",
                    "operation_id": contract["operation_id"],
                    "source_commit": prepared["source_commit"],
                    "previous_generation_id": prepared["pointer"]["previous_generation_id"],
                    "sequence": prepared["pointer"]["lease_sequence"],
                }
            )
        )
    canonical_targets = {
        key: repo_root / relative for key, relative in contract["canonical_paths"].items()
    }
    metadata_values = {
        **prepared["metadata"],
        "generation-manifest.json": _json_text(prepared["generation_manifest"]).encode("utf-8"),
    }
    metadata_targets = {name: root / name for name in metadata_values}
    original_canonical = {key: path.read_bytes() for key, path in canonical_targets.items()}
    previous_source = _source_bytes(repo_root, contract, prepared["source_commit"])
    if original_canonical != previous_source:
        lease_path.unlink(missing_ok=True)
        _reject("stale_canonical_generation")
    original_metadata = {
        name: path.read_bytes() if path.is_file() else None
        for name, path in metadata_targets.items()
    }
    staged: dict[str, Path] = {}
    committed = False
    try:
        for key, target in canonical_targets.items():
            staged[f"canonical:{key}"] = _write_temp(target, prepared["canonical"][key])
        for name, target in metadata_targets.items():
            staged[f"metadata:{name}"] = _write_temp(target, metadata_values[name])
        pointer_temp = _write_temp(pointer_path, _json_text(prepared["pointer"]).encode("utf-8"))
        staged["pointer"] = pointer_temp
        for key in CANONICAL_KEYS:
            if fail_at == f"before:{key}":
                raise OSError("injected_precommit_failure")
            os.replace(staged.pop(f"canonical:{key}"), canonical_targets[key])
            if fail_at == f"after:{key}":
                raise OSError("injected_precommit_failure")
        for name in metadata_values:
            os.replace(staged.pop(f"metadata:{name}"), metadata_targets[name])
        if fail_at == "before_pointer_replace":
            raise OSError("injected_precommit_failure")
        os.replace(staged.pop("pointer"), pointer_path)
        committed = True
        state = validate_live_state(repo_root, contract)
        if fail_at == "after_pointer_replace":
            raise CommittedAdoption("injected_postcommit_failure")
        return state
    except BaseException:
        if not committed:
            for key, target in canonical_targets.items():
                _replace_bytes(target, original_canonical[key])
            for name, target in metadata_targets.items():
                previous = original_metadata[name]
                if previous is None:
                    target.unlink(missing_ok=True)
                else:
                    _replace_bytes(target, previous)
            pointer_path.unlink(missing_ok=True)
            if any(
                canonical_targets[key].read_bytes() != original_canonical[key]
                for key in CANONICAL_KEYS
            ):
                raise AdoptionRejection("rollback_reread")
        raise
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)
        lease_path.unlink(missing_ok=True)


def validate_live_state(
    repo_root: Path, contract_value: object
) -> dict[str, Any]:
    contract = validate_contract(contract_value)
    validate_writer_inventory(repo_root, contract)
    root = repo_root / contract["clockwork_root"]
    pointer = _exact(
        _load(root / "current.json"),
        {
            "schema_version",
            "phase",
            "selected_generation_id",
            "selected_bundle_sha256",
            "previous_generation_id",
            "previous_source_commit",
            "lease_sequence",
            "writer",
        },
        "pointer_keys",
    )
    generation = _load(root / "generation-manifest.json")
    if (
        pointer["schema_version"] != POINTER_VERSION
        or pointer["phase"] != "clockwork_active"
        or pointer["writer"] != WRITER
        or pointer["selected_generation_id"] != generation["generation_id"]
        or pointer["selected_bundle_sha256"] != generation["bundle_sha256"]
        or not HEX40.fullmatch(pointer["previous_source_commit"])
    ):
        _reject("live_pointer")
    canonical = _canonical_bytes(repo_root, contract)
    canonical_sha256s = {key: _hash_bytes(value) for key, value in canonical.items()}
    metadata = {name: (root / name).read_bytes() for name in METADATA_NAMES}
    metadata_sha256s = {key: _hash_bytes(value) for key, value in metadata.items()}
    if (
        canonical_sha256s != generation["canonical_sha256s"]
        or metadata_sha256s != generation["metadata_sha256s"]
        or generation["bundle_sha256"]
        != _hash_json({"canonical": canonical_sha256s, "metadata": metadata_sha256s})
    ):
        _reject("canonical_drift")
    previous = _source_bytes(repo_root, contract, pointer["previous_source_commit"])
    previous_sha256s = {key: _hash_bytes(value) for key, value in previous.items()}
    if previous_sha256s != generation["previous_generation"]["canonical_sha256s"]:
        _reject("previous_generation_drift")
    ownership = json.loads(metadata["ownership.json"].decode("utf-8"))
    if (
        ownership["schema_version"] != OWNERSHIP_VERSION
        or ownership["phase"] != "clockwork_active"
        or len(ownership["surface_owners"]) != 10
        or set(ownership["surface_owners"].values()) != {WRITER}
        or set(ownership["legacy_writers"].values()) != {"retired"}
    ):
        _reject("live_ownership")
    head = _assert_git_state(repo_root, contract)
    _git(repo_root, "merge-base", "--is-ancestor", generation["source_commit"], head)
    return {
        "schema_version": "ariadne.governance_live_state.v1",
        "status": "passed",
        "head": head,
        "source_commit": generation["source_commit"],
        "generation_id": generation["generation_id"],
        "bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": pointer["previous_generation_id"],
        "previous_source_commit": pointer["previous_source_commit"],
        "clockwork_owned_surfaces": len(ownership["surface_owners"]),
        "dual_owned_surfaces": 0,
        "retired_legacy_writer_classes": len(ownership["legacy_writers"]),
        "canonical_drift": 0,
        "lease_sequence": pointer["lease_sequence"],
    }


def rollback_live_generation(
    repo_root: Path, contract_value: object, *, writer_id: str
) -> dict[str, Any]:
    contract = validate_contract(contract_value)
    if writer_id != WRITER:
        _reject("writer_not_clockwork")
    state = validate_live_state(repo_root, contract)
    root = repo_root / contract["clockwork_root"]
    pointer = _load(root / "current.json")
    previous = _source_bytes(repo_root, contract, pointer["previous_source_commit"])
    lease_path = root / "writer.lock"
    try:
        descriptor = os.open(lease_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as error:
        raise AdoptionRejection("lease_occupied") from error
    os.close(descriptor)
    try:
        for key, relative in contract["canonical_paths"].items():
            _replace_bytes(repo_root / relative, previous[key])
        ownership = _load(root / "ownership.json")
        ownership["phase"] = "rolled_back"
        ownership["surface_owners"] = {
            key: "legacy_oracle" for key in ownership["surface_owners"]
        }
        ownership["legacy_writers"] = {
            key: "rollback_available" for key in ownership["legacy_writers"]
        }
        _replace_bytes(root / "ownership.json", _json_text(ownership).encode("utf-8"))
        rolled_back = {
            "schema_version": POINTER_VERSION,
            "phase": "rolled_back",
            "selected_generation_id": pointer["previous_generation_id"],
            "selected_bundle_sha256": _hash_json(
                {key: _hash_bytes(value) for key, value in previous.items()}
            ),
            "previous_generation_id": pointer["selected_generation_id"],
            "previous_source_commit": pointer["previous_source_commit"],
            "lease_sequence": pointer["lease_sequence"] + 1,
            "writer": "legacy_oracle",
        }
        _replace_bytes(root / "current.json", _json_text(rolled_back).encode("utf-8"))
        if _canonical_bytes(repo_root, contract) != previous:
            _reject("rollback_reread")
        return {
            "schema_version": "ariadne.governance_live_rollback.v1",
            "status": "passed",
            "rolled_back_from_generation_id": state["generation_id"],
            "selected_generation_id": rolled_back["selected_generation_id"],
            "previous_source_commit": pointer["previous_source_commit"],
            "byte_exact": True,
        }
    finally:
        lease_path.unlink(missing_ok=True)


def load_contract_and_intent(
    repo_root: Path, contract_path: Path, intent_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = validate_contract(_load(contract_path))
    intent = validate_intent(_load(intent_path), contract)
    return contract, intent
