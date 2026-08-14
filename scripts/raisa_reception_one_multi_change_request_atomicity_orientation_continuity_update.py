"""Advance Continuity and Compass for the multi-change atomicity orientation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
HANDOVER = ROOT / "AGENTS.md"
MASTER_PLAN = ROOT / "implementation_plan.md"
NODE_ID = "raisa-reception-one-multi-change-request-atomicity-orientation"
PARENT = (
    "raisa-reception-one-selected-action-console-progressive-disclosure-composition"
)
SOURCE_HEAD = "fbb7ffb46e041bbfc193ff3a76b2f970c06dee58"
UPDATED_AT = "2026-08-14T11:47:54Z"
PLAN = "docs/raisa-reception-one-multi-change-request-atomicity-orientation-plan.md"
ARCHITECTURE = "docs/raisa-reception-one-multi-change-request-atomicity-architecture.md"
THREAT = "docs/security/raisa-reception-one-multi-change-request-atomicity-orientation-threat-model-delta.md"
ROOT_EVIDENCE = "orchestration/continuity/raisa-reception-one-multi-change-request-atomicity-orientation"
CONTRACT_SCHEMA = f"{ROOT_EVIDENCE}/multi-change-action-atomicity-contract.schema.json"
CONTRACT = f"{ROOT_EVIDENCE}/multi-change-action-atomicity-contract.json"
NATIVE = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-native-analysis.md"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-review-packet.md"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-predispatch-receipt.json"
PRE_ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-review-receipt.json"
RECONCILIATION = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-gemini-report-reconciliation-incident.json"
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-269.md"
TEST = "tests/test_raisa_reception_one_multi_change_request_atomicity_orientation.py"
CLOSEOUT = (
    "docs/raisa-reception-one-multi-change-request-atomicity-orientation-closeout.md"
)
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-multi-change-request-atomicity-orientation.md"
UPDATER = "scripts/raisa_reception_one_multi_change_request_atomicity_orientation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_multi_change_request_atomicity_orientation_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT_SCHEMA,
        CONTRACT,
        NATIVE,
        PREFLIGHT,
        PACKET,
        PREDISPATCH,
        PRE_ACCEPTANCE,
        GEMINI,
        RECONCILIATION,
        REGISTER_REVISION,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One multi-change request atomicity orientation",
        "kind": "review",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Raisa and channel adapters may emit only typed inert action candidates; visible controls remain authorised-human presentation affordances and model authority remains zero.",
                "Time, duration and practitioner compose into one existing update-family proposal and confirmation, never a client sequence.",
                "Status remains a distinct command family; cross-family requests are non-executable and make no atomicity or rollback claim.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-multi-change-atomicity-orientation",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept typed inert candidates and one-family-owned command composition as the safe multi-change boundary.",
            }
        ],
        "claim_scope": [
            "The exact current update and status proposal/confirm families are mapped with directly proven, structurally supported and unproved claims kept distinct.",
            "Same-update-family composition is one patch, proposal, review and explicit confirmation; status-plus-update remains a non-executable review plan.",
            "Gemini passed 457 exact tests at unchanged clean source; AER-0308 reconciles only receipt command-count and Ruff wording.",
            "Evidence is repository_static_authored_synthetic and changes no product, API, database, adapter or runtime source.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, ARCHITECTURE, CONTRACT, CLOSEOUT],
                "note": "The semantic keyboard admits one-family multi-field meaning without granting Raisa or an adapter command authority.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [ARCHITECTURE, THREAT, CONTRACT, CLOSEOUT],
                "note": "Provisional requests remain distinct from fresh source truth and the kernel revalidates before any command.",
            },
        ],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [
                CONTRACT_SCHEMA,
                CONTRACT,
                NATIVE,
                RECONCILIATION,
                REGISTER_REVISION,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREFLIGHT, PACKET, PREDISPATCH, PRE_ACCEPTANCE, GEMINI],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Prove one existing update proposal/confirm transaction changing practitioner, time and duration together, including stale truth, conflict, idempotency, audit and rollback.",
            "No compound editor, conversational execution, patient-channel runtime or cross-family atomic command is implemented.",
            "Product data, providers, watcher/runtime, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-action-console progressive-disclosure composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One multi-change request atomicity orientation at exact source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`, the accepted Reception One selected-action-console progressive-disclosure composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One multi-change request atomicity orientation acceptance | `docs/raisa-reception-one-multi-change-request-atomicity-orientation-plan.md`, `docs/raisa-reception-one-multi-change-request-atomicity-architecture.md`, `docs/security/raisa-reception-one-multi-change-request-atomicity-orientation-threat-model-delta.md`, `orchestration/continuity/raisa-reception-one-multi-change-request-atomicity-orientation/`, `orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-native-analysis.md`, `orchestration/agent_inbox/antigravity/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-269.md`, `docs/raisa-reception-one-multi-change-request-atomicity-orientation-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-multi-change-request-atomicity-orientation.md`, `scripts/raisa_reception_one_multi_change_request_atomicity_orientation_continuity_update.py`, and `tests/test_raisa_reception_one_multi_change_request_atomicity_orientation_continuity.py` |"
    if row not in handover:
        anchor = next(
            line
            for line in handover.splitlines()
            if line.startswith("| Current result |")
        )
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 291 / Compass 273, `raisa_reception_one_multi_change_request_atomicity_orientation_pass` is accepted at exact reviewed source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`. Raisa and future adapters may emit only typed inert action candidates. Time, duration and practitioner may compose into one existing update-family proposal and human confirmation; status remains distinct and any cross-family request is non-executable. Gemini passed 457 exact tests at an unchanged clean candidate; AER-0308 reconciles only its receipt wording. No product or runtime source changed. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the provider-free authored-synthetic `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal`. Exercise the existing appointment update proposal/confirm path with changed time, duration and practitioner in one command, plus stale-current-truth, conflict, idempotency, audit and failure-injection rollback checks. Prefer tests over product changes and add no UI, new route, schema, command family or database migration. No external patient/channel runtime, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    register_prefix = "| Ariadne agent error and correction register acceptance |"
    register_index = next(
        i for i, line in enumerate(lines) if line.startswith(register_prefix)
    )
    lines[register_index] = lines[register_index].replace(
        "revisions 2-267 including current `docs/ariadne-agent-error-correction-register-revision-267.md`",
        "revisions 2-269 including current `docs/ariadne-agent-error-correction-register-revision-269.md`",
        1,
    )
    if "revision-269.md" not in lines[register_index]:
        raise SystemExit("Agent-error register handover anchor missing")

    track_index = next(
        i for i, line in enumerate(lines) if line.startswith("| Active product track |")
    )
    old = "A read-only multi-change request atomicity orientation is next before any compound edit or another command field."
    new = "The multi-change request atomicity orientation now freezes typed inert candidates: time, duration and practitioner may share one update proposal and confirmation, while status remains separate and cross-family requests are non-executable. The same-update-family multi-change kernel rehearsal is next before any compound editor or conversational activation."
    if old in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old, new, 1)
    elif new not in lines[track_index]:
        raise SystemExit("Active product track multi-change anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The selected-action-console progressive-disclosure composition now passes at
exact reviewed source `1d9e58fd2624f87b8b3def538297054999e7bef3`.
Reception One shows one current-truth summary, four route-inert native choices
and at most one existing field editor; abandoned drafts are discarded and
busy, confirmation, interruption and fresh-reconciliation states fail closed.
All four existing command paths remain distinct and unchanged. The next narrow
descendant is a provider-free read-only multi-change request atomicity
orientation before any compound edit or another command field is considered.
No watcher runtime, existing database/source access, persistence, product data,
external patient client, compound command, restart/unknown-commit claim,
provider, deployment, production or release is opened."""
    new_plan = """The provider-free multi-change request atomicity orientation now passes at
exact reviewed source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`.
Raisa and future adapters may emit only typed inert candidates. Time, duration
and practitioner may compose into one existing update-family proposal and one
explicit confirmation; status remains separate and cross-family requests stay
non-executable. The next narrow descendant is an authored-synthetic kernel
rehearsal of practitioner, time and duration together through the existing
update path, including stale truth, conflict, idempotency, audit and rollback.
No watcher runtime, existing product data, external patient client, new command
family, provider, deployment, production or release is opened."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan multi-change anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 290 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 291
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 291 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected multi-change orientation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze adapter-neutral multi-change meaning before any compound Reception One editor",
        "outcome": "One-family update composition is permitted; cross-family requests remain non-executable and model authority remains zero.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 272
        and compass["source_graph_revision"] == 290
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 273
        and compass["source_graph_revision"] == 291
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected multi-change orientation Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Let Raisa understand richer appointment requests without receiving a generic tool belt",
        "why_now": "The compact four-action console is implemented and needs an exact composition rule before compound UI or conversational activation.",
        "outcome": "Typed inert candidates now map same-update-family requests to one existing command and keep status-plus-update non-executable.",
        "unlocks": [
            "Rehearse practitioner, time and duration together through the existing update proposal/confirm kernel.",
            "Consider a later multi-field editor only after the exact kernel properties pass.",
        ],
        "does_not_solve": [
            "Successful practitioner/time/duration confirmation, exact replay and injected rollback remain unproved.",
            "No compound editor, cross-family transaction or conversational command execution is implemented.",
            "Patient channels, product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 291 / Compass 273. Multi-change meaning is frozen as typed inert candidates and one-family-owned commands; the same-update-family kernel rehearsal is next."
    )
    limit = "The multi-change orientation is repository-static architecture evidence; it does not prove a compound UI, live channel delegation or practitioner/time/duration transaction behavior."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 291
    compass["map_revision"] = 273
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    _update_handover_and_plan()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
