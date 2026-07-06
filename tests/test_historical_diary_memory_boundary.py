from pathlib import Path


RUNTIME_BOUNDARY_FILES = [
    "app/services/ai/knowledge_base.py",
    "app/services/ai/access_service.py",
    "app/services/practice_knowledge/boundary.py",
    "app/services/practice_knowledge/retriever.py",
    "app/services/diary/policy.py",
    "app/services/diary/confirm_gate.py",
    "app/services/diary/slot_search.py",
    "app/services/bernie/session.py",
    "app/services/bernie/session_store.py",
]
FORBIDDEN_HISTORICAL_RUNTIME_FRAGMENTS = {
    "h15_semantic_candidates",
    "historical_diary_semantic_candidate_builder",
    "semantic_h15_candidate_fixtures",
    "semantic_h15_prototype_neutral_aggregate",
    "historical-diary-trove-h15-approved-gate",
}


def test_runtime_services_do_not_import_historical_diary_candidate_fixtures():
    repo_root = Path(__file__).resolve().parents[1]
    errors = []
    for rel_path in RUNTIME_BOUNDARY_FILES:
        path = repo_root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        leaked = sorted(
            fragment for fragment in FORBIDDEN_HISTORICAL_RUNTIME_FRAGMENTS if fragment in text
        )
        if leaked:
            errors.append(f"{rel_path}: forbidden historical diary runtime fragment(s) {leaked}")

    assert not errors, "\n".join(errors)


def test_historical_diary_candidates_are_not_access_ai_or_practice_knowledge_sources():
    repo_root = Path(__file__).resolve().parents[1]
    runtime_text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in [
            repo_root / "app/services/ai/knowledge_base.py",
            repo_root / "app/services/practice_knowledge/examples.py",
            repo_root / "app/services/practice_knowledge/retriever.py",
        ]
        if path.exists()
    )

    assert "h15_semantic_candidates" not in runtime_text
    assert "historical-diary-trove" not in runtime_text
    assert "semantic_h15" not in runtime_text
