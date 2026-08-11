#!/usr/bin/env python3
"""Run the fixed provider-free CF-D2 no-crash recovery diagnostic."""

from __future__ import annotations

import json
import sys

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal as rehearsal,
)


def main() -> int:
    if len(sys.argv) != 1:
        print("This fixed-path diagnostic accepts no arguments.", file=sys.stderr)
        return 2
    evidence = rehearsal.run_recovery_diagnostic()
    rehearsal.write_diagnostic_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "evidence": rehearsal.DIAGNOSTIC_EVIDENCE_PATH.relative_to(
                    rehearsal.ROOT
                ).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == rehearsal.DIAGNOSTIC_PASS_RESULT else 2


if __name__ == "__main__":
    raise SystemExit(main())
