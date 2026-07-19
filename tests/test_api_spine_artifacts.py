"""
Deterministic validation tests for Sprint 101 API Spine prototype artifacts.
"""

import re
from pathlib import Path

import pytest

SPINE_DIR = Path("docs/api-spine")
PERMISSION_MATRIX = SPINE_DIR / "security" / "permission-matrix.yaml"
INTEGRATION_EVENTS = SPINE_DIR / "async" / "integration-events.yaml"
AGENT_CAPABILITY_CHARTERS = (
    SPINE_DIR / "manifests" / "agent-capability-charters.yaml"
)


def _files_under(subdir, *suffixes):
    target = SPINE_DIR / subdir
    if not target.is_dir():
        return []
    result = []
    for child in target.iterdir():
        if child.is_file() and any(
            child.name.lower().endswith(suf.lower()) for suf in suffixes
        ):
            result.append(child)
    return sorted(result)


def _all_files_under(subdir):
    target = SPINE_DIR / subdir
    if not target.is_dir():
        return []
    return sorted(p for p in target.rglob("*") if p.is_file())


# Forbidden field patterns (lowercase)
BANNED = frozenset({
    "provider prompt", "provider_response", "model_output",
    "gemini", "llm", "raw_model", "ai_provider",
    "historical_diary", "diary_trove", "h15_", "h_series",
    "semantic_candidate", "local_data", "ignored_local",
    "raw_phil", "raw_text", "phil_bearing",
    "unrestricted_notes", "all_patient_notes", "raw_clinical",
})

# Section markers whose children declare exclusions.
_ALLOW_SECTION_MARKERS = frozenset({
    "must_not:", "blocked_gates:", "forbidden:",
})

# Terms on the same line that prove the line declares an exclusion.
_SAME_LINE_EXCLUSION_TERMS = frozenset({
    "blocked", "deny", "denied", "gate_closed",
})


def _is_under_blocking_section(lines, idx):
    """Return True if lines[idx] is indented under a section marker that
    declares excluded capabilities."""
    line = lines[idx]
    if not line.strip():
        return False
    # Fast-path: line itself declares exclusion
    line_lower = line.lower()
    for term in _SAME_LINE_EXCLUSION_TERMS:
        if term in line_lower:
            return True
    indent = len(line) - len(line.lstrip())
    for j in range(idx - 1, -1, -1):
        prev = lines[j]
        if not prev.strip():
            continue
        prev_indent = len(prev) - len(prev.lstrip())
        if prev_indent >= indent:
            continue
        stripped = prev.strip()
        if stripped in _ALLOW_SECTION_MARKERS:
            return True
        # Also accept default_deny / defaults + deny pattern
        if stripped in ("defaults:", "default_deny:"):
            return True
        break
    return False


def _strip_comments(text, lang="graphql"):
    tq = chr(34) * 3
    if lang == "graphql":
        text = re.sub(tq + r'[^' + chr(34) + r']*' + tq, "", text, flags=re.DOTALL)
        lines = [L for L in text.splitlines() if not L.strip().startswith("#")]
        return "\n".join(lines)
    if lang in ("yaml", "yml"):
        lines = [L for L in text.splitlines() if not L.strip().startswith("#")]
        return "\n".join(lines)
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _check_no_forbidden(path, lang="graphql"):
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = _strip_comments(raw, lang=lang)
    lines = clean.splitlines()

    hits = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Skip lines that declare something as excluded/blocked
        if _is_under_blocking_section(lines, i):
            continue
        for pat in BANNED:
            if pat.lower() in line_lower:
                hits.append((line.strip()[:80], pat))
                break

    assert not hits, (
        f"{path} contains forbidden patterns in non-exclusion content:\n"
        + "\n".join(f"  [{pat}] {text}" for text, pat in hits)
        + "\nThe ADR forbids provider prompts, raw model responses, "
        "raw diary trove/H15/H-series fixtures, ignored local outputs, "
        "broad tenant introspection, and unrestricted clinical note dumps."
    )


def _load_yaml_file(path):
    pytest.importorskip("yaml", reason="PyYAML not installed.")
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


class TestSpineDirectoryExists:

    def test_spine_root_is_directory(self):
        assert SPINE_DIR.is_dir(), f"Sprint 101 root {SPINE_DIR} missing."

    def test_spine_subdirectories_present(self):
        expected = {"graphql", "async", "manifests", "security"}
        actual = {d.name for d in SPINE_DIR.iterdir() if d.is_dir()}
        missing = expected - actual
        assert not missing, f"Missing subdirs: {sorted(missing)}."


