"""Advisory action classification from observable filesystem artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from .models import ActionClassification, BoundaryClass

PATH_POLICY_SCHEMA_VERSION = "ariadne.path_boundary_policy.v1"
_BOUNDARY_RANK = {
    BoundaryClass.GREEN: 0,
    BoundaryClass.BLUE: 1,
    BoundaryClass.AMBER: 2,
    BoundaryClass.RED: 3,
    BoundaryClass.BLACK: 4,
}


@dataclass(frozen=True, slots=True)
class PathBoundaryRule:
    path_prefix: str
    boundary_class: BoundaryClass
    classification: ActionClassification

    def matches(self, path: str) -> bool:
        return path == self.path_prefix or path.startswith(self.path_prefix)


@dataclass(frozen=True, slots=True)
class PathBoundaryPolicy:
    rules: tuple[PathBoundaryRule, ...]
    default_boundary_class: BoundaryClass
    default_classification: ActionClassification

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PathBoundaryPolicy":
        if set(payload) != {"schema_version", "rules", "default"}:
            raise ValueError("Path policy fields must exactly match the schema")
        if payload["schema_version"] != PATH_POLICY_SCHEMA_VERSION:
            raise ValueError("Unsupported path policy schema version")
        rules_payload = payload["rules"]
        if not isinstance(rules_payload, list) or not rules_payload:
            raise ValueError("Path policy requires at least one rule")
        rules: list[PathBoundaryRule] = []
        for item in rules_payload:
            if not isinstance(item, dict) or set(item) != {
                "path_prefix",
                "boundary_class",
                "classification",
            }:
                raise ValueError("Invalid path boundary rule")
            prefix = _validate_relative_path(item["path_prefix"], allow_directory=True)
            rules.append(
                PathBoundaryRule(
                    path_prefix=prefix,
                    boundary_class=BoundaryClass(item["boundary_class"]),
                    classification=ActionClassification(item["classification"]),
                )
            )
        default = payload["default"]
        if not isinstance(default, dict) or set(default) != {
            "boundary_class",
            "classification",
        }:
            raise ValueError("Invalid path policy default")
        return cls(
            rules=tuple(rules),
            default_boundary_class=BoundaryClass(default["boundary_class"]),
            default_classification=ActionClassification(default["classification"]),
        )


@dataclass(frozen=True, slots=True)
class ObservableAction:
    action_id: str
    changed_paths: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ObservableAction":
        if set(payload) != {"action_id", "changed_paths"}:
            raise ValueError("Observable action fields must exactly match the schema")
        action_id = payload["action_id"]
        paths = payload["changed_paths"]
        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError("Observable action id must be a non-empty string")
        if not isinstance(paths, list) or not paths:
            raise ValueError("Observable action requires changed paths")
        normalized = tuple(_validate_relative_path(path) for path in paths)
        if len(set(normalized)) != len(normalized):
            raise ValueError("Observable action paths must be unique")
        return cls(action_id=action_id, changed_paths=normalized)


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    boundary_class: BoundaryClass
    classification: ActionClassification
    matched_paths: tuple[str, ...]


def _validate_relative_path(value: Any, *, allow_directory: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Paths must be non-empty, repo-relative POSIX paths")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        raise ValueError("Paths must be normalized, repo-relative paths")
    if allow_directory and value.endswith("/"):
        return value
    return str(path)


def classify_observable_action(
    action: ObservableAction, policy: PathBoundaryPolicy
) -> ClassificationResult:
    """Classify only changed paths; action prose and model intent are excluded."""

    candidates: list[tuple[PathBoundaryRule, str]] = []
    for path in action.changed_paths:
        matching_rules = [rule for rule in policy.rules if rule.matches(path)]
        if not matching_rules:
            continue
        rule = max(
            matching_rules,
            key=lambda item: (_BOUNDARY_RANK[item.boundary_class], len(item.path_prefix)),
        )
        candidates.append((rule, path))
    if not candidates:
        return ClassificationResult(
            boundary_class=policy.default_boundary_class,
            classification=policy.default_classification,
            matched_paths=(),
        )
    highest_rank = max(_BOUNDARY_RANK[rule.boundary_class] for rule, _ in candidates)
    highest = [item for item in candidates if _BOUNDARY_RANK[item[0].boundary_class] == highest_rank]
    result_rule = max(highest, key=lambda item: len(item[0].path_prefix))[0]
    return ClassificationResult(
        boundary_class=result_rule.boundary_class,
        classification=result_rule.classification,
        matched_paths=tuple(path for rule, path in highest if rule == result_rule),
    )
