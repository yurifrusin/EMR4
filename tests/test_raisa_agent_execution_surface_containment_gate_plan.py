from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-agent-execution-surface-containment-gate-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-agent-execution-surface-containment-gate-threat-model-delta.md"
)
FABRIC = ROOT / "docs" / "raisa-practice-context-fabric-direction.md"
MASTER = ROOT / "implementation_plan.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_containment_gate_is_placed_after_database_only_durability() -> None:
    plan = _text(PLAN)
    fabric = _text(FABRIC)

    assert "after the current provider-free Context Fabric durability" in plan
    assert "does not block the current disposable PostgreSQL behavior/" in plan
    assert fabric.index(
        "16. **Disposable behavior/transaction rehearsal**"
    ) < fabric.index("17. **Agent Execution Surface and Containment Gate**")
    assert fabric.index(
        "17. **Agent Execution Surface and Containment Gate**"
    ) < fabric.index("18. **Real product read descendants**")


def test_selected_boundary_is_external_and_generation_scoped() -> None:
    plan = _text(PLAN)

    required = {
        "central capability-broker design",
        "No ambient authority",
        "Metadata denial",
        "Immutable generation manifest",
        "Exact egress",
        "Cumulative limits",
        "Generation revocation",
        "External kill switch",
        "Supply-chain identity",
    }
    assert all(item in plan for item in required)
    assert "intelligence never increases authority" in plan


def test_api_spine_and_context_authority_remain_separate() -> None:
    plan = _text(PLAN)

    assert "does not add a GraphQL mutation or generic command tunnel" in plan
    assert "single-purpose REST/OpenAPI command plane" in plan
    assert "`command_authority: false`" in plan
    assert "cannot confirm it for the user" in plan


def test_finite_descendants_and_hostile_set_are_recorded() -> None:
    plan = _text(PLAN)

    for gate in ("AES-C0", "AES-C1", "AES-C2", "AES-C3", "AES-C4", "AES-C5"):
        assert gate in plan
    for challenge in (
        "HDF5-style external storage",
        "template",
        "metadata",
        "encoded",
        "exception-message",
        "stale tokens",
        "cross-generation",
    ):
        assert challenge in plan


def test_threat_delta_closes_ambient_authority_and_command_bypass() -> None:
    threat = _text(THREAT)

    assert "Work cell has no credential" in threat
    assert "Cumulative denial/action/time/destination budget" in threat
    assert "Model selects executable, SQL, route or cleanup target" in threat
    assert "Command-shaped candidate remains inert" in threat
    assert "externally owned automatic stop/revoke" in threat


def test_master_plan_records_gate_without_opening_runtime() -> None:
    master = _text(MASTER)

    assert "### 2.12 Agent Execution Surface and Containment Gate" in master
    assert "does not delay the networkless database-only rehearsal" in master
    assert "grants no continuing provider call, real product context" in master
    assert (
        "read, credential flow, provider tool, command, deployment or production"
        in master
    )
