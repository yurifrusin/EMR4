"""Bounded, synthetic maintenance controls for the CI-A source selection."""

import builtins
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import (
    historical_diary_leakage_lint,
    security_bandit_gate,
    verification_runtime,
)
from scripts.historical_diary_leakage_lint import lint_paths, lint_text
from scripts.python_source_state import SourceStateError
from scripts.security_bandit_gate import parse_report, validate_report


ROOT = Path(__file__).resolve().parents[1]

SELECTED_BANDIT_PATHS = ("app/synthetic_a.py", "scripts/synthetic_b.py")


def _bandit_result(path: str, test_id: str, line: int, code: str) -> dict:
    return {
        "filename": path,
        "test_id": test_id,
        "line_number": line,
        "code": code,
        "issue_severity": "MEDIUM",
        "issue_confidence": "HIGH",
    }


def _reviewed_row(result: dict) -> dict:
    return {
        "path": result["filename"],
        "test_id": result["test_id"],
        "line_number": result["line_number"],
        "code_sha256": hashlib.sha256(result["code"].encode("utf-8")).hexdigest(),
    }


def _bandit_evidence() -> tuple[dict, list[dict]]:
    results = [
        _bandit_result("app/synthetic_a.py", "B101", 2, "assert False\n"),
        _bandit_result("scripts/synthetic_b.py", "B602", 4, "run(shell=True)\n"),
    ]
    per_file = {
        "loc": 5,
        "nosec": 0,
        "skipped_tests": 0,
        "CONFIDENCE.HIGH": 1,
        "CONFIDENCE.MEDIUM": 0,
        "CONFIDENCE.LOW": 0,
        "CONFIDENCE.UNDEFINED": 0,
        "SEVERITY.HIGH": 0,
        "SEVERITY.MEDIUM": 1,
        "SEVERITY.LOW": 0,
        "SEVERITY.UNDEFINED": 0,
    }
    metrics = {path: per_file.copy() for path in SELECTED_BANDIT_PATHS}
    metrics["_totals"] = {key: value * 2 for key, value in per_file.items()}
    return {"errors": [], "metrics": metrics, "results": results}, [
        _reviewed_row(result) for result in results
    ]


def _set_bandit_marginals(
    report: dict, by_path: dict[str, tuple[tuple[str, ...], tuple[str, ...]]]
) -> None:
    for path in SELECTED_BANDIT_PATHS:
        row = report["metrics"][path]
        for key in row:
            if key.startswith(("SEVERITY.", "CONFIDENCE.")):
                row[key] = 0
        severities, confidences = by_path[path]
        for severity in severities:
            row[f"SEVERITY.{severity}"] += 1
        for confidence in confidences:
            row[f"CONFIDENCE.{confidence}"] += 1
    report["metrics"]["_totals"] = {
        key: sum(report["metrics"][path][key] for path in SELECTED_BANDIT_PATHS)
        for key in report["metrics"][SELECTED_BANDIT_PATHS[0]]
    }


def _validate_bandit(report: dict, reviewed: list[dict], *, returncode: int = 1):
    return validate_report(
        report,
        selected_paths=SELECTED_BANDIT_PATHS,
        reviewed_findings=reviewed,
        returncode=returncode,
    )


def _synthetic_selection(tmp_path: Path, *, status: str) -> tuple[Path, str, Path]:
    repo_root = tmp_path / "synthetic-repo"
    contents = {
        "app/synthetic_a.py": "# synthetic\nassert False\n",
        "scripts/synthetic_b.py": "# synthetic\n\n\nrun(shell=True)\n",
        "tests/test_synthetic.py": "def test_smoke():\n    assert True\n",
        "docs/synthetic-historical-diary.md": "neutral historical diary note\n",
        "pyproject.toml": "[tool.pytest.ini_options]\n",
    }
    kinds = {
        "app/synthetic_a.py": "source",
        "scripts/synthetic_b.py": "source",
        "tests/test_synthetic.py": "test",
        "docs/synthetic-historical-diary.md": "data",
        "pyproject.toml": "config",
    }
    digests = {}
    for relative_path, source in contents.items():
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = source.encode("utf-8")
        path.write_bytes(payload)
        digests[relative_path] = hashlib.sha256(payload).hexdigest()
    _report, reviewed = _bandit_evidence()
    bandit_scope = [
        [path, digests[path]] for path in sorted(SELECTED_BANDIT_PATHS)
    ]
    scope_payload = json.dumps(bandit_scope, separators=(",", ":")).encode("utf-8")
    manifest = {
        "schema_version": "emr4.python_source_state.v2",
        "target_python": "3.11",
        "scope": "bounded_ordinary_verification",
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "completeness": {
            "repository_wide": False,
            "pending": ["ordinary population beyond this synthetic selection"],
        },
        "files": [
            {"path": path, "sha256": digests[path], "kind": kinds[path]}
            for path in sorted(contents)
        ],
        "phases": {
            "compile": [
                "app/synthetic_a.py",
                "scripts/synthetic_b.py",
                "tests/test_synthetic.py",
            ],
            "ruff": ["app/synthetic_a.py", "scripts/synthetic_b.py"],
            "bandit": list(SELECTED_BANDIT_PATHS),
            "leakage": ["docs/synthetic-historical-diary.md"],
            "tests": ["tests/test_synthetic.py::test_smoke"],
        },
        "configs": {
            "ruff": "pyproject.toml",
            "bandit": "pyproject.toml",
            "pytest": "pyproject.toml",
        },
        "bandit_review": {
            "status": status,
            "scope_sha256": hashlib.sha256(scope_payload).hexdigest(),
            "reviewed_findings": reviewed if status == "reviewed" else [],
        },
    }
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    selection_path = repo_root / "synthetic-selection.json"
    selection_path.write_bytes(payload)
    return selection_path, hashlib.sha256(payload).hexdigest(), repo_root


def _guard_physical_observation(guard, forbidden) -> None:
    for owner, names in (
        (os, ("stat", "lstat", "open")),
        (Path, ("resolve", "stat", "lstat", "open", "read_bytes", "read_text")),
        (builtins, ("open",)),
        (io, ("open",)),
    ):
        for name in names:
            guard.setattr(owner, name, forbidden)


def test_receipt_writer_emits_canonical_utf8_lf_bytes(tmp_path: Path):
    # This legacy writer is deliberately imported only by its unselected test.
    from scripts.ariadne_orchestrator_preflight import write_json_lf

    path = tmp_path / "receipt.json"
    write_json_lf(path, {"z": 1, "a": "receipt"})

    payload = path.read_bytes()
    assert payload.endswith(b"\n")
    assert b"\r\n" not in payload
    assert json.loads(payload) == {"a": "receipt", "z": 1}


def test_verification_runtime_labels_launcher_timeout(
    monkeypatch, tmp_path: Path, capsys
):
    command = verification_runtime.VerificationCommand(
        "bounded test", ["python", "ignored.py"], 7
    )
    observed = []

    def expire(argv, **kwargs):
        observed.append((argv, kwargs))
        raise subprocess.TimeoutExpired(cmd=argv, timeout=7)

    monkeypatch.setattr(verification_runtime.os, "environ", {"SYNTHETIC": "base"})
    monkeypatch.setattr(subprocess, "run", expire)
    result = verification_runtime.run_command(
        command, cwd=tmp_path, env={"SYNTHETIC": "override"}
    )

    assert result == verification_runtime.LAUNCHER_TIMEOUT_EXIT
    assert observed == [
        (
            ["python", "ignored.py"],
            {
                "cwd": tmp_path,
                "env": {"SYNTHETIC": "override"},
                "check": False,
                "timeout": 7,
            },
        )
    ]
    assert "[launcher_timeout] bounded test exceeded 7s" in capsys.readouterr().err


def test_verification_runtime_preserves_child_exit_code(
    monkeypatch, tmp_path: Path, capsys
):
    command = verification_runtime.VerificationCommand(
        "failing child", ["python", "ignored.py"], 7
    )
    observed = []

    def fail(argv, **kwargs):
        observed.append((argv, kwargs))
        return subprocess.CompletedProcess(args=argv, returncode=9)

    monkeypatch.setattr(verification_runtime.os, "environ", {"SYNTHETIC": "base"})
    monkeypatch.setattr(subprocess, "run", fail)
    result = verification_runtime.run_command(command, cwd=tmp_path)

    assert result == 9
    assert result != verification_runtime.LAUNCHER_TIMEOUT_EXIT
    assert observed == [
        (
            ["python", "ignored.py"],
            {
                "cwd": tmp_path,
                "env": {"SYNTHETIC": "base"},
                "check": False,
                "timeout": 7,
            },
        )
    ]
    assert "[child_failure] failing child exited 9" in capsys.readouterr().err


def test_verification_runtime_stops_after_first_child_failure(
    monkeypatch, tmp_path: Path, capsys
):
    commands = [
        verification_runtime.VerificationCommand(
            "first child", ["python", "first.py"], 7
        ),
        verification_runtime.VerificationCommand(
            "second child", ["python", "second.py"], 7
        ),
    ]
    observed = []

    def fail_first(argv, **kwargs):
        observed.append((argv, kwargs))
        return subprocess.CompletedProcess(args=argv, returncode=9)

    monkeypatch.setattr(verification_runtime.os, "environ", {"SYNTHETIC": "base"})
    monkeypatch.setattr(subprocess, "run", fail_first)

    result = verification_runtime.run_commands(
        commands, cwd=tmp_path, env={"SYNTHETIC": "override"}
    )

    assert result == 9
    assert observed == [
        (
            ["python", "first.py"],
            {
                "cwd": tmp_path,
                "env": {"SYNTHETIC": "override"},
                "check": False,
                "timeout": 7,
            },
        )
    ]
    assert "[child_failure] first child exited 9" in capsys.readouterr().err


def test_historical_diary_lint_allows_neutral_and_policy_context():
    neutral = Path("docs/synthetic-historical-diary-example.md")
    policy = Path("docs/adversarial/synthetic-historical-diary-policy.md")

    assert lint_text(neutral, "strong_diary_grid is an observed layout class.\n") == []
    assert lint_text(
        policy, "Do not infer that strong_diary_grid means booked.\n"
    ) == []
    assert lint_text(neutral, "It is forbidden to infer booked appointments.\n") == []


