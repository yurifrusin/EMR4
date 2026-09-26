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
    source = (
        ROOT / "alembic/versions/d4787e8e3629_phase_0_baseline.py"
    ).read_text(encoding="utf-8")

    assert "emr4_phase0_empty_bootstrap_marker" in source
    assert "def _prepare_legacy_baseline()" in source
    assert "Phase-0 legacy baseline is incomplete" in source
    assert "def _is_empty_database_bootstrap()" in source
    assert 'op.drop_table("mbs_directory")' in source
    assert 'op.drop_table("snomed_directory")' in source
    assert "type_name.typtype = 'e'" in source
