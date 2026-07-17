"""Generate or verify the synthetic Silver all-192 coherence audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_coherence import (  # noqa: E402
    COHERENT_ADMISSION_PATH,
    COHERENT_CANDIDATE_PATH,
    DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH,
    DEFAULT_FINAL_REPORT_PATH,
    DEFAULT_PRE_REPORT_PATH,
    build_final_artifacts,
    build_accepted_robustness_report,
    build_pre_repair_report,
    write_json,
    write_jsonl,
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pre_report = build_pre_repair_report()
    candidates, final_report, admission = build_final_artifacts()
    robustness_report = build_accepted_robustness_report()
    if args.write:
        write_json(DEFAULT_PRE_REPORT_PATH, pre_report)
        write_jsonl(COHERENT_CANDIDATE_PATH, candidates)
        write_json(DEFAULT_FINAL_REPORT_PATH, final_report)
        write_json(COHERENT_ADMISSION_PATH, admission)
        write_json(DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH, robustness_report)
    else:
        expected = {
            DEFAULT_PRE_REPORT_PATH: pre_report,
            DEFAULT_FINAL_REPORT_PATH: final_report,
            COHERENT_ADMISSION_PATH: admission,
            DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH: robustness_report,
        }
        for path, value in expected.items():
            if not path.exists() or _load(path) != value:
                raise SystemExit(f"artifact does not regenerate: {path}")
        candidate_lines = COHERENT_CANDIDATE_PATH.read_text(encoding="utf-8").splitlines()
        if [json.loads(line) for line in candidate_lines if line.strip()] != candidates:
            raise SystemExit(f"artifact does not regenerate: {COHERENT_CANDIDATE_PATH}")

    print(
        "pre="
        f"{pre_report['population']['accepted']}/{pre_report['population']['candidates']} "
        "final="
        f"{final_report['population']['accepted']}/{final_report['population']['candidates']} "
        f"quarantine={admission['quarantine_count']}"
    )
    print(f"pre_report_hash={pre_report['report_hash']}")
    print(f"final_report_hash={final_report['report_hash']}")
    print(f"candidate_hash={admission['canonical_candidate_hash']}")
    print(f"admission_hash={admission['admission_hash']}")
    print(
        "accepted_robustness="
        f"{robustness_report['population']['complete_candidates']}/"
        f"{robustness_report['population']['candidates']} "
        f"safety={robustness_report['safety']['passed']}/"
        f"{robustness_report['safety']['total']}"
    )
    print(f"accepted_robustness_hash={robustness_report['report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