class TestGraphQLArtifact:

    def _find_sdl(self):
        candidates = _files_under("graphql", ".graphql", ".gql", ".sdl", ".graphqls")
        assert candidates, "No GraphQL SDL under docs/api-spine/graphql/."
        return candidates[0]

    def test_graphql_sdl_file_exists(self):
        p = self._find_sdl()
        assert p.read_bytes(), f"{p} is empty."

    def test_graphql_has_no_mutation_type(self):
        text = self._find_sdl().read_text(encoding="utf-8")
        assert "type Mutation" not in text, "GraphQL SDL has type Mutation."

    def test_graphql_has_query_type(self):
        text = self._find_sdl().read_text(encoding="utf-8")
        assert "type Query" in text, "GraphQL SDL missing type Query."

    def test_graphql_no_forbidden_field_patterns(self):
        _check_no_forbidden(self._find_sdl(), lang="graphql")

    def test_graphql_schema_is_not_mutation_forwarding(self):
        clean = _strip_comments(
            self._find_sdl().read_text(encoding="utf-8"), lang="graphql"
        )
        suspicious = [L for L in clean.splitlines() if "mutation" in L.lower()]
        assert not suspicious, f"Non-comment mutation refs: {suspicious}."


class TestOpenAPICommandArtifact:

    OPENAPI_DIRS = ("openapi", "async")

    def _find_openapi(self):
        for sub in self.OPENAPI_DIRS:
            dirpath = SPINE_DIR / sub
            if dirpath.is_dir():
                candidates = _files_under(sub, ".yaml", ".yml", ".json")
                for c in candidates:
                    text = c.read_text(encoding="utf-8", errors="replace")
                    if "openapi" in text.lower() or "swagger" in text.lower():
                        return c
                if candidates:
                    return candidates[0]
        assert False, "No OpenAPI artifact found."

    def test_openapi_artifact_exists(self):
        p = self._find_openapi()
        assert p.read_bytes(), f"{p} is empty."

    def test_openapi_includes_idempotency_key(self):
        text = self._find_openapi().read_text(encoding="utf-8")
        assert ("Idempotency-Key" in text or "idempotency-key" in text.lower()), \
            "Missing Idempotency-Key."

    def test_openapi_includes_confirm_and_proposal_paths(self):
        text = self._find_openapi().read_text(encoding="utf-8").lower()
        assert "proposal" in text, "Missing proposal reference."
        assert "confirm" in text, "Missing confirm reference."

    def test_openapi_includes_warnings_and_blocks(self):
        text = self._find_openapi().read_text(encoding="utf-8").lower()
        assert "warning" in text or "warnings" in text, "Missing warnings."
        assert "block" in text or "blocks" in text, "Missing blocks."

    def test_openapi_includes_audit_and_confirmer(self):
        text = self._find_openapi().read_text(encoding="utf-8").lower()
        assert "audit" in text, "Missing audit."
        assert any(kw in text for kw in ("confirmer", "staff_confirmation", "confirming")), \
            "Missing confirmer identity."

    def test_openapi_no_forbidden_field_patterns(self):
        _check_no_forbidden(self._find_openapi(), lang="yaml")


class TestYAMLManifests:

    def test_manifests_directory_has_files(self):
        files = _all_files_under("manifests")
        assert files, "No files under docs/api-spine/manifests/."

    def test_yaml_import_available(self):
        pytest.importorskip("yaml", reason="PyYAML not installed.")

    def test_manifests_include_default_deny_or_blocked(self):
        """Manifests must include default-deny, deny, or blocked language."""
        pytest.importorskip("yaml", reason="PyYAML not installed.")
        files = _all_files_under("manifests")
        assert files, "No manifest files."
        import yaml
        found = False
        for f in files:
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data is None:
                continue
            t = str(data).lower()
            if any(kw in t for kw in ("default-deny", "default_deny", "deny", "blocked")):
                found = True
                break
        assert found, (
            "No manifest has default-deny, deny, or blocked language. "
            "At least one of these is required per the ADR."
        )

    def test_manifests_include_blocked_gate_language(self):
        pytest.importorskip("yaml", reason="PyYAML not installed.")
        files = _all_files_under("manifests")
        assert files, "No manifest files."
        import yaml
        found = False
        for f in files:
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data is None:
                continue
            t = str(data).lower()
            if "blocked" in t or "gate" in t:
                found = True
                break
        assert found, "No manifest has blocked/gate."

    def test_manifests_no_forbidden_field_patterns(self):
        pytest.importorskip("yaml", reason="PyYAML not installed.")
        files = _all_files_under("manifests")
        if not files:
            pytest.skip("No manifest files.")
        for f in files:
            _check_no_forbidden(f, lang="yaml")


