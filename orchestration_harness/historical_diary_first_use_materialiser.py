"""One-run local materialiser for an exact historical-derived scenario."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from orchestration_harness import historical_diary_first_use_candidate_gate as gate
from orchestration_harness import historical_diary_local_measured_privacy_probe as probe
from orchestration_harness.governance_clockwork_tick import (
    HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUND_ROOT = REPO_ROOT / "local_data/historical-diary-trove/raw/pilot_01"
ATTEMPT_ROOT = REPO_ROOT / (
    "local_data/historical-diary-trove/first-use-attempts/"
    "2026-08-24-check-in-context-v1"
)
FIXTURE_ROOT = REPO_ROOT / (
    "local_data/historical-diary-trove/derived-scenarios/"
    "2026-08-24-first-use-check-in-context-v1"
)
CONTRACT_PATH = REPO_ROOT / (
    "orchestration/continuity/raisa-provider-free-governance-clockwork-"
    "historical-derived-first-use-materialisation-subgate-rehearsal/"
    "next-tranche-contract.json"
)
LATCH_PATH = REPO_ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
CORE_PATH = Path(__file__).resolve()
EXTRACTOR_PATH = REPO_ROOT / "scripts/historical_diary_local_measured_privacy_probe.ps1"
WORD_CLEANUP_PATH = REPO_ROOT / "scripts/historical_diary_owned_word_cleanup.ps1"
MANIFEST_PATH = ATTEMPT_ROOT / "private-binding-manifest.json"
SAFE_BINDING_PATH = ATTEMPT_ROOT / "safe-binding-reading.json"
WORD_CONTROL_PATH = ATTEMPT_ROOT / "owned-word-process-control.json"
WORD_PROGRESS_PATH = ATTEMPT_ROOT / "word-extraction-progress.json"
WORD_CLEANUP_RECEIPT_PATH = ATTEMPT_ROOT / "parent-word-cleanup.json"
CONTENT_TERMINAL_PATH = ATTEMPT_ROOT / "content-run-terminal.json"
FIXTURE_PATH = FIXTURE_ROOT / "scenario.json"
FIXTURE_TEMP_PATH = FIXTURE_ROOT / ".scenario.json.tmp"

CONTRACT_SHA256 = "3e07a40f3e7c722e89cf7e082c2e9399a6836998c7b061350423ce54a813ba5f"
GATE_SOURCE_COMMIT = "abcd4206a363b0c565c070e0f2cb9c54d627b3b3"
PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
OPERATION_ID = (
    "raisa-local-only-historical-derived-minimised-check-in-context-scenario-"
    "first-use-materialisation-rehearsal"
)
MAX_PRIVATE_PIPE_BYTES = probe.MAX_PRIVATE_PIPE_BYTES

TerminalDecision = Literal[
    "blocked",
    "revision_required",
    "materialised_for_exact_declared_local_test_artifact_only",
]


class MaterialisationError(RuntimeError):
    """The one-run materialisation failed closed."""


@dataclass(frozen=True)
class _ObservedEvent:
    event_kind: gate.EventKind
    minute: int
    token: str
    resource: str


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MaterialisationError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise MaterialisationError(f"json_object_required:{path.name}")
    return value


def _write_public(path: Path, value: dict[str, Any]) -> None:
    if path.parent.resolve() != ATTEMPT_ROOT.resolve():
        raise MaterialisationError("public_write_path_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _git_bytes(commit: str, relative_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise MaterialisationError("git_source_unreadable")
    return completed.stdout


def _git_ref(ref: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or len(value) != 40:
        raise MaterialisationError("git_ref_unreadable")
    return value


def _assert_owned_roots() -> None:
    trove = (REPO_ROOT / "local_data/historical-diary-trove").resolve()
    for root in (ATTEMPT_ROOT, FIXTURE_ROOT):
        resolved = root.resolve()
        if not resolved.is_relative_to(trove) or resolved == trove:
            raise MaterialisationError("owned_root_invalid")


def load_contract() -> dict[str, Any]:
    raw = CONTRACT_PATH.read_bytes()
    if _sha256_bytes(raw) != CONTRACT_SHA256:
        raise MaterialisationError("materialiser_contract_hash_mismatch")
    contract = json.loads(raw)
    if contract.get("operation_id") != OPERATION_ID:
        raise MaterialisationError("materialiser_contract_operation_mismatch")
    if contract.get("candidate_gate_source") != GATE_SOURCE_COMMIT:
        raise MaterialisationError("materialiser_gate_source_mismatch")
    if set(contract.get("clockwork_materialisation_mode", [])) != set(
        HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES
    ):
        raise MaterialisationError("materialiser_clockwork_mode_mismatch")
    return contract


def preflight() -> dict[str, Any]:
    """Verify all non-content prerequisites before the metadata bind."""

    _assert_owned_roots()
    contract = load_contract()
    latch = _json(LATCH_PATH)
    historical = {
        item for item in latch.get("protected_boundaries", []) if "historical" in item
    }
    if (
        latch.get("operation_id") != OPERATION_ID
        or latch.get("status") != "in_progress"
        or historical != set(HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES)
    ):
        raise MaterialisationError("active_latch_materialisation_mode_mismatch")
    relative_gate = "orchestration_harness/historical_diary_first_use_candidate_gate.py"
    if _git_bytes(GATE_SOURCE_COMMIT, relative_gate) != (REPO_ROOT / relative_gate).read_bytes():
        raise MaterialisationError("candidate_gate_git_blob_mismatch")
    for ref in (
        "refs/heads/master",
        "refs/remotes/origin/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/handoff/current",
    ):
        if _git_ref(ref) != PROTECTED_COMMIT:
            raise MaterialisationError("protected_ref_mismatch")
    root = BOUND_ROOT.resolve(strict=True)
    ignored = (REPO_ROOT / "local_data/historical-diary-trove").resolve()
    if (
        root != BOUND_ROOT.resolve()
        or not root.is_relative_to(ignored)
        or probe._is_reparse(BOUND_ROOT)
    ):
        raise MaterialisationError("source_root_invalid")
    if ATTEMPT_ROOT.exists() or FIXTURE_ROOT.exists():
        raise MaterialisationError("owned_output_root_preexists")
    return {
        "schema_version": "raisa.historical_first_use_materialiser_preflight.v1",
        "status": "passed",
        "contract_sha256": CONTRACT_SHA256,
        "gate_source_commit": GATE_SOURCE_COMMIT,
        "clockwork_mode_member_count": len(
            HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES
        ),
        "source_root_count": 1,
        "archive_content_reads": 0,
        "attempt_root_absent": True,
        "fixture_root_absent": True,
        "provider_or_model_calls": 0,
        "protected_refs_aligned": True,
        "maximum_file_count": contract["private_input_ceiling"]["maximum_file_count"],
    }


def bind() -> dict[str, Any]:
    """Perform the sole metadata-only bind and create its private manifest."""

    preflight()
    manifest, public = probe.build_binding_manifest(
        attempt_root=ATTEMPT_ROOT,
        core_path=CORE_PATH,
        extractor_path=EXTRACTOR_PATH,
    )
    ATTEMPT_ROOT.mkdir(parents=True, exist_ok=False)
    probe._safe_public_write(MANIFEST_PATH, manifest.model_dump(mode="json"))
    _write_public(SAFE_BINDING_PATH, public)
    return public


def _load_manifest() -> probe.BindingManifest:
    try:
        manifest = probe.BindingManifest.model_validate_json(
            MANIFEST_PATH.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise MaterialisationError("binding_manifest_invalid") from error
    if (
        Path(manifest.root) != BOUND_ROOT.resolve()
        or Path(manifest.attempt_root) != ATTEMPT_ROOT.resolve()
        or manifest.core_sha256 != _sha256_path(CORE_PATH)
        or manifest.extractor_sha256 != _sha256_path(EXTRACTOR_PATH)
        or len(manifest.files) != probe.MAX_FILES
    ):
        raise MaterialisationError("binding_parser_or_path_drift")
    total = 0
    timestamps: list[datetime] = []
    for expected_index, item in enumerate(manifest.files):
        path = Path(item.absolute_path)
        if item.sequence_index != expected_index or path.parent != BOUND_ROOT.resolve():
            raise MaterialisationError("binding_manifest_scope_invalid")
        if probe._is_reparse(path) or not path.is_file() or path.suffix.lower() != ".doc":
            raise MaterialisationError("binding_file_scope_drift")
        stat = path.stat()
        if stat.st_size != item.size_bytes or stat.st_mtime_ns != item.modified_time_ns:
            raise MaterialisationError("binding_file_metadata_drift")
        total += stat.st_size
        timestamps.append(datetime.fromisoformat(item.observation_timestamp))
    if total != manifest.total_bytes or total > probe.MAX_TOTAL_BYTES:
        raise MaterialisationError("binding_total_byte_drift")
    if (
        timestamps != sorted(timestamps)
        or len(timestamps) != len(set(timestamps))
        or any(
            value.date().isoformat() != manifest.selected_source_day
            for value in timestamps
        )
    ):
        raise MaterialisationError("binding_timestamp_drift")
    first = timestamps[0]
    if any(
        item.observation_offset_seconds != int((timestamp - first).total_seconds())
        for item, timestamp in zip(manifest.files, timestamps, strict=True)
    ):
        raise MaterialisationError("binding_offset_drift")
    return manifest


def _projected_events(projection: probe.PrivateProjection) -> tuple[_ObservedEvent, ...]:
    events: set[_ObservedEvent] = set()
    for previous, current in zip(projection.snapshots, projection.snapshots[1:]):
        observation_minute = current.observation_interval_start_seconds // 60
        previous_by_token = {cell.cell_token: cell for cell in previous.cells}
        current_by_token = {cell.cell_token: cell for cell in current.cells}
        previous_positions = {
            (cell.table_index, cell.row_index, cell.column_index, cell.segment_ordinal): cell
            for cell in previous.cells
        }
        current_positions = {
            (cell.table_index, cell.row_index, cell.column_index, cell.segment_ordinal): cell
            for cell in current.cells
        }

        for token in current_by_token.keys() - previous_by_token.keys():
            cell = current_by_token[token]
            events.add(
                _ObservedEvent(
                    "scheduled_slot_added",
                    observation_minute,
                    token,
                    cell.resource_ordinal,
                )
            )
        for token in previous_by_token.keys() - current_by_token.keys():
            cell = previous_by_token[token]
            events.add(
                _ObservedEvent(
                    "scheduled_slot_removed",
                    observation_minute,
                    token,
                    cell.resource_ordinal,
                )
            )
        for token in previous_by_token.keys() & current_by_token.keys():
            before = previous_by_token[token]
            after = current_by_token[token]
            if (
                before.table_index,
                before.row_index,
                before.column_index,
                before.segment_ordinal,
            ) != (
                after.table_index,
                after.row_index,
                after.column_index,
                after.segment_ordinal,
            ):
                events.add(
                    _ObservedEvent(
                        "scheduled_slot_moved",
                        observation_minute,
                        token,
                        after.resource_ordinal,
                    )
                )
            if before.format_bucket != after.format_bucket:
                events.add(
                    _ObservedEvent(
                        "scheduled_slot_format_changed",
                        observation_minute,
                        token,
                        after.resource_ordinal,
                    )
                )
        for position in previous_positions.keys() & current_positions.keys():
            before = previous_positions[position]
            after = current_positions[position]
            if (
                before.content_token != after.content_token
            ):
                events.add(
                    _ObservedEvent(
                        "scheduled_slot_replaced",
                        observation_minute,
                        after.cell_token,
                        after.resource_ordinal,
                    )
                )

    if projection.snapshots:
        final_minute = projection.snapshots[-1].observation_interval_start_seconds // 60
        for cell in projection.snapshots[-1].cells:
            events.add(
                _ObservedEvent(
                    "scheduled_slot_present",
                    final_minute,
                    cell.cell_token,
                    cell.resource_ordinal,
                )
            )
    return tuple(
        sorted(
            events,
            key=lambda item: (
                item.minute,
                item.event_kind,
                item.resource,
                item.token,
            ),
        )
    )


def _choose_events(events: list[_ObservedEvent]) -> list[_ObservedEvent] | None:
    if len({item.minute for item in events}) < 3 or len({item.event_kind for item in events}) < 2:
        return None
    ordered = sorted(
        events,
        key=lambda item: (item.minute, item.event_kind, item.resource, item.token),
    )
    chosen: list[_ObservedEvent] = [ordered[0], ordered[-1]]
    for minute in sorted({item.minute for item in ordered}):
        if minute not in {item.minute for item in chosen}:
            chosen.append(next(item for item in ordered if item.minute == minute))
        if len({item.minute for item in chosen}) >= 3:
            break
    for kind in sorted({item.event_kind for item in ordered}):
        if kind not in {item.event_kind for item in chosen}:
            chosen.append(next(item for item in ordered if item.event_kind == kind))
        if len({item.event_kind for item in chosen}) >= 2:
            break
    for item in ordered:
        if item not in chosen:
            chosen.append(item)
        if len(chosen) >= 12:
            break
    chosen = sorted(
        chosen[:12],
        key=lambda item: (item.minute, item.event_kind, item.resource, item.token),
    )
    if (
        not 3 <= len(chosen) <= 12
        or len({item.minute for item in chosen}) < 3
        or len({item.event_kind for item in chosen}) < 2
        or not 10 <= chosen[-1].minute - chosen[0].minute <= 120
    ):
        return None
    return chosen


def derive_candidate(projection: probe.PrivateProjection) -> gate.CandidatePayload | None:
    """Select one bounded structural candidate without retaining token mappings."""

    observed = _projected_events(projection)
    minutes = sorted({item.minute for item in observed})
    for start in minutes:
        for end in minutes:
            if not 10 <= end - start <= 120:
                continue
            window = [item for item in observed if start <= item.minute <= end]
            resource_counts = Counter(item.resource for item in window)
            resources = [
                item
                for item, _count in sorted(
                    resource_counts.items(), key=lambda row: (-row[1], row[0])
                )[:8]
            ]
            for resource_count in (1, 2):
                for resource_subset in itertools.combinations(resources, resource_count):
                    resource_events = [
                        item for item in window if item.resource in resource_subset
                    ]
                    token_counts = Counter(item.token for item in resource_events)
                    tokens = [
                        item
                        for item, _count in sorted(
                            token_counts.items(), key=lambda row: (-row[1], row[0])
                        )[:12]
                    ]
                    for token_count in range(1, min(4, len(tokens)) + 1):
                        for token_subset in itertools.combinations(tokens, token_count):
                            chosen = _choose_events(
                                [
                                    item
                                    for item in resource_events
                                    if item.token in token_subset
                                ]
                            )
                            if chosen is None:
                                continue
                            base = min(item.minute for item in chosen)
                            subject_slots = {
                                token: index
                                for index, token in enumerate(
                                    sorted({item.token for item in chosen})
                                )
                            }
                            resource_slots = {
                                resource: index
                                for index, resource in enumerate(
                                    sorted({item.resource for item in chosen})
                                )
                            }
                            candidate = gate.CandidatePayload(
                                events=tuple(
                                    gate.StructuralEvent(
                                        event_kind=item.event_kind,
                                        relative_minute=item.minute - base,
                                        synthetic_subject_slot=subject_slots[item.token],
                                        resource_slot=resource_slots[item.resource],
                                    )
                                    for item in chosen
                                )
                            )
                            utility = gate.structural_utility(candidate)
                            if (
                                3 <= utility.event_count <= 12
                                and utility.distinct_relative_minutes >= 3
                                and 10 <= utility.relative_minute_span <= 120
                                and utility.distinct_event_kinds >= 2
                                and utility.synthetic_subject_slots <= 4
                                and utility.resource_slots <= 2
                            ):
                                return candidate
    return None


def _candidate_bytes(candidate: gate.CandidatePayload) -> bytes:
    return json.dumps(
        candidate.model_dump(mode="json"),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _candidate_envelope(candidate: gate.CandidatePayload) -> gate.CandidateEnvelope:
    return gate.CandidateEnvelope(
        declaration=gate.CandidateDeclaration(
            full_40_character_accepted_source_commit=gate.ACCEPTED_SOURCE_COMMIT,
            candidate_sha256=gate.canonical_candidate_sha256(candidate),
            closed_artifact_class="minimised_structural_scenario",
            exact_development_purpose=(
                "provider_free_reception_check_in_context_scenario_development"
            ),
            source_independent_synthetic_identity_policy=(
                "source_independent_synthetic_identity_only"
            ),
            relative_or_shifted_date_policy="relative_day_offset_only",
            deterministic_zero_forbidden_field_reading=0,
            structural_utility_reading=gate.structural_utility(candidate),
            non_transitive_authority_ceiling="local_provider_free_development_test_only",
        ),
        candidate=candidate,
    )


def _remove_owned_fixture(created_root: bool) -> None:
    if not created_root:
        return
    _assert_owned_roots()
    for path in (FIXTURE_TEMP_PATH, FIXTURE_PATH):
        if path.exists():
            path.unlink()
    if FIXTURE_ROOT.exists():
        if any(FIXTURE_ROOT.iterdir()):
            raise MaterialisationError("fixture_cleanup_unexpected_child")
        FIXTURE_ROOT.rmdir()


def _write_fixture(candidate: gate.CandidatePayload, expected_digest: str) -> str:
    if FIXTURE_ROOT.exists():
        raise MaterialisationError("fixture_root_preexists")
    _assert_owned_roots()
    payload = _candidate_bytes(candidate)
    if _sha256_bytes(payload) != expected_digest:
        raise MaterialisationError("candidate_bytes_digest_mismatch")
    created_root = False
    try:
        FIXTURE_ROOT.mkdir(parents=True, exist_ok=False)
        created_root = True
        with FIXTURE_TEMP_PATH.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if _sha256_path(FIXTURE_TEMP_PATH) != expected_digest:
            raise MaterialisationError("temporary_fixture_digest_mismatch")
        os.replace(FIXTURE_TEMP_PATH, FIXTURE_PATH)
        if _sha256_path(FIXTURE_PATH) != expected_digest:
            raise MaterialisationError("final_fixture_digest_mismatch")
        if sorted(path.name for path in FIXTURE_ROOT.iterdir()) != ["scenario.json"]:
            raise MaterialisationError("fixture_root_postcondition_failed")
        return expected_digest
    except Exception:
        _remove_owned_fixture(created_root)
        raise


def _cleanup_private_files() -> list[str]:
    removed: list[str] = []
    for path, label in (
        (MANIFEST_PATH, "private_manifest"),
        (WORD_CONTROL_PATH, "word_control"),
        (WORD_PROGRESS_PATH, "word_progress"),
        (WORD_CLEANUP_RECEIPT_PATH, "word_cleanup_receipt"),
    ):
        if path.exists():
            path.unlink()
            removed.append(label)
    return removed


def _sanitized_reason(error: Exception) -> str:
    if isinstance(error, (MaterialisationError, probe.ProbeError)):
        candidate = str(error).partition(":")[0]
        if candidate and all(
            character.islower() or character.isdigit() or character == "_"
            for character in candidate
        ):
            return candidate
    return "internal_local_materialisation_failure"


def _terminal(
    *,
    status: Literal["in_progress", "completed", "failed"],
    decision: TerminalDecision | None,
    reason_codes: list[str],
    gate_result: gate.GateResult | None = None,
    fixture_digest: str | None = None,
    cleanup_removed: list[str] | None = None,
) -> dict[str, Any]:
    candidate_utility = None
    candidate_digest = None
    if gate_result is not None and gate_result.binding is not None:
        candidate_digest = gate_result.binding.candidate_sha256
    value = {
        "schema_version": "raisa.historical_first_use_materialisation_terminal.v1",
        "evidence_label": "private_derived_local_first_use_terminal_non_phi",
        "status": status,
        "decision": decision,
        "reason_codes": reason_codes,
        "gate_decision": None if gate_result is None else gate_result.decision,
        "candidate_sha256": candidate_digest,
        "fixture_sha256": fixture_digest,
        "candidate_fixture_digest_match": (
            candidate_digest is not None and candidate_digest == fixture_digest
        ),
        "candidate_utility": candidate_utility,
        "fixture_count": 1 if fixture_digest is not None else 0,
        "private_cleanup_removed": cleanup_removed or [],
        "privacy": {
            "source_text_emitted": False,
            "identity_contact_note_emitted": False,
            "filename_path_or_exact_timestamp_emitted": False,
            "token_key_or_mapping_emitted": False,
            "private_projection_persisted": False,
        },
        "authority": {
            "provider_or_model_calls": 0,
            "product_database_client_or_runtime": False,
            "ordinary_practice": False,
            "authority_non_transitive": True,
        },
    }
    return value


def execute() -> dict[str, Any]:
    """Consume the sole content run and materialise one admitted fixture or none."""

    if CONTENT_TERMINAL_PATH.exists():
        raise MaterialisationError("content_run_already_consumed")
    manifest = _load_manifest()
    if FIXTURE_ROOT.exists():
        raise MaterialisationError("fixture_root_preexists")
    _write_public(
        CONTENT_TERMINAL_PATH,
        _terminal(status="in_progress", decision=None, reason_codes=[]),
    )
    try:
        completed = probe.run_owned_word_subprocess(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(EXTRACTOR_PATH),
                "-Manifest",
                str(MANIFEST_PATH),
                "-ControlPath",
                str(WORD_CONTROL_PATH),
                "-ProgressPath",
                str(WORD_PROGRESS_PATH),
                "-ExecutionProfile",
                "HistoricalFirstUseMaterialisation",
            ],
            timeout_seconds=1800,
            control_path=WORD_CONTROL_PATH,
            cleanup_receipt_path=WORD_CLEANUP_RECEIPT_PATH,
            cleanup_script_path=WORD_CLEANUP_PATH,
        )
        if len(completed.stdout) > MAX_PRIVATE_PIPE_BYTES:
            raise MaterialisationError("private_pipe_byte_cap_exceeded")
        try:
            extraction = probe.PrivateExtraction.model_validate_json(completed.stdout)
        except ValueError as error:
            raise MaterialisationError("private_extraction_invalid") from error
        if len(extraction.snapshots) != len(manifest.files):
            raise MaterialisationError("extraction_manifest_count_mismatch")
        cleanup = probe.cleanup_owned_word_process(
            control_path=WORD_CONTROL_PATH,
            receipt_path=WORD_CLEANUP_RECEIPT_PATH,
            cleanup_script_path=WORD_CLEANUP_PATH,
            control_absence_is_safe=extraction.word_cleanup_completed,
        )
        if not cleanup.exact_owned_process_absent:
            raise MaterialisationError("owned_word_cleanup_failed")
        projection, aggregate = probe.project_and_measure(extraction)
        if (
            aggregate["privacy"]["source_value_leakage_count"] != 0
            or projection.source_filename_or_path_emitted
            or projection.exact_source_timestamp_emitted
            or projection.key_or_mapping_emitted
            or projection.page_coordinate_or_distance_emitted
        ):
            raise MaterialisationError("private_projection_boundary_failed")
        candidate = derive_candidate(projection)
        if candidate is None:
            removed = _cleanup_private_files()
            result = _terminal(
                status="completed",
                decision="revision_required",
                reason_codes=["no_admissible_minimised_structural_candidate"],
                cleanup_removed=removed,
            )
            _write_public(CONTENT_TERMINAL_PATH, result)
            return result
        envelope = _candidate_envelope(candidate)
        gate_result = gate.evaluate(envelope)
        if gate_result.decision != "admitted_for_exact_declared_artifact_only":
            removed = _cleanup_private_files()
            decision: TerminalDecision = gate_result.decision
            result = _terminal(
                status="completed",
                decision=decision,
                reason_codes=list(gate_result.reason_codes),
                gate_result=gate_result,
                cleanup_removed=removed,
            )
            _write_public(CONTENT_TERMINAL_PATH, result)
            return result
        if gate_result.binding is None or not gate_result.binding.non_transitive:
            raise MaterialisationError("gate_binding_missing_or_transitive")
        fixture_digest = _write_fixture(
            candidate, gate_result.binding.candidate_sha256
        )
        removed = _cleanup_private_files()
        result = _terminal(
            status="completed",
            decision="materialised_for_exact_declared_local_test_artifact_only",
            reason_codes=[],
            gate_result=gate_result,
            fixture_digest=fixture_digest,
            cleanup_removed=removed,
        )
        result["candidate_utility"] = gate.structural_utility(candidate).model_dump(
            mode="json"
        )
        _write_public(CONTENT_TERMINAL_PATH, result)
        return result
    except Exception as error:
        cleanup = probe.cleanup_owned_word_process(
            control_path=WORD_CONTROL_PATH,
            receipt_path=WORD_CLEANUP_RECEIPT_PATH,
            cleanup_script_path=WORD_CLEANUP_PATH,
            control_absence_is_safe=True,
        )
        fixture_cleanup_succeeded = True
        if FIXTURE_ROOT.exists():
            try:
                _remove_owned_fixture(created_root=True)
            except (MaterialisationError, OSError):
                fixture_cleanup_succeeded = False
        removed = _cleanup_private_files()
        reasons = [_sanitized_reason(error)]
        if not cleanup.exact_owned_process_absent:
            reasons.append("owned_word_cleanup_failed")
        if not fixture_cleanup_succeeded:
            reasons.append("fixture_cleanup_incomplete")
        result = _terminal(
            status="failed",
            decision="blocked",
            reason_codes=reasons,
            cleanup_removed=removed,
        )
        result["owned_word_process_absent"] = cleanup.exact_owned_process_absent
        _write_public(CONTENT_TERMINAL_PATH, result)
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--preflight", action="store_true")
    phase.add_argument("--bind", action="store_true")
    phase.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        if arguments.preflight:
            result = preflight()
        elif arguments.bind:
            result = bind()
        else:
            result = execute()
    except Exception as error:
        print(
            json.dumps(
                {
                    "schema_version": "raisa.historical_first_use_materialiser_failure.v1",
                    "status": "blocked",
                    "reason_code": _sanitized_reason(error),
                    "archive_content_retry_authorized": False,
                    "source_value_emitted": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") != "failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