@pytest.mark.parametrize(
    "source,reason",
    [
        pytest.param(
            "def test_h_series_" "patient_arrived(): pass\n",
            "test name combines H-series/historical diary with receptionist semantics",
            id="test-name-promotion",
        ),
        pytest.param(
            "The diary was booked.\n",
            "semantic promotion wording outside policy context",
            id="prose-promotion",
        ),
        pytest.param(
            "deterministic_uses allows this view.\n",
            "deterministic_uses must stay metadata, not permission logic",
            id="deterministic-uses-permission",
        ),
        pytest.param(
            "time_grid_" "delta\nmeans an appointment was scheduled.\n",
            "neutral H-series class is framed as booking/reception semantics",
            id="cross-line-neutral-promotion",
        ),
    ],
)
def test_historical_diary_lint_rejects_specific_drift(source, reason):
    path = Path("docs/synthetic-historical-diary-example.md")

    issues = lint_text(path, source)

    assert len(issues) == 1
    assert issues[0].path == path
    assert issues[0].line == 1
    assert issues[0].reason.startswith(reason)


def test_historical_diary_lint_paths_reads_only_explicit_literal_files(
    tmp_path: Path, monkeypatch
):
    selected = tmp_path / "selected-historical-diary.md"
    unselected = tmp_path / "unselected-historical-diary.md"
    selected.write_text(
        "time_grid_" "delta means an appointment was scheduled.\n", encoding="utf-8"
    )
    unselected.write_text("The diary was booked.\n", encoding="utf-8")

    def forbid_walk(*_args, **_kwargs):
        raise AssertionError("a literal selection must not walk its parent directory")

    monkeypatch.setattr(Path, "rglob", forbid_walk)
    issues = lint_paths([selected])

    assert len(issues) == 1
    assert issues[0].path == selected
    assert issues[0].line == 1
    assert issues[0].reason.startswith(
        "neutral H-series class is framed as booking/reception semantics"
    )


@pytest.mark.parametrize(
    "bad_input,reason",
    [
        pytest.param("missing", "missing_literal_lint_path", id="missing"),
        pytest.param("directory", "literal_lint_not_regular", id="directory"),
        pytest.param("duplicate", "duplicate_literal_lint_path", id="duplicate"),
        pytest.param("glob", "invalid_literal_lint_path", id="glob"),
        pytest.param("redirection", "invalid_literal_lint_path", id="redirection"),
        pytest.param("symlink", "literal_lint_redirection", id="symlink"),
    ],
)
def test_historical_diary_lint_paths_rejects_invalid_literals(
    tmp_path: Path, bad_input: str, reason: str
):
    selected = tmp_path / "selected-historical-diary.md"
    selected.write_text("neutral historical diary note\n", encoding="utf-8")
    assert lint_paths([selected]) == []
    if bad_input == "missing":
        paths = [tmp_path / "absent-historical-diary.md"]
    elif bad_input == "directory":
        directory = tmp_path / "directory-historical-diary.md"
        directory.mkdir()
        paths = [directory]
    elif bad_input == "duplicate":
        paths = [selected, selected]
    elif bad_input == "glob":
        paths = [tmp_path / "*-historical-diary.md"]
    elif bad_input == "redirection":
        paths = [tmp_path / "nested" / ".." / selected.name]
    else:
        alias = tmp_path / "alias-historical-diary.md"
        alias.symlink_to(selected)
        paths = [alias]

    with pytest.raises(SourceStateError, match=f"(?i:{reason})"):
        lint_paths(paths)


@pytest.mark.parametrize(
    "mutation,reason",
    [
        pytest.param(
            "late-reserved-ancestor",
            "invalid_literal_lint_path",
            id="late-reserved-ancestor",
        ),
        pytest.param(
            "late-duplicate",
            "duplicate_literal_lint_path",
            id="late-duplicate",
        ),
    ],
)
def test_historical_diary_lint_paths_validates_all_rows_before_observation(
    tmp_path: Path, monkeypatch, mutation: str, reason: str
):
    valid = tmp_path / "selected-historical-diary.md"
    valid.write_text("neutral historical diary note\n", encoding="utf-8")
    assert lint_paths([valid]) == []
    later = (
        tmp_path / "aux" / "note.md"
        if mutation == "late-reserved-ancestor"
        else valid
    )

    def forbid_file_observation(*_args, **_kwargs):
        raise AssertionError("all paths must validate before physical observation")

    with monkeypatch.context() as guard:
        _guard_physical_observation(guard, forbid_file_observation)
        with pytest.raises(SourceStateError, match=reason):
            lint_paths([valid, later])


def test_bandit_accepts_complete_exact_scope_and_reviewed_findings():
    report, reviewed = _bandit_evidence()

    assert _validate_bandit(report, reviewed) is None


def test_bandit_normalizes_dot_prefixed_metric_and_result_filenames():
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None
    report["metrics"] = {
        path if path == "_totals" else f"./{path}": values
        for path, values in report["metrics"].items()
    }
    for result in report["results"]:
        result["filename"] = f"./{result['filename']}"

    assert _validate_bandit(report, reviewed) is None


def test_bandit_rejects_canonical_and_dot_prefixed_metric_alias():
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None
    canonical = SELECTED_BANDIT_PATHS[0]
    report["metrics"][f"./{canonical}"] = report["metrics"][canonical].copy()

    with pytest.raises(SourceStateError, match="bandit_metric_scope_mismatch"):
        _validate_bandit(report, reviewed)


def test_bandit_accepts_empty_filtered_results_with_ambiguous_marginals(
):
    report, _reviewed = _bandit_evidence()
    report["results"] = []
    _set_bandit_marginals(
        report,
        {
            SELECTED_BANDIT_PATHS[0]: (
                ("MEDIUM", "LOW"),
                ("LOW", "MEDIUM"),
            ),
            SELECTED_BANDIT_PATHS[1]: ((), ()),
        },
    )

    assert _validate_bandit(report, [], returncode=0) is None


def test_bandit_rejects_empty_results_when_marginals_prove_an_eligible_finding():
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None
    report["results"] = []
    _set_bandit_marginals(
        report,
        {
            SELECTED_BANDIT_PATHS[0]: (("MEDIUM",), ("MEDIUM",)),
            SELECTED_BANDIT_PATHS[1]: ((), ()),
        },
    )

    with pytest.raises(SourceStateError, match="bandit_filtered_results_incomplete"):
        _validate_bandit(report, [], returncode=0)


@pytest.mark.parametrize(
    "mutation,reason",
    [
        pytest.param(
            "missing-metric", "incomplete_bandit_metrics", id="missing-metric"
        ),
        pytest.param(
            "extra-metric", "bandit_metric_scope_mismatch", id="extra-metric"
        ),
        pytest.param("missing-rank", "malformed_bandit_metrics", id="missing-rank"),
        pytest.param("negative-rank", "malformed_bandit_metrics", id="negative-rank"),
        pytest.param(
            "noninteger-rank", "malformed_bandit_metrics", id="noninteger-rank"
        ),
        pytest.param(
            "totals-mismatch", "incomplete_bandit_metrics", id="totals-mismatch"
        ),
        pytest.param(
            "scanner-error", "malformed_or_errored_bandit_report", id="scanner-error"
        ),
        pytest.param(
            "unexpected",
            "bandit_reviewed_fingerprint_mismatch",
            id="unexpected-finding",
        ),
        pytest.param(
            "omitted", "bandit_filtered_results_incomplete", id="omitted-finding"
        ),
        pytest.param(
            "mismatched-hash",
            "bandit_reviewed_fingerprint_mismatch",
            id="mismatched-hash",
        ),
        pytest.param(
            "duplicate-result",
            "unexpected_or_duplicate_bandit_result",
            id="duplicate-result",
        ),
        pytest.param(
            "duplicate-review", "duplicate_reviewed_finding", id="duplicate-review"
        ),
        pytest.param(
            "wrong-path",
            "unexpected_or_duplicate_bandit_result",
            id="result-outside-scope",
        ),
    ],
)
def test_bandit_rejects_incomplete_or_mismatched_evidence(mutation: str, reason: str):
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None
    report = copy.deepcopy(report)
    reviewed = copy.deepcopy(reviewed)
    if mutation == "missing-metric":
        del report["metrics"][SELECTED_BANDIT_PATHS[1]]
    elif mutation == "extra-metric":
        report["metrics"]["app/unselected.py"] = report["metrics"][
            SELECTED_BANDIT_PATHS[0]
        ].copy()
    elif mutation == "missing-rank":
        del report["metrics"][SELECTED_BANDIT_PATHS[0]]["CONFIDENCE.LOW"]
    elif mutation == "negative-rank":
        report["metrics"][SELECTED_BANDIT_PATHS[0]]["CONFIDENCE.LOW"] = -1
    elif mutation == "noninteger-rank":
        report["metrics"][SELECTED_BANDIT_PATHS[0]]["CONFIDENCE.HIGH"] = "1"
    elif mutation == "totals-mismatch":
        report["metrics"]["_totals"]["SEVERITY.MEDIUM"] -= 1
    elif mutation == "scanner-error":
        report["errors"] = ["synthetic scan failure"]
    elif mutation == "unexpected":
        report["results"].append(
            _bandit_result(SELECTED_BANDIT_PATHS[0], "B102", 3, "exec('x')\n")
        )
        for key in ("CONFIDENCE.HIGH", "SEVERITY.MEDIUM"):
            report["metrics"][SELECTED_BANDIT_PATHS[0]][key] += 1
            report["metrics"]["_totals"][key] += 1
    elif mutation == "omitted":
        report["results"].pop()
    elif mutation == "mismatched-hash":
        report["results"][0]["code"] = "assert True\n"
    elif mutation == "duplicate-result":
        report["results"].append(copy.deepcopy(report["results"][0]))
        for key in ("CONFIDENCE.HIGH", "SEVERITY.MEDIUM"):
            report["metrics"][SELECTED_BANDIT_PATHS[0]][key] += 1
            report["metrics"]["_totals"][key] += 1
    elif mutation == "duplicate-review":
        reviewed.append(copy.deepcopy(reviewed[0]))
    else:
        report["results"][0]["filename"] = "app/unselected.py"

    with pytest.raises(SourceStateError, match=reason):
        _validate_bandit(report, reviewed)