class TestAsyncEventContracts:

    def test_async_directory_has_files(self):
        files = _all_files_under("async")
        assert files, "No files under docs/api-spine/async/."

    def test_async_contracts_no_forbidden_field_patterns(self):
        files = _all_files_under("async")
        if not files:
            pytest.skip("No async files.")
        for f in files:
            _check_no_forbidden(f, lang="yaml")


class TestSecurityArtifacts:

    def test_security_directory_has_files(self):
        files = _all_files_under("security")
        assert files, "No files under docs/api-spine/security/."

    def test_security_includes_default_deny(self):
        pytest.importorskip("yaml", reason="PyYAML not installed.")
        files = _all_files_under("security")
        assert files, "No security files."
        import yaml
        found = False
        for f in files:
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data is None:
                continue
            t = str(data).lower()
            if "default-deny" in t or "default_deny" in t:
                found = True
                break
        assert found, "No security artifact has default-deny."

    def test_security_no_forbidden_field_patterns(self):
        files = _all_files_under("security")
        if not files:
            pytest.skip("No security files.")
        for f in files:
            _check_no_forbidden(f, lang="yaml")


class TestBernieCommittedEventAwarenessDesign:

    @staticmethod
    def _diary_family():
        data = _load_yaml_file(INTEGRATION_EVENTS)
        families = [
            family
            for family in data["event_families"]
            if family["family_id"] == "diary"
        ]
        assert len(families) == 1
        return data, families[0]

    @staticmethod
    def _bernie_charter():
        data = _load_yaml_file(AGENT_CAPABILITY_CHARTERS)
        agents = [
            agent for agent in data["agents"] if agent["agent_id"] == "bernie"
        ]
        assert len(agents) == 1
        return data, agents[0]

    def test_proactive_diary_runtime_remains_blocked(self):
        events, _ = self._diary_family()
        charters, bernie = self._bernie_charter()

        assert events["source_safety"]["proactive_diary_delivery_runtime"] == "blocked"
        assert events["blocked_gates"]["proactive_diary_delivery_runtime"] == "blocked"
        assert charters["source_safety"]["proactive_diary_delivery_runtime"] == "blocked"
        assert bernie["blocked_gates"]["proactive_diary_delivery_runtime"] == "blocked"

    def test_diary_events_are_committed_typed_signals_not_commands(self):
        _, diary = self._diary_family()
        delivery = diary["delivery_semantics"]
        commands = diary["command_boundary"]

        assert delivery["publish_after_commit_only"] is True
        assert delivery["transactional_outbox_or_equivalent_required"] is True
        assert delivery["stable_event_identity_required"] is True
        assert delivery["aggregate_revision_required"] is True
        assert delivery["user_visible_deduplication_required"] is True
        assert delivery["fresh_scoped_read_before_display"] is True
        assert commands["event_is_command_authority"] is False
        assert commands["appointment_mutation_requires_rest_command"] is True
        assert commands["staff_confirmation_required_for_mutation"] is True

    def test_diary_event_attention_contract_is_low_interruption(self):
        _, diary = self._diary_family()
        attention = diary["attention_boundary"]

        assert attention["low_interruption_filter_required"] is True
        assert attention["practice_role_resource_recheck_required"] is True
        assert attention["unrelated_event_suppression_required"] is True
        assert attention["explain_why_required"] is True
        assert attention["automatic_spoken_phi"] is False
        assert {
            "dismiss",
            "snooze",
            "mute_event_family",
            "show_context",
        } <= set(attention["user_controls"])

    def test_diary_event_payload_excludes_free_text_and_direct_identifiers(self):
        _, diary = self._diary_family()

        assert {
            "patient_name",
            "phone_number",
            "date_of_birth",
            "medicare_number",
            "appointment_reason_text",
            "appointment_note",
            "raw_instruction",
            "free_text_transcript",
            "provider_output",
            "credential",
        } <= set(diary["prohibited_payload_fields"])

    def test_bernie_event_frame_requires_fresh_read_and_never_grants_action(self):
        _, bernie = self._bernie_charter()
        event_frames = [
            frame
            for frame in bernie["allowed_context_frames"]
            if frame["frame"] == "committed_diary_event_context"
        ]

        assert len(event_frames) == 1
        assert event_frames[0]["committed_only"] is True
        assert event_frames[0]["fresh_scoped_read_before_display"] is True
        assert "surface_low_interruption_committed_diary_change" in bernie["may"]
        assert "treat_event_as_command_authority" in bernie["must_not"]
        assert (
            "use_event_payload_as_substitute_for_fresh_authorized_read"
            in bernie["must_not"]
        )


