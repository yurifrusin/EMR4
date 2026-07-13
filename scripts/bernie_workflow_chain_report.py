"""Safe aggregate CLI report for the workflow-chain harness.

Loads all committed chain fixtures, runs each through the chain harness,
and emits aggregate-only JSON with no utterance text or payload identifiers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.workflow_chain.harness import (
    WF_CHAIN_REPORT_SCHEMA_VERSION,
    WORKFLOW_CHAIN_HARNESS_SCHEMA_VERSION,
    WorkflowChain,
    WorkflowStep,
    WorkflowStepResult,
    assert_workflow_chain_report_safety,
    build_chain_report,
    run_workflow_chain,
)

DEFAULT_FIXTURE_DIR = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "bernie_workflow_chains"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_chain_fixtures(fixture_dir: Path) -> tuple[WorkflowChain, ...]:
    """Load all committed chain fixtures from the given directory."""
    if not fixture_dir.exists():
        raise ValueError(f"Fixture directory does not exist: {fixture_dir}")
    if not fixture_dir.is_dir():
        raise ValueError(f"Fixture path is not a directory: {fixture_dir}")

    fixture_paths = sorted(fixture_dir.glob("*.json"))
    if not fixture_paths:
        raise ValueError(f"No JSON fixtures found in: {fixture_dir}")

    chains: list[WorkflowChain] = []
    for path in fixture_paths:
        payload = _load_json(path)
        schema_version = payload.get("schema_version")
        if schema_version != WORKFLOW_CHAIN_HARNESS_SCHEMA_VERSION:
            raise ValueError(
                f"Unexpected fixture schema_version in {path.name}: "
                f"{schema_version!r}"
            )
        source = payload.get("source")
        if source != "authored_synthetic":
            raise ValueError(
                f"Unexpected fixture source in {path.name}: {source!r}"
            )

        chain_list = payload.get("chains")
        if not isinstance(chain_list, list) or not chain_list:
            raise ValueError(f"No chains found in fixture: {path.name}")

        for chain_data in chain_list:
            steps_data = chain_data.get("steps", [])
            if not steps_data:
                raise ValueError(f"No steps in chain {chain_data.get('chain_id', '?')}")
            steps = tuple(
                WorkflowStep(
                    utterance=step["utterance"],
                    step_label=step["step_label"],
                    expected_verb=step.get("expected_verb"),
                    expected_dispatch=step.get("expected_dispatch"),
                    expected_frame_kind=step.get("expected_frame_kind"),
                    expected_resolution=step.get("expected_resolution"),
                )
                for step in steps_data
            )
            chains.append(
                WorkflowChain(
                    chain_id=chain_data["chain_id"],
                    label=chain_data["label"],
                    steps=steps,
                )
            )

    if not chains:
        raise ValueError(f"No workflow chains loaded from: {fixture_dir}")

    return tuple(chains)


def build_workflow_report(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    """Build a safe aggregate report from loaded chain fixtures."""
    chains = load_chain_fixtures(fixture_dir)
    all_results: list[tuple[WorkflowStepResult, ...]] = []
    all_classifications = []

    for chain in chains:
        _, step_results, classification = run_workflow_chain(chain)
        all_results.append(step_results)
        all_classifications.append(classification)

    from tests.workflow_chain.harness import Resolution

    return build_chain_report(
        chains,
        tuple(all_results),
        tuple(all_classifications),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate workflow chain report."
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing workflow chain fixtures.",
    )
    args = parser.parse_args()
    report = build_workflow_report(args.fixture_dir)
    assert_workflow_chain_report_safety(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
