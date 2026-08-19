import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
ERROR_REGISTER = ROOT / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
CLOCKWORK_POINTER = ROOT / "orchestration/continuity/ariadne-governance-clockwork/current.json"
NODE_ID = "raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
SOURCE_HEAD = "da03039f637d3808c8785a6d6fc95309650044d9"
HTTP_NODE_ID = "raisa-provider-free-delete-confirm-http-route-convergence"
HTTP_SOURCE_HEAD = "c7a01edd96ebabf3ea2c07be89a5b405c9629853"
HTTP_POSTGRES_NODE_ID = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-http-"
    "integration-rehearsal"
)
HTTP_POSTGRES_SOURCE_HEAD = "fe5dbcb31b06b027285aa84ee3cafb4fbbffb9db"
EFFECTIVENESS_NODE_ID = "ariadne-recent-work-effectiveness-and-transport-repair"
EFFECTIVENESS_SOURCE_HEAD = "73bea42b37424ca3f53240d52f8e5c10120a5ce7"
CANCELLATION_NODE_ID = (
    "raisa-reception-one-selected-appointment-cancellation-composition"
)
CANCELLATION_SOURCE_HEAD = "856ebc3d832d5b64ce65c2e0732eaa63d926c600"
ORDINARY_REVIEW_NODE_ID = (
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
)
ORDINARY_CONVERGENCE_NODE_ID = (
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition"
)
ORDINARY_CONVERGENCE_SOURCE_HEAD = "bfac65298e1d4aaca85d1c9dcb20329ef298c485"
POST_CANCELLATION_ORIENTATION_NODE_ID = (
    "raisa-provider-free-read-only-post-cancellation-programme-orientation"
)
POST_CANCELLATION_ORIENTATION_SOURCE_HEAD = (
    "74da22d5372299eb2d2e38bb2266b76c89a97035"
)
ARRIVAL_CHECK_IN_REVIEW_NODE_ID = (
    "raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review"
)
ARRIVAL_CHECK_IN_REVIEW_SOURCE_HEAD = "3bed3eb32dd1b8723bf5aa6218963b757ebc0e3d"
CHECK_IN_ADAPTER_NODE_ID = (
    "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal"
)
CHECK_IN_ADAPTER_SOURCE_HEAD = "8de886c5148b3259428c8c517674f10ea92d937e"
EXACT_TOOL_HARNESS_NODE_ID = (
    "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-"
    "development-admission"
)
CURRENT_REPAIR_NODE_ID = "ariadne-post-native-harness-successor-resolution-repair"
CURRENT_REPAIR_SOURCE_HEAD = "2a31437f6da0defa2dc9247491f04d5b23c97608"
CURRENT_REVIEW_NODE_ID = (
    "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review"
)
CURRENT_REVIEW_SOURCE_HEAD = "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"
CLOCK_NODE_ID = (
    "ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal"
)
CLOCK_SOURCE_HEAD = "762cd8fd1a6493f4d4b82e24f97d851531b6f7f0"
ADMISSION_ARCHITECTURE_NODE_ID = (
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture"
)
ADMISSION_ARCHITECTURE_SOURCE_HEAD = "752b521c59f5b44bf46de0cf776a33ac74b8134d"
ADMISSION_KERNEL_NODE_ID = (
    "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
ADMISSION_KERNEL_SOURCE_HEAD = "4204ec6348abb0f92b1a30314699d4a469fa860a"
CLOCKWORK_ARCHITECTURE_NODE_ID = (
    "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
)
CLOCKWORK_ARCHITECTURE_SOURCE_HEAD = "f6cbd33fd3322754e06ac6dafa1503f5200e0803"
CLOCKWORK_REHEARSAL_NODE_ID = (
    "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
)
CLOCKWORK_REHEARSAL_SOURCE_HEAD = "a4044010e9f9319e149660ad889141a32cc8d000"
LIVE_CLOCKWORK_NODE_ID = (
    "ariadne-provider-free-clockwork-live-canonical-adoption-retirement"
)
LIVE_CLOCKWORK_SOURCE_HEAD = "9014e08a3fb4e3253759e0133d93c5aaf99a7ace"
LIVE_CLOCKWORK_PARENT_ID = (
    "ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal"
)
LIVE_CLOCKWORK_FLOOR_SOURCE_HEAD = "d03cc6386fdf3e2714881089514380d93824e160"
ROUTE_CONVERGENCE_SOURCE_HEAD = "c82c3a741053a9c8da260aa62e1a968af22bb54e"
UNMOUNTED_SOURCE_HEAD = "43e993a98ffec3f9ffe2740b0b38816bcb2d6adb"
ARCHITECTURE_SOURCE_HEAD = "9f0c166be2276d4e236dbdb4ed5657074ffbd0aa"
ROUTE_REVIEW_SOURCE_HEAD = "1cc75672abba6e011e0de03f26a3ad2ba9bae396"
BEHAVIOR_SOURCE_HEAD = "49dd2aaa72877adb844da4d0d5d5bb28039c90c8"
RISK_REFORM_SOURCE_HEAD = "51866ce084c33fce600b792c66b180927658ed9e"
SCAFFOLD_SOURCE_HEAD = "843769b415597f4545663d78044eaaad303c7692"
HARNESS_NODE_ID = (
    "ariadne-provider-free-continuity-journal-and-refinement-promotion-safeguards"
)
HARNESS_SOURCE_HEAD = "79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce"
REPRESENTABILITY_SOURCE_HEAD = "bc066a1b639c5c57cc72f2697c063c5842511840"
KERNEL_SOURCE_HEAD = "356b28a1750e7a7b379406e864f2a3501606938a"
READINESS_SOURCE_HEAD = "bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735"
EDITOR_SOURCE_HEAD = "daed421954d65c159871585559f45caa32d95aee"
ORIENTATION_ATOMICITY_SOURCE_HEAD = "fbb7ffb46e041bbfc193ff3a76b2f970c06dee58"
CONSOLE_SOURCE_HEAD = "1d9e58fd2624f87b8b3def538297054999e7bef3"
CONSOLE_ORIENTATION_SOURCE_HEAD = "2d602cfd822235977676bfe9ee8d8dc0a14714fe"
PRACTITIONER_SOURCE_HEAD = "f085fc98ead21a3e7929ee9adbda81abfc7542c9"
DURATION_SOURCE_HEAD = "f397a3706f3b870b8436eb3993bd90c6c0c742a8"
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


def test_continuity_and_compass_bind_risk_weighted_result_and_product_position() -> (
    None
):
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == compass["source_graph_revision"]
    if CLOCKWORK_POINTER.is_file():
        assert graph["nodes"][-1]["id"] == LIVE_CLOCKWORK_NODE_ID
        assert (
            graph["nodes"][-1]["coordinates"]["source_head"]
            == LIVE_CLOCKWORK_SOURCE_HEAD
        )
        assert graph["nodes"][-1]["relationships"] == [
            {"node_id": LIVE_CLOCKWORK_PARENT_ID, "relation": "builds_on"}
        ]
    else:
        assert graph["nodes"][-1]["id"] == LIVE_CLOCKWORK_PARENT_ID
        assert graph["nodes"][-1]["coordinates"]["source_head"] == (
            LIVE_CLOCKWORK_FLOOR_SOURCE_HEAD
        )
        assert graph["nodes"][-1]["relationships"] == [
            {
                "node_id": "ariadne-provider-free-clockwork-governance-projection-consolidation-repair",
                "relation": "builds_on",
            }
        ]
    assert compass["map_revision"] > 0
    assert compass["current_position"]["node_id"] == graph["nodes"][-1]["id"]


def test_live_baton_rows_accept_behavior_and_resume_narrow_product_work() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    clockwork_active = (
        CLOCKWORK_POINTER.is_file()
        and json.loads(CLOCKWORK_POINTER.read_text(encoding="utf-8")).get("phase")
        == "clockwork_active"
    )
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    product = _table_row(text, "Active product track")
    next_work = _table_row(text, "Next implementation")
    implementation_relation = _table_row(
        text, "Current delete-confirm implementation source"
    )
    reform_relation = _table_row(text, "Ariadne risk-weighted reform Git relation")
    ordinary_relation = _table_row(text, "Current ordinary Diary cancellation relation")
    orientation_relation = _table_row(text, "Current arrival/check-in convergence relation")
    clockwork_relation = _table_row(
        text,
        "Current clockwork relation"
        if clockwork_active
        else "Current shadow clockwork relation",
    )
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    assert f"Continuity {graph['graph_revision']} / Compass {compass['map_revision']}" in current
    assert graph["nodes"][-1]["coordinates"]["source_head"] in current
    if clockwork_active:
        assert "ten repository-governance surfaces" in current.lower()
        assert "one clockwork owner" in current.lower()
        assert "previous git generation" in current.lower()
        assert LIVE_CLOCKWORK_SOURCE_HEAD in clockwork_relation
        assert LIVE_CLOCKWORK_FLOOR_SOURCE_HEAD in clockwork_relation
    else:
        assert "exclusive mirror ownership" in current.lower()
        assert "23/23 fault safety" in current.lower()
        assert "actual canonical adoption and retirement flags remain false" in current.lower()
        assert CLOCKWORK_ARCHITECTURE_SOURCE_HEAD in clockwork_relation
        assert CLOCKWORK_REHEARSAL_SOURCE_HEAD in clockwork_relation
    error_register = _table_row(
        text, "Ariadne agent error and correction register acceptance"
    ).lower()
    register = json.loads(ERROR_REGISTER.read_text(encoding="utf-8"))
    assert "revision " in error_register
    assert "bounded incidents" in error_register
    assert f"revision {register['register_revision']}" in error_register
    assert f"{len(register['incidents'])} bounded incidents" in error_register
    assert register["incidents"][-1]["incident_id"].lower() in error_register
    assert RISK_REFORM_SOURCE_HEAD in reform_relation
    assert BEHAVIOR_SOURCE_HEAD in reform_relation
    assert ARCHITECTURE_SOURCE_HEAD in relation
    assert SOURCE_HEAD in implementation_relation
    assert UNMOUNTED_SOURCE_HEAD in implementation_relation
    assert HTTP_SOURCE_HEAD in implementation_relation
    assert HTTP_POSTGRES_SOURCE_HEAD in implementation_relation
    assert HTTP_SOURCE_HEAD in implementation_relation
    assert HTTP_POSTGRES_SOURCE_HEAD in implementation_relation
    assert ROUTE_REVIEW_SOURCE_HEAD in relation
    assert "cancellation" in product.lower()
    assert "accepted reusable unmounted adapter" in product.lower()
    assert CHECK_IN_ADAPTER_SOURCE_HEAD in product
    assert ORDINARY_CONVERGENCE_SOURCE_HEAD in ordinary_relation
    assert POST_CANCELLATION_ORIENTATION_SOURCE_HEAD in orientation_relation
    assert CHECK_IN_ADAPTER_SOURCE_HEAD in orientation_relation
    assert CHECK_IN_ADAPTER_SOURCE_HEAD in relation
    assert CANCELLATION_SOURCE_HEAD in relation
    assert REPRESENTABILITY_SOURCE_HEAD in relation
    assert KERNEL_SOURCE_HEAD in relation
    assert READINESS_SOURCE_HEAD in relation
    assert EDITOR_SOURCE_HEAD in relation
    assert ORIENTATION_ATOMICITY_SOURCE_HEAD in relation
    assert CONSOLE_SOURCE_HEAD in relation
    assert CONSOLE_ORIENTATION_SOURCE_HEAD in relation
    assert PRACTITIONER_SOURCE_HEAD in relation
    assert DURATION_SOURCE_HEAD in relation
    assert TIME_RESCHEDULE_SOURCE_HEAD in relation
    assert TRUTH_PARITY_SOURCE_HEAD in relation
    assert STATUS_COMPOSITION_SOURCE_HEAD in relation
    assert CF_D2_SOURCE_HEAD in relation
    assert ORIENTATION_SOURCE_HEAD in relation
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert COMPOSITION_SOURCE_HEAD in relation
    assert ADMISSION_KERNEL_SOURCE_HEAD in relation
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
    if clockwork_active:
        assert "clockwork-governed-check-in-successor-resolution" in next_work.lower()
        assert "provider-free and read-only" in next_work.lower()
        assert "occupied deepseek/hmr" in next_work.lower()
        assert "ordinary-practice enablement" in next_work.lower()
        assert "product/data/runtime" in next_work.lower()
        assert "protected-ref movement" in next_work.lower()
    else:
        assert "explicit adoption boundary" in next_work.lower()
        assert "live canonical clockwork adoption/retirement" in next_work.lower()
        assert "no dual writer" in next_work.lower()
        assert "exact rollback" in next_work.lower()
        assert "canonical-check-in-route-adapter-convergence-rehearsal" in next_work.lower()
        assert "neither branch is inferred" in next_work.lower()
        assert "occupied deepseek/hmr" in next_work.lower()
        assert "product/practice/data/runtime" in next_work.lower()
        assert "protected-ref movement" in next_work.lower()
    assert "primeintellect" not in next_work.lower()
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
    clockwork_active = (
        CLOCKWORK_POINTER.is_file()
        and json.loads(CLOCKWORK_POINTER.read_text(encoding="utf-8")).get("phase")
        == "clockwork_active"
    )
    phrases = (
        (
            "clockwork-governed-check-in-successor-resolution",
            "provider-free and read-only",
            "occupied deepseek/hmr",
            "ordinary-practice enablement",
            "product/data/runtime",
            "deployment",
            "protected-ref movement",
            "docs/branding/",
            "stage explicit paths only",
        )
        if clockwork_active
        else (
            "explicit adoption boundary",
            "live canonical clockwork adoption/retirement",
            "no dual writer",
            "exact rollback",
            "canonical-check-in-route-adapter-convergence-rehearsal",
            "neither branch is inferred",
            "occupied deepseek/hmr",
            "product/practice/data/runtime",
            "deployment",
            "protected-ref movement",
            "docs/branding/",
            "stage explicit paths only",
        )
    )
    for phrase in phrases:
        assert phrase in next_work
    assert "single-owner-migration-retirement-rehearsal" not in next_work
