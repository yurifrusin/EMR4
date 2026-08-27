"""Focused tests for the pure G1A.1 canonical verdict kernel."""

from __future__ import annotations

import pytest

from orchestration_harness.verdict import (
    ArtifactKind,
    ReviewVerdict,
    VerdictAssessment,
    parse_artifact_verdict,
)


def test_exact_pass_decision_grants_artifact_authority() -> None:
    result = parse_artifact_verdict("DECISION: PASS\n", ArtifactKind.DECISION)

    assert result.artifact_valid is True
    assert result.review_verdict is ReviewVerdict.PASS
    assert result.integration_authorized is True
    assert result.canonical_marker == "DECISION: PASS"
    assert result.reason_code == "terminal_marker_observed"


def test_exact_revision_required_is_valid_without_authority() -> None:
    result = parse_artifact_verdict("DECISION: REVISION_REQUIRED\n", "decision")

    assert result.artifact_valid is True
    assert result.review_verdict is ReviewVerdict.REVISION_REQUIRED
    assert result.integration_authorized is False
    assert result.canonical_marker == "DECISION: REVISION_REQUIRED"


def test_exact_completion_has_no_review_verdict_or_authority() -> None:
    result = parse_artifact_verdict("STATUS: COMPLETE\n", "completion")

    assert result.artifact_valid is True
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.canonical_marker == "STATUS: COMPLETE"


@pytest.mark.parametrize(
    ("body", "kind", "canonical"),
    [
        ("decision: pass", "decision", "DECISION: PASS"),
        ("Decision: Revision_Required", "decision", "DECISION: REVISION_REQUIRED"),
        ("status: complete", "completion", "STATUS: COMPLETE"),
    ],
)
def test_markers_are_case_insensitive_and_canonicalized(
    body: str, kind: str, canonical: str
) -> None:
    assert parse_artifact_verdict(body, kind).canonical_marker == canonical


@pytest.mark.parametrize(
    "body",
    [
        "## DECISION: PASS",
        "**DECISION: PASS**",
        "__DECISION: PASS__",
        "`DECISION: PASS`",
        "*DECISION: PASS*",
        "_DECISION: PASS_",
        "| Verdict | **`DECISION: PASS`** |",
        "| Verdict | **`DECISION: PASS`** | Notes |",
    ],
)
def test_heading_balanced_wrappers_and_table_cells_are_compatible(body: str) -> None:
    assert parse_artifact_verdict(body, "decision").artifact_valid is True


@pytest.mark.parametrize(
    "body",
    [
        "Example: `left | DECISION: PASS | right`",
        "> | DECISION: PASS |",
        "- | DECISION: PASS |",
        "not a table | DECISION: PASS | quoted example",
        r"\| DECISION: PASS \|",
    ],
)
def test_noneligible_pipe_contexts_are_fail_closed(body: str) -> None:
    result = parse_artifact_verdict(body, "decision")

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "non_authoritative_marker_context"


@pytest.mark.parametrize(
    "rejected_context",
    [
        "Example: `left | DECISION: REVISION_REQUIRED | right`",
        "> | DECISION: REVISION_REQUIRED |",
        "- | DECISION: REVISION_REQUIRED |",
        "not a table | DECISION: REVISION_REQUIRED | quoted example",
        r"\| DECISION: REVISION_REQUIRED \|",
    ],
)
def test_visible_pass_and_rejected_pipe_context_are_fail_closed(
    rejected_context: str,
) -> None:
    result = parse_artifact_verdict(f"DECISION: PASS\n{rejected_context}", "decision")

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "non_authoritative_marker_context"


def test_arbitrary_prose_containing_marker_words_is_not_authority() -> None:
    result = parse_artifact_verdict(
        "The expected DECISION: PASS marker will be added after the review.",
        "decision",
    )

    assert result.artifact_valid is False
    assert result.reason_code == "missing_authoritative_marker"


