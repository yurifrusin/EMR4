"""LC4V3 content-blind certification framework.

This module is the content-blind LC4V3 certification framework.  It validates
structure, manifest, seal, and aggregate evaluation without loading or
inspecting actual corpus content.  The real corpus is authored by Sol after
all external workers close.

The fixed production shape is:
  - 24 groups (lc4v3_group_001 through lc4v3_group_024)
  - 12 variants per group (9 surface + 3 multi-turn trajectories)
  - 288 total scenarios, 72 trajectories
  - 2 deterministic repeats -> 576 production aggregate samples

Authority boundaries
-------------------
- This module never loads a real v3 corpus, manifest, seal, or report.
- Protected holdouts v1 and v2 remain sealed and are never imported.
- No provider, route/API, database, UI, deployment, runtime, historical diary,
  memory, confirmation, release, or write-authority surface is referenced.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import re
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    score_interpretation_replay_pair,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Fixed production shape – content-blind contract constants
# ---------------------------------------------------------------------------

LC4V3_CORPUS_IDENTITY: str = "lc4-holdout-v3"
LC4V3_MANIFEST_SCHEMA: str = "lc4v3.manifest.v1"
LC4V3_SEAL_SCHEMA: str = "lc4v3.seal.v1"
LC4V3_EVALUATOR_VERSION: str = "lc4v3.aggregate_evaluator.v1"
LC4V3_EVALUATION_ID: str = "lc4-holdout-v3-baseline-001"
LC4V3_GROUP_COUNT: int = 24
LC4V3_VARIANTS_PER_GROUP: int = 12
LC4V3_SURFACE_PER_GROUP: int = 9
LC4V3_MT_PER_GROUP: int = 3
LC4V3_TOTAL_SCENARIOS: int = 288
LC4V3_TOTAL_TRAJECTORIES: int = 72
LC4V3_REPEAT_COUNT: int = 2
LC4V3_TOTAL_SAMPLES: int = 576
LC4V3_GROUP_PREFIX: str = "lc4v3_group_"
LC4V3_REPORT_SCHEMA: str = "lc4v3.aggregate_evaluation.v1"
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SCENARIO_ID_RE = re.compile(r"^lc4v3_(?:var|mt)_\d{3}_\d{2}$")

_MANIFEST_KEYS = {
    "schema_version", "corpus_identity", "group_count", "variants_per_group",
    "surface_variants_per_group", "multi_turn_per_group", "total_scenarios",
    "total_trajectories", "repeat_count", "total_production_samples",
    "evaluation_id", "evaluator_version", "files", "corpus_hash",
}
_SEAL_KEYS = {
    "seal_version", "manifest_hash", "corpus_hash", "source_commit",
    "evaluator_version", "evaluation_id", "repeat_count", "consumed",
}
_REPORT_KEYS = {
    "schema_version", "evaluation_id", "evaluator_version", "source_commit",
    "manifest_hash", "corpus_hash", "total_groups", "total_scenarios",
    "total_trajectories", "total_samples", "repeat_count", "per_dimension",
    "failure_layers", "critical_slices", "variance", "coverage_cells",
    "report_hash",
}

# Canonical lattice dimension vocabularies (same as LC4)
ALL_ACTIONS: list[str] = [
    "create", "move", "resize", "cancel",
    "status_change", "explain_schedule",
]
ALL_DIARY_STATES: list[str] = [
    "empty", "exact_duplicate", "overlap", "same_day_distinct",
    "terminal", "stale", "concurrent", "roster_absent",
    "break", "no_slots", "elapsed_window",
]
ALL_ENTITY_SEMANTICS: list[str] = [
    "exact", "omitted", "ambiguous", "corrected", "negated", "mismatched",
]
ALL_TEMPORAL_RELATIONS: list[str] = [
    "exact", "not_before", "not_after", "interval", "approximate", "unspecified",
]
ALL_DIALOGUE_FORMS: list[str] = [
    "one_shot", "clarification", "correction", "reversal",
    "ellipsis", "anaphora", "repeated", "session_restart",
]
ALL_LANGUAGE_FORMS: list[str] = [
    "plain", "paraphrase", "filler", "abbreviation",
    "typo", "speech_like", "punctuation_variant", "adversarial",
]

# Pre-declared aggregate dimension names (the only permitted per-dimension keys)
# These use plural/qualified forms to avoid conflict with prohibited case-level keys.
PER_DIMENSION_NAMES: list[str] = [
    "complete_composed_contract", "intended_action", "action_semantics",
    "temporal_relation", "normalized_values", "entity_semantics",
    "clarification", "downstream_outcome", "replay_tool_sequence",
    "interpretation_tools", "authority", "appointment_deltas",
    "audit_deltas", "safety",
]

# Failure layers
FAILURE_LAYERS: list[str] = [
    "interpretation", "policy", "integration", "safety",
]

# Prohibited keys at every nesting depth (case-insensitive).
# These would disclose per-case structure and are forbidden in aggregate reports.
_PROHIBITED_AGGREGATE_KEYS: frozenset[str] = frozenset({
    # scenario / variant / group identifiers
    "scenario_id", "scenario", "group_id", "variant_id", "variant",
    # utterances and dialogue
    "utterance", "utterance_text", "dialogue_turn", "turn_text", "turn",
    "observation_text", "receptionist_text", "patient_text",
    # expected / observed outcome labels
    "expected_outcome", "expected", "expected_label", "observed",
    "observed_outcome", "actual_outcome", "actual",
    # expected tools / tool sequences
    "expected_tool", "expected_tool_sequence", "tool_sequence",
    "expected_delta", "appointment_delta", "delta",
    # source spans
    "source_span", "source_spans", "span", "span_text",
    # normalized values
    "normalized_value", "normalized",
    # case findings / per-case results
    "case_finding", "case_findings", "finding", "findings",
    "per_case_result", "per_case", "result", "per_sample",
    # forbidden content
    "forbidden_outcome", "forbidden_tool",
})
_PROHIBITED_KEY_FRAGMENTS = (
    "utterance", "dialogue_turn", "source_span", "scenario_id", "group_id",
    "variant_id", "expected_", "observed_", "actual_", "tool_sequence",
    "appointment_delta", "audit_delta", "normalized_value", "case_finding",
    "per_case", "per_sample",
)
_SAFE_FRAGMENT_KEYS = {
    "replay_tool_sequence", "appointment_deltas", "audit_deltas",
    "normalized_values",
}


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest with ``sha256:`` prefix."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _file_hash(filepath: pathlib.Path) -> str:
    """Compute SHA-256 of file contents."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return "sha256:" + sha.hexdigest()


