"""Static, fail-closed admission for provider-free pytest selections.

The classifier never imports pytest, a selected test module, or repository
conftest.  It recognizes a deliberately small fixture-declaration grammar and
rejects everything it cannot resolve before a subprocess is allowed to start.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


SCHEMA_VERSION = "ariadne.provider_free_no_database_selection.v1"
MANIFEST_ADMISSION_SCHEMA_VERSION = "ariadne.provider_free_no_database_admission.v1"
POLICY_VERSION = "ariadne.provider_free_no_database_policy.v1"
PYTEST_CORE_FIXTURES = (
    "capfd",
    "capfdbinary",
    "caplog",
    "capsys",
    "capsysbinary",
    "doctest_namespace",
    "monkeypatch",
    "pytestconfig",
    "record_property",
    "record_testsuite_property",
    "record_xml_attribute",
    "recwarn",
    "request",
    "tmp_path",
    "tmp_path_factory",
    "tmpdir",
    "tmpdir_factory",
)
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class _Fixture:
    name: str
    dependencies: tuple[str, ...]
    autouse: bool


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    """Return the canonical prefixed digest used at broker boundaries."""
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _source_sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _dotted_name(value: ast.expr) -> str | None:
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        parent = _dotted_name(value.value)
        return f"{parent}.{value.attr}" if parent is not None else None
    return None


def _literal_string_list(value: ast.expr, *, reason: str) -> tuple[str, ...]:
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        names = tuple(item.strip() for item in value.value.split(","))
    elif isinstance(value, (ast.List, ast.Tuple)):
        if not all(
            isinstance(item, ast.Constant) and isinstance(item.value, str)
            for item in value.elts
        ):
            raise ValueError(reason)
        names = tuple(str(item.value).strip() for item in value.elts)
    else:
        raise ValueError(reason)
    if not names or any(not item or not item.isidentifier() for item in names):
        raise ValueError(reason)
    if len(names) != len(set(names)):
        raise ValueError(reason)
    return names


def _required_parameters(function: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    positional = [*function.args.posonlyargs, *function.args.args]
    required_positional = positional[
        : len(positional) - len(function.args.defaults)
        if function.args.defaults
        else len(positional)
    ]
    required = [argument.arg for argument in required_positional]
    required.extend(
        argument.arg
        for argument, default in zip(
            function.args.kwonlyargs, function.args.kw_defaults, strict=True
        )
        if default is None
    )
    return tuple(name for name in required if name not in {"self", "cls"})


def _pytest_aliases(tree: ast.Module) -> tuple[set[str], set[str], set[str]]:
    pytest_names = {"pytest"}
    fixture_names: set[str] = set()
    mark_names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pytest":
                    pytest_names.add(alias.asname or "pytest")
        elif isinstance(node, ast.ImportFrom) and node.module == "pytest":
            for alias in node.names:
                if alias.name == "*":
                    raise ValueError("star_import_unsupported")
                if alias.name == "fixture":
                    fixture_names.add(alias.asname or alias.name)
                elif alias.name == "mark":
                    mark_names.add(alias.asname or alias.name)
    return pytest_names, fixture_names, mark_names


def _fixture_decorator(
    decorator: ast.expr,
    *,
    pytest_names: set[str],
    fixture_names: set[str],
) -> tuple[bool, str | None, bool] | None:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    dotted = _dotted_name(target)
    is_fixture = dotted in fixture_names or any(
        dotted == f"{pytest_name}.fixture" for pytest_name in pytest_names
    )
    if not is_fixture:
        return None
    if not isinstance(decorator, ast.Call):
        return True, None, False
    if decorator.args:
        raise ValueError("fixture_decorator_dynamic")
    allowed = {"scope", "params", "autouse", "ids", "name"}
    if any(keyword.arg not in allowed for keyword in decorator.keywords):
        raise ValueError("fixture_decorator_dynamic")
    name: str | None = None
    autouse = False
    for keyword in decorator.keywords:
        if keyword.arg == "name":
            if not (
                isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
                and keyword.value.value.isidentifier()
            ):
                raise ValueError("fixture_name_dynamic")
            name = keyword.value.value
        elif keyword.arg == "autouse":
            if not (
                isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, bool)
            ):
                raise ValueError("fixture_autouse_dynamic")
            autouse = keyword.value.value
        elif keyword.arg in {"scope", "params", "ids"}:
            try:
                ast.literal_eval(keyword.value)
            except (ValueError, TypeError) as error:
                raise ValueError("fixture_decorator_dynamic") from error
    return True, name, autouse


def _mark_kind(
    decorator: ast.expr, *, pytest_names: set[str], mark_names: set[str]
) -> tuple[str, ast.Call] | None:
    if not isinstance(decorator, ast.Call):
        return None
    dotted = _dotted_name(decorator.func)
    for kind in ("parametrize", "usefixtures"):
        admitted = {f"{name}.mark.{kind}" for name in pytest_names}
        admitted.update(f"{name}.{kind}" for name in mark_names)
        if dotted in admitted:
            return kind, decorator
    return None


def _mark_bindings(
    decorators: Sequence[ast.expr],
    *,
    pytest_names: set[str],
    mark_names: set[str],
) -> tuple[set[str], set[str]]:
    parametrized: set[str] = set()
    required: set[str] = set()
    for decorator in decorators:
        mark = _mark_kind(
            decorator, pytest_names=pytest_names, mark_names=mark_names
        )
        if mark is None:
            continue
        kind, call = mark
        if kind == "usefixtures":
            if call.keywords or not call.args:
                raise ValueError("usefixtures_dynamic")
            for argument in call.args:
                required.update(
                    _literal_string_list(argument, reason="usefixtures_dynamic")
                )
            continue
        if len(call.args) < 2 or len(call.args) > 4:
            raise ValueError("parametrize_dynamic")
        names = set(
            _literal_string_list(call.args[0], reason="parametrize_names_dynamic")
        )
        indirect: bool | set[str] = False
        for keyword in call.keywords:
            if keyword.arg != "indirect":
                continue
            if isinstance(keyword.value, ast.Constant) and isinstance(
                keyword.value.value, bool
            ):
                indirect = keyword.value.value
            else:
                indirect = set(
                    _literal_string_list(
                        keyword.value, reason="parametrize_indirect_dynamic"
                    )
                )
                if not set(indirect).issubset(names):
                    raise ValueError("parametrize_indirect_unknown")
        if indirect is True:
            required.update(names)
        elif isinstance(indirect, set):
            required.update(indirect)
            parametrized.update(names - indirect)
        else:
            parametrized.update(names)
    return parametrized, required


def _module_marks(
    tree: ast.Module, *, pytest_names: set[str], mark_names: set[str]
) -> tuple[ast.expr, ...]:
    marks: list[ast.expr] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in targets):
            continue
        value = node.value
        values = value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value]
        if any(
            _mark_kind(item, pytest_names=pytest_names, mark_names=mark_names)
            is None
            for item in values
        ):
            raise ValueError("pytestmark_dynamic")
        marks.extend(values)
    return tuple(marks)


def _reject_unsafe_imports(tree: ast.Module) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == "tests.conftest" or alias.name.endswith(".conftest") for alias in node.names):
                raise ValueError("provider_free_conftest_import_forbidden")
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or any(alias.name == "*" for alias in node.names):
                raise ValueError("star_or_relative_import_unsupported")
            if node.module == "conftest" or node.module.endswith(".conftest"):
                raise ValueError("provider_free_conftest_import_forbidden")
        elif isinstance(node, ast.Call):
            name = _dotted_name(node.func)
            if name in {"__import__", "importlib.import_module"}:
                if not node.args or not (
                    isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    raise ValueError("dynamic_import_unsupported")
                imported = node.args[0].value
                if imported == "conftest" or imported.endswith(".conftest"):
                    raise ValueError("provider_free_conftest_import_forbidden")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(
                isinstance(target, ast.Name) and target.id == "pytest_plugins"
                for target in targets
            ):
                raise ValueError("pytest_plugin_declaration_forbidden")


def _fixtures(
    tree: ast.Module, *, pytest_names: set[str], fixture_names: set[str]
) -> dict[str, _Fixture]:
    fixtures: dict[str, _Fixture] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        matched: tuple[bool, str | None, bool] | None = None
        for decorator in node.decorator_list:
            candidate = _fixture_decorator(
                decorator,
                pytest_names=pytest_names,
                fixture_names=fixture_names,
            )
            if candidate is not None:
                if matched is not None:
                    raise ValueError("fixture_decorator_duplicate")
                matched = candidate
        if matched is None:
            continue
        name = matched[1] or node.name
        if name in fixtures:
            raise ValueError(f"fixture_name_ambiguous:{name}")
        fixtures[name] = _Fixture(
            name=name,
            dependencies=_required_parameters(node),
            autouse=matched[2],
        )
    return fixtures


def _shared_fixture_names(conftest_source: bytes) -> tuple[str, ...]:
    try:
        tree = ast.parse(conftest_source.decode("utf-8"), filename="tests/conftest.py")
    except (SyntaxError, UnicodeDecodeError) as error:
        raise ValueError("shared_conftest_parse_failed") from error
    pytest_names, fixture_names, _mark_names = _pytest_aliases(tree)
    return tuple(sorted(_fixtures(
        tree, pytest_names=pytest_names, fixture_names=fixture_names
    )))


def _test_functions(
    tree: ast.Module,
) -> list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, tuple[ast.expr, ...]]]:
    selected: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, tuple[ast.expr, ...]]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            selected.append((node, ()))
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                    selected.append((child, tuple(node.decorator_list)))
    return selected


def _safe_test_path(repo_root: Path, relative: str) -> tuple[Path, str]:
    normalized = relative.replace("\\", "/")
    value = PurePosixPath(normalized)
    if (
        not normalized
        or value.is_absolute()
        or ".." in value.parts
        or not normalized.startswith("tests/")
        or value.suffix != ".py"
        or "::" in normalized
    ):
        raise ValueError(f"provider_free_test_selector_invalid:{normalized}")
    candidate = repo_root.joinpath(*value.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(repo_root)
    except (OSError, ValueError) as error:
        raise ValueError(f"selected_test_path_invalid:{normalized}") from error
    current = candidate
    while current != repo_root:
        if current.is_symlink():
            raise ValueError(f"selected_test_symlink_forbidden:{normalized}")
        current = current.parent
    if not resolved.is_file():
        raise ValueError(f"selected_test_path_missing:{normalized}")
    return resolved, normalized


def admit_test_paths(*, repo_root: Path, test_paths: Sequence[str]) -> dict[str, Any]:
    """Classify exact test files and return a canonical no-database reading."""
    root = repo_root.resolve(strict=True)
    if not root.is_dir() or not test_paths:
        raise ValueError("provider_free_test_paths_required")
    normalized = [path.replace("\\", "/") for path in test_paths]
    if len(normalized) != len(set(normalized)):
        raise ValueError("provider_free_test_selector_duplicate")

    conftest_path = root / "tests" / "conftest.py"
    if not conftest_path.is_file() or conftest_path.is_symlink():
        raise ValueError("shared_conftest_missing_or_unsafe")
    conftest_source = conftest_path.read_bytes()
    shared_names = set(_shared_fixture_names(conftest_source))
    core_names = set(PYTEST_CORE_FIXTURES)
    selected_rows: list[dict[str, Any]] = []

    for supplied in test_paths:
        test_path, relative = _safe_test_path(root, supplied)
        source = test_path.read_bytes()
        try:
            tree = ast.parse(source.decode("utf-8"), filename=relative)
        except (SyntaxError, UnicodeDecodeError) as error:
            raise ValueError(f"selected_test_parse_failed:{relative}") from error
        _reject_unsafe_imports(tree)
        pytest_names, fixture_names, mark_names = _pytest_aliases(tree)
        local = _fixtures(
            tree, pytest_names=pytest_names, fixture_names=fixture_names
        )
        overlap = sorted(set(local) & shared_names)
        if overlap:
            raise ValueError(f"fixture_override_ambiguous:{overlap[0]}")
        module_marks = _module_marks(
            tree, pytest_names=pytest_names, mark_names=mark_names
        )
        tests = _test_functions(tree)
        if not tests:
            raise ValueError(f"selected_test_contains_no_tests:{relative}")
        autouse = {name for name, fixture in local.items() if fixture.autouse}
        edges: set[tuple[str, str, str]] = set()

        def resolve(consumer: str, name: str, stack: tuple[str, ...]) -> None:
            if name in stack:
                raise ValueError(f"fixture_dependency_cycle:{name}")
            if name in shared_names:
                raise ValueError(
                    f"provider_free_shared_postgresql_fixture_reachable:{name}"
                )
            if name in core_names:
                edges.add((consumer, name, "pytest_core"))
                return
            fixture = local.get(name)
            if fixture is None:
                raise ValueError(f"provider_free_fixture_unknown:{name}")
            edges.add((consumer, name, "file_local"))
            for dependency in fixture.dependencies:
                resolve(name, dependency, (*stack, name))

        for function, inherited in tests:
            parametrized, marked = _mark_bindings(
                (*module_marks, *inherited, *function.decorator_list),
                pytest_names=pytest_names,
                mark_names=mark_names,
            )
            required = set(_required_parameters(function)) - parametrized
            required.update(marked)
            required.update(autouse)
            for name in sorted(required):
                resolve(function.name, name, ())

        selected_rows.append(
            {
                "path": relative,
                "source_sha256": _source_sha256(source),
                "test_count": len(tests),
                "local_fixtures": sorted(local),
                "resolved_fixture_edges": [
                    {"consumer": consumer, "fixture": fixture, "source": source_kind}
                    for consumer, fixture, source_kind in sorted(edges)
                ],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "policy_version": POLICY_VERSION,
        "pytest_core_fixture_allowlist": list(PYTEST_CORE_FIXTURES),
        "shared_conftest": {
            "path": "tests/conftest.py",
            "source_sha256": _source_sha256(conftest_source),
            "fixture_names": sorted(shared_names),
        },
        "selected_tests": selected_rows,
    }


def validate_manifest_admission(value: object) -> dict[str, Any]:
    """Validate the aggregate artifact consumed by the broker boundary."""
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "status",
        "command_manifest_sha256",
        "commands",
    }:
        raise ValueError("provider_free_admission_keys_not_exact")
    if (
        value["schema_version"] != MANIFEST_ADMISSION_SCHEMA_VERSION
        or value["status"] != "passed"
        or not isinstance(value["command_manifest_sha256"], str)
        or DIGEST_PATTERN.fullmatch(value["command_manifest_sha256"]) is None
    ):
        raise ValueError("provider_free_admission_identity_invalid")
    commands = value["commands"]
    if not isinstance(commands, list) or not commands:
        raise ValueError("provider_free_admission_commands_required")
    observed: set[str] = set()
    for row in commands:
        if not isinstance(row, dict) or set(row) != {
            "command_id",
            "argv_sha256",
            "selection",
            "selection_sha256",
        }:
            raise ValueError("provider_free_admission_command_keys_not_exact")
        if not isinstance(row["command_id"], str) or row["command_id"] in observed:
            raise ValueError("provider_free_admission_command_id_invalid")
        observed.add(row["command_id"])
        selection = validate_selection_admission(row["selection"])
        if (
            row["selection_sha256"] != canonical_sha256(selection)
            or not isinstance(row["argv_sha256"], str)
            or DIGEST_PATTERN.fullmatch(row["argv_sha256"]) is None
        ):
            raise ValueError("provider_free_admission_command_invalid")
    return value


def validate_selection_admission(value: object) -> dict[str, Any]:
    """Validate an exact static selection reading without touching the files."""
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "status",
        "policy_version",
        "pytest_core_fixture_allowlist",
        "shared_conftest",
        "selected_tests",
    }:
        raise ValueError("provider_free_selection_keys_not_exact")
    if (
        value["schema_version"] != SCHEMA_VERSION
        or value["status"] != "passed"
        or value["policy_version"] != POLICY_VERSION
        or value["pytest_core_fixture_allowlist"] != list(PYTEST_CORE_FIXTURES)
    ):
        raise ValueError("provider_free_selection_identity_invalid")
    shared = value["shared_conftest"]
    if (
        not isinstance(shared, dict)
        or set(shared) != {"path", "source_sha256", "fixture_names"}
        or shared["path"] != "tests/conftest.py"
        or not isinstance(shared["source_sha256"], str)
        or DIGEST_PATTERN.fullmatch(shared["source_sha256"]) is None
        or not isinstance(shared["fixture_names"], list)
        or shared["fixture_names"] != sorted(set(shared["fixture_names"]))
        or any(not isinstance(name, str) or not name.isidentifier() for name in shared["fixture_names"])
    ):
        raise ValueError("provider_free_selection_conftest_invalid")
    selected = value["selected_tests"]
    if not isinstance(selected, list) or not selected:
        raise ValueError("provider_free_selection_tests_required")
    paths: set[str] = set()
    for row in selected:
        if not isinstance(row, dict) or set(row) != {
            "path",
            "source_sha256",
            "test_count",
            "local_fixtures",
            "resolved_fixture_edges",
        }:
            raise ValueError("provider_free_selection_test_keys_not_exact")
        path = row["path"]
        if (
            not isinstance(path, str)
            or path in paths
            or not path.startswith("tests/")
            or not path.endswith(".py")
            or ".." in PurePosixPath(path).parts
            or not isinstance(row["source_sha256"], str)
            or DIGEST_PATTERN.fullmatch(row["source_sha256"]) is None
            or not isinstance(row["test_count"], int)
            or isinstance(row["test_count"], bool)
            or row["test_count"] < 1
            or not isinstance(row["local_fixtures"], list)
            or row["local_fixtures"] != sorted(set(row["local_fixtures"]))
            or not isinstance(row["resolved_fixture_edges"], list)
        ):
            raise ValueError("provider_free_selection_test_invalid")
        paths.add(path)
        for edge in row["resolved_fixture_edges"]:
            if (
                not isinstance(edge, dict)
                or set(edge) != {"consumer", "fixture", "source"}
                or not isinstance(edge["consumer"], str)
                or not isinstance(edge["fixture"], str)
                or edge["source"] not in {"file_local", "pytest_core"}
            ):
                raise ValueError("provider_free_selection_edge_invalid")
    return value