@pytest.mark.parametrize(
    ("body", "kind"),
    [
        ("```text\nDECISION: PASS\n```", "decision"),
        ("~~~text\nSTATUS: COMPLETE\n~~~", "completion"),
        ("    DECISION: PASS", "decision"),
        ("<!-- DECISION: PASS -->", "decision"),
        ("<!--\nSTATUS: COMPLETE\n-->", "completion"),
    ],
)
def test_hidden_markdown_markers_are_fail_closed(body: str, kind: str) -> None:
    result = parse_artifact_verdict(body, kind)

    assert result.artifact_valid is False
    assert result.integration_authorized is False
    assert result.reason_code == "non_authoritative_marker_context"


@pytest.mark.parametrize(
    "body",
    [
        "DECISION: PASS\n<!-- DECISION: REVISION_REQUIRED -->",
        "DECISION: REVISION_REQUIRED\n```\nDECISION: PASS\n```",
    ],
)
def test_visible_and_hidden_decisions_are_fail_closed(body: str) -> None:
    result = parse_artifact_verdict(body, "decision")

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "non_authoritative_marker_context"


@pytest.mark.parametrize(
    ("body", "kind"),
    [
        ("DECISıON: PASS", "decision"),
        ("ſTATUS: COMPLETE", "completion"),
        ("DECISION: PΑSS", "decision"),
    ],
)
def test_non_ascii_marker_lexemes_are_fail_closed(body: str, kind: str) -> None:
    result = parse_artifact_verdict(body, kind)

    assert result.artifact_valid is False
    assert result.integration_authorized is False
    assert result.reason_code == "non_ascii_marker_lexeme"


def test_non_ascii_prose_does_not_taint_a_visible_ascii_marker() -> None:
    result = parse_artifact_verdict(
        "Résumé: independently checked.\nDECISION: PASS", "decision"
    )

    assert result.artifact_valid is True
    assert result.integration_authorized is True


def test_missing_marker_is_rejected() -> None:
    result = parse_artifact_verdict("Review finished without a marker.", "decision")

    assert result.artifact_valid is False
    assert result.reason_code == "missing_authoritative_marker"


def test_duplicate_pass_markers_are_rejected() -> None:
    result = parse_artifact_verdict("DECISION: PASS\nDECISION: PASS\n", "decision")

    assert result.artifact_valid is False
    assert result.reason_code == "duplicate_authoritative_markers"


def test_pass_and_revision_required_conflict_is_rejected() -> None:
    result = parse_artifact_verdict(
        "DECISION: PASS\nDECISION: REVISION_REQUIRED\n", "decision"
    )

    assert result.artifact_valid is False
    assert result.reason_code == "conflicting_decision_markers"


def test_supported_marker_outside_terminal_window_is_rejected() -> None:
    result = parse_artifact_verdict(
        "DECISION: PASS\n" + "\n".join(f"evidence {index}" for index in range(9)),
        "decision",
    )

    assert result.artifact_valid is False
    assert result.reason_code == "terminal_marker_not_near_artifact_end"


@pytest.mark.parametrize("indentation", [" ", "  ", "   "])
def test_one_to_three_space_visible_lines_count_toward_terminal_window(
    indentation: str,
) -> None:
    body = "DECISION: PASS\n" + "\n".join(
        f"{indentation}visible evidence line {index}" for index in range(9)
    )

    result = parse_artifact_verdict(body, "decision")

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "terminal_marker_not_near_artifact_end"


@pytest.mark.parametrize("indentation", [" ", "  ", "   "])
def test_indented_visible_contradictory_conclusion_cannot_leave_early_pass_authority(
    indentation: str,
) -> None:
    trailing_lines = [
        *(f"{indentation}visible evidence line {index}" for index in range(8)),
        f"{indentation}visible conclusion: revisions remain necessary",
    ]

    result = parse_artifact_verdict(
        "DECISION: PASS\n" + "\n".join(trailing_lines), "decision"
    )

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "terminal_marker_not_near_artifact_end"