class TestSecurityPermissionArtifacts:

    def test_permission_matrix_enterprise_auth_boundary_is_static_only(self):
        data = _load_yaml_file(PERMISSION_MATRIX)

        assert data["status"] == "prototype_only"
        assert data["artifact_kind"] == "non_invasive_permission_fixture_example"
        assert data["source_safety"]["enterprise_auth_fga_boundary"] == "static_mapping_only"

        blocked_source_flags = {
            "runtime_fga_clients",
            "runtime_wiring",
            "provider_calls",
            "live_provider_opening",
            "external_patient_clients",
            "graph_ql_mutations",
            "historical_diary_trove_access",
            "h15_or_h_series_runtime_imports",
            "memory_rag_graphrag",
            "model_to_database_writes",
        }
        for flag in blocked_source_flags:
            assert data["source_safety"][flag] == "blocked"

    def test_permission_matrix_keeps_access_ai_boundary_gates_closed(self):
        data = _load_yaml_file(PERMISSION_MATRIX)

        required_blocked_gates = {
            "runtime_fga_clients",
            "live_provider_runtime",
            "external_patient_clients",
            "broad_historical_diary_trove_mining",
            "h15_h_series_runtime_imports",
            "memory_rag_graphrag_runtime",
            "graph_ql_mutations",
            "model_to_database_writes",
        }
        assert required_blocked_gates <= set(data["blocked_gates"])
        for gate in required_blocked_gates:
            assert data["blocked_gates"][gate]["decision"] == "deny"

    def test_permission_matrix_allow_examples_do_not_enable_blocked_runtime_surfaces(self):
        data = _load_yaml_file(PERMISSION_MATRIX)

        prohibited_fragments = {
            "runtime_fga_client",
            "runtime_fga_clients",
            "live_provider_runtime",
            "live_provider_opening",
            "external_patient_client",
            "external_patient_clients",
            "graph_ql_mutation",
            "graphql_mutation",
            "memory_rag_graphrag",
            "graphrag_runtime",
            "historical_diary_trove",
            "h15_or_h_series",
            "model_to_database_write",
            "database_write",
            "writes_authorized",
        }

        hits = []
        for idx, example in enumerate(data["allow_examples"]):
            serialized = repr(example).lower()
            for fragment in prohibited_fragments:
                if fragment in serialized:
                    hits.append((idx, fragment, example))
        assert not hits, (
            "Permission allow_examples must stay role/action/resource examples "
            "and must not imply runtime FGA clients, live providers, external "
            "patient clients, GraphQL mutations, memory/RAG/GraphRAG, H15/trove "
            f"access, or model-to-database writes: {hits}"
        )


class TestEvidenceLabels:

    def _all_text(self):
        parts = []
        for f in SPINE_DIR.rglob("*"):
            if f.is_file():
                try:
                    parts.append(f.read_text(encoding="utf-8", errors="replace").lower())
                except Exception:
                    continue
        return "\n".join(parts)

    def test_evidence_label_fixture_present(self):
        assert "fixture" in self._all_text(), "Missing fixture."

    def test_evidence_label_intercepted_present(self):
        assert "intercepted" in self._all_text(), "Missing intercepted."

    def test_evidence_label_fake_present(self):
        assert "fake" in self._all_text(), "Missing fake."

    def test_evidence_label_live_present(self):
        assert "live" in self._all_text(), "Missing live."

    def test_evidence_distinctions_not_only_in_one_artifact(self):
        label_paths = {}
        for label in ("fixture", "intercepted", "fake", "live"):
            label_paths[label] = []
            for f in SPINE_DIR.rglob("*"):
                if f.is_file():
                    try:
                        if label in f.read_text(encoding="utf-8", errors="replace").lower():
                            label_paths[label].append(f)
                    except Exception:
                        continue
        subdirs = set()
        for files in label_paths.values():
            for f in files:
                subdirs.add(f.relative_to(SPINE_DIR).parts[0])
        assert len(subdirs) >= 2, f"Evidence labels in only {subdirs}."