def test_bandit_rejects_unreviewed_findings():
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None

    with pytest.raises(SourceStateError, match="bandit_reviewed_fingerprint_mismatch"):
        _validate_bandit(report, [])


def test_bandit_rejects_reviewed_fingerprint_missing_from_complete_report():
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None
    reviewed.append(
        {
            "path": SELECTED_BANDIT_PATHS[0],
            "test_id": "B999",
            "line_number": 8,
            "code_sha256": hashlib.sha256(b"synthetic reviewed only\n").hexdigest(),
        }
    )

    with pytest.raises(SourceStateError, match="bandit_reviewed_fingerprint_mismatch"):
        _validate_bandit(report, reviewed)


@pytest.mark.parametrize(
    "returncode",
    [
        pytest.param(0, id="success-with-findings"),
        pytest.param(2, id="scanner-error-exit"),
    ],
)
def test_bandit_rejects_inconsistent_or_failed_scanner_exit(returncode: int):
    report, reviewed = _bandit_evidence()
    assert _validate_bandit(report, reviewed) is None

    with pytest.raises(SourceStateError, match="bandit_returncode_inconsistent"):
        _validate_bandit(report, reviewed, returncode=returncode)


def test_bandit_parser_rejects_duplicate_raw_json_keys():
    report, _reviewed = _bandit_evidence()
    raw = json.dumps(report, separators=(",", ":"))
    repeated = '"app/synthetic_a.py":'
    assert raw.count(repeated) == 1
    assert parse_report(raw) == report
    raw = raw.replace(repeated, '"app/synthetic_a.py":{},' + repeated)

    with pytest.raises(SourceStateError, match="duplicate_bandit_json_key"):
        parse_report(raw)


def test_bandit_cli_scans_only_authenticated_literal_files(tmp_path: Path, monkeypatch):
    selection_path, selection_sha256, repo_root = _synthetic_selection(
        tmp_path, status="reviewed"
    )
    report, _reviewed = _bandit_evidence()
    observed = []

    def fake_scan(argv, **kwargs):
        observed.append((argv, kwargs))
        return subprocess.CompletedProcess(
            args=argv, returncode=1, stdout=json.dumps(report), stderr=""
        )

    monkeypatch.setattr(security_bandit_gate, "REPO_ROOT", repo_root)
    monkeypatch.setattr(subprocess, "run", fake_scan)

    assert security_bandit_gate.main(
        ["--selection", str(selection_path), "--selection-sha256", selection_sha256]
    ) == 0
    assert observed == [
        (
            [
                sys.executable,
                "-B",
                "-m",
                "bandit",
                *SELECTED_BANDIT_PATHS,
                "-ll",
                "-ii",
                "-c",
                "pyproject.toml",
                "-f",
                "json",
                "-q",
            ],
            {
                "cwd": repo_root,
                "capture_output": True,
                "text": True,
                "check": False,
                "timeout": 120,
            },
        )
    ]


def test_bandit_cli_rejects_pending_review_before_scanner(
    tmp_path: Path, monkeypatch, capsys
):
    selection_path, selection_sha256, repo_root = _synthetic_selection(
        tmp_path, status="pending"
    )

    def forbid_scan(*_args, **_kwargs):
        raise AssertionError("pending review must reject before Bandit is launched")

    monkeypatch.setattr(security_bandit_gate, "REPO_ROOT", repo_root)
    monkeypatch.setattr(subprocess, "run", forbid_scan)

    assert security_bandit_gate.main(
        ["--selection", str(selection_path), "--selection-sha256", selection_sha256]
    ) != 0
    assert "bandit_review_pending" in capsys.readouterr().err


def test_historical_diary_cli_uses_authenticated_literal_selection(
    tmp_path: Path, monkeypatch
):
    selection_path, selection_sha256, repo_root = _synthetic_selection(
        tmp_path, status="pending"
    )
    unselected = repo_root / "docs/unselected-historical-diary.md"
    unselected.write_text("The diary was booked.\n", encoding="utf-8")

    def forbid_walk(*_args, **_kwargs):
        raise AssertionError("leakage CLI must not walk outside literal selection")

    monkeypatch.setattr(historical_diary_leakage_lint, "REPO_ROOT", repo_root)
    monkeypatch.setattr(Path, "rglob", forbid_walk)

    assert historical_diary_leakage_lint.main(
        ["--selection", str(selection_path), "--selection-sha256", selection_sha256]
    ) == 0


@pytest.mark.parametrize(
    "module",
    [
        pytest.param(security_bandit_gate, id="bandit"),
        pytest.param(historical_diary_leakage_lint, id="leakage"),
    ],
)
def test_scanner_clis_require_explicit_selection_before_observation(
    module, monkeypatch
):
    def forbid_loader(*_args, **_kwargs):
        raise AssertionError("missing selection must reject before loader")

    def forbid_scan(*_args, **_kwargs):
        raise AssertionError("missing selection must reject before subprocess")

    monkeypatch.setattr(module, "load_source_state", forbid_loader)
    monkeypatch.setattr(subprocess, "run", forbid_scan)

    with pytest.raises(SystemExit) as exc:
        module.main([])
    assert exc.value.code == 2


@pytest.mark.parametrize(
    "module,selection_value,digest_value,reason,expected_exit",
    [
        pytest.param(
            security_bandit_gate,
            "absolute",
            "not-a-sha256",
            "manifest_digest",
            2,
            id="bandit-bad-digest",
        ),
        pytest.param(
            security_bandit_gate,
            "relative\\selection.json",
            "a" * 64,
            "invalid_manifest_argument",
            2,
            id="bandit-backslash-relative-path",
        ),
        pytest.param(
            historical_diary_leakage_lint,
            "absolute",
            "not-a-sha256",
            "manifest_digest",
            1,
            id="leakage-bad-digest",
        ),
        pytest.param(
            historical_diary_leakage_lint,
            "relative\\selection.json",
            "a" * 64,
            "invalid_manifest_argument",
            1,
            id="leakage-backslash-relative-path",
        ),
    ],
)
def test_scanner_clis_reject_bad_binding_before_loader_or_scanner(
    tmp_path: Path, monkeypatch, capsys, module, selection_value, digest_value, reason,
    expected_exit
):
    import argparse

    def forbid_scan(*_args, **_kwargs):
        raise AssertionError("invalid binding must reject before subprocess")

    def forbid_file_read(*_args, **_kwargs):
        raise AssertionError("invalid binding must reject before physical file read")

    valid_path, _valid_digest, repo_root = _synthetic_selection(
        tmp_path, status="pending"
    )
    selection_path = (
        str(valid_path)
        if selection_value == "absolute"
        else selection_value
    )
    with monkeypatch.context() as guard:
        guard.setattr(module, "REPO_ROOT", repo_root)
        guard.setattr(subprocess, "run", forbid_scan)
        # Keep real parsing while preventing only parser locale-catalog discovery.
        guard.setattr(argparse, "_", lambda message: message)
        _guard_physical_observation(guard, forbid_file_read)
        with pytest.raises(
            AssertionError, match="invalid binding must reject before physical file read"
        ):
            valid_path.stat()

        result = module.main(
            ["--selection", selection_path, "--selection-sha256", digest_value]
        )

    assert result == expected_exit
    error_output = capsys.readouterr().err.lower()
    assert reason in error_output


def test_phase0_migration_has_empty_bootstrap_and_symmetric_cleanup():
    import ast

    source = (
        ROOT / "alembic/versions/d4787e8e3629_phase_0_baseline.py"
    ).read_text(encoding="utf-8")
    assert "emr4_phase0_empty_bootstrap_marker" in source
    assert "def _prepare_legacy_baseline()" in source
    assert "Phase-0 refuses incomplete or unexpected legacy tables" in source
    assert "def _is_empty_database_bootstrap()" in source

    # Directory cleanup is now a loop restricted to an owned fresh bootstrap.
    # PostgreSQL preservation behavior is covered by test_phase0_migration_preservation.
    tree = ast.parse(source)
    downgrade = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "downgrade")
    drops = [node for node in ast.walk(downgrade)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name) and node.func.value.id == "op"
             and node.func.attr == "drop_table"]
    assert len(drops) == 1
    fresh_loops = [loop for branch in ast.walk(downgrade)
                   if isinstance(branch, ast.If) and isinstance(branch.test, ast.Name)
                   and branch.test.id == "fresh"
                   for loop in branch.body if isinstance(loop, ast.For)
                   and drops[0] in list(ast.walk(loop))]
    assert len(fresh_loops) == 1
    loop = fresh_loops[0]
    assert {"mbs_directory", "snomed_directory"} <= set(ast.literal_eval(loop.iter))
    assert isinstance(loop.target, ast.Name)
    assert len(drops[0].args) == 1 and isinstance(drops[0].args[0], ast.Name)
    assert drops[0].args[0].id == loop.target.id
    assert [(kw.arg, ast.literal_eval(kw.value)) for kw in drops[0].keywords] == [("schema", "public")]
    assert "t.typtype = 'e'" in source


class _CiBIntSubclass(int):
    pass


class _CiBStrSubclass(str):
    pass


def _ci_b_valid_config(**changes):
    from scripts.verify_empty_database_migrations import MigrationConfig

    fields = {
        "host": "127.0.0.1",
        "port": 5432,
        "user": "migration_verify",
        "database_name": "emr4_migration_verify_0123456789abcdef",
        "system_identifier": "12345678901234567890",
    }
    fields.update(changes)
    return MigrationConfig(**fields)


def test_ci_b_config_accepts_explicit_literal_target_and_is_frozen():
    from dataclasses import FrozenInstanceError

    from scripts.verify_empty_database_migrations import validate_config

    config = _ci_b_valid_config()
    validate_config(config)

    assert config.host == "127.0.0.1"
    assert config.port == 5432
    assert config.user == "migration_verify"
    assert config.database_name == "emr4_migration_verify_0123456789abcdef"
    assert config.system_identifier == "12345678901234567890"
    assert config.total_seconds == 300
    assert config.cleanup_seconds == 30
    assert config.connect_timeout_seconds == 5
    assert config.statement_timeout_ms == 10000
    with pytest.raises(FrozenInstanceError):
        config.port = 5433