@pytest.mark.parametrize("indentation", ["", " ", "  ", "   "])
def test_zero_to_three_space_pass_at_artifact_end_remains_authoritative(
    indentation: str,
) -> None:
    body = "\n".join(f"visible evidence line {index}" for index in range(9))
    body += f"\n{indentation}DECISION: PASS"

    result = parse_artifact_verdict(body, "decision")

    assert result.artifact_valid is True
    assert result.review_verdict is ReviewVerdict.PASS
    assert result.integration_authorized is True
    assert result.canonical_marker == "DECISION: PASS"


@pytest.mark.parametrize("indentation", ["    ", "\t"])
def test_four_space_and_tab_indented_pass_remain_non_authoritative(
    indentation: str,
) -> None:
    result = parse_artifact_verdict(f"{indentation}DECISION: PASS", "decision")

    assert result.artifact_valid is False
    assert result.review_verdict is None
    assert result.integration_authorized is False
    assert result.reason_code == "non_authoritative_marker_context"


def test_unsupported_decision_value_is_rejected() -> None:
    result = parse_artifact_verdict("DECISION: INCONCLUSIVE", "decision")

    assert result.artifact_valid is False
    assert result.reason_code == "unsupported_decision_marker"


def test_unsupported_status_value_is_rejected() -> None:
    result = parse_artifact_verdict("STATUS: COMPLETED", "completion")

    assert result.artifact_valid is False
    assert result.reason_code == "unsupported_status_marker"


@pytest.mark.parametrize(
    ("body", "kind"),
    [("STATUS: COMPLETE", "decision"), ("DECISION: PASS", "completion")],
)
def test_wrong_kind_markers_are_rejected(body: str, kind: str) -> None:
    result = parse_artifact_verdict(body, kind)

    assert result.artifact_valid is False
    assert result.reason_code == "wrong_artifact_kind_marker"


def test_legacy_verdict_authority_is_rejected() -> None:
    result = parse_artifact_verdict("VERDICT: PASS", "decision")

    assert result.artifact_valid is False
    assert result.reason_code == "legacy_verdict_marker"


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "artifact_kind": ArtifactKind.COMPLETION,
            "artifact_valid": True,
            "review_verdict": ReviewVerdict.PASS,
            "canonical_marker": "STATUS: COMPLETE",
            "reason_code": "terminal_marker_observed",
        },
        {
            "artifact_kind": ArtifactKind.DECISION,
            "artifact_valid": False,
            "review_verdict": ReviewVerdict.PASS,
            "canonical_marker": "DECISION: PASS",
            "reason_code": "missing_authoritative_marker",
        },
        {
            "artifact_kind": ArtifactKind.DECISION,
            "artifact_valid": True,
            "review_verdict": ReviewVerdict.REVISION_REQUIRED,
            "canonical_marker": "DECISION: PASS",
            "reason_code": "terminal_marker_observed",
        },
    ],
)
def test_contradictory_assessment_construction_fails(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        VerdictAssessment(**kwargs)  # type: ignore[arg-type]


def test_completion_can_never_grant_integration_authority() -> None:
    result = parse_artifact_verdict("STATUS: COMPLETE", "completion")

    assert result.integration_authorized is False


def test_invalid_artifact_can_never_grant_integration_authority() -> None:
    result = parse_artifact_verdict("DECISION: REJECT", "decision")

    assert result.integration_authorized is False


def test_serialization_and_reason_codes_are_deterministic() -> None:
    first = parse_artifact_verdict("DECISION: REVISION_REQUIRED", "decision")
    second = parse_artifact_verdict("decision: revision_required", "decision")

    assert (
        first.to_dict()
        == second.to_dict()
        == {
            "artifact_kind": "decision",
            "artifact_valid": True,
            "review_verdict": "revision_required",
            "integration_authorized": False,
            "canonical_marker": "DECISION: REVISION_REQUIRED",
            "reason_code": "terminal_marker_observed",
        }
    )
    assert first.to_json() == second.to_json()
