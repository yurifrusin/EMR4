"""Validate the provider-free delete-confirm physical representability review."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "orchestration" / "continuity" / (
    "raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review"
)
CONTRACT_PATH = BASE / "review-contract.json"
SCHEMA_PATH = BASE / "provider-free-review-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-review-evidence.json"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_review(
    evidence: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
    schema: dict[str, Any] | None = None,
) -> dict[str, int]:
    contract = contract or _json(CONTRACT_PATH)
    schema = schema or _json(SCHEMA_PATH)
    Draft202012Validator(schema).validate(evidence)

    if evidence["review_baseline"] != contract["review_baseline"]:
        raise ValueError("review baseline mismatch")
    if evidence["source_hashes"] != contract["source_hashes"]:
        raise ValueError("source hash map mismatch")
    if evidence["overall_verdict"] != contract["overall_verdict"]:
        raise ValueError("overall verdict mismatch")
    if evidence["next_gate"] != contract["next_gate_if_positive"]:
        raise ValueError("next gate mismatch")

    for relative, expected_hash in contract["source_hashes"].items():
        if _sha256(ROOT / relative) != expected_hash:
            raise ValueError(f"source hash mismatch: {relative}")

    physical_sources = set(contract["physical_source_paths"])
    domain_ids = [row["domain_id"] for row in contract["domains"]]
    domain_set = set(domain_ids)
    if len(domain_ids) != 6 or len(domain_set) != 6:
        raise ValueError("contract domain set is not closed")

    observations = evidence["observations"]
    observation_ids = [row["observation_id"] for row in observations]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("duplicate observation id")

    for observation in observations:
        source_path = observation["source_path"]
        if source_path not in physical_sources:
            raise ValueError("observation source outside physical allowlist")
        if not set(observation["supports_domains"]).issubset(domain_set):
            raise ValueError("observation references unknown domain")
        start = observation["line_start"]
        end = observation["line_end"]
        lines = (ROOT / source_path).read_text(encoding="utf-8").splitlines()
        if end < start or end > len(lines):
            raise ValueError("observation line range invalid")
        segment = "\n".join(lines[start - 1 : end])
        for anchor in observation["required_anchors"]:
            if anchor not in segment:
                raise ValueError(
                    f"observation anchor missing: {observation['observation_id']}"
                )

    verdicts = evidence["domain_verdicts"]
    verdict_ids = [row["domain_id"] for row in verdicts]
    if verdict_ids != domain_ids:
        raise ValueError("domain verdict order or membership mismatch")
    known_observations = set(observation_ids)
    allowed_verdicts = set(contract["verdict_vocabulary"])
    for verdict in verdicts:
        if verdict["verdict"] not in allowed_verdicts:
            raise ValueError("unknown verdict")
        if not set(verdict["observation_ids"]).issubset(known_observations):
            raise ValueError("verdict references unknown observation")
        if verdict["verdict"] == "already_represented" and verdict["additive_gaps"]:
            raise ValueError("already represented verdict cannot carry additive gaps")
        if (
            verdict["verdict"] == "representable_with_additive_change"
            and not verdict["additive_gaps"]
        ):
            raise ValueError("additive verdict requires additive gaps")

    if evidence["hostile_mutations_rejected"] < contract["minimum_hostile_mutations"]:
        raise ValueError("hostile mutation minimum not met")
    if evidence["implementation_authorized"] is not False:
        raise ValueError("implementation authority must remain false")

    return {
        "source_count": len(contract["source_hashes"]),
        "physical_source_count": len(physical_sources),
        "observation_count": len(observations),
        "domain_count": len(verdicts),
    }


def build_hostile_mutations(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []

    def add(mutator) -> None:  # type: ignore[no-untyped-def]
        candidate = copy.deepcopy(evidence)
        mutator(candidate)
        mutations.append(candidate)

    add(lambda row: row.__setitem__("schema_version", "wrong"))
    add(lambda row: row.__setitem__("review_baseline", "0" * 40))
    add(lambda row: row.__setitem__("evidence_label", "live_database"))
    add(lambda row: row.__setitem__("implementation_authorized", True))
    add(lambda row: row.__setitem__("overall_verdict", "implementation_admitted"))
    add(lambda row: row.__setitem__("next_gate", "mounted_delete_route"))
    add(lambda row: row.__setitem__("hostile_mutations_rejected", 39))
    add(lambda row: row.__setitem__("unexpected", True))

    for source_path in evidence["source_hashes"]:
        add(lambda row, path=source_path: row["source_hashes"].__setitem__(path, "0" * 64))

    for index in range(len(evidence["observations"])):
        add(
            lambda row, item=index: row["observations"][item].__setitem__(
                "required_anchors", ["anchor_not_present_in_exact_source"]
            )
        )

    add(lambda row: row["domain_verdicts"].pop())
    add(
        lambda row: row["domain_verdicts"][1].__setitem__(
            "domain_id", row["domain_verdicts"][0]["domain_id"]
        )
    )
    add(lambda row: row["domain_verdicts"][0].__setitem__("verdict", "unknown"))
    add(
        lambda row: row["domain_verdicts"][0].__setitem__(
            "observation_ids", ["OBS-99"]
        )
    )
    add(lambda row: row["domain_verdicts"][0].__setitem__("additive_gaps", []))

    if len(mutations) != 52:
        raise AssertionError(f"expected 52 hostile mutations, got {len(mutations)}")
    return mutations


def run_acceptance() -> dict[str, Any]:
    contract = _json(CONTRACT_PATH)
    schema = _json(SCHEMA_PATH)
    evidence = _json(EVIDENCE_PATH)
    counts = validate_review(evidence, contract=contract, schema=schema)

    rejected = 0
    for candidate in build_hostile_mutations(evidence):
        try:
            validate_review(candidate, contract=contract, schema=schema)
        except Exception:
            rejected += 1
        else:
            raise AssertionError("hostile mutation was admitted")

    if rejected != evidence["hostile_mutations_rejected"]:
        raise AssertionError("hostile mutation evidence count mismatch")
    return {
        "result": "raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass",
        **counts,
        "hostile_mutations_rejected": rejected,
        "implementation_authorized": False,
        "overall_verdict": evidence["overall_verdict"],
        "next_gate": evidence["next_gate"],
    }


def main() -> int:
    print(json.dumps(run_acceptance(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