def test_ci_b_import_and_help_have_no_database_or_child_effects(monkeypatch):
    import argparse
    import dataclasses
    import gettext
    import importlib.util
    import types

    # Prefetch only the helper source. All later module execution is guarded.
    source_path = ROOT / "scripts/verify_empty_database_migrations.py"
    source_code = compile(source_path.read_bytes(), str(source_path), "exec")
    assert argparse and dataclasses and gettext and importlib.util
    assert types and verification_runtime
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".", 1)[0] in {"app", "psycopg2", "sqlalchemy"}:
            raise AssertionError("import or help crossed an application/database import")
        return original_import(name, *args, **kwargs)

    def forbidden_effect(*_args, **_kwargs):
        raise AssertionError("import or help caused physical observation or process effect")

    module_name = "ci_b_inert_migration_probe"
    module = types.ModuleType(module_name)
    module.__file__ = str(source_path)
    module.__package__ = "scripts"
    with monkeypatch.context() as guard:
        guard.setitem(sys.modules, module_name, module)
        guard.setattr(builtins, "__import__", guarded_import)
        guard.setattr(subprocess, "run", forbidden_effect)
        guard.setattr(subprocess, "Popen", forbidden_effect)
        guard.setattr(argparse, "_", lambda text: text)
        _guard_physical_observation(guard, forbidden_effect)
        exec(source_code, module.__dict__)
        guard.setattr(module, "verify", forbidden_effect)
        with pytest.raises(SystemExit) as exit_info:
            module.main(["--help"])

    assert exit_info.value.code == 0

class _CiBDatabaseError(Exception):
    pass


class _CiBIdentifier:
    def __init__(self, value):
        self.value = value


class _CiBComposedSQL:
    def __init__(self, template, identifiers):
        self.template = template
        self.identifiers = identifiers


class _CiBSQL:
    def __init__(self, template):
        self.template = template

    def format(self, *identifiers):
        assert all(isinstance(item, _CiBIdentifier) for item in identifiers)
        return _CiBComposedSQL(self.template, tuple(item.value for item in identifiers))


class _CiBClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class _CiBCursor:
    def __init__(self, owner, connection):
        self.owner = owner
        self.connection = connection
        self.one = None
        self.all_rows = []

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        return False

    def execute(self, query, params=None):
        self.one, self.all_rows = self.owner.execute(self.connection, query, params)

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.all_rows


class _CiBConnection:
    def __init__(self, owner, kwargs, admin_ordinal):
        import re

        self.owner = owner
        self.kwargs = kwargs
        option_match = re.fullmatch(
            r"-c statement_timeout=([1-9][0-9]*) -c lock_timeout=\1",
            kwargs["options"],
        )
        assert option_match is not None, "unbounded connection options"
        self.statement_limit_ms = int(option_match.group(1))
        self.admin_ordinal = admin_ordinal
        self.autocommit = False
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.close()
        return False

    def cursor(self):
        return _CiBCursor(self.owner, self)

    def close(self):
        if not self.closed:
            self.closed = True
            self.owner.events.append(("close", self.kwargs["dbname"]))


class _CiBDatabase:
    IDENTITY_SQL = (
        "SELECT (SELECT system_identifier::text FROM pg_control_system()), "
        "current_user, (SELECT oid FROM pg_roles WHERE rolname = current_user), "
        "inet_server_addr()::text, inet_server_port()"
    )
    LOOKUP_SQL = "SELECT oid, datdba FROM pg_database WHERE datname = %s"
    TABLES_SQL = (
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
        "AND tablename <> 'alembic_version' ORDER BY tablename"
    )
    LIMIT_SQL = (
        "SELECT set_config('statement_timeout', %s, false), "
        "set_config('lock_timeout', %s, false)"
    )
    CREATE_SQL = "CREATE DATABASE {} WITH OWNER {} TEMPLATE template0"
    DROP_SQL = "DROP DATABASE {}"

    def __init__(self, config, *, scenario=None):
        self.config = config
        self.scenario = scenario or {}
        self.events = []
        self.connections = []
        self.clock = _CiBClock()
        self.role_oid = 71
        self.database_oid = 901
        self.admin_connections = 0
        self.lookup_calls = 0
        self.table_calls = 0
        self.limit_calls = 0
        self.cleanup_limit_calls = 0
        self.child_calls = 0
        self.database_exists = bool(self.scenario.get("preexisting"))

    def _advance_after(self, event):
        seconds = self.scenario.get("advance_after", {}).get(event, 0)
        if callable(seconds):
            seconds = seconds(self)
        self.clock.advance(seconds)

    def _emit_output(self, phase):
        self.events.append(("output_marker", phase))
        print(f"CI_B_PYTHON_{phase}_MARKER")
        os.write(1, f"CI_B_FD1_{phase}_MARKER\n".encode("ascii"))
        os.write(2, f"CI_B_FD2_{phase}_MARKER\n".encode("ascii"))

    def connect(self, **kwargs):
        dbname = kwargs.get("dbname")
        assert dbname in {"postgres", self.config.database_name}
        if dbname == "postgres":
            self.admin_connections += 1
            admin_ordinal = self.admin_connections
        else:
            admin_ordinal = 0
        if self.scenario.get("connect_error_at") == f"{dbname}:{admin_ordinal}":
            self.events.append(("connect_error", dbname, kwargs.copy()))
            raise _CiBDatabaseError("password=SHOULD_NOT_LEAK connect")
        connection = _CiBConnection(self, kwargs, admin_ordinal)
        self.connections.append(connection)
        self.events.append(("connect", dbname, kwargs.copy()))
        self._advance_after(f"connect:{dbname}:{admin_ordinal}")
        return connection

    def execute(self, connection, query, params):
        dbname = connection.kwargs["dbname"]
        phase_deadline = (
            self.config.total_seconds
            if connection.admin_ordinal >= 2
            else self.config.total_seconds - self.config.cleanup_seconds
        )
        remaining_ms = int((phase_deadline - self.clock.now) * 1000)
        if connection.statement_limit_ms > remaining_ms:
            self.events.append((
                "unsafe_sql", dbname, connection.statement_limit_ms, remaining_ms
            ))
        if isinstance(query, _CiBComposedSQL):
            if query.template == self.CREATE_SQL:
                assert query.identifiers == (self.config.database_name, self.config.user)
                assert params is None
                self.events.append(("create", query.identifiers))
                self.database_exists = True
                self._advance_after("create")
                if self.scenario.get("create_uncertain"):
                    raise _CiBDatabaseError("password=SHOULD_NOT_LEAK create")
                return None, []
            if query.template == self.DROP_SQL:
                assert query.identifiers == (self.config.database_name,)
                assert params is None
                self.events.append(("drop", query.identifiers))
                self._advance_after("drop")
                if self.scenario.get("drop_uncertain"):
                    raise _CiBDatabaseError("password=SHOULD_NOT_LEAK drop")
                self.database_exists = bool(self.scenario.get("drop_readback_present"))
                return None, []
            raise AssertionError(f"unknown composed SQL: {query.template!r}")

        assert isinstance(query, str), "unknown SQL object"
        statement = " ".join(query.split())
        if statement == self.LIMIT_SQL:
            assert isinstance(params, tuple) and len(params) == 2
            assert all(isinstance(value, str) and value.isdecimal() for value in params)
            if int(params[0]) > remaining_ms:
                self.events.append(("unsafe_new_limit", dbname, params[0]))
            self.limit_calls += 1
            connection.statement_limit_ms = int(params[0])
            if connection.admin_ordinal >= 2:
                self.cleanup_limit_calls += 1
            self.events.append(("set_config", dbname, params))
            self._advance_after(f"limit:{self.limit_calls}")
            if self.lookup_calls == 1 and not self.database_exists:
                self._advance_after("limit_after_absence_lookup")
            self._advance_after(f"cleanup_limit:{self.cleanup_limit_calls}")
            return (params[0], params[1]), []
        if statement == self.IDENTITY_SQL:
            assert dbname in {"postgres", self.config.database_name} and params is None
            if dbname == self.config.database_name:
                phase = "target"
            else:
                phase = "cleanup" if connection.admin_ordinal >= 2 else "precreate"
            row = self.scenario.get(f"{phase}_identity") or (
                self.config.system_identifier,
                self.config.user,
                self.role_oid,
                self.config.host,
                self.config.port,
            )
            self.events.append(("identity", phase, row))
            if phase == "precreate" and self.scenario.get("emit_output"):
                self._emit_output("DB")
            self._advance_after(f"identity:{phase}")
            if self.scenario.get("identity_error") == phase:
                raise _CiBDatabaseError("password=SHOULD_NOT_LEAK identity")
            return row, []
        if statement == self.LOOKUP_SQL:
            assert dbname == "postgres"
            assert params == (self.config.database_name,)
            self.lookup_calls += 1
            default = (
                None
                if (self.lookup_calls == 1 and not self.database_exists)
                or not self.database_exists
                else (self.database_oid, self.role_oid)
            )
            row = self.scenario.get("lookup_rows", {}).get(self.lookup_calls, default)
            self.events.append(("lookup", self.lookup_calls, params, row))
            self._advance_after(f"lookup:{self.lookup_calls}")
            if self.scenario.get("lookup_error") == self.lookup_calls:
                raise _CiBDatabaseError("password=SHOULD_NOT_LEAK lookup")
            return row, []
        if statement == self.TABLES_SQL:
            assert dbname == self.config.database_name and params is None
            self.table_calls += 1
            rows = self.scenario.get("table_rows", {}).get(self.table_calls, [])
            self.events.append(("tables", self.table_calls, rows))
            self._advance_after(f"tables:{self.table_calls}")
            if self.scenario.get("tables_error") == self.table_calls:
                raise _CiBDatabaseError("password=SHOULD_NOT_LEAK tables")
            return None, rows
        raise AssertionError(f"unknown SQL: {statement!r}")

    def run_child(self, argv, **kwargs):
        self.child_calls += 1
        self.events.append(("child", self.child_calls, list(argv), kwargs.copy()))
        if self.child_calls == 1 and self.scenario.get("emit_output"):
            self._emit_output("CHILD")
        self._advance_after(f"child:{self.child_calls}")
        if self.scenario.get("child_timeout") == self.child_calls:
            raise subprocess.TimeoutExpired(cmd=argv, timeout=kwargs["timeout"])
        code = self.scenario.get("child_codes", {}).get(self.child_calls, 0)
        return subprocess.CompletedProcess(args=argv, returncode=code)

    def install(self, monkeypatch, migrations):
        from types import ModuleType, SimpleNamespace

        fake = ModuleType("psycopg2")
        fake.Error = _CiBDatabaseError
        fake.connect = self.connect
        fake.sql = SimpleNamespace(SQL=_CiBSQL, Identifier=_CiBIdentifier)
        monkeypatch.setitem(sys.modules, "psycopg2", fake)
        monkeypatch.setitem(sys.modules, "psycopg2.sql", fake.sql)
        monkeypatch.setattr(subprocess, "run", self.run_child)
        monkeypatch.setattr(
            migrations, "time", SimpleNamespace(monotonic=self.clock.monotonic)
        )
        monkeypatch.setattr(
            os, "environ", {"PATH": "synthetic", "DATABASE_URL": "ambient://wrong"}
        )

