"""Check a complete literal Bandit report against an active reviewed scope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


REPO_ROOT = Path(__file__).absolute().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.python_source_state import (  # noqa: E402
    SourceStateError,
    _literal_path,
    load_source_state,
)
from scripts.verification_runtime import TIMEOUT_SECONDS  # noqa: E402


FINGERPRINT_KEYS = {"path", "test_id", "line_number", "code_sha256"}
METRIC_KEYS = {"loc", "nosec", "skipped_tests"}
RANKS = ("UNDEFINED", "LOW", "MEDIUM", "HIGH")
ISSUE_KEYS = {f"{axis}.{rank}" for axis in ("SEVERITY", "CONFIDENCE")
              for rank in RANKS}
ALL_METRIC_KEYS = METRIC_KEYS | ISSUE_KEYS


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise SourceStateError(reason)


def _normalized_path(value: str) -> str:
    # Preserve the historical Bandit fingerprint spelling semantics.
    return value.replace("\\", "/").removeprefix("./")


def parse_report(raw: str) -> dict:
    _need(type(raw) is str, "malformed_bandit_json")
    def pairs(rows: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in rows:
            _need(key not in result, "duplicate_bandit_json_key")
            result[key] = value
        return result

    def nonfinite(_: str) -> None:
        raise SourceStateError("nonfinite_bandit_json")

    try:
        report = json.loads(raw, object_pairs_hook=pairs,
                            parse_constant=nonfinite)
    except json.JSONDecodeError as exc:
        raise SourceStateError("malformed_bandit_json") from exc
    _need(type(report) is dict, "malformed_bandit_json")
    return report


def _fingerprint(result: dict[str, object]) -> tuple[str, str, int, str]:
    code = result["code"]
    _need(type(code) is str and type(result["filename"]) is str
          and type(result["test_id"]) is str
          and re.fullmatch(r"B[0-9]{3}", result["test_id"]) is not None
          and type(result["line_number"]) is int
          and result["line_number"] > 0,
          "malformed_bandit_result")
    return (
        _normalized_path(result["filename"]),
        result["test_id"],
        result["line_number"],
        hashlib.sha256(code.encode("utf-8")).hexdigest(),
    )


def validate_report(report: dict, *, selected_paths: list[str] | tuple[str, ...],
                    reviewed_findings: list[dict], returncode: int) -> None:
    """Reject incomplete, aliased or unreviewed scanner evidence."""
    _need(type(selected_paths) in {list, tuple} and selected_paths
          and all(type(path) is str and _literal_path(path) == path
                  for path in selected_paths)
          and len({path.casefold() for path in selected_paths}) == len(selected_paths),
          "invalid_bandit_selection")
    selected = set(selected_paths)
    _need(type(report) is dict
          and set(report) >= {"metrics", "errors", "results"}
          and report["errors"] == []
          and type(report["metrics"]) is dict
          and type(report["results"]) is list,
          "malformed_or_errored_bandit_report")
    metrics = report["metrics"]
    _need("_totals" in metrics and type(metrics["_totals"]) is dict,
          "bandit_totals_missing")
    metric_paths: set[str] = set()
    metric_rows: dict[str, dict] = {}
    for filename, values in metrics.items():
        if filename == "_totals":
            continue
        _need(type(filename) is str and type(values) is dict
              and ALL_METRIC_KEYS <= set(values)
              and all(type(values[key]) is int and values[key] >= 0
                      for key in ALL_METRIC_KEYS), "malformed_bandit_metrics")
        path = _normalized_path(filename)
        _need(path in selected and path not in metric_paths,
              "bandit_metric_scope_mismatch")
        metric_paths.add(path)
        metric_rows[path] = values
        _need(sum(values[f"SEVERITY.{rank}"] for rank in RANKS)
              == sum(values[f"CONFIDENCE.{rank}"] for rank in RANKS),
              "inconsistent_bandit_issue_metrics")
    totals = metrics["_totals"]
    _need(metric_paths == selected and ALL_METRIC_KEYS <= set(totals)
          and all(type(totals[key]) is int and totals[key] >= 0
                  and totals[key] == sum(row[key] for row in metric_rows.values())
                  for key in ALL_METRIC_KEYS),
          "incomplete_bandit_metrics")

    _need(type(reviewed_findings) is list, "malformed_reviewed_findings")
    reviewed: set[tuple[str, str, int, str]] = set()
    for item in reviewed_findings:
        _need(type(item) is dict and set(item) == FINGERPRINT_KEYS
              and type(item["path"]) is str and item["path"] in selected
              and type(item["test_id"]) is str
              and re.fullmatch(r"B[0-9]{3}", item["test_id"]) is not None
              and type(item["line_number"]) is int and item["line_number"] > 0
              and type(item["code_sha256"]) is str
              and re.fullmatch(r"[0-9a-f]{64}", item["code_sha256"]) is not None,
              "malformed_reviewed_finding")
        fingerprint = (item["path"], item["test_id"],
                       item["line_number"], item["code_sha256"])
        _need(fingerprint not in reviewed, "duplicate_reviewed_finding")
        reviewed.add(fingerprint)

    actual: set[tuple[str, str, int, str]] = set()
    observed_ranks: dict[str, dict[str, int]] = {
        path: {key: 0 for key in ISSUE_KEYS} for path in selected
    }
    for item in report["results"]:
        _need(type(item) is dict and
              {"filename", "test_id", "line_number", "code",
               "issue_severity", "issue_confidence"} <= set(item)
              and type(item["issue_severity"]) is str
              and type(item["issue_confidence"]) is str
              and item["issue_severity"] in {"MEDIUM", "HIGH"}
              and item["issue_confidence"] in {"MEDIUM", "HIGH"},
              "malformed_or_out_of_scope_bandit_result")
        fingerprint = _fingerprint(item)
        _need(fingerprint[0] in selected and fingerprint not in actual,
              "unexpected_or_duplicate_bandit_result")
        actual.add(fingerprint)
        observed_ranks[fingerprint[0]][f"SEVERITY.{item['issue_severity']}"] += 1
        observed_ranks[fingerprint[0]][f"CONFIDENCE.{item['issue_confidence']}"] += 1
    for path, values in metric_rows.items():
        observed = observed_ranks[path]
        _need(all(observed[key] <= values[key] for key in ISSUE_KEYS),
              "bandit_result_metric_mismatch")
        qualifying = sum(observed[f"SEVERITY.{rank}"]
                         for rank in ("MEDIUM", "HIGH"))
        remaining = sum(values[f"SEVERITY.{rank}"] for rank in RANKS) - qualifying
        remaining_severity = sum(values[f"SEVERITY.{rank}"] - observed[f"SEVERITY.{rank}"]
                                 for rank in ("MEDIUM", "HIGH"))
        remaining_confidence = sum(values[f"CONFIDENCE.{rank}"] - observed[f"CONFIDENCE.{rank}"]
                                   for rank in ("MEDIUM", "HIGH"))
        # All medium/high pairs must appear in filtered results. Lower-ranked
        # pairs may remain unreported, so only their feasible margins matter.
        _need(remaining_severity + remaining_confidence <= remaining,
              "bandit_filtered_results_incomplete")
    _need(actual == reviewed, "bandit_reviewed_fingerprint_mismatch")
    _need(type(returncode) is int and returncode == (1 if actual else 0),
          "bandit_returncode_inconsistent")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--selection-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        state = load_source_state(args.selection,
                                  manifest_sha256=args.selection_sha256,
                                  repo_root=REPO_ROOT)
        review = state["bandit_review"]
        _need(review["status"] == "reviewed", "bandit_review_pending")
        selected = state["phases"]["bandit"]
        command = [
            sys.executable, "-B", "-m", "bandit", *selected,
            "-ll", "-ii", "-c", state["configs"]["bandit"],
            "-f", "json", "-q",
        ]
        completed = subprocess.run(
            command, cwd=REPO_ROOT, capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS["tool"], check=False,
        )
        report = parse_report(completed.stdout)
        validate_report(report, selected_paths=selected,
                        reviewed_findings=review["reviewed_findings"],
                        returncode=completed.returncode)
    except (SourceStateError, subprocess.TimeoutExpired) as exc:
        print(f"[bandit_gate_failure] {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "bounded_scoped_report_valid",
        "selected_paths": len(selected),
        "reviewed_findings": len(review["reviewed_findings"]),
        "repository_wide": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