# ---------------------------------------------------------------------------
# Source-commit helper
# ---------------------------------------------------------------------------


def get_source_commit() -> str:
    """Return the current full Git HEAD, failing closed on any uncertainty."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=pathlib.Path(__file__).resolve().parent,
        )
        commit = result.stdout.strip().lower()
    except (subprocess.SubprocessError, FileNotFoundError) as error:
        raise ValueError("cannot resolve frozen source commit") from error
    if not _COMMIT_RE.fullmatch(commit):
        raise ValueError("Git HEAD is not a full 40-hex source commit")
    return commit


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{label} schema drift: {sorted(set(value) ^ expected)}")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{label} must be canonical sha256:<64 lowercase hex>")
    return value


def _require_commit(value: Any, label: str = "source_commit") -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{label} must be a full 40-hex Git commit")
    return value


def _validated_group_scenarios(
    data: dict[str, Any], group_index: int,
) -> tuple[list[ReceptionScenarioSpec], list[ReceptionScenarioSpec]]:
    _require_exact_keys(
        data,
        {"group_id", "surface_variants", "multi_turn_variants"},
        f"group {group_index}",
    )
    expected_group_id = f"{LC4V3_GROUP_PREFIX}{group_index:03d}"
    if data["group_id"] != expected_group_id:
        raise ValueError(f"group {group_index} identity drift")
    raw_surface = data["surface_variants"]
    raw_multi = data["multi_turn_variants"]
    if not isinstance(raw_surface, list) or len(raw_surface) != LC4V3_SURFACE_PER_GROUP:
        raise ValueError(f"{expected_group_id}: invalid surface variant count")
    if not isinstance(raw_multi, list) or len(raw_multi) != LC4V3_MT_PER_GROUP:
        raise ValueError(f"{expected_group_id}: invalid multi-turn variant count")

    def validate(raw: Any, *, position: int, multi_turn: bool) -> ReceptionScenarioSpec:
        if not isinstance(raw, dict):
            raise ValueError(f"{expected_group_id}: scenario must be an object")
        expected_id = (
            f"lc4v3_mt_{group_index:03d}_{position:02d}"
            if multi_turn else f"lc4v3_var_{group_index:03d}_{position:02d}"
        )
        if raw.get("scenario_id") != expected_id or not _SCENARIO_ID_RE.fullmatch(expected_id):
            raise ValueError(f"{expected_group_id}: scenario identity drift")
        if "expected_outcome_kind" not in raw:
            raise ValueError(f"{expected_id}: explicit expected outcome is required")
        if raw.get("provenance") != "gold" or raw.get("adjudication") != "adjudicated":
            raise ValueError(f"{expected_id}: certification cases must be Gold/adjudicated")
        if not isinstance(raw.get("source_spans"), dict) or not raw["source_spans"]:
            raise ValueError(f"{expected_id}: non-empty lossless source spans are required")
        initial = raw.get("initial_diary_state")
        if not isinstance(initial, dict) or initial.get("synthetic") is not True:
            raise ValueError(f"{expected_id}: diary state must be explicitly synthetic")
        scenario = ReceptionScenarioSpec.model_validate(raw)
        if multi_turn and len(scenario.dialogue_turns) < 2:
            raise ValueError(f"{expected_id}: trajectory must contain multiple turns")
        if not multi_turn and len(scenario.dialogue_turns) != 1:
            raise ValueError(f"{expected_id}: surface variant must be one turn")
        return scenario

    surfaces = [validate(raw, position=i, multi_turn=False) for i, raw in enumerate(raw_surface, 1)]
    multi = [validate(raw, position=i, multi_turn=True) for i, raw in enumerate(raw_multi, 1)]
    return surfaces, multi


# ---------------------------------------------------------------------------
# Manifest building and reconstruction
# ---------------------------------------------------------------------------


def build_manifest(corpus_dir: pathlib.Path) -> dict[str, Any]:
    """Build the LC4V3 manifest from a corpus directory.

    Scans for group JSON files, validates count (24), variant shape
    (9 surface + 3 multi-turn per group), computes file hashes, and
    returns the manifest dict with canonical corpus hash.

    Parameters
    ----------
    corpus_dir :
        Directory containing the 24 group JSON files.

    Returns
    -------
    dict
        The manifest dict with ``schema_version``, ``files``, ``corpus_hash``,
        and all fixed shape fields.

    Raises
    ------
    NotADirectoryError
        If *corpus_dir* does not exist.
    ValueError
        If the group count, filenames, variant shape, or totals mismatch.
    """
    if not corpus_dir.is_dir():
        raise NotADirectoryError(f"Corpus directory not found: {corpus_dir}")

    group_files: list[pathlib.Path] = sorted(
        corpus_dir.glob(f"{LC4V3_GROUP_PREFIX}*.json")
    )

    if len(group_files) != LC4V3_GROUP_COUNT:
        raise ValueError(
            f"Expected {LC4V3_GROUP_COUNT} group files, found {len(group_files)}"
        )

    expected_names: list[str] = [
        f"{LC4V3_GROUP_PREFIX}{i:03d}.json"
        for i in range(1, LC4V3_GROUP_COUNT + 1)
    ]
    actual_names: list[str] = [f.name for f in group_files]
    if actual_names != expected_names:
        raise ValueError(
            f"Group filenames do not match expected pattern. "
            f"Expected first {expected_names[0]!r}, last {expected_names[-1]!r}; "
            f"got first {actual_names[0]!r}, last {actual_names[-1]!r}"
        )

    file_entries: list[dict[str, str]] = []
    total_scenarios_count: int = 0
    total_trajectories_count: int = 0
    all_ids: set[str] = set()

    for group_index, gf in enumerate(group_files, 1):
        fhash: str = _file_hash(gf)
        file_entries.append({"filename": gf.name, "file_hash": fhash})

        with open(gf, "r", encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"{gf.name}: group payload must be an object")
        surfaces, multi_turns = _validated_group_scenarios(data, group_index)
        for scenario in [*surfaces, *multi_turns]:
            if scenario.scenario_id in all_ids:
                raise ValueError(f"duplicate scenario ID: {scenario.scenario_id}")
            all_ids.add(scenario.scenario_id)

        total_scenarios_count += len(surfaces) + len(multi_turns)
        total_trajectories_count += len(multi_turns)

    if total_scenarios_count != LC4V3_TOTAL_SCENARIOS:
        raise ValueError(
            f"Total scenarios {total_scenarios_count} != expected "
            f"{LC4V3_TOTAL_SCENARIOS}"
        )
    if total_trajectories_count != LC4V3_TOTAL_TRAJECTORIES:
        raise ValueError(
            f"Total trajectories {total_trajectories_count} != expected "
            f"{LC4V3_TOTAL_TRAJECTORIES}"
        )
    if len(all_ids) != LC4V3_TOTAL_SCENARIOS:
        raise ValueError("scenario identity population is incomplete")

    corpus_hash_input: str = _canonical_json(file_entries)
    corpus_hash: str = _stable_hash(corpus_hash_input)

    manifest: dict[str, Any] = {
        "schema_version": LC4V3_MANIFEST_SCHEMA,
        "corpus_identity": LC4V3_CORPUS_IDENTITY,
        "group_count": LC4V3_GROUP_COUNT,
        "variants_per_group": LC4V3_VARIANTS_PER_GROUP,
        "surface_variants_per_group": LC4V3_SURFACE_PER_GROUP,
        "multi_turn_per_group": LC4V3_MT_PER_GROUP,
        "total_scenarios": LC4V3_TOTAL_SCENARIOS,
        "total_trajectories": LC4V3_TOTAL_TRAJECTORIES,
        "repeat_count": LC4V3_REPEAT_COUNT,
        "total_production_samples": LC4V3_TOTAL_SAMPLES,
        "evaluation_id": LC4V3_EVALUATION_ID,
        "evaluator_version": LC4V3_EVALUATOR_VERSION,
        "files": file_entries,
        "corpus_hash": corpus_hash,
    }

    return manifest


def reconstruct_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct and verify a manifest dict.

    Validates all fixed-shape fields, recomputes the corpus hash from
    the file entries, and returns the verified manifest.

    Parameters
    ----------
    manifest :
        The manifest dict to verify.

    Returns
    -------
    dict
        The verified manifest (same as input on success).

    Raises
    ------
    ValueError
        On any schema, count, hash, or field mismatch.
    """
    _require_exact_keys(manifest, _MANIFEST_KEYS, "manifest")
    # Schema identity
    if manifest.get("schema_version") != LC4V3_MANIFEST_SCHEMA:
        raise ValueError(
            f"Manifest schema version mismatch: "
            f"{manifest.get('schema_version')!r} != {LC4V3_MANIFEST_SCHEMA!r}"
        )
    if manifest.get("corpus_identity") != LC4V3_CORPUS_IDENTITY:
        raise ValueError(
            f"Manifest corpus identity mismatch: "
            f"{manifest.get('corpus_identity')!r} != {LC4V3_CORPUS_IDENTITY!r}"
        )

    # Fixed counts
    _require_equal(manifest, "group_count", LC4V3_GROUP_COUNT)
    _require_equal(manifest, "variants_per_group", LC4V3_VARIANTS_PER_GROUP)
    _require_equal(manifest, "surface_variants_per_group", LC4V3_SURFACE_PER_GROUP)
    _require_equal(manifest, "multi_turn_per_group", LC4V3_MT_PER_GROUP)
    _require_equal(manifest, "total_scenarios", LC4V3_TOTAL_SCENARIOS)
    _require_equal(manifest, "total_trajectories", LC4V3_TOTAL_TRAJECTORIES)
    _require_equal(manifest, "repeat_count", LC4V3_REPEAT_COUNT)
    _require_equal(manifest, "total_production_samples", LC4V3_TOTAL_SAMPLES)
    _require_equal(manifest, "evaluation_id", LC4V3_EVALUATION_ID)
    _require_equal(manifest, "evaluator_version", LC4V3_EVALUATOR_VERSION)

    # File entries
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != LC4V3_GROUP_COUNT:
        raise ValueError("Manifest file population is missing or has the wrong count")

    # Verify filenames are sorted and match expected pattern
    if not all(isinstance(entry, dict) for entry in files):
        raise ValueError("Manifest file entries must be objects")
    filenames: list[str] = [f.get("filename", "") for f in files]
    if filenames != sorted(filenames):
        raise ValueError("Manifest filenames are not sorted")

    for i, entry in enumerate(files):
        _require_exact_keys(entry, {"filename", "file_hash"}, f"manifest file[{i}]")
        expected_filename = f"{LC4V3_GROUP_PREFIX}{i + 1:03d}.json"
        if entry.get("filename") != expected_filename:
            raise ValueError(
                f"Manifest file[{i}] filename {entry.get('filename')!r} "
                f"!= expected {expected_filename!r}"
            )
        _require_sha256(entry.get("file_hash"), f"manifest file[{i}] hash")

    # Reconstruct corpus hash
    corpus_hash_input: str = _canonical_json(files)
    recomputed_hash: str = _stable_hash(corpus_hash_input)
    if recomputed_hash != manifest.get("corpus_hash"):
        raise ValueError(
            f"Manifest corpus hash mismatch: "
            f"recomputed={recomputed_hash} != stored={manifest.get('corpus_hash')}"
        )

    return manifest