def _ci_b_url_parts(url):
    from urllib.parse import parse_qsl, urlsplit

    parsed = urlsplit(url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    return parsed, pairs, dict(pairs)

def _ci_b_result_fields(result):
    return (
        result.primary_exit_code,
        result.cleanup_exit_code,
        result.database_created,
        result.database_removed,
        result.failure_reason,
        result.cleanup_reason,
    )


@pytest.mark.parametrize(
    "field,value,reason",
    [
        pytest.param("host", "localhost", "invalid_host", id="hostname"),
        pytest.param("host", "127.0.0.2", "invalid_host", id="other-loopback"),
        pytest.param("host", "postgresql://host", "invalid_host", id="url-host"),
        pytest.param("host", 123, "invalid_host", id="host-type"),
        pytest.param("host", _CiBStrSubclass("127.0.0.1"), "invalid_host", id="host-subclass"),
        pytest.param("port", 0, "invalid_port", id="port-zero"),
        pytest.param("port", 65536, "invalid_port", id="port-overflow"),
        pytest.param("port", True, "invalid_port", id="port-bool"),
        pytest.param("port", "5432", "invalid_port", id="port-coercion"),
        pytest.param("port", _CiBIntSubclass(5432), "invalid_port", id="port-subclass"),
        pytest.param("user", "Bad-Role", "invalid_user", id="role-syntax"),
        pytest.param("user", "-option", "invalid_user", id="role-option"),
        pytest.param("user", _CiBStrSubclass("migration_verify"), "invalid_user", id="role-subclass"),
        pytest.param("database_name", "other_database", "invalid_database_name", id="foreign-name"),
        pytest.param("database_name", "emr4_migration_verify_ABCDEF0123456789", "invalid_database_name", id="uppercase-name"),
        pytest.param("system_identifier", "12; DROP", "invalid_system_identifier", id="system-id-syntax"),
        pytest.param("system_identifier", 123, "invalid_system_identifier", id="system-id-type"),
        pytest.param("system_identifier", _CiBStrSubclass("12345678901234567890"), "invalid_system_identifier", id="system-id-subclass"),
        pytest.param("total_seconds", 0, "invalid_total_seconds", id="total-zero"),
        pytest.param("total_seconds", 601, "invalid_total_seconds", id="total-over-cap"),
        pytest.param("total_seconds", 300.0, "invalid_total_seconds", id="total-float"),
        pytest.param("total_seconds", float("nan"), "invalid_total_seconds", id="total-nan"),
        pytest.param("total_seconds", _CiBIntSubclass(300), "invalid_total_seconds", id="total-subclass"),
        pytest.param("cleanup_seconds", 4, "invalid_cleanup_seconds", id="cleanup-under-five"),
        pytest.param("cleanup_seconds", 300, "invalid_cleanup_seconds", id="cleanup-not-less"),
        pytest.param("cleanup_seconds", 30.0, "invalid_cleanup_seconds", id="cleanup-float"),
        pytest.param("cleanup_seconds", _CiBIntSubclass(30), "invalid_cleanup_seconds", id="cleanup-subclass"),
        pytest.param("connect_timeout_seconds", 0, "invalid_connect_timeout_seconds", id="connect-zero"),
        pytest.param("connect_timeout_seconds", 11, "invalid_connect_timeout_seconds", id="connect-over-ten"),
        pytest.param("connect_timeout_seconds", True, "invalid_connect_timeout_seconds", id="connect-bool"),
        pytest.param("connect_timeout_seconds", 5.0, "invalid_connect_timeout_seconds", id="connect-float"),
        pytest.param("connect_timeout_seconds", _CiBIntSubclass(5), "invalid_connect_timeout_seconds", id="connect-subclass"),
        pytest.param("statement_timeout_ms", 0, "invalid_statement_timeout_ms", id="statement-zero"),
        pytest.param("statement_timeout_ms", 10001, "invalid_statement_timeout_ms", id="statement-over-cap"),
        pytest.param("statement_timeout_ms", "10000", "invalid_statement_timeout_ms", id="statement-coercion"),
        pytest.param("statement_timeout_ms", float("inf"), "invalid_statement_timeout_ms", id="statement-infinite"),
        pytest.param("statement_timeout_ms", _CiBIntSubclass(10000), "invalid_statement_timeout_ms", id="statement-subclass"),
    ],
)
def test_ci_b_invalid_config_has_exact_reason_without_runtime_effect(
    field, value, reason, monkeypatch
):
    from scripts import verify_empty_database_migrations as migrations

    valid = _ci_b_valid_config()
    assert migrations.validate_config(valid) is None
    invalid = _ci_b_valid_config(**{field: value})
    with pytest.raises(ValueError, match=f"^{reason}$"):
        migrations.validate_config(invalid)

    original_import = builtins.__import__

    def forbid_database_import(name, *args, **kwargs):
        if name.split(".", 1)[0] == "psycopg2":
            raise AssertionError("invalid config imported database package")
        return original_import(name, *args, **kwargs)

    def forbid_child(*_args, **_kwargs):
        raise AssertionError("invalid config launched a child")

    with monkeypatch.context() as guard:
        guard.setattr(builtins, "__import__", forbid_database_import)
        guard.setattr(subprocess, "run", forbid_child)
        result = migrations.verify(invalid)

    assert _ci_b_result_fields(result) == (2, 0, False, False, reason, None)
    assert result.exit_code == 2


def test_ci_b_rejects_wrong_config_object_before_database_import(monkeypatch):
    from scripts import verify_empty_database_migrations as migrations

    original_import = builtins.__import__

    def forbid_database_import(name, *args, **kwargs):
        if name.split(".", 1)[0] == "psycopg2":
            raise AssertionError("wrong config type imported database package")
        return original_import(name, *args, **kwargs)

    with pytest.raises(ValueError, match="^invalid_config_type$"):
        migrations.validate_config(object())
    with monkeypatch.context() as guard:
        guard.setattr(builtins, "__import__", forbid_database_import)
        result = migrations.verify(object())
    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "invalid_config_type", None
    )


def test_ci_b_connect_cap_must_fit_cleanup_reserve_before_runtime(monkeypatch):
    from scripts import verify_empty_database_migrations as migrations

    assert migrations.validate_config(_ci_b_valid_config()) is None
    invalid = _ci_b_valid_config(cleanup_seconds=5, connect_timeout_seconds=6)
    with pytest.raises(ValueError, match="^invalid_connect_timeout_seconds$"):
        migrations.validate_config(invalid)

    original_import = builtins.__import__

    def forbid_database_import(name, *args, **kwargs):
        if name.split(".", 1)[0] == "psycopg2":
            raise AssertionError("invalid coupled bound imported database package")
        return original_import(name, *args, **kwargs)

    def forbid_child(*_args, **_kwargs):
        raise AssertionError("invalid coupled bound launched child")

    with monkeypatch.context() as guard:
        guard.setattr(builtins, "__import__", forbid_database_import)
        guard.setattr(subprocess, "run", forbid_child)
        result = migrations.verify(invalid)

    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "invalid_connect_timeout_seconds", None
    )
    assert result.exit_code == 2


def test_ci_b_ambient_pg_override_fails_before_database_import(monkeypatch):
    from scripts import verify_empty_database_migrations as migrations

    config = _ci_b_valid_config()
    assert migrations.validate_config(config) is None
    original_import = builtins.__import__

    def forbid_database_import(name, *args, **kwargs):
        if name.split(".", 1)[0] == "psycopg2":
            raise AssertionError("PG override imported database package")
        return original_import(name, *args, **kwargs)

    def forbid_child(*_args, **_kwargs):
        raise AssertionError("PG override launched a child")

    with monkeypatch.context() as guard:
        guard.setattr(os, "environ", {"pGhOsT": "other", "PATH": "synthetic"})
        guard.setattr(builtins, "__import__", forbid_database_import)
        guard.setattr(subprocess, "run", forbid_child)
        result = migrations.verify(config)

    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "ambient_pg_override", None
    )

def _ci_b_verify(monkeypatch, *, scenario=None, config_changes=None):
    from scripts import verify_empty_database_migrations as migrations

    config = _ci_b_valid_config(**(config_changes or {}))
    assert migrations.validate_config(config) is None
    fake = _CiBGuardedDatabase(config, scenario=scenario)
    with monkeypatch.context() as guard:
        fake.install(guard, migrations)
        result = migrations.verify(config)
    assert fake.violations == []
    assert not any(
        event[0] in {"unsafe_sql", "unsafe_new_limit"}
        for event in fake.events
    )
    assert all(connection.closed and connection.autocommit for connection in fake.connections)
    return config, result, fake


def _ci_b_semantic_events(fake):
    return [event for event in fake.events if event[0] not in {
        "connect", "close", "set_config"
    }]


