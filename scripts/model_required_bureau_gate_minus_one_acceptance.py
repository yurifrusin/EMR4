"""Deterministic acceptance for the Gate -1 Bureau hardening portfolio."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = (
    ROOT
    / "docs"
    / "security"
    / "hardening"
    / "model-required-bureau-gate-minus-one"
)
INDEX_PATH = ANALYSIS / "evidence-index.json"
HARDENING_PATH = ANALYSIS / "hardening.json"
PORTFOLIO_PATH = ANALYSIS / "hardening.md"
CONTEXT_PATH = ANALYSIS / "context.md"
PLAN_PATH = ROOT / "docs" / "emr4-rayleen-davida-controlled-recovery-development-plan.md"
THREAT_PATH = (
    ROOT
    / "docs"
    / "security"
    / "emr4-model-required-bureaus-gate-minus-one-threat-model-delta.md"
)
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "model-required-bureau-gate-minus-one"
    / "provider-free-acceptance-evidence.json"
)
EXPECTED_RESULT = "model_required_bureau_gate_minus_one_provider_free_acceptance_pass"
EXPECTED_OPPORTUNITIES = {
    "deterministic-information-flow-confinement": "bureau-labeled-capability-envelope",
    "cognitive-cell-compromise-containment": "one-shot-brokered-cell",
}
REQUIRED_FILES = {
    "context.md",
    "evidence-index.json",
    "hardening.json",
    "hardening.md",
    "proposals/deterministic-information-flow-confinement.md",
    "proposals/cognitive-cell-compromise-containment.md",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(revision: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _validate_evidence_collection(index: dict[str, Any]) -> dict[str, Any]:
    artifacts = index["artifacts"]
    ids = [entry["id"] for entry in artifacts]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate evidence ID")
    if len(artifacts) != index["artifact_count"]:
        raise ValueError("evidence artifact count mismatch")

    lines = sorted(
        f'{entry["id"]}|{entry["artifact"]}|{entry["identity"]}'
        for entry in artifacts
    )
    collection_hash = _sha256((("\n".join(lines)) + "\n").encode("utf-8"))
    if collection_hash != index["collection_sha256"]:
        raise ValueError("evidence collection hash mismatch")

    local_count = 0
    for entry in artifacts:
        path = entry.get("path")
        if path is None:
            if not entry.get("url", "").startswith("https://"):
                raise ValueError(f'external evidence {entry["id"]} is not HTTPS')
            continue
        local_count += 1
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError(f'unsafe evidence path {entry["id"]}')
        recorded = entry["identity"]
        if not recorded.startswith("sha256:"):
            raise ValueError(f'missing source hash {entry["id"]}')
        actual = _sha256(_git_blob(index["target_revision"], path))
        if recorded != f"sha256:{actual}":
            raise ValueError(f'source hash drift {entry["id"]}')

    return {
        "artifact_count": len(artifacts),
        "local_artifact_count": local_count,
        "external_primary_source_count": len(artifacts) - local_count,
        "collection_sha256": collection_hash,
        "target_revision": index["target_revision"],
    }


def _validate_portfolio(
    hardening: dict[str, Any],
    evidence_ids: set[str],
) -> dict[str, Any]:
    if hardening["documentType"] != "codex-security.hardening-analysis":
        raise ValueError("unexpected hardening document type")
    if hardening["schemaVersion"] != "1.0":
        raise ValueError("unexpected hardening schema version")
    source = hardening["sourceEvidence"]
    if source["kind"] != "document_collection":
        raise ValueError("unexpected source-evidence kind")
    if source["sourceDrift"] != "none":
        raise ValueError("source drift is not closed")
    if hardening["assessment"]["outcome"] != "opportunities_identified":
        raise ValueError("unexpected assessment outcome")
    if not hardening["constraints"]["nonNegotiables"]:
        raise ValueError("missing hardening non-negotiables")

    opportunities = hardening["opportunities"]
    ids = [item["opportunityId"] for item in opportunities]
    if set(ids) != set(EXPECTED_OPPORTUNITIES) or len(ids) != len(set(ids)):
        raise ValueError("hardening opportunity inventory mismatch")

    selected: dict[str, str] = {}
    diagram_count = 0
    for opportunity in opportunities:
        opportunity_id = opportunity["opportunityId"]
        options = opportunity["options"]
        option_ids = [option["optionId"] for option in options]
        if len(option_ids) < 3 or len(option_ids) != len(set(option_ids)):
            raise ValueError(f"insufficient or duplicate options for {opportunity_id}")
        if opportunity["recommendedOptionId"] not in option_ids:
            raise ValueError(f"recommendation is not an option for {opportunity_id}")
        if opportunity["recommendedOptionId"] != EXPECTED_OPPORTUNITIES[opportunity_id]:
            raise ValueError(f"unexpected recommendation for {opportunity_id}")
        proposal = ANALYSIS / opportunity["proposalPath"]
        if not proposal.is_file():
            raise ValueError(f"missing proposal for {opportunity_id}")
        for evidence in opportunity["evidence"]:
            if evidence["evidenceId"] not in evidence_ids:
                raise ValueError(
                    f"unknown evidence ID {evidence['evidenceId']} for {opportunity_id}"
                )
            if evidence["claimType"] not in {"observed", "inferred"}:
                raise ValueError("invalid evidence claim type")
        before_paths: set[str] = set()
        for option in options:
            if option["kind"] not in {
                "baseline",
                "incremental",
                "structural",
                "isolation",
                "foundational",
            }:
                raise ValueError("invalid option kind")
            tradeoffs = {item["dimension"]: item for item in option["tradeoffs"]}
            required_dimensions = {
                "security",
                "performance",
                "memory",
                "reliability",
                "operability",
                "migration",
            }
            if set(tradeoffs) != required_dimensions:
                raise ValueError(
                    f"tradeoff dimensions mismatch for "
                    f"{opportunity_id}/{option['optionId']}"
                )
            for tradeoff in tradeoffs.values():
                if tradeoff["direction"] not in {
                    "improves",
                    "regresses",
                    "neutral",
                    "unknown",
                }:
                    raise ValueError("invalid tradeoff direction")
                if tradeoff["confidence"] not in {"high", "medium", "low"}:
                    raise ValueError("invalid tradeoff confidence")
                if tradeoff["basis"] not in {
                    "measured",
                    "source-derived",
                    "analogous",
                    "hypothetical",
                }:
                    raise ValueError("invalid tradeoff basis")
                for field in (
                    "direction",
                    "confidence",
                    "basis",
                    "assessment",
                    "validationPlan",
                ):
                    if not tradeoff.get(field):
                        raise ValueError(
                            f"missing {field} for "
                            f"{opportunity_id}/{option['optionId']}"
                        )
            if not option["evidenceCoverage"]:
                raise ValueError(
                    f"missing evidence coverage for "
                    f"{opportunity_id}/{option['optionId']}"
                )
            for mapping in option["evidenceCoverage"]:
                if mapping["evidenceId"] not in evidence_ids:
                    raise ValueError(
                        f"unknown coverage evidence ID {mapping['evidenceId']}"
                    )
                if mapping["effect"] not in {
                    "addresses",
                    "mitigates",
                    "unaffected",
                    "unknown",
                }:
                    raise ValueError("invalid evidence-coverage effect")
            before_path = option["diagramPaths"]["before"]
            after_path = option["diagramPaths"]["after"]
            before_paths.add(before_path)
            for relative in (before_path, after_path):
                if Path(relative).is_absolute() or ".." in Path(relative).parts:
                    raise ValueError("unsafe diagram path")
                if not (ANALYSIS / relative).is_file():
                    raise ValueError(f"missing diagram {relative}")
            diagram_count += 1
            readiness = option["implementationReadiness"]
            for field in (
                "affectedComponents",
                "workPackages",
                "acceptanceCriteria",
                "migrationNotes",
                "rollback",
            ):
                if not readiness.get(field):
                    raise ValueError(
                        f"missing readiness {field} for "
                        f"{opportunity_id}/{option['optionId']}"
                    )
        if len(before_paths) != 1:
            raise ValueError(f"before diagram drift for {opportunity_id}")
        diagram_count += 1
        selected[opportunity_id] = opportunity["recommendedOptionId"]

    if (ANALYSIS / "implementation").exists():
        raise ValueError("implementation directory is forbidden before option approval")
    return {
        "opportunity_count": len(opportunities),
        "option_count": sum(len(item["options"]) for item in opportunities),
        "diagram_count": diagram_count,
        "selected": selected,
    }


def _validate_documents() -> dict[str, Any]:
    present = {
        path.relative_to(ANALYSIS).as_posix()
        for path in ANALYSIS.rglob("*")
        if path.is_file()
    }
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        raise ValueError(f"missing required hardening artifacts: {missing}")

    heading_sets = {
        PORTFOLIO_PATH: (
            "## Evidence Basis",
            "## Constraints",
            "## Opportunity Portfolio",
            "## Recommendation Summary",
            "## Next Decisions",
        ),
        ANALYSIS / "proposals" / "deterministic-information-flow-confinement.md": (
            "## Decision",
            "## Executive Recommendation",
            "## Evidence",
            "## Current Design And Failure Mode",
            "## Desired Invariants",
            "## Constraints And Non-Goals",
            "## Before Architecture",
            "## Options",
            "## Comparison",
            "## Recommendation",
            "## Evidence Coverage And Residual Risk",
            "## Migration And Rollout",
            "## Validation Plan",
            "## Implementation Work Packages",
            "## Open Questions",
        ),
        ANALYSIS / "proposals" / "cognitive-cell-compromise-containment.md": (
            "## Decision",
            "## Executive Recommendation",
            "## Evidence",
            "## Current Design And Failure Mode",
            "## Desired Invariants",
            "## Constraints And Non-Goals",
            "## Before Architecture",
            "## Options",
            "## Comparison",
            "## Recommendation",
            "## Evidence Coverage And Residual Risk",
            "## Migration And Rollout",
            "## Validation Plan",
            "## Implementation Work Packages",
            "## Open Questions",
        ),
    }
    for path, headings in heading_sets.items():
        text = path.read_text(encoding="utf-8")
        positions = [text.find(heading) for heading in headings]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            raise ValueError(f"required heading order mismatch in {path.name}")

    distributable = [
        path
        for path in ANALYSIS.rglob("*")
        if path.is_file() and path != CONTEXT_PATH
    ]
    for path in distributable:
        text = path.read_text(encoding="utf-8")
        if "C:\\Users\\" in text or "C:/Users/" in text:
            raise ValueError(f"absolute local path in distributable artifact {path}")

    checked_local_links = 0
    for path in ANALYSIS.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_file():
                raise ValueError(f"broken local link {target} in {path.name}")
            checked_local_links += 1

    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (CONTEXT_PATH, PORTFOLIO_PATH, PLAN_PATH, THREAT_PATH)
    ).lower()
    required_phrases = (
        "direct or indirect prompt injection",
        "provider model",
        "untrusted candidate generator",
        "integrity",
        "confidentiality",
        "authority ceiling",
        "one-attempt",
        "deny-by-default",
        "no ambient network",
        "human confirmation",
        "defense in depth",
        "gate zero remains closed",
    )
    absent = [phrase for phrase in required_phrases if phrase not in combined]
    if absent:
        raise ValueError(f"required architecture statements absent: {absent}")

    forbidden_claims = (
        "prompt injection is eliminated",
        "sandbox is invulnerable",
        "production ready",
        "patient data is authorized",
    )
    present_forbidden = [phrase for phrase in forbidden_claims if phrase in combined]
    if present_forbidden:
        raise ValueError(f"overclaim present: {present_forbidden}")

    return {
        "required_artifact_count": len(REQUIRED_FILES),
        "heading_checked_document_count": len(heading_sets),
        "distributable_artifact_count": len(distributable),
        "checked_local_link_count": checked_local_links,
        "required_phrase_count": len(required_phrases),
        "forbidden_claim_count": len(present_forbidden),
    }


def build_evidence() -> dict[str, Any]:
    index = _load_json(INDEX_PATH)
    hardening = _load_json(HARDENING_PATH)
    evidence_collection = _validate_evidence_collection(index)
    source = hardening["sourceEvidence"]
    if source["targetRevision"] != index["target_revision"]:
        raise ValueError("hardening and evidence-index revision drift")
    if source["artifactCount"] != index["artifact_count"]:
        raise ValueError("hardening and evidence-index count drift")
    if source["collectionSha256"] != index["collection_sha256"]:
        raise ValueError("hardening and evidence-index hash drift")

    evidence_ids = {item["id"] for item in index["artifacts"]}
    portfolio = _validate_portfolio(hardening, evidence_ids)
    documents = _validate_documents()
    return {
        "schema_version": "emr4.model-required-bureau-gate-minus-one.acceptance.v1",
        "result": EXPECTED_RESULT,
        "passed": True,
        "mode": "repository_local_provider_free_architecture_acceptance",
        "evidence_collection": evidence_collection,
        "hardening_portfolio": portfolio,
        "documents": documents,
        "authority_and_side_effects": {
            "provider_calls": 0,
            "backend_calls": 0,
            "database_reads": 0,
            "database_writes": 0,
            "product_data_reads": 0,
            "patient_or_clinical_data_fields": 0,
            "model_runtime_wirings": 0,
            "new_tool_or_actuator_capabilities": 0,
            "cloud_or_iam_mutations": 0,
            "deployments": 0,
            "protected_ref_movements": 0,
        },
        "claim_boundary": {
            "proves": [
                "A source-hashed, research-backed adversarial architecture review identifies two hardening opportunities and compares meaningful alternatives.",
                "The selected Gate-zero candidates are a deterministic labeled capability envelope and one-attempt brokered cognitive cells.",
                "The artifacts preserve mandatory provider-model participation while denying the model authority.",
            ],
            "does_not_prove": [
                "Implementation or runtime enforcement of either selected hardening control.",
                "Prompt-injection immunity, sandbox invulnerability or provider trustworthiness.",
                "Safety for real identity, product-derived, patient, health or clinical data.",
                "Deployment, production fitness or release readiness.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    if args.write_evidence:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
