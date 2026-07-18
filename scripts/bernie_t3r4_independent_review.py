"""Run one fresh, bundle-isolated Gemini review of the committed T3R4 result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "antigravity"
    / "t3r4-pragmatic-live-independent-review.md"
)
BUNDLE_ROOT = ROOT / "local_data" / "t3r4-live" / "review-bundles"
FILES = (
    "docs/bernie-t3r4-pragmatic-live-comparison-approval.json",
    "docs/bernie-t3r4-pragmatic-live-comparison-plan.md",
    "docs/bernie-t3r4-pragmatic-live-comparison-observations.jsonl",
    "docs/bernie-t3r4-pragmatic-live-comparison-report.json",
    "app/services/ai/evals/bernie_shadow_live_comparison.py",
    "scripts/bernie_t3r4_live_comparison.py",
    "tests/test_bernie_t3r4_live_comparison.py",
)


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if completed.returncode != 0:
        raise ValueError("git metadata check failed")
    return completed.stdout.strip()


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_bundle() -> tuple[Path, str, dict[str, str]]:
    if _git("status", "--porcelain"):
        raise ValueError("T3R4 review requires a clean exact source worktree")
    source_head = _git("rev-parse", "HEAD")
    BUNDLE_ROOT.mkdir(parents=True, exist_ok=True)
    bundle = Path(tempfile.mkdtemp(prefix="t3r4-gemini-", dir=BUNDLE_ROOT))
    hashes: dict[str, str] = {}
    for relative in FILES:
        source = ROOT / relative
        if not source.is_file():
            raise ValueError(f"missing review source: {relative}")
        destination = bundle / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        hashes[relative] = _hash(destination)
    manifest = {
        "schema_version": "emr4.bernie.t3r4_review_bundle.v1",
        "source_head": source_head,
        "files": hashes,
        "protected_access": False,
        "raw_prompt_or_response_included": False,
    }
    (bundle / "bundle-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return bundle, source_head, hashes


def review_prompt(source_head: str, hashes: dict[str, str]) -> str:
    return f"""You are the fresh independent reviewer for EMR4 Bernie T3R4.
Review only files inside this isolated bundle. Do not access parent directories, repositories,
history, network sources, protected holdouts, historical diary data, or any other project.
Do not edit files. The bundle contains synthetic normalized evidence only.

Bound source head: {source_head}
Bound file hashes: {json.dumps(hashes, sort_keys=True)}

Independently inspect the approval, plan, 89-line observation ledger, aggregate report,
implementation, runner, and tests. Check:
1. observation keys are unique; no raw prompt, raw response, dialogue instruction, PHI,
   historical material, external corpus, or protected evidence is persisted;
2. GPT/Gemini are the primary practical system surfaces and DeepSeek is auxiliary only;
3. GPT's 17 consumed observations include 12 successes and five errors, and its 250,258
   reported tokens validly trigger the frozen 250,000-token hard stop without retry;
4. Gemini is 48 consumed / 46 success, DeepSeek is 24 consumed / 23 success, and all
   status, correctness, safety, variance, paired-case, usage, and hash arithmetic agrees;
5. the five fully paired GPT/Gemini cases contain ten successful observations per lane and
   both lanes are 60/60 on that narrow paired slice;
6. the report does not overclaim a pure-model comparison, exact reproducibility, production
   provider choice, clinical validation, runtime readiness, or DeepSeek deployment eligibility;
7. provider subprocesses remain developer-script-only and product runtime, routes, database,
   audit, appointment, confirmation, deployment, release, and write authority stay closed.

Return a concise review ending with exactly these lines:
DECISION: pass|revision_required
SOURCE_HEAD: {source_head}
OBSERVATIONS: <n>
GPT: <consumed>/<success>/<correctness passes>/<correctness total>
GEMINI: <consumed>/<success>/<correctness passes>/<correctness total>
DEEPSEEK_AUXILIARY: <consumed>/<success>/<correctness passes>/<correctness total>
PRIMARY_PAIRED: <case count>/<sample count per lane>/<GPT passes>/<Gemini passes>
RAW_PERSISTENCE: false|true
PROTECTED_ACCESS: false|true
PRODUCT_AUTHORITY_CHANGED: false|true
"""


def run_review(output: Path) -> dict[str, str]:
    bundle, source_head, hashes = build_bundle()
    command = [
        "agy",
        "-p",
        review_prompt(source_head, hashes),
        "--new-project",
        "--add-dir",
        str(bundle),
        "--model",
        "Gemini 3.5 Flash (Medium)",
        "--mode",
        "plan",
        "--sandbox",
        "--print-timeout",
        "20m",
    ]
    completed = subprocess.run(
        command,
        cwd=bundle,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=1300,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Gemini review transport exited {completed.returncode}")
    result = completed.stdout.strip()
    if "DECISION: pass" not in result and "DECISION: revision_required" not in result:
        raise RuntimeError("Gemini review omitted its required decision")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "# T3R4 Pragmatic Live Comparison - Independent Review\n\n"
        f"Reviewer: Gemini 3.5 Flash (Medium) via fresh isolated Antigravity project\n\n"
        f"Source head: `{source_head}`\n\n"
        f"Bundle manifest: `{_hash(bundle / 'bundle-manifest.json')}`\n\n"
        + result
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "source_head": source_head,
        "decision": "pass" if "DECISION: pass" in result else "revision_required",
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = run_review(args.output.resolve())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "blocked", "safe_error_code": type(error).__name__}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["decision"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