def test_ci_b_full_lifecycle_has_bound_endpoint_order_and_owned_cleanup(monkeypatch):
    config, result, fake = _ci_b_verify(monkeypatch)

    assert _ci_b_result_fields(result) == (0, 0, True, True, None, None)
    assert result.exit_code == 0
    assert [(event[0], event[1] if event[0] in {"tables", "child", "identity"} else None)
            for event in _ci_b_semantic_events(fake)] == [
        ("identity", "precreate"),
        ("lookup", None),
        ("create", None),
        ("lookup", None),
        ("identity", "target"),
        ("tables", 1),
        ("child", 1),
        ("child", 2),
        ("child", 3),
        ("identity", "target"),
        ("tables", 2),
        ("child", 4),
        ("child", 5),
        ("identity", "cleanup"),
        ("lookup", None),
        ("drop", None),
        ("lookup", None),
    ]
    assert fake.admin_connections >= 2
    assert sum(event[0] == "create" for event in fake.events) == 1
    assert sum(event[0] == "drop" for event in fake.events) == 1
    assert all(connection.closed and connection.autocommit for connection in fake.connections)

    for event in fake.events:
        if event[0] != "connect":
            continue
        database, kwargs = event[1:]
        assert database in {"postgres", config.database_name}
        assert kwargs["host"] == kwargs["hostaddr"] == config.host
        assert kwargs["port"] == config.port
        assert kwargs["user"] == config.user
        assert kwargs["dbname"] == database
        assert isinstance(kwargs["connect_timeout"], int)
        assert 1 <= kwargs["connect_timeout"] <= config.connect_timeout_seconds
        assert kwargs["sslmode"] == kwargs["gssencmode"] == "disable"
        assert kwargs["passfile"] == os.devnull
        assert "statement_timeout" in kwargs["options"]
        assert "lock_timeout" in kwargs["options"]
        assert not {"password", "service", "dsn"}.intersection(kwargs)

    child_events = [event for event in fake.events if event[0] == "child"]
    expected_arguments = [
        ["upgrade", "head"],
        ["check"],
        ["downgrade", "base"],
        ["upgrade", "head"],
        ["check"],
    ]
    for event, arguments in zip(child_events, expected_arguments, strict=True):
        argv, kwargs = event[2:]
        assert argv == [
            sys.executable, "-I", "-B", "-m", "alembic", "-c",
            str(ROOT / "alembic.ini"), *arguments,
        ]
        assert kwargs["cwd"] == ROOT
        assert kwargs["check"] is False
        assert isinstance(kwargs["timeout"], int)
        assert 1 <= kwargs["timeout"] <= config.total_seconds - config.cleanup_seconds
        parsed, pairs, query = _ci_b_url_parts(kwargs["env"]["DATABASE_URL"])
        assert parsed.scheme == "postgresql+psycopg2"
        assert parsed.hostname == config.host
        assert parsed.port == config.port
        assert parsed.username == config.user
        assert parsed.password is None
        assert parsed.path == "/" + config.database_name
        assert parsed.fragment == ""
        assert len(pairs) == len(query) == 6
        assert set(query) == {
            "hostaddr", "connect_timeout", "sslmode", "gssencmode",
            "passfile", "options",
        }
        assert query["hostaddr"] == config.host
        assert query["sslmode"] == query["gssencmode"] == "disable"
        assert query["passfile"] == os.devnull
        assert "ambient://wrong" not in kwargs["env"]["DATABASE_URL"]
        assert not any(key.upper().startswith("PG") for key in kwargs["env"])

    limit_events = [event for event in fake.events if event[0] == "set_config"]
    assert len(limit_events) >= 10
    assert all(
        0 < int(value) <= config.statement_timeout_ms
        for event in limit_events for value in event[2]
    )

@pytest.mark.parametrize(
    "scenario,reason",
    [
        pytest.param(
            {"precreate_identity": ("999", "migration_verify", 71, "127.0.0.1", 5432)},
            "primary_server_identity_mismatch",
            id="wrong-server",
        ),
        pytest.param(
            {"precreate_identity": ("12345678901234567890", "other_role", 71, "127.0.0.1", 5432)},
            "primary_role_mismatch",
            id="wrong-role",
        ),
        pytest.param(
            {"precreate_identity": ("12345678901234567890", "migration_verify", 71, "127.0.0.2", 5432)},
            "primary_endpoint_mismatch",
            id="wrong-server-address",
        ),
        pytest.param(
            {"precreate_identity": ("12345678901234567890", "migration_verify", 71, "127.0.0.1", 5433)},
            "primary_endpoint_mismatch",
            id="wrong-server-port",
        ),
        pytest.param(
            {"lookup_rows": {1: (901, 71)}},
            "database_already_exists",
            id="existing-target-name",
        ),
        pytest.param(
            {"connect_error_at": "postgres:1"},
            "admin_precondition_failed",
            id="admin-connect-error",
        ),
        pytest.param(
            {"lookup_error": 1},
            "admin_precondition_failed",
            id="precreate-absence-lookup-error",
        ),
    ],
)
def test_ci_b_precreate_refusal_has_no_create_drop_or_children(
    monkeypatch, capsys, scenario, reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert _ci_b_result_fields(baseline) == (0, 0, True, True, None, None)

    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (2, 0, False, False, reason, None)
    assert result.exit_code == 2
    assert not any(event[0] in {"create", "drop", "child"} for event in fake.events)
    assert all(connection.closed for connection in fake.connections)
    if "connect_error_at" in scenario:
        assert any(event[0] == "connect_error" for event in fake.events)
    if "lookup_error" in scenario:
        assert any(event[0] == "lookup" and event[1] == 1 for event in fake.events)
    captured = capsys.readouterr()
    assert "SHOULD_NOT_LEAK" not in captured.out + captured.err
    assert "SHOULD_NOT_LEAK" not in repr(_ci_b_result_fields(result))


@pytest.mark.parametrize(
    "scenario,primary_reason,cleanup_reason,created",
    [
        pytest.param(
            {"create_uncertain": True},
            "create_acknowledgement_uncertain",
            "create_acknowledgement_uncertain",
            False,
            id="create-acknowledgement-lost",
        ),
        pytest.param(
            {"lookup_rows": {2: None}},
            "created_database_unconfirmed",
            "ownership_unconfirmed",
            True,
            id="created-oid-missing",
        ),
        pytest.param(
            {"lookup_rows": {2: (901, 72)}},
            "created_database_unconfirmed",
            "ownership_unconfirmed",
            True,
            id="created-owner-wrong",
        ),
    ],
)
def test_ci_b_unproven_creation_never_guesses_drop(
    monkeypatch, capsys, scenario, primary_reason, cleanup_reason, created
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (
        2, 3, created, False, primary_reason, cleanup_reason
    )
    assert result.exit_code == 2
    assert sum(event[0] == "create" for event in fake.events) == 1
    assert not any(event[0] in {"drop", "child"} for event in fake.events)
    captured = capsys.readouterr()
    assert "SHOULD_NOT_LEAK" not in captured.out + captured.err
    assert "SHOULD_NOT_LEAK" not in repr(_ci_b_result_fields(result))


@pytest.mark.parametrize(
    "table_call,expected_children,reason",
    [
        pytest.param(1, 0, "initial_public_user_tables_present", id="initial-tables"),
        pytest.param(2, 3, "downgrade_public_user_tables_present", id="after-downgrade"),
    ],
)
def test_ci_b_public_user_tables_stop_primary_and_cleanup_owned_database(
    monkeypatch, table_call, expected_children, reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    scenario = {"table_rows": {table_call: [("unexpected_table",)]}}
    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (2, 0, True, True, reason, None)
    assert fake.table_calls == table_call
    assert fake.child_calls == expected_children
    assert sum(event[0] == "create" for event in fake.events) == 1
    assert sum(event[0] == "drop" for event in fake.events) == 1


@pytest.mark.parametrize(
    "child_number,reason",
    [
        pytest.param(1, "upgrade_failed", id="upgrade"),
        pytest.param(2, "head_check_failed", id="head-check"),
        pytest.param(3, "downgrade_failed", id="downgrade"),
        pytest.param(4, "reupgrade_failed", id="reupgrade"),
        pytest.param(5, "reupgrade_check_failed", id="reupgrade-check"),
    ],
)
def test_ci_b_child_failure_retains_code_and_stops_remaining_children(
    monkeypatch, child_number, reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"child_codes": {child_number: 9}}
    )
    assert _ci_b_result_fields(result) == (9, 0, True, True, reason, None)
    assert result.exit_code == 9
    assert fake.child_calls == child_number
    assert sum(event[0] == "drop" for event in fake.events) == 1


@pytest.mark.parametrize(
    "scenario,expected_code",
    [
        pytest.param({"child_timeout": 2}, 124, id="timeout-124"),
        pytest.param({"child_codes": {2: -9}}, -9, id="negative-signal-code"),
    ],
)
def test_ci_b_child_special_exit_codes_survive_cleanup(
    monkeypatch, scenario, expected_code
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (
        expected_code, 0, True, True, "head_check_failed", None
    )
    assert result.exit_code == expected_code
    assert fake.child_calls == 2
    assert sum(event[0] == "drop" for event in fake.events) == 1


@pytest.mark.parametrize(
    "scenario,primary_code,primary_reason",
    [
        pytest.param({}, 0, None, id="cleanup-only"),
        pytest.param(
            {"child_codes": {1: 9}}, 9, "upgrade_failed", id="primary-and-cleanup"
        ),
    ],
)
def test_ci_b_drop_uncertainty_is_reported_without_retry(
    monkeypatch, capsys, scenario, primary_code, primary_reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    scenario = {**scenario, "drop_uncertain": True}
    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (
        primary_code, 3, True, False, primary_reason,
        "drop_acknowledgement_uncertain",
    )
    assert result.exit_code == (primary_code or 3)
    assert sum(event[0] == "drop" for event in fake.events) == 1
    assert sum(event[0] == "create" for event in fake.events) == 1
    captured = capsys.readouterr()
    assert "SHOULD_NOT_LEAK" not in captured.out + captured.err
    assert "SHOULD_NOT_LEAK" not in repr(_ci_b_result_fields(result))

@pytest.mark.parametrize(
    "scenario,reason",
    [
        pytest.param(
            {"cleanup_identity": ("999", "migration_verify", 71, "127.0.0.1", 5432)},
            "cleanup_server_identity_mismatch",
            id="server-replaced",
        ),
        pytest.param(
            {"cleanup_identity": ("12345678901234567890", "other_role", 71, "127.0.0.1", 5432)},
            "cleanup_role_mismatch",
            id="role-replaced",
        ),
        pytest.param(
            {"cleanup_identity": ("12345678901234567890", "migration_verify", 72, "127.0.0.1", 5432)},
            "cleanup_role_oid_mismatch",
            id="same-name-role-oid-replaced",
        ),
        pytest.param(
            {"cleanup_identity": ("12345678901234567890", "migration_verify", 71, "127.0.0.2", 5432)},
            "cleanup_endpoint_mismatch",
            id="address-replaced",
        ),
        pytest.param(
            {"cleanup_identity": ("12345678901234567890", "migration_verify", 71, "127.0.0.1", 5433)},
            "cleanup_endpoint_mismatch",
            id="port-replaced",
        ),
        pytest.param(
            {"lookup_rows": {3: (902, 71)}},
            "cleanup_database_identity_mismatch",
            id="database-oid-replaced",
        ),
        pytest.param(
            {"lookup_rows": {3: (901, 72)}},
            "cleanup_database_identity_mismatch",
            id="database-owner-replaced",
        ),
    ],
)
def test_ci_b_cleanup_requires_same_server_role_oid_and_database_owner(
    monkeypatch, scenario, reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(monkeypatch, scenario=scenario)
    assert _ci_b_result_fields(result) == (0, 3, True, False, None, reason)
    assert result.exit_code == 3
    assert fake.child_calls == 5
    assert fake.admin_connections >= 2
    assert not any(event[0] == "drop" for event in fake.events)
    assert all(connection.closed for connection in fake.connections)


def test_ci_b_drop_acknowledgement_needs_absence_readback(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"drop_readback_present": True}
    )
    assert _ci_b_result_fields(result) == (
        0, 3, True, False, None, "cleanup_database_still_present"
    )
    assert result.exit_code == 3
    assert sum(event[0] == "drop" for event in fake.events) == 1
    assert any(event[0] == "lookup" and event[1] == 4 for event in fake.events)

def test_ci_b_cleanup_absence_readback_error_preserves_uncertainty(
    monkeypatch, capsys
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"lookup_error": 4}
    )
    assert _ci_b_result_fields(result) == (
        0, 3, True, False, None, "cleanup_absence_unconfirmed"
    )
    assert result.exit_code == 3
    assert any(event[0] == "lookup" and event[1] == 4 for event in fake.events)
    assert sum(event[0] == "drop" for event in fake.events) == 1
    assert sum(event[0] == "create" for event in fake.events) == 1
    captured = capsys.readouterr()
    assert "SHOULD_NOT_LEAK" not in captured.out + captured.err
    assert "password=" not in captured.out + captured.err
    assert "SHOULD_NOT_LEAK" not in repr(_ci_b_result_fields(result))

def test_ci_b_primary_cutoff_stops_children_but_preserves_cleanup_reserve(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"advance_after": {"child:1": 271}}
    )
    assert _ci_b_result_fields(result) == (
        2, 0, True, True, "primary_deadline_exhausted", None
    )
    assert fake.child_calls == 1
    assert sum(event[0] == "drop" for event in fake.events) == 1


def test_ci_b_total_deadline_exhaustion_leaves_cleanup_unresolved(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"advance_after": {"child:1": 301}}
    )
    assert _ci_b_result_fields(result) == (
        2, 3, True, False,
        "primary_deadline_exhausted", "cleanup_deadline_exhausted",
    )
    assert fake.child_calls == 1
    assert not any(event[0] == "drop" for event in fake.events)


def test_ci_b_deadline_recomputed_after_set_config_before_create(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"advance_after": {"limit_after_absence_lookup": 271}}
    )
    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "primary_deadline_exhausted", None
    )
    assert fake.limit_calls == 3
    assert not any(event[0] in {"create", "child", "drop"} for event in fake.events)


