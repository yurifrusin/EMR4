import json
from pathlib import Path

from app.services.bernie.lc4v6_content_blind_framework import (
    BoundHashes,
    OneShotPaths,
    OneShotStateMachine,
    build_unconsumed_seal,
    sha256_bytes,
    sha256_payload,
    sha256_text,
    validate_manifest,
)
from app.services.bernie.lc4v6_corpus import author_scenarios, corpus_hash
from app.services.bernie.lc4v6_one_shot import (
    COMPONENT_PATHS,
    FRAMEWORK_PATH,
    MANIFEST_PATH,
    STATE_ROOT,
    component_hashes,
    evaluator_bundle_hash,
)


SOURCE_COMMIT = "0527848bb7d4c86a4c138f49016472c447c05757"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_frozen_manifest_binds_exact_source_corpus_and_code() -> None:
    manifest = _load(MANIFEST_PATH)
    without_self_hash = dict(manifest)
    self_hash = without_self_hash.pop("manifest_hash")

    assert manifest["source_commit"] == SOURCE_COMMIT
    assert manifest["source_hash"] == sha256_text(SOURCE_COMMIT)
    assert self_hash == sha256_payload(without_self_hash)
    assert manifest["component_hashes"] == component_hashes()
    assert set(manifest["component_hashes"]) == set(COMPONENT_PATHS)
    assert manifest["framework_hash"] == sha256_bytes(FRAMEWORK_PATH.read_bytes())
    assert manifest["evaluator_hash"] == evaluator_bundle_hash(component_hashes())

    scenarios = tuple(author_scenarios())
    assert validate_manifest(manifest, scenarios).valid
    assert manifest["corpus_hash"] == corpus_hash()


def test_unconsumed_seal_is_exact_and_attempt_state_is_pristine() -> None:
    manifest = _load(MANIFEST_PATH)
    hashes = BoundHashes(
        source=manifest["source_hash"],
        corpus=manifest["corpus_hash"],
        manifest=manifest["manifest_hash"],
        framework=manifest["framework_hash"],
        evaluator=manifest["evaluator_hash"],
    )
    paths = OneShotPaths(STATE_ROOT)

    assert _load(paths.seal) == build_unconsumed_seal(SOURCE_COMMIT, hashes)
    assert OneShotStateMachine(paths, SOURCE_COMMIT, hashes).validate_prerun().valid
    assert not paths.marker.exists()
    assert not paths.report.exists()
    assert not paths.lock.exists()