def verify_manifest_against_corpus(
    corpus_dir: pathlib.Path, manifest: dict[str, Any],
) -> dict[str, Any]:
    """Rebuild a pre-consumption manifest and require exact equality."""
    reconstructed = reconstruct_manifest(manifest)
    live = build_manifest(corpus_dir)
    if live != reconstructed:
        raise ValueError("frozen manifest does not exactly match corpus")
    return reconstructed


def load_verified_scenarios(corpus_dir: pathlib.Path) -> list[ReceptionScenarioSpec]:
    """Load the exact validated scenario population before consumption."""
    group_files = sorted(corpus_dir.glob(f"{LC4V3_GROUP_PREFIX}*.json"))
    if [p.name for p in group_files] != [
        f"{LC4V3_GROUP_PREFIX}{i:03d}.json" for i in range(1, LC4V3_GROUP_COUNT + 1)
    ]:
        raise ValueError("LC4V3 group file population drift")
    scenarios: list[ReceptionScenarioSpec] = []
    for group_index, path in enumerate(group_files, 1):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}: group payload must be an object")
        surfaces, multi = _validated_group_scenarios(value, group_index)
        scenarios.extend(surfaces)
        scenarios.extend(multi)
    ids = [scenario.scenario_id for scenario in scenarios]
    if len(scenarios) != LC4V3_TOTAL_SCENARIOS or len(ids) != len(set(ids)):
        raise ValueError("LC4V3 scenario population or identity drift")
    return scenarios