def test_ci_b_cleanup_deadline_before_drop_forbids_drop(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"advance_after": {"lookup:3": 301}}
    )
    assert _ci_b_result_fields(result) == (
        0, 3, True, False, None, "cleanup_deadline_exhausted"
    )
    assert any(event[0] == "lookup" and event[1] == 3 for event in fake.events)
    assert not any(event[0] == "drop" for event in fake.events)


def test_ci_b_connection_one_second_cap_refuses_before_connect(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, config_changes={"connect_timeout_seconds": 1}
    )
    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "primary_deadline_exhausted", None
    )
    assert not any(event[0] in {"connect", "create", "child"} for event in fake.events)


def test_ci_b_child_timeout_decreases_after_elapsed_primary_time(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    config, result, fake = _ci_b_verify(
        monkeypatch,
        scenario={"advance_after": {"child:1": 8.25}},
        config_changes={"total_seconds": 30, "cleanup_seconds": 10},
    )
    assert _ci_b_result_fields(result) == (0, 0, True, True, None, None)
    children = [event for event in fake.events if event[0] == "child"]
    assert len(children) == 5
    first_timeout = children[0][3]["timeout"]
    second_timeout = children[1][3]["timeout"]
    assert isinstance(first_timeout, int) and isinstance(second_timeout, int)
    assert 1 <= second_timeout < first_timeout <= (
        config.total_seconds - config.cleanup_seconds
    )

@pytest.mark.parametrize(
    "argv,marker",
    [
        pytest.param([], "", id="missing-required-binding"),
        pytest.param(
            ["--host", "127.0.0.1", "--port", "SECRET_PORT_TOKEN",
             "--user", "migration_verify", "--database-name",
             "emr4_migration_verify_0123456789abcdef", "--system-identifier",
             "12345678901234567890"],
            "SECRET_PORT_TOKEN",
            id="nonnumeric-port-sanitized",
        ),
        pytest.param(
            ["--host", "127.0.0.1", "--port", "5432",
             "--user", "migration_verify", "--database-name",
             "emr4_migration_verify_0123456789abcdef", "--system-identifier",
             "12345678901234567890", "--secret-option=SECRET_UNKNOWN_TOKEN"],
            "SECRET_UNKNOWN_TOKEN",
            id="unknown-option-sanitized",
        ),
    ],
)
def test_ci_b_cli_bad_arguments_reject_without_effect_or_raw_marker(
    monkeypatch, capsys, argv, marker
):
    from scripts import verify_empty_database_migrations as migrations

    original_import = builtins.__import__

    def forbid_database_import(name, *args, **kwargs):
        if name.split(".", 1)[0] == "psycopg2":
            raise AssertionError("bad CLI arguments imported database package")
        return original_import(name, *args, **kwargs)

    def forbid_child(*_args, **_kwargs):
        raise AssertionError("bad CLI arguments launched child")

    with monkeypatch.context() as guard:
        guard.setattr(builtins, "__import__", forbid_database_import)
        guard.setattr(subprocess, "run", forbid_child)
        with pytest.raises(SystemExit) as exit_info:
            migrations.main(argv)

    assert exit_info.value.code == 2
    output = capsys.readouterr()
    assert "invalid_cli_arguments" in output.err
    if marker:
        assert marker not in output.out + output.err


def test_ci_b_cli_valid_binding_reports_only_structured_outcome(
    monkeypatch, capfd
):
    from scripts import verify_empty_database_migrations as migrations

    config = _ci_b_valid_config(
        total_seconds=40,
        cleanup_seconds=10,
        connect_timeout_seconds=3,
        statement_timeout_ms=2500,
    )
    fake = _CiBGuardedDatabase(config, scenario={"emit_output": True})
    argv = [
        "--host", config.host,
        "--port", str(config.port),
        "--user", config.user,
        "--database-name", config.database_name,
        "--system-identifier", config.system_identifier,
        "--total-seconds", str(config.total_seconds),
        "--cleanup-seconds", str(config.cleanup_seconds),
        "--connect-timeout-seconds", str(config.connect_timeout_seconds),
        "--statement-timeout-ms", str(config.statement_timeout_ms),
    ]
    with monkeypatch.context() as guard:
        fake.install(guard, migrations)
        exit_code = migrations.main(argv)

    assert exit_code == 0
    captured = capfd.readouterr()
    assert "CI_B_" not in captured.out + captured.err
    assert captured.err == ""
    report = json.loads(captured.out)
    assert report == {
        "primary_exit_code": 0,
        "cleanup_exit_code": 0,
        "database_created": True,
        "database_removed": True,
        "failure_reason": None,
        "cleanup_reason": None,
        "exit_code": 0,
    }
    assert fake.child_calls == 5
    assert sum(event[0] == "drop" for event in fake.events) == 1
    assert [event[1] for event in fake.events if event[0] == "output_marker"] == [
        "DB", "CHILD",
    ]
    assert fake.violations == []
    assert all(connection.closed and connection.autocommit for connection in fake.connections)
    assert "CI_B_" not in repr(report)

    print("CI_B_AFTER_PYTHON_MARKER")
    os.write(1, b"CI_B_AFTER_FD1_MARKER\n")
    os.write(2, b"CI_B_AFTER_FD2_MARKER\n")
    restored = capfd.readouterr()
    assert "CI_B_AFTER_PYTHON_MARKER" in restored.out
    assert "CI_B_AFTER_FD1_MARKER" in restored.out
    assert "CI_B_AFTER_FD2_MARKER" in restored.err

def test_ci_b_cli_accepts_python_stdout_capture_and_suppresses_fd_output(
    monkeypatch, capfd
):
    import contextlib

    from scripts import verify_empty_database_migrations as migrations

    config = _ci_b_valid_config()
    fake = _CiBGuardedDatabase(config, scenario={"emit_output": True})
    argv = [
        "--host", config.host,
        "--port", str(config.port),
        "--user", config.user,
        "--database-name", config.database_name,
        "--system-identifier", config.system_identifier,
    ]
    python_stdout = io.StringIO()
    with monkeypatch.context() as guard:
        fake.install(guard, migrations)
        with contextlib.redirect_stdout(python_stdout):
            exit_code = migrations.main(argv)

    captured = capfd.readouterr()
    combined_stdout = python_stdout.getvalue() + captured.out
    assert exit_code == 0
    assert "CI_B_" not in combined_stdout + captured.err
    assert captured.err == ""
    assert json.loads(combined_stdout) == {
        "primary_exit_code": 0,
        "cleanup_exit_code": 0,
        "database_created": True,
        "database_removed": True,
        "failure_reason": None,
        "cleanup_reason": None,
        "exit_code": 0,
    }
    assert fake.child_calls == 5
    assert [event[1] for event in fake.events if event[0] == "output_marker"] == [
        "DB", "CHILD",
    ]
    assert fake.violations == []
    assert all(connection.closed and connection.autocommit for connection in fake.connections)


def test_ci_b_cli_unhandled_verify_error_has_safe_json_and_restores_output(
    monkeypatch, capfd
):
    from scripts import verify_empty_database_migrations as migrations

    config = _ci_b_valid_config()
    argv = [
        "--host", config.host,
        "--port", str(config.port),
        "--user", config.user,
        "--database-name", config.database_name,
        "--system-identifier", config.system_identifier,
    ]
    calls = []

    def exceptional_verify(received):
        calls.append(received)
        print("CI_B_EXCEPTION_PYTHON_MARKER")
        os.write(1, b"CI_B_EXCEPTION_FD1_MARKER\n")
        os.write(2, b"CI_B_EXCEPTION_FD2_MARKER\n")
        raise RuntimeError("CI_B_EXCEPTION_SECRET")

    def forbidden_child(*_args, **_kwargs):
        raise AssertionError("exceptional CLI launched a child")

    with monkeypatch.context() as guard:
        guard.setattr(migrations, "verify", exceptional_verify)
        guard.setattr(subprocess, "run", forbidden_child)
        exit_code = migrations.main(argv)

    captured = capfd.readouterr()
    assert calls == [config]
    assert exit_code == 2
    assert "CI_B_EXCEPTION" not in captured.out + captured.err
    assert json.loads(captured.out) == {
        "primary_exit_code": 2,
        "cleanup_exit_code": 3,
        "database_created": None,
        "database_removed": None,
        "failure_reason": "cli_verification_unhandled",
        "cleanup_reason": "cleanup_unconfirmed",
        "exit_code": 2,
    }

    print("CI_B_AFTER_EXCEPTION_PYTHON_MARKER")
    os.write(1, b"CI_B_AFTER_EXCEPTION_FD1_MARKER\n")
    os.write(2, b"CI_B_AFTER_EXCEPTION_FD2_MARKER\n")
    restored = capfd.readouterr()
    assert "CI_B_AFTER_EXCEPTION_PYTHON_MARKER" in restored.out
    assert "CI_B_AFTER_EXCEPTION_FD1_MARKER" in restored.out
    assert "CI_B_AFTER_EXCEPTION_FD2_MARKER" in restored.err


def test_ci_b_prior_server_limit_must_fit_before_next_set_config(monkeypatch):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    def leave_less_than_prior_limit(fake):
        prior_ms = fake.connections[0].statement_limit_ms
        assert prior_ms > 500
        cutoff = fake.config.total_seconds - fake.config.cleanup_seconds
        target_now = cutoff - ((prior_ms - 500) / 1000)
        assert target_now > fake.clock.now
        return target_now - fake.clock.now

    _, result, fake = _ci_b_verify(
        monkeypatch,
        scenario={"advance_after": {
            "identity:precreate": leave_less_than_prior_limit
        }},
        config_changes={"total_seconds": 20, "cleanup_seconds": 5},
    )
    assert _ci_b_result_fields(result) == (
        2, 0, False, False, "primary_deadline_exhausted", None
    )
    assert fake.limit_calls == 1
    assert fake.lookup_calls == 0
    assert not any(event[0] in {"create", "child", "drop"} for event in fake.events)

@pytest.mark.parametrize(
    "table_call,expected_children,reason",
    [
        pytest.param(
            1, 0, "initial_public_tables_check_failed", id="initial-query-error"
        ),
        pytest.param(
            2, 3, "downgrade_public_tables_check_failed",
            id="post-downgrade-query-error",
        ),
    ],
)
def test_ci_b_public_table_sql_error_stops_children_but_cleans_up(
    monkeypatch, capsys, table_call, expected_children, reason
):
    _, baseline, _ = _ci_b_verify(monkeypatch)
    assert baseline.exit_code == 0

    _, result, fake = _ci_b_verify(
        monkeypatch, scenario={"tables_error": table_call}
    )
    assert _ci_b_result_fields(result) == (
        2, 0, True, True, reason, None
    )
    assert result.exit_code == 2
    assert any(event[0] == "tables" and event[1] == table_call for event in fake.events)
    assert fake.table_calls == table_call
    assert fake.child_calls == expected_children
    assert sum(event[0] == "drop" for event in fake.events) == 1
    captured = capsys.readouterr()
    assert "SHOULD_NOT_LEAK" not in captured.out + captured.err
    assert "SHOULD_NOT_LEAK" not in repr(_ci_b_result_fields(result))

class _CiBGuardedDatabase(_CiBDatabase):
    """Reject adapter drift even when verify catches the fake exception."""

    CONNECT_KEYS = {
        "host", "hostaddr", "port", "user", "dbname", "connect_timeout",
        "sslmode", "gssencmode", "passfile", "options",
    }

    def __init__(self, config, *, scenario=None):
        super().__init__(config, scenario=scenario)
        self.violations = []
        self.repo_root = None

    def _violate(self, reason):
        self.violations.append(reason)
        raise AssertionError(reason)

    def install(self, monkeypatch, migrations):
        self.repo_root = migrations.REPO_ROOT
        super().install(monkeypatch, migrations)

    def connect(self, **kwargs):
        if set(kwargs) != self.CONNECT_KEYS:
            self._violate("connection_keyword_scope")
        database = kwargs["dbname"]
        if database not in {"postgres", self.config.database_name}:
            self._violate("connection_database")
        if (kwargs["host"], kwargs["hostaddr"], kwargs["port"], kwargs["user"]) != (
            self.config.host, self.config.host, self.config.port, self.config.user
        ):
            self._violate("connection_endpoint")
        if kwargs["sslmode"] != "disable" or kwargs["gssencmode"] != "disable":
            self._violate("connection_transport")
        if kwargs["passfile"] != os.devnull:
            self._violate("connection_passfile")
        ordinal = self.admin_connections + 1 if database == "postgres" else 0
        deadline = (
            self.config.total_seconds
            if ordinal >= 2
            else self.config.total_seconds - self.config.cleanup_seconds
        )
        remaining = deadline - self.clock.now
        timeout = kwargs["connect_timeout"]
        if (
            type(timeout) is not int
            or timeout < 2
            or timeout > self.config.connect_timeout_seconds
            or timeout > int(remaining)
        ):
            self._violate("connection_timeout_bound")
        try:
            connection = super().connect(**kwargs)
        except AssertionError:
            self.violations.append("connection_adapter_operation")
            raise
        initial_limit = connection.statement_limit_ms
        if (
            initial_limit <= 0
            or initial_limit > self.config.statement_timeout_ms
            or initial_limit > int((remaining - timeout) * 1000)
        ):
            self._violate("initial_server_timeout_bound")
        return connection

    def execute(self, connection, query, params):
        deadline = (
            self.config.total_seconds
            if connection.admin_ordinal >= 2
            else self.config.total_seconds - self.config.cleanup_seconds
        )
        remaining_ms = int((deadline - self.clock.now) * 1000)
        if not 0 < connection.statement_limit_ms <= remaining_ms:
            self._violate("prior_server_timeout_bound")
        if isinstance(query, str) and " ".join(query.split()) == self.LIMIT_SQL:
            if (
                not isinstance(params, tuple)
                or len(params) != 2
                or not all(type(value) is str and value.isdecimal() for value in params)
            ):
                self._violate("set_config_parameter_shape")
            first, second = map(int, params)
            if (
                first != second
                or first <= 0
                or first > self.config.statement_timeout_ms
                or first > remaining_ms
            ):
                self._violate("set_config_timeout_bound")
        try:
            return super().execute(connection, query, params)
        except AssertionError:
            self.violations.append("unknown_sql_or_adapter_operation")
            raise

    def run_child(self, argv, **kwargs):
        import re

        if set(kwargs) != {"cwd", "env", "check", "timeout"}:
            self._violate("child_keyword_scope")
        if kwargs["cwd"] != self.repo_root or kwargs["check"] is not False:
            self._violate("child_runtime_binding")
        remaining = (
            self.config.total_seconds - self.config.cleanup_seconds - self.clock.now
        )
        timeout = kwargs["timeout"]
        if type(timeout) is not int or timeout <= 0 or timeout > int(remaining):
            self._violate("child_timeout_bound")
        if "DATABASE_URL" not in kwargs["env"]:
            self._violate("child_database_url_missing")
        try:
            parsed, pairs, query = _ci_b_url_parts(kwargs["env"]["DATABASE_URL"])
            endpoint = (
                parsed.scheme, parsed.hostname, parsed.port, parsed.username,
                parsed.password, parsed.path, parsed.fragment,
            )
        except (TypeError, ValueError, AttributeError):
            self._violate("child_database_url_malformed")
        if endpoint != (
            "postgresql+psycopg2", self.config.host, self.config.port,
            self.config.user, None, "/" + self.config.database_name, "",
        ):
            self._violate("child_database_url_target")
        required_query = {
            "hostaddr", "connect_timeout", "sslmode", "gssencmode",
            "passfile", "options",
        }
        if len(pairs) != len(query) or set(query) != required_query:
            self._violate("child_database_url_query_scope")
        if (
            query["hostaddr"] != self.config.host
            or query["sslmode"] != "disable"
            or query["gssencmode"] != "disable"
            or query["passfile"] != os.devnull
        ):
            self._violate("child_database_url_transport")
        connect_text = query["connect_timeout"]
        if not re.fullmatch(r"[1-9][0-9]*", connect_text):
            self._violate("child_connect_timeout_syntax")
        connect_timeout = int(connect_text)
        if not 2 <= connect_timeout <= min(
            self.config.connect_timeout_seconds, int(remaining)
        ):
            self._violate("child_connect_timeout_bound")
        option_match = re.fullmatch(
            r"-c statement_timeout=([1-9][0-9]*) -c lock_timeout=\1",
            query["options"],
        )
        if option_match is None:
            self._violate("child_server_timeout_syntax")
        server_limit = int(option_match.group(1))
        if not 0 < server_limit <= min(
            self.config.statement_timeout_ms, int(remaining * 1000)
        ):
            self._violate("child_server_timeout_bound")
        return super().run_child(argv, **kwargs)
