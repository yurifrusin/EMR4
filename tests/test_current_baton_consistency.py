import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
NODE_ID = "raisa-reception-one-selected-appointment-duration-composition"
SOURCE_HEAD = "f397a3706f3b870b8436eb3993bd90c6c0c742a8"
TIME_RESCHEDULE_SOURCE_HEAD = "d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a"
TRUTH_PARITY_SOURCE_HEAD = "18aa4b613d735a68a7f6f2e55d34e498176c9935"
STATUS_COMPOSITION_SOURCE_HEAD = "b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33"
ORIENTATION_SOURCE_HEAD = "edba8f57380a48fd98decc332608349f2d9012e6"
CF_D2_SOURCE_HEAD = "f4bd8ca5ec0654f8be7b1d2d74b1aca444038ee9"
STATUS_CONFIRM_SOURCE_HEAD = "b414eb256853c301099d9cf7797a69cd3ec077c5"
INTEGRATION_SOURCE_HEAD = "553d38c37af86ceefc7b4315b8eaa171d405ab95"
ADAPTER_SOURCE_HEAD = "b728b903c99fa35f231df04ba68263533261121a"
COMPOSITION_SOURCE_HEAD = "41f978ae9837cba50737cfb5f457ab62ac28dbdb"
PROTECTED_SHA = "2e34bdad732fdab32fbf778280b3d3c70d66d602"


def _table_row(text: str, label: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, f"expected one AGENTS row for {label}"
    return matches[0]


def test_continuity_and_compass_bind_the_live_duration_composition() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 287
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 269
    assert compass["source_graph_revision"] == 287
    assert compass["current_position"]["node_id"] == NODE_ID


def test_live_baton_rows_accept_duration_and_name_practitioner_next() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    next_work = _table_row(text, "Next implementation")

    assert "Continuity 287 / Compass 269" in current
    assert (
        "raisa_reception_one_selected_appointment_duration_composition_pass"
        in current
    )
    assert SOURCE_HEAD in current
    assert "existing update proposal/confirm path" in current
    assert "Twelve paired traces" in current
    assert "eight fresh-truth fields" in current
    assert SOURCE_HEAD in relation
    assert TIME_RESCHEDULE_SOURCE_HEAD in relation
    assert TRUTH_PARITY_SOURCE_HEAD in relation
    assert STATUS_COMPOSITION_SOURCE_HEAD in relation
    assert CF_D2_SOURCE_HEAD in relation
    assert ORIENTATION_SOURCE_HEAD in relation
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert COMPOSITION_SOURCE_HEAD in relation
    assert ADAPTER_SOURCE_HEAD in relation
    assert INTEGRATION_SOURCE_HEAD in relation
    assert "28cd0ce6639fd831960c57d5289b08f3d36ca3fb" in relation
    assert "fe8313d224a92115aa31bea14f0cd3b14e4c9967" in relation
    assert "018099dd6c5f0502121360732feb602252eb34cc" in relation
    assert "037eed060d4519f2f3d6721135143ecb6f70e358" in relation
    assert "f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c" in relation
    assert "47e08eada878d8f6dd2a9b100e706404d3594e5a" in relation
    assert "beb4e65cddf72437948d72e08dd18c2ea4f0c609" in relation
    assert "e1dca1c6dc5d3f3e241548f80a226e5bb776417f" in relation
    assert "47b5f09ecf35225da25812ba87bb656a1094fc7e" in relation
    assert "ed52950f451af88892a8f469157ecf8c8567da81" in relation
    assert "410ea6dbbe28b94cfaa83ac5f6b586910c77aa6a" in relation
    assert "78cbcca756476fddfd0fda4b4d1241f195b21ab6" in relation
    assert "9c7444ecce69b51ca5cac80818e8997724a11f13" in relation
    assert "48c1821ad8b28c68204e70dea9972b6ba27e4dc1" in relation
    assert "bd381de83bc0b5d4b6b43b4bbb4e1e70a68d7f62" in relation
    assert "30a49015d23bfcf069be0af838df7091032a40be" in relation
    assert "426ccbbd26a2ab0bfb70c65d7adce113f0239f3a" in relation
    assert "b9cc57b6e607e5896e822abc7b632442df2f907e" in relation
    assert "a1629f2441e2bdb350d00c6d6016e94123ff0d8d" in relation
    assert "530a1d479a48242df6985886acdbb796550e9093" in relation
    assert "826aad11c29007b13eaa377e3f7ea494cc82ce70" in relation
    assert "practitioner-only reassignment" in next_work
    assert "same existing update proposal/confirm path" in next_work
    assert "mandatory DeepSeek/Gemini/native-subagent" in next_work
    assert "product/patient data" in next_work
    assert "provider/ADC" in next_work
    assert "attempt-016" not in relation.lower()
    assert "attempt 016" not in relation.lower()
    assert "attempt-016" not in next_work.lower()
    assert "attempt 016" not in next_work.lower()


def test_master_plan_and_handover_contain_no_stale_next_work_instruction() -> None:
    handover = AGENTS.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())

    stale_review_next = (
        "The next recommended tranche is the bounded read-only "
        "architectural-health/conformance pulse"
    )
    stale_pause = "conformance pulse is next after Yuri's requested closeout pause"
    assert stale_review_next not in handover
    assert stale_pause not in plan
    assert "conformance repair named in that review now also" in compact_plan
    assert (
        "AES-C0 architecture, AES-C1 provider-free admission, AES-C2 inert broker simulation, AES-C3 provider-free hostile containment, AES-C4 bounded occupied authored- synthetic provider proof and AES-C5 product-runtime admission now pass"
        in compact_plan
    )
    assert (
        "The finite AES-C0 through AES-C5 sequence is complete; no AES-C6 is planned or authorised"
        in compact_plan
    )
    assert "five transaction protocols remain unproved" not in compact_plan
    assert "provider-free behavior/transaction rehearsal is next" not in compact_plan


def test_current_rows_preserve_closed_surface_boundary() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    next_work = _table_row(text, "Next implementation").lower()
    for phrase in (
        "practitioner-only reassignment",
        "date, start time, duration and every unrelated field",
        "limit targets to existing active practitioners",
        "zero raw or second command path",
        "no backend/api/openapi/graphql/database/event/watcher expansion",
        "cross-day move",
        "product/patient data",
        "provider/adc",
        "credentials/iam/network",
        "docs/branding/",
        "deploy",
        "release",
        "pages",
        "protected-ref movement",
        "explicit-path staging only",
    ):
        assert phrase in next_work
