"""Two-file journal scope using one externally authenticated maintenance base.

This is the successor maintenance route's manifest and committed-scope checker.
It does not invoke the historical whole-tree policy loader, change its behavior,
accept the journal implementation, or grant a commit/push operation. The caller
must authenticate the activation digest and original lineage externally.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from orchestration_harness.controller_maintenance_activation import (
    MaintenanceActivation,
    _parse_maintenance_activation_core,
)
from orchestration_harness.controller_maintenance_candidate import (
    _command,
    _compare_candidate_core,
)
from orchestration_harness.controller_maintenance_record import (
    MaintenanceRecord,
    parse_maintenance_record,
)
from orchestration_harness.controller_maintenance_request import canonical_bytes


JOURNAL_FILES = (
    (
        "orchestration_harness/clockwork_journal.py",
        "98686ae95c8477511e0ebee0170e0232ee39c5270b14d1cdcba74def11791b6c",
    ),
    (
        "tests/test_clockwork_journal.py",
        "53f9daef9c2051e2422924f179a23bd953dbc3cceedbfe956bf3dd4744620126",
    ),
)
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class MaintenanceJournalError(ValueError):
    def __init__(self, reason_code):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class JournalBaseBinding:
    """Consistency object whose external authentication belongs to its caller."""

    activation: MaintenanceActivation
    maintenance: MaintenanceRecord
    activation_sha256: str


def bind_journal_base(
    activation_payload: bytes,
    *,
    expected_activation_sha256: str,
    manifest_payload: bytes,
    original_commit: str,
    original_tree: str,
    governing_commit: str,
    governing_tree: str,
) -> JournalBaseBinding:
    activation = _parse_maintenance_activation_core(
        activation_payload,
        expected_sha256=expected_activation_sha256,
        manifest_payload=manifest_payload,
        original_commit=original_commit,
        original_tree=original_tree,
        governing_commit=governing_commit,
        governing_tree=governing_tree,
    )
    maintenance = parse_maintenance_record(
        manifest_payload, expected_sha256=activation.accepted_manifest_sha256
    )
    return JournalBaseBinding(activation, maintenance, expected_activation_sha256)


def _shared_current_base(binding: JournalBaseBinding) -> str:
    if type(binding) is not JournalBaseBinding:
        raise MaintenanceJournalError("authenticated_journal_base_required")
    # No first-descendant/arbitrary-HEAD fallback exists on the new route.
    return binding.activation.journal_base_commit


def validate_journal_manifest(value, *, binding: JournalBaseBinding) -> dict:
    base = _shared_current_base(binding)
    if type(value) is not dict or set(value) != {
        "schema_version",
        "phase",
        "base_commit",
        "candidate_head",
        "candidate_tree",
        "paths",
    }:
        raise MaintenanceJournalError("journal_manifest_shape_invalid")
    if (
        type(value["schema_version"]) is not str
        or value["schema_version"] != "ariadne.maintenance_journal_scope.v1"
    ):
        raise MaintenanceJournalError("journal_manifest_schema_invalid")
    if type(value["base_commit"]) is not str or value["base_commit"] != base:
        raise MaintenanceJournalError("journal_manifest_base_mismatch")
    for field in ("candidate_head", "candidate_tree"):
        if type(value[field]) is not str or _HEX40.fullmatch(value[field]) is None:
            raise MaintenanceJournalError("journal_manifest_identity_invalid")
    phase = value["phase"]
    if type(phase) is not str or phase not in {"development", "committed"}:
        raise MaintenanceJournalError("journal_manifest_phase_invalid")
    if (phase == "development") != (value["candidate_head"] == base):
        raise MaintenanceJournalError("journal_manifest_head_phase_mismatch")
    if (
        type(value["paths"]) is not list
        or any(type(path) is not str for path in value["paths"])
        or value["paths"] != [path for path, _digest in JOURNAL_FILES]
    ):
        raise MaintenanceJournalError("journal_scope_not_exactly_two_files")
    return {**value, "paths": tuple(value["paths"])}


def validate_journal_committed_scope(
    root: Path,
    value,
    *,
    binding: JournalBaseBinding,
    scratch_parent: Path,
) -> dict:
    normalized = validate_journal_manifest(value, binding=binding)
    base = _shared_current_base(binding)
    maintenance = binding.maintenance
    activation = binding.activation
    if _command(root, "rev-list", "--parents", "-n", "1", base).decode().split() != [
        base,
        maintenance.base_commit,
    ]:
        raise MaintenanceJournalError("journal_maintenance_parent_mismatch")
    if (
        _command(root, "rev-parse", base + "^{tree}").decode().strip()
        != activation.maintenance_tree
    ):
        raise MaintenanceJournalError("journal_maintenance_tree_mismatch")
    head = normalized["candidate_head"]
    # This route implements the first journal addition, not a later revision.
    for path, _digest in JOURNAL_FILES:
        if _command(root, "ls-tree", "--format=%(objecttype)", base, "--", path):
            raise MaintenanceJournalError("journal_addition_base_path_present")
    if normalized["phase"] == "committed":
        if _command(
            root, "rev-list", "--parents", "-n", "1", head
        ).decode().split() != [head, base]:
            raise MaintenanceJournalError("journal_commit_parent_mismatch")
        if (
            _command(root, "rev-parse", head + "^{tree}").decode().strip()
            != normalized["candidate_tree"]
        ):
            raise MaintenanceJournalError("journal_commit_tree_mismatch")
    record = asdict(maintenance)
    record.update(
        base_commit=base,
        base_tree=activation.maintenance_tree,
        candidate_tree=normalized["candidate_tree"],
        changed_files=[
            {
                "path": path,
                "mode": "100644",
                "before_sha256": None,
                "after_sha256": digest,
            }
            for path, digest in JOURNAL_FILES
        ],
        frozen_files=[
            {
                "path": row.path,
                "mode": "100644",
                "before_sha256": row.after_sha256,
                "after_sha256": row.after_sha256,
            }
            for row in (*maintenance.changed_files, *maintenance.frozen_files)
        ],
    )
    raw = canonical_bytes(record)
    comparison = _compare_candidate_core(
        root,
        raw,
        expected_manifest_sha256=hashlib.sha256(raw).hexdigest(),
        scratch_parent=scratch_parent,
        expected_current_head=head,
    )
    return {
        "schema_version": "ariadne.maintenance_journal_scope_evidence.v1",
        "journal_base_commit": base,
        "candidate_head": head,
        "candidate_tree": normalized["candidate_tree"],
        "paths": [path for path, _digest in JOURNAL_FILES],
        "maintenance_history_preserved": True,
        "observation_sha256": comparison["observation_sha256"],
        "operation_authority": False,
        "journal_review_acceptance": False,
        "complete_physical_worktree_attested": False,
    }