def _require_equal(obj: dict[str, Any], key: str, expected: Any) -> None:
    """Assert that *obj[key]* equals *expected*, else raise ``ValueError``."""
    actual = obj.get(key)
    if actual != expected:
        raise ValueError(
            f"Manifest {key}: {actual!r} != expected {expected!r}"
        )


# ---------------------------------------------------------------------------
# Seal creation and verification
# ---------------------------------------------------------------------------


def create_seal(
    manifest: dict[str, Any],
    *,
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Create a seal dict from a verified manifest.

    Reconstructs and verifies the manifest first, then binds the source
    commit, manifest hash, corpus hash, evaluator version, evaluation ID,
    and repeat policy.

    Parameters
    ----------
    manifest :
        The manifest to seal.  Must pass ``reconstruct_manifest``.
    source_commit :
        The Git commit hash to bind.  If None, auto-detects via
        ``get_source_commit()``.

    Returns
    -------
    dict
        The seal dict with ``consumed`` set to False.

    Raises
    ------
    ValueError
        If the manifest fails reconstruction/verification.
    """
    verified: dict[str, Any] = reconstruct_manifest(manifest)

    if source_commit is None:
        source_commit = get_source_commit()
    source_commit = _require_commit(source_commit)

    manifest_hash: str = _stable_hash(_canonical_json(verified))

    seal: dict[str, Any] = {
        "seal_version": LC4V3_SEAL_SCHEMA,
        "manifest_hash": manifest_hash,
        "corpus_hash": verified["corpus_hash"],
        "source_commit": source_commit,
        "evaluator_version": LC4V3_EVALUATOR_VERSION,
        "evaluation_id": LC4V3_EVALUATION_ID,
        "repeat_count": LC4V3_REPEAT_COUNT,
        "consumed": False,
    }

    return seal


def verify_seal(
    seal: dict[str, Any],
    manifest: dict[str, Any],
    *,
    expected_source_commit: str | None = None,
) -> dict[str, Any]:
    """Verify a seal against its manifest.

    Reconstructs the manifest, recomputes the expected manifest hash and
    corpus hash, and compares them against the seal.  Returns the verified
    seal on success.

    Parameters
    ----------
    seal :
        The seal dict to verify.
    manifest :
        The manifest dict that the seal was created from.

    Returns
    -------
    dict
        The verified seal (same as input on success).

    Raises
    ------
    ValueError
        On any hash, version, or field mismatch.
    """
    _require_exact_keys(seal, _SEAL_KEYS, "seal")
    if seal.get("seal_version") != LC4V3_SEAL_SCHEMA:
        raise ValueError(
            f"Seal version mismatch: {seal.get('seal_version')!r}"
        )
    if seal.get("evaluator_version") != LC4V3_EVALUATOR_VERSION:
        raise ValueError(
            f"Seal evaluator version mismatch: "
            f"{seal.get('evaluator_version')!r} != {LC4V3_EVALUATOR_VERSION!r}"
        )
    if seal.get("evaluation_id") != LC4V3_EVALUATION_ID:
        raise ValueError(
            f"Seal evaluation ID mismatch: "
            f"{seal.get('evaluation_id')!r} != {LC4V3_EVALUATION_ID!r}"
        )
    if seal.get("repeat_count") != LC4V3_REPEAT_COUNT:
        raise ValueError(
            f"Seal repeat count mismatch: "
            f"{seal.get('repeat_count')} != {LC4V3_REPEAT_COUNT}"
        )
    if seal.get("consumed") is not False:
        raise ValueError("Seal is already consumed or has invalid state")
    source_commit = _require_commit(seal.get("source_commit"), "seal source_commit")
    if expected_source_commit is not None:
        expected_source_commit = _require_commit(expected_source_commit, "expected source_commit")
        if source_commit != expected_source_commit:
            raise ValueError("Seal source commit does not match frozen HEAD")

    verified_manifest: dict[str, Any] = reconstruct_manifest(manifest)
    expected_manifest_hash: str = _stable_hash(_canonical_json(verified_manifest))

    if seal.get("manifest_hash") != expected_manifest_hash:
        raise ValueError(
            f"Seal manifest hash mismatch: "
            f"seal={seal.get('manifest_hash')} != expected={expected_manifest_hash}"
        )
    if seal.get("corpus_hash") != verified_manifest.get("corpus_hash"):
        raise ValueError(
            f"Seal corpus hash mismatch: "
            f"seal={seal.get('corpus_hash')} != manifest={verified_manifest.get('corpus_hash')}"
        )
    _require_sha256(seal.get("manifest_hash"), "seal manifest_hash")
    _require_sha256(seal.get("corpus_hash"), "seal corpus_hash")

    return seal


# ---------------------------------------------------------------------------
# Forbidden-key lint for aggregate-only reports
# ---------------------------------------------------------------------------


def check_forbidden_aggregate_keys(report: dict[str, Any]) -> None:
    """Recursively check for prohibited case-level keys in the report.

    Raises ``ValueError`` if any prohibited key is found at any nesting
    depth.  Also scans string values for patterns that could disclose
    case-level content.

    Parameters
    ----------
    report :
        The aggregate report dict to check.
    """
    _check_keys_recursive(report, path="root")


def _check_keys_recursive(obj: Any, path: str) -> None:
    """Recurse into *obj* checking for prohibited keys and patterns."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            if key_lower in _PROHIBITED_AGGREGATE_KEYS or (
                key_lower not in _SAFE_FRAGMENT_KEYS
                and any(fragment in key_lower for fragment in _PROHIBITED_KEY_FRAGMENTS)
            ):
                raise ValueError(
                    f"Aggregate report contains prohibited case-level key at {path}"
                )
            _check_keys_recursive(value, f"{path}.{key}")
            if isinstance(value, str):
                _check_forbidden_string(value, f"{path}.{key}")
            elif isinstance(value, (list, tuple)):
                _check_forbidden_sequence(value, f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        _check_forbidden_sequence(obj, path)


def _check_forbidden_sequence(items: list | tuple, path: str) -> None:
    """Check sequence items for prohibited structure."""
    for idx, item in enumerate(items):
        item_path = f"{path}[{idx}]"
        if isinstance(item, str):
            _check_forbidden_string(item, item_path)
        elif isinstance(item, dict):
            _check_keys_recursive(item, item_path)
        elif isinstance(item, (list, tuple)):
            _check_forbidden_sequence(item, item_path)


def _check_forbidden_string(value: str, path: str) -> None:
    """Check a string value for prohibited case-level patterns."""
    lower = value.lower()
    prohibited_patterns: list[str] = [
        "lc4v3_group_", "lc4v3_var_", "lc4v3_mt_",
    ]
    for pattern in prohibited_patterns:
        if pattern in lower:
            raise ValueError(
                f"Aggregate report value contains prohibited pattern "
                f"{pattern!r} at {path}"
            )


# ---------------------------------------------------------------------------
# Aggregate-only evaluation
# ---------------------------------------------------------------------------


def evaluate_aggregate(
    scenarios: list[ReceptionScenarioSpec],
    *,
    manifest_hash: str,
    corpus_hash: str,
    source_commit: str,
    repeats: int = LC4V3_REPEAT_COUNT,
) -> dict[str, Any]:
    """Run deterministic aggregate evaluation on a list of scenarios.

    Streams every scenario *repeats* times through the public deterministic
    interpretation, replay, and scoring path.  Retains per-case observations
    only in process and emits only aggregate totals.

    Parameters
    ----------
    scenarios :
        The list of ``ReceptionScenarioSpec`` instances to evaluate.
    repeats :
        Number of deterministic repeats per scenario (default 2).

    Returns
    -------
    dict
        The aggregate-only evaluation report with per-dimension pass/fail,
        failure-layer attribution, critical slices, variance, and coverage
        cell counts.  No per-case structure is emitted.

    Raises
    ------
    ValueError
        If *repeats* does not equal the contract value, or if the scenario
        count does not match.
    """
    if repeats != LC4V3_REPEAT_COUNT:
        raise ValueError(
            f"Expected {LC4V3_REPEAT_COUNT} repeats, got {repeats}"
        )
    manifest_hash = _require_sha256(manifest_hash, "manifest_hash")
    corpus_hash = _require_sha256(corpus_hash, "corpus_hash")
    source_commit = _require_commit(source_commit)

    total_scenarios = len(scenarios)
    if total_scenarios != LC4V3_TOTAL_SCENARIOS:
        raise ValueError(
            f"Expected {LC4V3_TOTAL_SCENARIOS} scenarios, got {total_scenarios}"
        )
    ids = [scenario.scenario_id for scenario in scenarios]
    if len(ids) != len(set(ids)) or not all(_SCENARIO_ID_RE.fullmatch(sid) for sid in ids):
        raise ValueError("Scenario IDs must be unique and LC4V3-namespaced")
    trajectory_count = 0
    for scenario in scenarios:
        if scenario.provenance != "gold" or scenario.adjudication != "adjudicated":
            raise ValueError("Certification scenarios must be Gold/adjudicated")
        if not scenario.source_spans:
            raise ValueError("Certification scenarios require lossless source spans")
        if scenario.initial_diary_state.get("synthetic") is not True:
            raise ValueError("Certification diary state must be explicitly synthetic")
        trajectory_count += int(len(scenario.dialogue_turns) > 1)
    if trajectory_count != LC4V3_TOTAL_TRAJECTORIES:
        raise ValueError("Trajectory population drift")

    total_samples = total_scenarios * repeats

    # Run deterministic interpretation + replay for every repeat
    results: list[ComposedSampleResult] = []
    for scenario in scenarios:
        for sample_idx in range(repeats):
            interp = deterministic_interpret(scenario)
            interp = _override_sample_index(interp, sample_idx)
            replay = deterministic_replay(scenario, interp)
            result = score_interpretation_replay_pair(scenario, interp, replay)
            results.append(result)

    # Per-dimension scores
    per_dim = _build_per_dimension_scores(results, total_scenarios, total_samples, repeats)

    # Critical slices
    slices = _build_critical_slices(results, scenarios)

    # Variance
    variance = _compute_variance(results)

    # Coverage cells
    coverage = _compute_coverage_cells(scenarios)

    # Build report (no report_hash yet)
    report_no_hash: dict[str, Any] = {
        "schema_version": LC4V3_REPORT_SCHEMA,
        "evaluation_id": LC4V3_EVALUATION_ID,
        "evaluator_version": LC4V3_EVALUATOR_VERSION,
        "source_commit": source_commit,
        "manifest_hash": manifest_hash,
        "corpus_hash": corpus_hash,
        "total_groups": LC4V3_GROUP_COUNT,
        "total_scenarios": LC4V3_TOTAL_SCENARIOS,
        "total_trajectories": LC4V3_TOTAL_TRAJECTORIES,
        "total_samples": total_samples,
        "repeat_count": repeats,
        "per_dimension": per_dim,
        "failure_layers": _build_failure_layer_totals(results),
        "critical_slices": slices,
        "variance": variance,
        "coverage_cells": coverage,
    }

    # Compute report hash over the complete canonical payload
    report_hash = _stable_hash(_canonical_json(report_no_hash))
    report_no_hash["report_hash"] = report_hash

    # Forbidden-key lint as safety net
    check_forbidden_aggregate_keys(report_no_hash)
    validation = check_aggregate_report(report_no_hash)
    if not validation["valid"]:
        raise ValueError("generated aggregate report failed closed validation")

    return report_no_hash


def _override_sample_index(
    interp: Any, sample_index: int,
) -> Any:
    """Override the sample_index on an InterpretationObservation copy."""
    return interp.__class__(
        scenario_id=interp.scenario_id,
        sample_index=sample_index,
        intended_action=interp.intended_action,
        action_semantics=interp.action_semantics,
        temporal_relation=interp.temporal_relation,
        normalized_values=interp.normalized_values,
        entity_semantics=interp.entity_semantics,
        requires_clarification=interp.requires_clarification,
        clarification_choices=interp.clarification_choices,
        selected_tool_sequence=interp.selected_tool_sequence,
        authority_claim=interp.authority_claim,
        claims_action_completed=interp.claims_action_completed,
        action_negated=interp.action_negated,
    )


def _build_per_dimension_scores(
    results: list[ComposedSampleResult],
    total_scenarios: int,
    total_samples: int,
    repeats: int,
) -> dict[str, Any]:
    """Build per-dimension pass/fail scores from results."""
    def _sf_passed(attr: str) -> dict[str, int]:
        passed = sum(
            1 for r in results
            if getattr(r.semantic_fields, attr, object()).passed
        )
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    def _dim_passed(dim: str) -> dict[str, int]:
        passed = sum(1 for r in results if getattr(r, dim, object()).passed)
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    return {
        "scenario_count": total_scenarios,
        "sample_count": total_samples,
        "repeats_per_scenario": repeats,
        "complete_composed_contract": {
            "passed": sum(1 for r in results if r.all_passed),
            "failed": sum(1 for r in results if not r.all_passed),
            "total": total_samples,
        },
        "intended_action": _sf_passed("intended_action"),
        "action_semantics": _sf_passed("action_semantics"),
        "temporal_relation": _sf_passed("temporal_relation"),
        "normalized_values": _sf_passed("normalized_values"),
        "entity_semantics": _sf_passed("entity_semantics"),
        "clarification": _dim_passed("clarification"),
        "downstream_outcome": _dim_passed("downstream_outcome"),
        "interpretation_tools": _dim_passed("interpretation_tools"),
        "replay_tool_sequence": _dim_passed("tool_sequence"),
        "authority": {
            "passed": sum(1 for r in results if r.authority.passed),
            "failed": sum(1 for r in results if not r.authority.passed),
            "total": total_samples,
        },
        "appointment_deltas": _dim_passed("appointment_deltas"),
        "audit_deltas": _dim_passed("audit_deltas"),
        "safety": _dim_passed("safety"),
    }


def _build_failure_layer_totals(
    results: list[ComposedSampleResult],
) -> dict[str, int]:
    """Count failures attributed to each layer."""
    counts: dict[str, int] = {layer: 0 for layer in FAILURE_LAYERS}
    for r in results:
        for layer in r.failure_layers:
            if layer in counts:
                counts[layer] += 1
    return counts


def _build_critical_slices(
    results: list[ComposedSampleResult],
    scenarios: list[ReceptionScenarioSpec],
) -> dict[str, Any]:
    """Build critical slices across all required dimensions."""
    scenario_map = {s.scenario_id: s for s in scenarios}

    registry: dict[str, dict[str, dict[str, int]]] = {
        "action": {},
        "temporal_relation": {},
        "diary_state": {},
        "entity_state": {},
        "dialogue_form": {},
        "language_form": {},
        "trajectory_type": {},
    }

    for r in results:
        sc = scenario_map.get(r.scenario_id)
        if sc is None:
            continue
        _acc(registry, "action", sc.intended_action, r.all_passed)
        _acc(registry, "temporal_relation", sc.temporal_relation, r.all_passed)
        _acc(registry, "diary_state", sc.diary_state, r.all_passed)
        _acc(registry, "entity_state", sc.entity_state, r.all_passed)
        _acc(registry, "dialogue_form", sc.dialogue_form, r.all_passed)
        _acc(registry, "language_form", sc.language_form, r.all_passed)
        tt = "trajectory" if len(sc.dialogue_turns) > 1 else "single_turn"
        _acc(registry, "trajectory_type", tt, r.all_passed)

    return {
        "worst_slice": _worst_slice(registry),
        "by_action": _entries(registry, "action"),
        "by_temporal_relation": _entries(registry, "temporal_relation"),
        "by_diary_state": _entries(registry, "diary_state"),
        "by_entity_state": _entries(registry, "entity_state"),
        "by_dialogue_form": _entries(registry, "dialogue_form"),
        "by_language_form": _entries(registry, "language_form"),
        "by_trajectory_type": _entries(registry, "trajectory_type"),
    }


def _acc(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
    key: str,
    passed: bool,
) -> None:
    """Accumulate a sample into the slice registry."""
    bucket = registry.setdefault(dim, {}).setdefault(
        key, {"total": 0, "passed": 0, "failed": 0}
    )
    bucket["total"] += 1
    if passed:
        bucket["passed"] += 1
    else:
        bucket["failed"] += 1


def _worst_slice(
    registry: dict[str, dict[str, dict[str, int]]],
) -> dict[str, Any] | None:
    """Find the worst-performing slice across all dimensions."""
    best_entry: dict[str, Any] | None = None
    for dim_name, dim_data in registry.items():
        for key, counts in dim_data.items():
            total = counts["total"]
            if total == 0:
                continue
            passed = counts["passed"]
            frac = passed / total
            if best_entry is None or frac < best_entry["pass_fraction"]:
                best_entry = {
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                }
            elif frac == best_entry["pass_fraction"] and key < best_entry["slice_key"]:
                best_entry.update({
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                })
    return best_entry


def _entries(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
) -> list[dict[str, Any]]:
    """Build sorted slice entries for a dimension."""
    result: list[dict[str, Any]] = []
    for key in sorted(registry.get(dim, {})):
        counts = registry[dim][key]
        result.append({
            "slice_key": key,
            "total": counts["total"],
            "passed": counts["passed"],
            "failed": counts["failed"],
            "pass_fraction": round(counts["passed"] / counts["total"], 4)
            if counts["total"] > 0 else 1.0,
        })
    return result


def _compute_variance(
    results: list[ComposedSampleResult],
) -> dict[str, Any]:
    """Compute repeat variance across samples."""
    scenario_fingerprints: dict[str, set[tuple[Any, ...]]] = {}
    for r in results:
        fp = _semantic_fingerprint(r)
        scenario_fingerprints.setdefault(r.scenario_id, set()).add(fp)

    variant_scenario_count = sum(
        1 for fps in scenario_fingerprints.values() if len(fps) > 1
    )
    variant_sample_count = sum(
        sum(1 for r in results if r.scenario_id == sid and len(fps) > 1)
        for sid, fps in scenario_fingerprints.items()
    )

    return {
        "variant_scenario_count": variant_scenario_count,
        "variant_sample_count": variant_sample_count,
        "total_repeats": LC4V3_REPEAT_COUNT,
        "all_samples_deterministic": (
            variant_scenario_count == 0 and variant_sample_count == 0
        ),
    }


def _semantic_fingerprint(result: ComposedSampleResult) -> tuple[Any, ...]:
    """Canonical fingerprint for variance detection."""
    s = result.semantic_fields

    def _cm(v: Any) -> Any:
        if isinstance(v, dict):
            return tuple(sorted((k, _cm(v2)) for k, v2 in v.items()))
        if isinstance(v, list):
            return tuple(_cm(x) for x in v)
        return v

    return (
        s.intended_action.observed,
        s.action_semantics.observed,
        s.temporal_relation.observed,
        _cm(s.normalized_values.observed),
        _cm(s.entity_semantics.observed),
        result.downstream_outcome.comparison.observed,
        result.tool_sequence.observed,
        result.interpretation_tools.observed,
        result.authority.authority_claim,
        result.clarification.observed_requires,
        result.failure_layers,
    )


def _compute_coverage_cells(
    scenarios: list[ReceptionScenarioSpec],
) -> dict[str, Any]:
    """Compute total distinct coverage cell counts."""
    covered_cells: set[tuple[str, str, str, str, str, str]] = set()
    for s in scenarios:
        cell = (
            s.intended_action, s.diary_state, s.entity_state,
            s.temporal_relation, s.dialogue_form, s.language_form,
        )
        covered_cells.add(cell)

    return {
        "distinct_cell_count": len(covered_cells),
        "total_possible_cells": (
            len(ALL_ACTIONS)
            * len(ALL_DIARY_STATES)
            * len(ALL_ENTITY_SEMANTICS)
            * len(ALL_TEMPORAL_RELATIONS)
            * len(ALL_DIALOGUE_FORMS)
            * len(ALL_LANGUAGE_FORMS)
        ),
    }


# ---------------------------------------------------------------------------
# Report hash validation
# ---------------------------------------------------------------------------


def validate_report_hash(report: dict[str, Any]) -> bool:
    """Recompute and verify the report hash.

    Removes ``report_hash`` from a copy of the report, recomputes SHA-256
    over the canonical JSON, and returns True only on exact match.

    Parameters
    ----------
    report :
        The report dict with a ``report_hash`` field.

    Returns
    -------
    bool
        True if the hash matches.
    """
    if "report_hash" not in report:
        raise ValueError("Report missing report_hash field")
    claimed = report["report_hash"]
    report_copy = dict(report)
    del report_copy["report_hash"]
    computed = _stable_hash(_canonical_json(report_copy))
    return computed == claimed


# ---------------------------------------------------------------------------
# Post-consumption aggregate check (never loads/hashes corpus)
# ---------------------------------------------------------------------------


def check_aggregate_report(report: dict[str, Any]) -> dict[str, Any]:
    """Validate an aggregate report without loading the corpus.

    After consumption, closeout may use only this function to verify the
    aggregate report.  It never loads or hashes the protected corpus.

    Validates:
    - Schema version, evaluation ID, evaluator version
    - Total group/scenario/trajectory/sample counts
    - Report hash integrity
    - Forbidden-key lint

    Parameters
    ----------
    report :
        The aggregate report dict.

    Returns
    -------
    dict
        A validation result dict with ``valid`` (bool) and ``errors`` (list).

    Notes
    -----
    This is a post-consumption check only.  It must not load or hash the
    protected corpus.
    """
    errors: list[str] = []

    def fail(code: str) -> None:
        if code not in errors:
            errors.append(code)

    if not isinstance(report, dict) or set(report) != _REPORT_KEYS:
        fail("report_schema_keys_invalid")
    if report.get("schema_version") != LC4V3_REPORT_SCHEMA:
        fail("report_schema_version_invalid")
    if report.get("evaluation_id") != LC4V3_EVALUATION_ID:
        fail("report_evaluation_id_invalid")
    if report.get("evaluator_version") != LC4V3_EVALUATOR_VERSION:
        fail("report_evaluator_version_invalid")
    try:
        _require_commit(report.get("source_commit"))
        _require_sha256(report.get("manifest_hash"), "manifest_hash")
        _require_sha256(report.get("corpus_hash"), "corpus_hash")
    except ValueError:
        fail("report_identity_invalid")

    for key, expected in (
        ("total_groups", LC4V3_GROUP_COUNT),
        ("total_scenarios", LC4V3_TOTAL_SCENARIOS),
        ("total_trajectories", LC4V3_TOTAL_TRAJECTORIES),
        ("total_samples", LC4V3_TOTAL_SAMPLES),
        ("repeat_count", LC4V3_REPEAT_COUNT),
    ):
        if report.get(key) != expected:
            fail(f"report_{key}_invalid")

    def score_ok(value: Any) -> bool:
        return (
            isinstance(value, dict)
            and set(value) == {"passed", "failed", "total"}
            and all(type(value[k]) is int and value[k] >= 0 for k in value)
            and value["total"] == LC4V3_TOTAL_SAMPLES
            and value["passed"] + value["failed"] == value["total"]
        )

    per_dim = report.get("per_dimension")
    expected_dimension_keys = set(PER_DIMENSION_NAMES) | {
        "scenario_count", "sample_count", "repeats_per_scenario",
    }
    if not isinstance(per_dim, dict) or set(per_dim) != expected_dimension_keys:
        fail("per_dimension_schema_invalid")
    else:
        if (
            per_dim["scenario_count"] != LC4V3_TOTAL_SCENARIOS
            or per_dim["sample_count"] != LC4V3_TOTAL_SAMPLES
            or per_dim["repeats_per_scenario"] != LC4V3_REPEAT_COUNT
        ):
            fail("per_dimension_population_invalid")
        if not all(score_ok(per_dim[name]) for name in PER_DIMENSION_NAMES):
            fail("per_dimension_totals_invalid")

    layers = report.get("failure_layers")
    if not (
        isinstance(layers, dict)
        and set(layers) == set(FAILURE_LAYERS)
        and all(type(value) is int and 0 <= value <= LC4V3_TOTAL_SAMPLES for value in layers.values())
    ):
        fail("failure_layers_invalid")

    variance = report.get("variance")
    if not (
        isinstance(variance, dict)
        and set(variance) == {
            "variant_scenario_count", "variant_sample_count", "total_repeats",
            "all_samples_deterministic",
        }
        and type(variance["variant_scenario_count"]) is int
        and 0 <= variance["variant_scenario_count"] <= LC4V3_TOTAL_SCENARIOS
        and type(variance["variant_sample_count"]) is int
        and 0 <= variance["variant_sample_count"] <= LC4V3_TOTAL_SAMPLES
        and variance["total_repeats"] == LC4V3_REPEAT_COUNT
        and type(variance["all_samples_deterministic"]) is bool
        and variance["all_samples_deterministic"]
        is (variance["variant_scenario_count"] == 0 and variance["variant_sample_count"] == 0)
    ):
        fail("variance_invalid")

    coverage = report.get("coverage_cells")
    total_possible = (
        len(ALL_ACTIONS) * len(ALL_DIARY_STATES) * len(ALL_ENTITY_SEMANTICS)
        * len(ALL_TEMPORAL_RELATIONS) * len(ALL_DIALOGUE_FORMS) * len(ALL_LANGUAGE_FORMS)
    )
    if not (
        isinstance(coverage, dict)
        and set(coverage) == {"distinct_cell_count", "total_possible_cells"}
        and type(coverage["distinct_cell_count"]) is int
        and 1 <= coverage["distinct_cell_count"] <= LC4V3_TOTAL_SCENARIOS
        and coverage["total_possible_cells"] == total_possible
    ):
        fail("coverage_cells_invalid")

    slices = report.get("critical_slices")
    axes = {
        "by_action": set(ALL_ACTIONS),
        "by_temporal_relation": set(ALL_TEMPORAL_RELATIONS),
        "by_diary_state": set(ALL_DIARY_STATES),
        "by_entity_state": set(ALL_ENTITY_SEMANTICS),
        "by_dialogue_form": set(ALL_DIALOGUE_FORMS),
        "by_language_form": set(ALL_LANGUAGE_FORMS),
        "by_trajectory_type": {"single_turn", "trajectory"},
    }
    expected_slice_keys = set(axes) | {"worst_slice"}
    if not isinstance(slices, dict) or set(slices) != expected_slice_keys:
        fail("critical_slices_schema_invalid")
    else:
        for axis, vocabulary in axes.items():
            entries = slices.get(axis)
            valid_entries = isinstance(entries, list) and bool(entries)
            total = 0
            seen: set[str] = set()
            if valid_entries:
                for entry in entries:
                    if not isinstance(entry, dict) or set(entry) != {
                        "slice_key", "total", "passed", "failed", "pass_fraction",
                    }:
                        valid_entries = False
                        break
                    key = entry["slice_key"]
                    if not isinstance(key, str) or key not in vocabulary or key in seen:
                        valid_entries = False
                        break
                    seen.add(key)
                    if not (
                        type(entry["total"]) is int and entry["total"] > 0
                        and type(entry["passed"]) is int and entry["passed"] >= 0
                        and type(entry["failed"]) is int and entry["failed"] >= 0
                        and entry["passed"] + entry["failed"] == entry["total"]
                        and isinstance(entry["pass_fraction"], (int, float))
                        and entry["pass_fraction"] == round(entry["passed"] / entry["total"], 4)
                    ):
                        valid_entries = False
                        break
                    total += entry["total"]
            if not valid_entries or total != LC4V3_TOTAL_SAMPLES:
                fail(f"critical_slice_{axis}_invalid")
        worst = slices.get("worst_slice")
        worst_dimensions = {
            "action": set(ALL_ACTIONS),
            "temporal_relation": set(ALL_TEMPORAL_RELATIONS),
            "diary_state": set(ALL_DIARY_STATES),
            "entity_state": set(ALL_ENTITY_SEMANTICS),
            "dialogue_form": set(ALL_DIALOGUE_FORMS),
            "language_form": set(ALL_LANGUAGE_FORMS),
            "trajectory_type": {"single_turn", "trajectory"},
        }
        worst_valid = (
            isinstance(worst, dict)
            and set(worst) == {
                "dimension", "slice_key", "total", "passed", "failed", "pass_fraction",
            }
            and isinstance(worst["dimension"], str)
            and worst["dimension"] in worst_dimensions
            and isinstance(worst["slice_key"], str)
            and worst["slice_key"] in worst_dimensions[worst["dimension"]]
            and type(worst["total"]) is int and worst["total"] > 0
            and type(worst["passed"]) is int and worst["passed"] >= 0
            and type(worst["failed"]) is int and worst["failed"] >= 0
            and worst["passed"] + worst["failed"] == worst["total"]
            and isinstance(worst["pass_fraction"], (int, float))
            and worst["pass_fraction"] == round(worst["passed"] / worst["total"], 4)
        )
        if not worst_valid:
            fail("worst_slice_invalid")
        else:
            axis_name = f"by_{worst['dimension']}"
            matching = [
                entry for entry in slices[axis_name]
                if entry["slice_key"] == worst["slice_key"]
            ]
            all_fractions = [
                entry["pass_fraction"]
                for axis_name in axes
                for entry in slices[axis_name]
                if isinstance(entry, dict) and "pass_fraction" in entry
            ]
            if (
                len(matching) != 1
                or any(matching[0][key] != worst[key] for key in ("total", "passed", "failed", "pass_fraction"))
                or not all_fractions
                or worst["pass_fraction"] != min(all_fractions)
            ):
                fail("worst_slice_invalid")

    try:
        check_forbidden_aggregate_keys(report)
    except ValueError:
        fail("forbidden_case_level_structure")
    try:
        if not validate_report_hash(report):
            fail("report_hash_invalid")
    except (ValueError, TypeError):
        fail("report_hash_invalid")

    return {"valid": not errors, "errors": errors}


# ---------------------------------------------------------------------------
# Import isolation guard
# ---------------------------------------------------------------------------

_PROHIBITED_IMPORT_PREFIXES: tuple[str, ...] = (
    "app.routers",
    "app.models",
    "app.db",
    "app.services.ai.providers",
    "sqlalchemy",
    "alembic",
)


def validate_lc4v3_isolation() -> None:
    """Assert that this module cannot reach providers, routes, or storage."""
    import ast

    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        imported: tuple[str, ...] = ()
        if isinstance(node, ast.Import):
            imported = tuple(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = (node.module,)
        for module_name in imported:
            if module_name.startswith(_PROHIBITED_IMPORT_PREFIXES):
                raise RuntimeError(
                    f"LC4V3 certification imports prohibited module: {module_name}"
                )


__all__ = [
    "LC4V3_CORPUS_IDENTITY",
    "LC4V3_MANIFEST_SCHEMA",
    "LC4V3_SEAL_SCHEMA",
    "LC4V3_EVALUATOR_VERSION",
    "LC4V3_EVALUATION_ID",
    "LC4V3_GROUP_COUNT",
    "LC4V3_VARIANTS_PER_GROUP",
    "LC4V3_SURFACE_PER_GROUP",
    "LC4V3_MT_PER_GROUP",
    "LC4V3_TOTAL_SCENARIOS",
    "LC4V3_TOTAL_TRAJECTORIES",
    "LC4V3_REPEAT_COUNT",
    "LC4V3_TOTAL_SAMPLES",
    "LC4V3_GROUP_PREFIX",
    "LC4V3_REPORT_SCHEMA",
    "ALL_ACTIONS",
    "ALL_DIARY_STATES",
    "ALL_ENTITY_SEMANTICS",
    "ALL_TEMPORAL_RELATIONS",
    "ALL_DIALOGUE_FORMS",
    "ALL_LANGUAGE_FORMS",
    "PER_DIMENSION_NAMES",
    "FAILURE_LAYERS",
    "get_source_commit",
    "build_manifest",
    "reconstruct_manifest",
    "verify_manifest_against_corpus",
    "load_verified_scenarios",
    "create_seal",
    "verify_seal",
    "check_forbidden_aggregate_keys",
    "evaluate_aggregate",
    "validate_report_hash",
    "check_aggregate_report",
    "validate_lc4v3_isolation",
]
