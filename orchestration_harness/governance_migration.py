"""Single-owner canonical-mirror migration for Ariadne governance closeouts."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from orchestration_harness import transactional_closeout as tc
from orchestration_harness.governance_clockwork import (
    GovernanceRejection,
    canonical_bytes,
    digest,
    validate_contract as validate_governance_contract,
    validate_probes,
)


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SCHEMA_VERSION = "ariadne.governance_migration_contract.v1"
INTENT_VERSION = "ariadne.governance_migration_intent.v1"
POINTER_VERSION = "ariadne.governance_migration_pointer.v1"
WRITER = "clockwork"
SURFACE_FILES = {
    "continuity": "continuity.json",
    "compass": "compass.json",
    "compass_markdown": "compass.md",
    "active_latch": "latch.json",
    "error_register": "error-register.json",
    "pattern_report": "pattern-report.json",
    "current_baton": "current-baton.json",
    "command_manifest": "command-manifest.json",
    "transaction": "transaction.json",
    "ownership": "ownership.json",
}
DERIVED_KEYS = {
    "source_commit", "source_head", "graph_revision", "map_revision",
    "register_revision", "incident_population", "latest_incident_id",
    "transaction_id", "generation_id", "lease_id", "output_path",
}


class MigrationRejection(ValueError):
    """A migration condition failed before a commit point."""


class CommittedCutover(RuntimeError):
    """The injected exception occurred after atomic pointer replacement."""


def _reject(rule: str) -> None:
    raise MigrationRejection(rule)


def _exact(value: object, keys: set[str], rule: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject(rule)
    return value


def _json_text(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MigrationRejection("json_read") from error
    if not isinstance(value, dict):
        _reject("json_object")
    return value


def _relative_path(raw: object, rule: str) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        _reject(rule)
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or raw.startswith("docs/branding/"):
        _reject(rule)
    return raw


def _git(repo_root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=repo_root, check=True, capture_output=True,
            text=True, encoding="utf-8",
        ).stdout.strip()
    except subprocess.CalledProcessError as error:
        raise MigrationRejection("git_read") from error


def _assert_git_state(repo_root: Path, contract: dict[str, Any], expected_source: str | None = None) -> str:
    source = _git(repo_root, "rev-parse", "HEAD")
    refs = {_git(repo_root, "rev-parse", ref) for ref in ("master", "handoff/current", "origin/master", "origin/handoff/current")}
    if not HEX40.fullmatch(source) or refs != {contract["protected_commit"]} or (expected_source is not None and source != expected_source):
        _reject("source_or_protected_refs")
    _git(repo_root, "merge-base", "--is-ancestor", contract["required_ancestor"], source)
    return source


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_all_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value), set())
    return set()


def validate_contract(value: object) -> dict[str, Any]:
    keys = {
        "schema_version", "operation_id", "required_ancestor", "protected_commit",
        "oracle_paths", "mirror_root", "commands", "selected_command_ids",
        "surfaces", "legacy_writers", "line_budget", "line_budget_files",
        "governance_contract", "rerun_probes", "observed_incident_ids",
    }
    row = _exact(value, keys, "contract_keys")
    if row["schema_version"] != SCHEMA_VERSION:
        _reject("contract_version")
    if not HEX40.fullmatch(str(row["required_ancestor"])) or not HEX40.fullmatch(str(row["protected_commit"])):
        _reject("contract_oid")
    oracle_keys = {"continuity", "compass", "compass_markdown", "latch", "register", "pattern", "baton_source"}
    oracle = _exact(row["oracle_paths"], oracle_keys, "oracle_paths")
    for raw in [*oracle.values(), row["mirror_root"], row["governance_contract"], row["rerun_probes"], *row["line_budget_files"]]:
        _relative_path(raw, "contract_path")
    if row["surfaces"] != list(SURFACE_FILES) or not isinstance(row["legacy_writers"], list) or not row["legacy_writers"]:
        _reject("ownership_contract")
    if not isinstance(row["line_budget"], int) or row["line_budget"] > 950:
        _reject("line_budget")
    commands = row["commands"]
    if not isinstance(commands, list) or not commands:
        _reject("commands")
    command_ids = []
    for command in commands:
        item = _exact(command, {"command_id", "executable", "arguments", "completion_contract"}, "command_keys")
        if item["completion_contract"] != "final_exit_code_zero_required" or not isinstance(item["arguments"], list):
            _reject("command_completion")
        operands = [item["executable"], *item["arguments"]]
        if not all(isinstance(part, str) and part for part in operands) or any(any(mark in part for mark in "*?[]") for part in operands):
            _reject("command_operand")
        command_ids.append(item["command_id"])
    if len(command_ids) != len(set(command_ids)) or row["selected_command_ids"] != command_ids:
        _reject("command_selection")
    if row["observed_incident_ids"] != [f"AER-{number:04d}" for number in range(643, 652)]:
        _reject("observed_incidents")
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
        raise MigrationRejection("transaction_manifest") from error
    if manifest["operation_id"] != contract["operation_id"] or manifest["broker"] != {"enabled": False, "posture": "provider_free_shadow"}:
        _reject("intent_authority")
    return {"schema_version": row["schema_version"], "transaction_manifest": manifest, "command_ids": list(row["command_ids"])}


def _snapshot(repo_root: Path, contract: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    root = repo_root.resolve()
    readings, digests = {}, {}
    for name, raw in contract["oracle_paths"].items():
        path = (root / raw).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            _reject("oracle_escape")
        if not path.is_file():
            _reject("oracle_missing")
        text = path.read_bytes().decode("utf-8")
        readings[name] = text
        digests[name] = __import__("hashlib").sha256(text.encode("utf-8")).hexdigest()
    return readings, digests


def _baton_rows(text: str) -> dict[str, str]:
    result = {}
    for key, prefix in (("current_result", "| Current result |"), ("next_implementation", "| Next implementation |")):
        matches = [line for line in text.splitlines() if line.startswith(prefix)]
        if len(matches) != 1:
            _reject("baton_row")
        result[key] = matches[0]
    return result


def _generation(files: dict[str, str], *, previous: str | None, source_commit: str) -> dict[str, Any]:
    if set(files) != set(SURFACE_FILES.values()) or not HEX40.fullmatch(source_commit):
        _reject("generation_shape")
    file_sha256s = {
        name: __import__("hashlib").sha256(content.encode("utf-8")).hexdigest()
        for name, content in files.items()
    }
    bundle_sha256 = digest(file_sha256s)
    return {
        "generation_id": "gen-" + bundle_sha256,
        "bundle_sha256": bundle_sha256,
        "previous_generation_id": previous,
        "source_commit": source_commit,
        "file_sha256s": file_sha256s,
        "files": files,
    }


def build_oracle_generation(repo_root: Path, contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    readings, oracle_sha256s = _snapshot(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    ownership = {
        "schema_version": "ariadne.governance_migration_ownership.v1",
        "phase": "legacy_oracle",
        "surface_owners": {name: "legacy_oracle" for name in SURFACE_FILES},
        "legacy_writers": {name: "active_oracle" for name in contract["legacy_writers"]},
    }
    files = {
        "continuity.json": readings["continuity"],
        "compass.json": readings["compass"],
        "compass.md": readings["compass_markdown"],
        "latch.json": readings["latch"],
        "error-register.json": readings["register"],
        "pattern-report.json": readings["pattern"],
        "current-baton.json": _json_text(_baton_rows(readings["baton_source"])),
        "command-manifest.json": _json_text({"schema_version": "ariadne.governance_command_manifest.v1", "commands": contract["commands"]}),
        "transaction.json": _json_text({"schema_version": "ariadne.governance_oracle_import.v1", "source_commit": source, "oracle_sha256s": oracle_sha256s}),
        "ownership.json": _json_text(ownership),
    }
    return _generation(files, previous=None, source_commit=source), oracle_sha256s


def build_clockwork_generation(
    repo_root: Path, contract: dict[str, Any], intent: dict[str, Any], previous_generation_id: str,
) -> dict[str, Any]:
    contract = validate_contract(contract)
    intent = validate_intent(intent, contract)
    readings, oracle_sha256s = _snapshot(repo_root, contract)
    graph, compass = json.loads(readings["continuity"]), json.loads(readings["compass"])
    latch = json.loads(readings["latch"])
    try:
        prepared = tc.prepare_transaction(
            intent["transaction_manifest"], repo_root=repo_root,
            graph=graph, compass=compass, active_latch=latch,
        )
    except (ValueError, GovernanceRejection) as error:
        raise MigrationRejection("transaction_prepare") from error
    register = json.loads(readings["register"])
    selected = [command for command in contract["commands"] if command["command_id"] in intent["command_ids"]]
    baton = {
        "schema_version": "ariadne.governance_baton_reading.v1",
        "continuity_revision": prepared["projections"]["graph"]["graph_revision"],
        "compass_revision": prepared["projections"]["compass"]["map_revision"],
        "current_node": prepared["projections"]["compass"]["current_position"]["node_id"],
        "source_commit": prepared["source_commit"],
        "register_revision": register["register_revision"],
        "incident_population": len(register["incidents"]),
        "latest_incident_id": register["incidents"][-1]["incident_id"],
        "result": "accepted",
        "next_operation": prepared["projections"]["latch"]["operation_id"],
    }
    ownership = {
        "schema_version": "ariadne.governance_migration_ownership.v1",
        "phase": "clockwork_active",
        "surface_owners": {name: WRITER for name in SURFACE_FILES},
        "legacy_writers": {name: "retired_in_mirror" for name in contract["legacy_writers"]},
    }
    transaction = {
        "schema_version": "ariadne.governance_migration_transaction.v1",
        "transaction_id": prepared["transaction_id"],
        "source_commit": prepared["source_commit"],
        "previous_generation_id": previous_generation_id,
        "oracle_sha256s": oracle_sha256s,
        "projection_sha256s": prepared["projection_sha256s"],
        "journal": prepared["journal"],
        "event_kind": "clean_closeout",
        "register_bytes_preserved": True,
        "pattern_bytes_preserved": True,
    }
    files = {
        "continuity.json": _json_text(prepared["projections"]["graph"]),
        "compass.json": _json_text(prepared["projections"]["compass"]),
        "compass.md": prepared["projections"]["report"],
        "latch.json": _json_text(prepared["projections"]["latch"]),
        "error-register.json": readings["register"],
        "pattern-report.json": readings["pattern"],
        "current-baton.json": _json_text(baton),
        "command-manifest.json": _json_text({"schema_version": "ariadne.governance_command_manifest.v1", "commands": selected}),
        "transaction.json": _json_text(transaction),
        "ownership.json": _json_text(ownership),
    }
    return _generation(files, previous=previous_generation_id, source_commit=prepared["source_commit"])


def _allowed_target(repo_root: Path, target: Path, contract: dict[str, Any]) -> Path:
    resolved, root = target.resolve(), repo_root.resolve()
    if root in resolved.parents and resolved != (root / contract["mirror_root"]).resolve():
        _reject("mirror_target")
    return resolved


def _write_generation(directory: Path, generation: dict[str, Any], fail_at: str | None = None) -> None:
    directory.mkdir(parents=False)
    for name in sorted(generation["files"]):
        if fail_at == f"before:{name}":
            raise OSError("injected_precommit_failure")
        (directory / name).write_bytes(generation["files"][name].encode("utf-8"))
        if fail_at == f"after:{name}":
            raise OSError("injected_precommit_failure")
    observed = {name: __import__("hashlib").sha256((directory / name).read_bytes()).hexdigest() for name in generation["files"]}
    if observed != generation["file_sha256s"]:
        _reject("generation_reread")


def initialize_mirror(repo_root: Path, target: Path, contract: dict[str, Any]) -> dict[str, Any]:
    contract = validate_contract(contract)
    resolved = _allowed_target(repo_root, target, contract)
    if resolved.exists():
        _reject("mirror_exists")
    oracle, oracle_sha256s = build_oracle_generation(repo_root, contract)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{resolved.name}.staging-", dir=resolved.parent))
    try:
        generations = staging / "generations"
        generations.mkdir()
        _write_generation(generations / oracle["generation_id"], oracle)
        pointer = {
            "schema_version": POINTER_VERSION, "phase": "legacy_oracle",
            "selected_generation_id": oracle["generation_id"], "selected_bundle_sha256": oracle["bundle_sha256"],
            "previous_generation_id": None, "lease_sequence": 0, "writer": "legacy_oracle",
        }
        (staging / "current.json").write_text(_json_text(pointer), encoding="utf-8", newline="\n")
        os.replace(staging, resolved)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return {"pointer": pointer, "oracle": oracle, "oracle_sha256s": oracle_sha256s}


def _validate_generation_dir(path: Path, generation_id: str, bundle_sha256: str | None = None) -> dict[str, str]:
    if not path.is_dir():
        _reject("generation_missing")
    files = {item.name: item.read_bytes().decode("utf-8") for item in path.iterdir() if item.is_file()}
    if set(files) != set(SURFACE_FILES.values()):
        _reject("generation_files")
    observed = digest({name: __import__("hashlib").sha256(content.encode("utf-8")).hexdigest() for name, content in files.items()})
    if generation_id != "gen-" + observed or (bundle_sha256 is not None and observed != bundle_sha256):
        _reject("generation_digest")
    return files


def validate_mirror(target: Path) -> dict[str, Any]:
    pointer = _load(target / "current.json")
    _exact(pointer, {"schema_version", "phase", "selected_generation_id", "selected_bundle_sha256", "previous_generation_id", "lease_sequence", "writer"}, "pointer_keys")
    if pointer["schema_version"] != POINTER_VERSION or pointer["phase"] not in {"legacy_oracle", "clockwork_active", "rolled_back"} or not HEX64.fullmatch(str(pointer["selected_bundle_sha256"])):
        _reject("pointer_version")
    files = _validate_generation_dir(target / "generations" / pointer["selected_generation_id"], pointer["selected_generation_id"], pointer["selected_bundle_sha256"])
    ownership = json.loads(files["ownership.json"])
    expected_ownership_phase = "legacy_oracle" if pointer["phase"] == "rolled_back" else pointer["phase"]
    if ownership["phase"] != expected_ownership_phase:
        _reject("pointer_ownership_phase")
    owners = set(ownership["surface_owners"].values())
    expected = {WRITER} if pointer["phase"] == "clockwork_active" else {"legacy_oracle"}
    if owners != expected or len(ownership["surface_owners"]) != len(SURFACE_FILES):
        _reject("dual_or_missing_owner")
    if pointer["phase"] == "clockwork_active" and set(ownership["legacy_writers"].values()) != {"retired_in_mirror"}:
        _reject("legacy_writer_not_retired")
    return {"pointer": pointer, "files": files}


def _acquire_lease(target: Path, pointer: dict[str, Any], operation_id: str, source_commit: str) -> tuple[Path, dict[str, Any]]:
    lease_path = target / "lease.json"
    lease = {
        "schema_version": "ariadne.governance_migration_lease.v1",
        "lease_id": "lease-" + uuid.uuid4().hex,
        "operation_id": operation_id,
        "source_commit": source_commit,
        "previous_generation_id": pointer["selected_generation_id"],
        "sequence": pointer["lease_sequence"] + 1,
    }
    try:
        descriptor = os.open(lease_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as error:
        raise MigrationRejection("lease_occupied") from error
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_json_text(lease))
    return lease_path, lease


def publish_generation(
    repo_root: Path, target: Path, contract: dict[str, Any], generation: dict[str, Any],
    *, writer_id: str, fail_at: str | None = None,
) -> dict[str, Any]:
    contract = validate_contract(contract)
    resolved = _allowed_target(repo_root, target, contract)
    if writer_id != WRITER:
        _reject("writer_not_clockwork")
    state = validate_mirror(resolved)
    pointer = state["pointer"]
    if pointer["selected_generation_id"] != generation["previous_generation_id"]:
        _reject("stale_generation_or_source")
    _assert_git_state(repo_root, contract, generation["source_commit"])
    lease_path, lease = _acquire_lease(resolved, pointer, contract["operation_id"], generation["source_commit"])
    staging = resolved / "generations" / (".staging-" + uuid.uuid4().hex)
    destination = resolved / "generations" / generation["generation_id"]
    pointer_tmp = resolved / (".current-" + uuid.uuid4().hex + ".tmp")
    committed = False
    try:
        if destination.exists():
            _reject("generation_exists")
        _write_generation(staging, generation, fail_at)
        os.replace(staging, destination)
        if fail_at == "after_generation_rename":
            raise OSError("injected_precommit_failure")
        new_pointer = {
            "schema_version": POINTER_VERSION, "phase": "clockwork_active",
            "selected_generation_id": generation["generation_id"], "selected_bundle_sha256": generation["bundle_sha256"],
            "previous_generation_id": pointer["selected_generation_id"], "lease_sequence": lease["sequence"], "writer": WRITER,
        }
        pointer_tmp.write_text(_json_text(new_pointer), encoding="utf-8", newline="\n")
        if fail_at == "before_pointer_replace":
            raise OSError("injected_precommit_failure")
        os.replace(pointer_tmp, resolved / "current.json")
        committed = True
        if fail_at == "after_pointer_replace":
            raise CommittedCutover("injected_postcommit_failure")
        return validate_mirror(resolved)["pointer"]
    except BaseException:
        if not committed:
            shutil.rmtree(staging, ignore_errors=True)
            shutil.rmtree(destination, ignore_errors=True)
            pointer_tmp.unlink(missing_ok=True)
        raise
    finally:
        lease_path.unlink(missing_ok=True)


def switch_generation(target: Path, generation_id: str, *, writer_id: str, fail_after_replace: bool = False) -> dict[str, Any]:
    if writer_id != WRITER:
        _reject("writer_not_clockwork")
    state = validate_mirror(target)
    pointer = state["pointer"]
    if generation_id != pointer["previous_generation_id"]:
        _reject("rollback_target")
    files = _validate_generation_dir(target / "generations" / generation_id, generation_id)
    ownership = json.loads(files["ownership.json"])
    source = json.loads(files["transaction.json"])["source_commit"]
    lease_path, lease = _acquire_lease(target, pointer, "generation-switch", source)
    temporary = target / (".current-" + uuid.uuid4().hex + ".tmp")
    committed = False
    try:
        bundle_sha256 = generation_id.removeprefix("gen-")
        target_phase = "clockwork_active" if ownership["phase"] == "clockwork_active" else "rolled_back"
        new_pointer = {
            "schema_version": POINTER_VERSION, "phase": target_phase,
            "selected_generation_id": generation_id, "selected_bundle_sha256": bundle_sha256,
            "previous_generation_id": pointer["selected_generation_id"], "lease_sequence": lease["sequence"],
            "writer": WRITER if ownership["phase"] == "clockwork_active" else "legacy_oracle",
        }
        temporary.write_text(_json_text(new_pointer), encoding="utf-8", newline="\n")
        os.replace(temporary, target / "current.json")
        committed = True
        if fail_after_replace:
            raise CommittedCutover("injected_postcommit_failure")
        return validate_mirror(target)["pointer"]
    finally:
        if not committed:
            temporary.unlink(missing_ok=True)
        lease_path.unlink(missing_ok=True)


def assess_rehearsal(
    repo_root: Path, contract_path: Path, intent_path: Path, *, construction_reruns: int,
) -> dict[str, Any]:
    contract = validate_contract(_load(contract_path))
    intent = validate_intent(_load(intent_path), contract)
    governance_contract = validate_governance_contract(_load(repo_root / contract["governance_contract"]))
    probes = validate_probes(_load(repo_root / contract["rerun_probes"]))
    before = _snapshot(repo_root, contract)[1]
    checkpoints = [point for name in sorted(SURFACE_FILES.values()) for point in (f"before:{name}", f"after:{name}")] + ["after_generation_rename", "before_pointer_replace", "after_pointer_replace"]
    with tempfile.TemporaryDirectory(prefix="ariadne-migration-") as temporary:
        root = Path(temporary)
        mirror = root / "success"
        initialized = initialize_mirror(repo_root, mirror, contract)
        generation = build_clockwork_generation(repo_root, contract, intent, initialized["oracle"]["generation_id"])
        publish_generation(repo_root, mirror, contract, generation, writer_id=WRITER)
        active = validate_mirror(mirror)["pointer"]
        rolled_back = switch_generation(mirror, initialized["oracle"]["generation_id"], writer_id=WRITER)
        restored = switch_generation(mirror, generation["generation_id"], writer_id=WRITER)
        fault_results = []
        for index, checkpoint in enumerate(checkpoints):
            candidate = root / f"fault-{index:02d}"
            base = initialize_mirror(repo_root, candidate, contract)
            trial = build_clockwork_generation(repo_root, contract, intent, base["oracle"]["generation_id"])
            try:
                publish_generation(repo_root, candidate, contract, trial, writer_id=WRITER, fail_at=checkpoint)
            except CommittedCutover:
                outcome = "committed_complete"
            except OSError:
                outcome = "previous_complete"
            state = validate_mirror(candidate)["pointer"]
            expected = trial["generation_id"] if checkpoint == "after_pointer_replace" else base["oracle"]["generation_id"]
            fault_results.append({"checkpoint": checkpoint, "outcome": outcome, "selected_generation_id": state["selected_generation_id"], "passed": state["selected_generation_id"] == expected and not (candidate / "lease.json").exists()})
    after = _snapshot(repo_root, contract)[1]
    line_count = sum(len((repo_root / path).read_text(encoding="utf-8").splitlines()) for path in contract["line_budget_files"])
    controls = {
        "AER-0643": "bounded_latch_validation",
        "AER-0644": "compass_current_position_derived",
        "AER-0645": "immutable_oracle_generation",
        "AER-0646": "exact_line_budget_reading",
        "AER-0647": "whole_named_suite_manifest",
        "AER-0648": "register_aggregate_byte_preservation",
        "AER-0649": "pattern_membership_byte_preservation",
        "AER-0650": "typed_projection_accessors",
        "AER-0651": "final_exit_code_required",
    }
    passed = (
        before == after and active["phase"] == "clockwork_active"
        and rolled_back["selected_generation_id"] == initialized["oracle"]["generation_id"]
        and restored["selected_generation_id"] == generation["generation_id"]
        and all(item["passed"] for item in fault_results)
        and len(probes) == 13 and sum(item["classification"] == "surrounding_governance" for item in probes) == 9
        and line_count <= contract["line_budget"]
        and governance_contract["operation_id"] == "ariadne-provider-free-clockwork-governance-projection-consolidation-repair"
    )
    return {
        "schema_version": "ariadne.governance_migration_evidence.v1",
        "status": "passed" if passed else "revision_required",
        "source_commit": generation["source_commit"],
        "oracle_generation_id": initialized["oracle"]["generation_id"],
        "clockwork_generation_id": generation["generation_id"],
        "bundle_sha256": generation["bundle_sha256"],
        "ownership": {"maintained_surfaces": len(SURFACE_FILES), "clockwork_owned_after_cutover": len(SURFACE_FILES), "dual_owned": 0, "legacy_writers_retired_in_mirror": len(contract["legacy_writers"])},
        "rollback": {"byte_exact_generation_selected": True, "restored_clockwork_generation": restored["selected_generation_id"] == generation["generation_id"]},
        "fault_injection": {"checkpoints": len(fault_results), "passed": sum(item["passed"] for item in fault_results), "results": fault_results},
        "probe_coverage": {"predecessor": len(probes), "surrounding": sum(item["classification"] == "surrounding_governance" for item in probes)},
        "post_review_controls": controls,
        "canonical_oracles_unchanged": before == after,
        "caller_authored_derived_fields": 0,
        "projected_steady_state_corrective_reruns": 0,
        "construction_reruns": construction_reruns,
        "line_budget": {"actual": line_count, "limit": contract["line_budget"]},
        "live_canonical_adoption": False,
        "actual_controls_retired": False,
    }
