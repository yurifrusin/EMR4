"""Validate the read-only compatibility-consumer admission inventory."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = (
    ROOT
    / "orchestration/continuity"
    / "raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review"
    / "consumer-and-preservation-inventory.json"
)


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _render(node: ast.AST, constants: dict[str, str]) -> str:
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Name):
        return constants.get(node.id, "{" + node.id + "}")
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                if isinstance(value.value, ast.Name) and value.value.id in constants:
                    parts.append(constants[value.value.id])
                else:
                    parts.append("{expr}")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _render(node.left, constants) + _render(node.right, constants)
    return ast.unparse(node)


def _module_constants(tree: ast.Module) -> dict[str, str]:
    constants: dict[str, str] = {}
    changed = True
    while changed:
        changed = False
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = _render(node.value, constants)
            if "/api/v1/appointments" not in value:
                continue
            for target in targets:
                if isinstance(target, ast.Name) and constants.get(target.id) != value:
                    constants[target.id] = value
                    changed = True
    return constants


def _family(method: str, url: str) -> str | None:
    if method == "post" and url.rstrip("/") == "/api/v1/appointments":
        return "create"
    if method == "put" and url.startswith("/api/v1/appointments/") and "/proposals/" not in url:
        return "update"
    if (
        method == "patch"
        and url.startswith("/api/v1/appointments/")
        and url.endswith("/status")
        and "/proposals/" not in url
    ):
        return "status"
    if method == "delete" and url.startswith("/api/v1/appointments/") and "/proposals/" not in url:
        return "delete"
    return None


def census() -> dict[str, object]:
    rows: list[tuple[str, str, int]] = []
    for base in (ROOT / "tests", ROOT / "review"):
        for path in sorted(base.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
            constants = _module_constants(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                method = node.func.attr.lower()
                if method not in {"post", "put", "patch", "delete", "request"}:
                    continue
                args = [_render(arg, constants) for arg in node.args[:2]]
                url = args[0] if args else ""
                if method == "request" and len(args) > 1:
                    method, url = args[0].lower(), args[1]
                family = _family(method, url)
                if family:
                    rows.append((family, path.relative_to(ROOT).as_posix(), node.lineno))
    counts = {family: sum(row[0] == family for row in rows) for family in ("create", "update", "status", "delete")}
    return {
        "counts": counts,
        "total": len(rows),
        "files": sorted({row[1] for row in rows}),
    }


def validate() -> dict[str, object]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    reasons: list[str] = []
    for relative, expected in inventory["source_bindings"].items():
        actual = _git_blob(ROOT / relative)
        if actual != expected:
            reasons.append(f"source_binding_mismatch:{relative}:{actual}")

    observed = census()
    expected_files = inventory["consumer_census"]["executable_conformance"]["files"]
    expected_counts = {
        row["family"]: row["direct_test_call_expressions"]
        for row in inventory["route_families"]
    }
    if observed["counts"] != expected_counts:
        reasons.append(f"consumer_count_mismatch:{observed['counts']!r}")
    if observed["total"] != inventory["consumer_census"]["executable_conformance"]["direct_call_expression_count"]:
        reasons.append(f"consumer_total_mismatch:{observed['total']}")
    if observed["files"] != expected_files:
        reasons.append("consumer_file_set_mismatch")

    diary = (ROOT / "docs/diary/diary.js").read_text(encoding="utf-8")
    for fragment in (
        "apiFetch(`/appointments`,",
        "apiFetch(`/appointments/${editingAppointmentId}`,",
        "apiFetch(`/appointments/${appt.id}/status`,",
        "apiFetch(`/appointments/${appt.id}`,",
    ):
        if fragment in diary:
            reasons.append(f"native_raw_call_present:{fragment}")

    result = {
        "schema_version": "raisa.compatibility_consumer_kernel_convergence_admission_evidence.v1",
        "status": "passed" if not reasons else "failed",
        "reasons": reasons,
        "observed": observed,
        "selected_first_slice": inventory["selected_first_slice"],
        "external_consumer_posture": inventory["consumer_census"]["external_consumer_posture"],
    }
    return result


def main() -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
