from __future__ import annotations

import ast
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def test_all_continuity_updater_source_heads_are_full_commit_ids() -> None:
    checked: list[str] = []
    for path in sorted((ROOT / "scripts").glob("*continuity_update.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assignments = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "SOURCE_HEAD"
                for target in node.targets
            )
        ]
        for assignment in assignments:
            assert isinstance(assignment.value, ast.Constant)
            assert isinstance(assignment.value.value, str)
            assert FULL_COMMIT.fullmatch(assignment.value.value), (
                f"{path.relative_to(ROOT)} SOURCE_HEAD must be 40 lowercase hex characters"
            )
            checked.append(str(path.relative_to(ROOT)))
    assert checked


def test_current_updater_resolves_commit_before_building_continuity_node() -> None:
    path = (
        ROOT
        / "scripts/raisa_provider_free_read_only_ordinary_practice_check_in_admission_readiness_review_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    resolution = source.index("source_resolution = resolve_commit_source")
    graph_read = source.index('graph = json.loads(GRAPH.read_text(encoding="utf-8"))')
    assert resolution < graph_read
