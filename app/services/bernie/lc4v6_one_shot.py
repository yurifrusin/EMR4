"""Protected Sol-owned entry point for the single sealed LC4V6 evaluation."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.lc4v6_acceptance_rule import decide_certification
from app.services.bernie.lc4v6_content_blind_framework import (
    BoundHashes,
    OneShotPaths,
    OneShotStateMachine,
    aggregate_observations,
    canonical_json,
    sha256_bytes,
    sha256_payload,
    sha256_text,
    validate_manifest,
    validate_observations,
)
from app.services.bernie.lc4v6_corpus import author_scenarios, corpus_hash
from app.services.bernie.lc4v6_evaluator import evaluate_all


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
STATE_ROOT = REPOSITORY_ROOT / "orchestration" / "agent_inbox" / "codex"
MANIFEST_PATH = STATE_ROOT / "lc4v6-source-manifest.json"
RECEIPT_PATH = STATE_ROOT / "lc4v6-production-run-receipt.json"

COMPONENT_PATHS = {
    "acceptance_rule": REPOSITORY_ROOT
    / "app"
    / "services"
    / "bernie"
    / "lc4v6_acceptance_rule.py",
    "evaluator": REPOSITORY_ROOT
    / "app"
    / "services"
    / "bernie"
    / "lc4v6_evaluator.py",
    "runner": Path(__file__).resolve(),
}
FRAMEWORK_PATH = (
    REPOSITORY_ROOT
    / "app"
    / "services"
    / "bernie"
    / "lc4v6_content_blind_framework.py"
)


class PreRunError(RuntimeError):
    """Raised before interpretation starts when frozen source evidence drifts."""


def component_hashes() -> dict[str, str]:
    """Return exact hashes for all code participating in the one-shot decision."""
    return {
        name: sha256_bytes(path.read_bytes())
        for name, path in sorted(COMPONENT_PATHS.items())
    }


def evaluator_bundle_hash(components: Mapping[str, str]) -> str:
    return sha256_payload(dict(components))


def _load_mapping(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PreRunError(f"required JSON is unavailable or malformed: {path.name}") from error
    if not isinstance(payload, Mapping):
        raise PreRunError(f"required JSON is not an object: {path.name}")
    return payload


def _bound_hashes(manifest: Mapping[str, Any]) -> BoundHashes:
    payload = {
        "source": manifest.get("source_hash"),
        "corpus": manifest.get("corpus_hash"),
        "manifest": manifest.get("manifest_hash"),
        "framework": manifest.get("framework_hash"),
        "evaluator": manifest.get("evaluator_hash"),
    }
    if not all(isinstance(value, str) for value in payload.values()):
        raise PreRunError("manifest hash bindings are missing")
    hashes = BoundHashes(**payload)
    if not hashes.valid():
        raise PreRunError("manifest hash bindings are malformed")
    return hashes


def validate_frozen_source() -> tuple[tuple[Any, ...], Mapping[str, Any], BoundHashes]:
    """Validate exact named source evidence without executing interpretation."""
    manifest = _load_mapping(MANIFEST_PATH)
    components = component_hashes()
    errors: list[str] = []

    manifest_without_hash = dict(manifest)
    claimed_manifest_hash = manifest_without_hash.pop("manifest_hash", None)
    if claimed_manifest_hash != sha256_payload(manifest_without_hash):
        errors.append("manifest self-hash drifted")
    if manifest.get("component_hashes") != components:
        errors.append("one-shot component hashes drifted")
    if manifest.get("framework_hash") != sha256_bytes(FRAMEWORK_PATH.read_bytes()):
        errors.append("framework hash drifted")
    if manifest.get("evaluator_hash") != evaluator_bundle_hash(components):
        errors.append("evaluator bundle hash drifted")

    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or manifest.get("source_hash") != sha256_text(source_commit):
        errors.append("source commit binding drifted")

    scenarios = tuple(author_scenarios())
    if manifest.get("corpus_hash") != corpus_hash():
        errors.append("corpus hash drifted")
    manifest_validation = validate_manifest(manifest, scenarios)
    errors.extend(manifest_validation.errors)
    if errors:
        raise PreRunError("; ".join(dict.fromkeys(errors)))

    hashes = _bound_hashes(manifest)
    state = OneShotStateMachine(
        OneShotPaths(STATE_ROOT), str(source_commit), hashes
    ).validate_prerun()
    if not state.valid:
        raise PreRunError("; ".join(state.errors))
    return scenarios, manifest, hashes


def _atomic_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoded = (canonical_json(payload) + "\n").encode("utf-8")
    with temporary.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    if path.exists():
        temporary.unlink(missing_ok=True)
        raise FileExistsError(f"refusing to overwrite {path.name}")
    os.replace(temporary, path)


def run_once() -> Mapping[str, Any]:
    """Execute the protected population once and persist aggregate evidence only."""
    scenarios, manifest, hashes = validate_frozen_source()

    observations, exception_count = evaluate_all(scenarios)
    observation_validation = validate_observations(observations, scenarios)
    report = aggregate_observations(
        observations,
        hashes,
        evaluation_exception_count=exception_count,
        case_level_artifact_count=0,
    )
    if not observation_validation.valid:
        report["missing_dimension_count"] = max(
            int(report["missing_dimension_count"]), len(observation_validation.errors)
        )

    state_machine = OneShotStateMachine(
        OneShotPaths(STATE_ROOT), str(manifest["source_commit"]), hashes
    )
    transition = state_machine.consume(report)
    if not transition.valid:
        raise RuntimeError("one-shot transition failed closed: " + "; ".join(transition.errors))

    decision = decide_certification(report, hashes)
    paths = OneShotPaths(STATE_ROOT)
    receipt = {
        "schema_version": "lc4v6.production_run_receipt.v1",
        "attempt_id": report["attempt_id"],
        "decision": decision.decision,
        "evidence_gates": dict(decision.evidence_gates),
        "product_gates": dict(decision.product_gates),
        "worst_slice_rate": decision.worst_slice_rate,
        "report_hash": sha256_payload(report),
        "marker_file_hash": sha256_bytes(paths.marker.read_bytes()),
        "consumed_seal_file_hash": sha256_bytes(paths.seal.read_bytes()),
        "hashes": asdict(hashes),
    }
    _atomic_new_json(RECEIPT_PATH, receipt)
    return receipt


def main() -> int:
    receipt = run_once()
    print(canonical_json(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "COMPONENT_PATHS",
    "FRAMEWORK_PATH",
    "MANIFEST_PATH",
    "RECEIPT_PATH",
    "STATE_ROOT",
    "PreRunError",
    "component_hashes",
    "evaluator_bundle_hash",
    "run_once",
    "validate_frozen_source",
]
