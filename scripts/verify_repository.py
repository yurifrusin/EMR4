"""Canonical, timeout-bounded repository verification entry point."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.verification_runtime import (
    TIMEOUT_SECONDS,
    VerificationCommand,
    run_commands,
)


RUFF_PATHS = [
    "app/dependencies.py",
    "app/middleware",
    "app/models",
    "app/routers",
    "app/schemas",
    "app/services/appointment_idempotency.py",
    "app/services/bernie/session.py",
    "app/services/bernie/session_store.py",
    "app/services/diary",
    "app/services/practice",
    "alembic",
    "orchestration_harness",
    "scripts/ariadne_orchestrator_preflight.py",
    "scripts/historical_diary_leakage_lint.py",
    "scripts/security_bandit_gate.py",
    "scripts/verification_runtime.py",
    "scripts/verify_empty_database_migrations.py",
    "scripts/verify_repository.py",
    "tests/test_agents_handover_archive.py",
    "tests/test_api_spine_appointment_idempotency_model_migration.py",
    "tests/test_api_spine_artifacts.py",
    "tests/test_ariadne_orchestrator_preflight.py",
    "tests/test_repository_maintenance.py",
]

COMPILE_PATHS = [path for path in RUFF_PATHS if not path.startswith("tests/")]

FOCUSED_TESTS = [
    "tests/test_agents_handover_archive.py",
    "tests/test_api_spine_appointment_idempotency_model_migration.py",
    "tests/test_api_spine_artifacts.py",
    "tests/test_ariadne_orchestrator_preflight.py",
    "tests/test_repository_maintenance.py",
]


def _fast_commands() -> list[VerificationCommand]:
    python = sys.executable
    commands = [
        VerificationCommand(
            "Ruff ordinary product/infrastructure baseline",
            [python, "-m", "ruff", "check", *RUFF_PATHS],
            TIMEOUT_SECONDS["tool"],
        ),
        VerificationCommand(
            "Python compilation",
            [python, "-m", "compileall", "-q", *COMPILE_PATHS],
            TIMEOUT_SECONDS["tool"],
        ),
        VerificationCommand(
            "focused API Spine, handover, receipt, and maintenance tests",
            [python, "-m", "pytest", *FOCUSED_TESTS],
            TIMEOUT_SECONDS["focused_tests"],
        ),
    ]
    if shutil.which("node"):
        commands.append(
            VerificationCommand(
                "Diary JavaScript syntax",
                ["node", "--check", "docs/diary/diary.js"],
                TIMEOUT_SECONDS["tool"],
            )
        )
    commands.append(
        VerificationCommand(
            "Git whitespace",
            ["git", "diff", "--check"],
            TIMEOUT_SECONDS["tool"],
        )
    )
    return commands


def _lint_commands() -> list[VerificationCommand]:
    python = sys.executable
    return [
        VerificationCommand(
            "Ruff ordinary product/infrastructure baseline",
            [python, "-m", "ruff", "check", *RUFF_PATHS],
            TIMEOUT_SECONDS["tool"],
        ),
        VerificationCommand(
            "historical diary leakage lint",
            [python, "scripts/historical_diary_leakage_lint.py", "tests", "docs"],
            TIMEOUT_SECONDS["tool"],
        ),
    ]


def _bandit_commands() -> list[VerificationCommand]:
    return [
        VerificationCommand(
            "reviewed Bandit baseline",
            [sys.executable, "scripts/security_bandit_gate.py"],
            TIMEOUT_SECONDS["tool"],
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("fast", "ci-lint", "ci-bandit", "ci-security", "migration"),
        default="fast",
    )
    args = parser.parse_args()

    if args.profile == "migration":
        commands = [
            VerificationCommand(
                "disposable empty-database Alembic lifecycle",
                [sys.executable, "scripts/verify_empty_database_migrations.py"],
                TIMEOUT_SECONDS["full_tests"],
            )
        ]
    elif args.profile == "ci-security":
        commands = [*_lint_commands(), *_bandit_commands()]
    elif args.profile == "ci-lint":
        commands = _lint_commands()
    elif args.profile == "ci-bandit":
        commands = _bandit_commands()
    else:
        commands = _fast_commands()
    return run_commands(commands, cwd=REPO_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
