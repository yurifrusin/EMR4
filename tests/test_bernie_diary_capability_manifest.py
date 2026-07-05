from dataclasses import FrozenInstanceError
from typing import Any
import json
import re

import pytest

from app.models.appointments import AppointmentStatus
from app.schemas.appointments import STATUS_REASON_CODES, STATUS_SPECIFIC_REASON_CODE_POLICY
from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.diary.capability_manifest import (
    MANIFEST_SCHEMA_VERSION,
    build_bernie_diary_capability_manifest,
)
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS, DiaryConfirmAction
from app.services.diary.envelopes import DiaryActionAuthor, DiaryActionSuggestion
from app.services.diary.outcomes import BernieBookingOutcomeKind
from app.services.diary.schedule_explanations import DiaryScheduleExplanationReason


def test_manifest_has_expected_schema_and_authority_statement():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert "read-only context" in manifest["authority_statement"]
    assert "cannot authorize writes" in manifest["authority_statement"]
    assert "schema-literate, not code-authoritative" in manifest["principles"][0]


def test_manifest_appointment_statuses_match_backend_enum():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["entities"]["appointment_statuses"]["values"] == [
        status.value for status in AppointmentStatus
    ]
    assert manifest["entities"]["appointment_statuses"]["authority"] == "source_of_truth"


def test_manifest_reason_codes_match_backend_sources():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["reason_codes"]["appointment_status_reason_codes"] == sorted(STATUS_REASON_CODES)
    assert manifest["reason_codes"]["status_specific_reason_code_policy"] == {
        status.value: sorted(codes)
        for status, codes in STATUS_SPECIFIC_REASON_CODE_POLICY.items()
    }
    assert manifest["reason_codes"]["schedule_reason_codes"] == [
        reason.value for reason in DiaryScheduleExplanationReason
    ]
    assert "frontend" in manifest["reason_codes"]["drift_note"].lower()


def test_manifest_capabilities_are_source_derived_and_non_authoritative():
    manifest = build_bernie_diary_capability_manifest()
    manifest_capabilities = manifest["capabilities"]["items"]

    assert len(manifest_capabilities) == len(BERNIE_CAPABILITY_REGISTRY)
    assert manifest["capabilities"]["authority"] == "declared_not_enforced"
    assert "future work" in manifest["capabilities"]["note"]

    registry_by_name = {capability.name: capability for capability in BERNIE_CAPABILITY_REGISTRY}
    manifest_by_name = {capability["name"]: capability for capability in manifest_capabilities}
    assert set(manifest_by_name) == set(registry_by_name)

    for name, capability in registry_by_name.items():
        row = manifest_by_name[name]
        assert row["tier"] == capability.tier.value
        assert row["summary"] == capability.summary
        assert row["requires_staff_confirmation"] is capability.requires_staff_confirmation
        assert row["allowed_authors"] == [author.value for author in capability.allowed_authors]


def test_capability_registry_entries_are_frozen_and_unique():
    names = [capability.name for capability in BERNIE_CAPABILITY_REGISTRY]
    assert len(names) == len(set(names))

    with pytest.raises(FrozenInstanceError):
        BERNIE_CAPABILITY_REGISTRY[0].summary = "mutable"

    for capability in BERNIE_CAPABILITY_REGISTRY:
        assert capability.name and capability.name.isidentifier()
        assert isinstance(capability.tier, BernieCapabilityTier)
        assert capability.summary
        assert all(isinstance(author, DiaryActionAuthor) for author in capability.allowed_authors)
        assert get_bernie_capability(capability.name) is capability

    assert get_bernie_capability("not_a_capability") is None


def test_confirm_capabilities_are_staff_only_and_bridge_to_signed_gate():
    confirm_capabilities = [
        capability for capability in BERNIE_CAPABILITY_REGISTRY
        if capability.tier == BernieCapabilityTier.confirm
    ]
    assert confirm_capabilities

    for capability in confirm_capabilities:
        assert capability.requires_staff_confirmation is True
        assert capability.allowed_authors == (DiaryActionAuthor.staff_ui,)
        assert DiaryActionAuthor.bernie not in capability.allowed_authors

    confirm_booking = get_bernie_capability("confirm_booking")
    assert confirm_booking is not None
    assert DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.bernie_create].endpoint in confirm_booking.implemented_as


def test_non_confirm_capabilities_cannot_claim_write_authority():
    for capability in BERNIE_CAPABILITY_REGISTRY:
        assert not hasattr(capability, "writes_authorized")
        assert not hasattr(capability, "evidence_refs")
        assert not hasattr(capability, "freshness_id")
        if capability.tier == BernieCapabilityTier.read_only:
            assert capability.requires_staff_confirmation is False
        if capability.tier == BernieCapabilityTier.meta:
            assert capability.requires_staff_confirmation is False
        if capability.tier == BernieCapabilityTier.propose:
            assert capability.requires_staff_confirmation is True
            summary = capability.summary.lower()
            assert "proposal" in summary or "prepare" in summary
            assert "writes nothing" in summary or "for staff review" in summary


def test_manifest_outcomes_cover_backend_outcome_enum():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["outcomes"]["kinds"] == [
        outcome.value for outcome in BernieBookingOutcomeKind
    ]
    assert set(manifest["outcomes"]["outcome_session_states"]) == {
        outcome.value for outcome in BernieBookingOutcomeKind
    }
    assert manifest["outcomes"]["authority"] == "deterministic_guard"
    assert "report-only" in manifest["outcomes"]["note"]


def test_manifest_confirmation_sequence_is_the_only_write_boundary():
    manifest = build_bernie_diary_capability_manifest()
    sequence = {entry["type"]: entry for entry in manifest["confirmation_boundaries"]["envelope_sequence"]}

    assert sequence["intent"]["writes_authorized"] is False
    assert sequence["proposal"]["writes_authorized"] is False
    assert sequence["suggestion"]["writes_authorized"] is False
    assert sequence["confirmation"]["writes_authorized"] is True
    assert sequence["confirmation"]["requires_staff_confirmation"] is True
    assert manifest["confirmation_boundaries"]["authority"] == "staff_confirmation_required"


def test_manifest_explicitly_lists_non_authority_boundaries():
    manifest = build_bernie_diary_capability_manifest()
    boundaries = " ".join(manifest["non_authority_boundaries"]).lower()

    assert "rbac" in boundaries
    assert "availability" in boundaries
    assert "signed confirmation evidence" in boundaries
    assert "display copy" in boundaries
    assert "raw patient data" in boundaries


# -----------------------------------------------------------------------------
# Adversarial prompt-consumption tests
# -----------------------------------------------------------------------------

_WRITE_AUTHORITY_PHRASES = frozenset({
    "may create",
    "can create",
    "may book",
    "can book",
    "may write",
    "can write",
    "may update",
    "can update",
    "may cancel",
    "can cancel",
    "may delete",
    "can delete",
    "grants permission",
    "has permission to",
    "is authorized to",
    "has authority to",
})


def _recursive_strings(value: Any) -> list[str]:
    """Yield all leaf string values from a nested dict/list structure."""
    strings: list[str] = []

    def _walk(v: Any) -> None:
        if isinstance(v, str):
            strings.append(v)
        elif isinstance(v, dict):
            for sub in v.values():
                _walk(sub)
        elif isinstance(v, (list, tuple)):
            for item in v:
                _walk(item)

    _walk(value)
    return strings


_MANIFEST_SAFE_SECTIONS = frozenset({
    "authority_statement", "principles", "non_authority_boundaries",
    "schema_version", "name",
})


def _sections_to_scan(manifest: dict) -> dict:
    """Return manifest sections excluding declared safety boundaries."""
    return {k: v for k, v in manifest.items() if k not in _MANIFEST_SAFE_SECTIONS}


# ---- Test 1: Write-authority phrasing ----

def test_adversarial_no_write_authority_phrasing_outside_boundaries():
    """No manifest section outside the explicit authority boundaries should
    use phrasing a model could interpret as granting Bernie write permission."""
    manifest = build_bernie_diary_capability_manifest()
    scan = _sections_to_scan(manifest)
    lower_text = " ".join(_recursive_strings(scan)).lower()

    hits = [phrase for phrase in sorted(_WRITE_AUTHORITY_PHRASES) if phrase in lower_text]
    assert not hits, f"Write-authority phrasing found outside declared boundaries: {hits}"


# ---- Test 2: PHI / credential leakage ----

# SQL patterns only match uppercase keywords so plain-English words like
# "update" in capability summaries are not flagged.
_PHI_LEAKAGE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("bearer_token", re.compile(r"\b[Bb]earer\s+[A-Za-z0-9\-_]+\b")),
    ("password", re.compile(r"\b(passwd|password)\s*[:=]\s*\S", re.IGNORECASE)),
    ("api_key_value", re.compile(r"\b(api_?key|api_?secret)\s*[:=]\s*\S", re.IGNORECASE)),
    ("secret_key_value", re.compile(r"\bsecret_?key\s*[:=]\s*\S", re.IGNORECASE)),
    # Uppercase SQL keyword followed by SQL-like identifier
    ("raw_sql", re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|DROP)\s+[A-Z_`\"\[]")),
    ("create_table_sql", re.compile(r"CREATE\s+TABLE\s+")),
]


def test_adversarial_no_phi_or_credential_leakage():
    """The manifest must not contain credential values, raw SQL, or DB table
    references that could leak PHI or backend internals to the prompt."""
    manifest = build_bernie_diary_capability_manifest()
    all_strings = _recursive_strings(manifest)

    for label, pattern in _PHI_LEAKAGE_PATTERNS:
        for s in all_strings:
            if pattern.search(s):
                pytest.fail(
                    f"PHI/leakage pattern '{label}' matched in manifest value: {s!r}"
                )


# ---- Test 3: Source fields are paths/endpoints, not code blocks ----

_SOURCE_FIELDS = {"source", "implemented_as"}


def test_adversarial_source_fields_are_module_paths_not_code_blocks():
    """Every 'source' or 'implemented_as' field must name a module path,
    URL endpoint, or human-readable description — never embedded code
    blocks, SQL, or file contents."""
    manifest = build_bernie_diary_capability_manifest()

    def _walk_source(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                _walk_source(v, f"{path}.{k}")
            for key in _SOURCE_FIELDS & value.keys():
                text = value[key]
                if text is None:
                    continue  # planned, not yet implemented
                assert isinstance(text, str), (
                    f"Unexpected non-string source at {path}.{key}: {text!r}"
                )
                assert "\n" not in text, (
                    f"Source field at {path}.{key} contains a line break: {text!r}"
                )
                assert not text.strip().startswith(("def ", "class ", "import ")), (
                    f"Source field at {path}.{key} starts with Python code: {text!r}"
                )
        elif isinstance(value, (list, tuple)):
            for idx, item in enumerate(value):
                _walk_source(item, f"{path}[{idx}]")

    _walk_source(manifest, "manifest")


# ---- Test 4: Non-confirmation envelopes cannot claim write ----

def test_adversarial_non_confirmation_envelopes_cannot_claim_write():
    """Only the 'confirmation' envelope type may have writes_authorized=True."""
    manifest = build_bernie_diary_capability_manifest()
    sequence = manifest["confirmation_boundaries"]["envelope_sequence"]

    for entry in sequence:
        if entry["type"] == "confirmation":
            assert entry["writes_authorized"] is True, (
                "Confirmation envelope itself must have writes_authorized=True"
            )
        else:
            assert entry["writes_authorized"] is False, (
                f"Non-confirmation envelope '{entry['type']}' must have "
                f"writes_authorized=False"
            )


# ---- Test 5: Backend policy bypass phrasing ----

_BYPASS_PHRASES = frozenset({
    "bypass",
    "bypasses",
    "ignore policy",
    "ignore backend",
    "ignore guardrail",
    "may proceed without",
    "waive confirmation",
    "waive evidence",
    "override policy",
    "override guardrail",
    "skip confirmation",
    "skip evidence",
    "skip validation",
    "force create",
    "force book",
})


def test_adversarial_no_backend_policy_bypass_phrasing():
    """The manifest must not contain language that could be parsed as letting
    Bernie override backend policy gates.  The non_authority_boundaries section
    is excluded because it declares prohibitions (e.g. \"must not bypass\")."""
    manifest = build_bernie_diary_capability_manifest()
    scan = _sections_to_scan(manifest)
    lower_text = " ".join(_recursive_strings(scan)).lower()

    hits = [phrase for phrase in sorted(_BYPASS_PHRASES) if phrase in lower_text]
    assert not hits, f"Backend-policy-bypass phrasing found outside boundaries: {hits}"


# ---- Test 6: Capability-tier / author coherence ----

def test_adversarial_capability_tier_author_coherence():
    """Verify coherence rules across the full capability registry."""
    for capability in BERNIE_CAPABILITY_REGISTRY:
        authors = [a.value for a in capability.allowed_authors]

        if capability.tier == BernieCapabilityTier.confirm:
            assert len(authors) == 1, (
                f"confirm cap '{capability.name}' should have exactly one author, got {authors}"
            )
            assert DiaryActionAuthor.staff_ui.value in authors, (
                f"confirm cap '{capability.name}' must allow staff_ui"
            )
            assert DiaryActionAuthor.bernie.value not in authors, (
                f"confirm cap '{capability.name}' must not allow bernie"
            )
            assert capability.requires_staff_confirmation is True

        if capability.tier == BernieCapabilityTier.read_only:
            assert capability.requires_staff_confirmation is False, (
                f"read_only cap '{capability.name}' must have requires_staff_confirmation=False"
            )

        if capability.tier == BernieCapabilityTier.meta:
            assert capability.requires_staff_confirmation is False, (
                f"meta cap '{capability.name}' must have requires_staff_confirmation=False"
            )

        if capability.tier == BernieCapabilityTier.propose:
            assert capability.requires_staff_confirmation is True, (
                f"propose cap '{capability.name}' must have requires_staff_confirmation=True"
            )


# ---- Test 7: Suggestion envelope rejects confirm-grade evidence keys ----

def test_adversarial_suggestion_rejects_confirm_grade_payload_keys():
    """DiaryActionSuggestion must reject payloads containing keys that belong
    only to the confirmation envelope."""
    forbidden_in_payload = {
        "audit_evidence": [],
        "confirmation_evidence": {},
        "staff_confirmed": True,
        "confirmed_at": "2026-01-01T00:00:00",
        "confirmed_by_user_id": "u-1",
        "candidate_freshness_ids": [],
        "fresh_for_turn_ref": "t-1",
        "proposal_freshness_id": "pf-1",
    }
    for key, value in forbidden_in_payload.items():
        with pytest.raises(ValueError, match="confirm-grade evidence"):
            DiaryActionSuggestion(
                author=DiaryActionAuthor.bernie,
                channel="internal",
                action_name="test",
                suggestion_id="s-1",
                title="Test Suggestion",
                reason_code="test",
                payload={key: value},
            )


# ---- Test 8: Schema version boundary ----

def test_adversarial_manifest_schema_version_does_not_collide_with_envelope_versions():
    """Manifest schema version must not match any envelope schema version."""
    manifest_version = MANIFEST_SCHEMA_VERSION
    envelope_versions = {
        "intent": "diary.action.intent.v1",
        "proposal": "diary.action.proposal.v1",
        "confirmation": "diary.action.confirmation.v1",
        "suggestion": "diary.action.suggestion.v1",
    }
    for env_type, env_version in envelope_versions.items():
        assert manifest_version != env_version, (
            f"Manifest schema version {manifest_version} collides with "
            f"{env_type} envelope version {env_version}"
        )


# ---- Test 9: Non-authority boundaries self-consistency ----

def test_adversarial_non_authority_boundaries_self_consistent():
    """Each declared non-authority boundary must be respected by the
    corresponding manifest section."""
    manifest = build_bernie_diary_capability_manifest()
    boundaries_text = " ".join(manifest["non_authority_boundaries"]).lower()

    assert "rbac" in boundaries_text
    for section in ("entities", "capabilities"):
        section_json = json.dumps(manifest.get(section, {})).lower()
        if "rbac" in section_json:
            pytest.fail(f"Section '{section}' contains RBAC language despite boundary")

    assert "availability" in boundaries_text
    outcomes_note = manifest["outcomes"]["note"].lower()
    assert "report-only" in outcomes_note, "Outcomes must disclaim availability authority"

    assert "signed confirmation evidence" in boundaries_text
    assert "display copy" in boundaries_text

    assert "raw patient data" in boundaries_text
    manifest_json = json.dumps(manifest)
    # Only flag concrete PHI patterns (names, DOB, MRN).  The word "patient"
    # itself is a legitimate generic noun in capability descriptions.
    for key in ("margaret", "thompson", "date_of_birth", "mrn", "medicare"):
        for match in re.finditer(rf'\b{re.escape(key)}\b', manifest_json, re.IGNORECASE):
            start = max(0, match.start() - 40)
            snippet = manifest_json[start:match.end() + 40]
            if "app.models" in snippet or "app.schemas" in snippet or "app.services" in snippet:
                continue  # module-path reference, not PHI
            pytest.fail(
                f"Potential concrete-PHI key '{key}' found in manifest JSON "
                f"outside module-path context: ...{snippet}..."
            )


# ---- Test 10: Prompt-injection pattern scan ----

_PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("ignore_previous", re.compile(r"ignore\s+(all\s+)?previous\s+(instructions|prompts|commands)", re.IGNORECASE)),
    ("new_system_prompt", re.compile(r"(new\s+)?system\s+prompt", re.IGNORECASE)),
    ("you_are_now", re.compile(r"you\s+are\s+(now\s+)?(a\s+)?(free|unrestricted|unconstrained|admin|superuser|god)", re.IGNORECASE)),
    ("act_as", re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+)?(bypass|override|admin|superuser)", re.IGNORECASE)),
    ("do_anything", re.compile(r"you\s+can\s+do\s+anything|you\s+have\s+no\s+(limits|restrictions|boundaries)", re.IGNORECASE)),
    ("forget_rules", re.compile(r"forget\s+(all\s+)?(rules|constraints|boundaries|restrictions|limitations)", re.IGNORECASE)),
    ("output_markdown", re.compile(r"output\s+(in\s+)?markdown\s+code\s*block|respond\s+with\s+markdown", re.IGNORECASE)),
    ("print_full", re.compile(r"(print|output|show|return)\s+(the\s+)?(full|complete|entire|whole)\s+(source|code|file|script)", re.IGNORECASE)),
]


def test_adversarial_no_prompt_injection_patterns():
    """The manifest must not contain phrasing exploitable as a prompt-injection
    or jailbreak instruction."""
    manifest = build_bernie_diary_capability_manifest()
    all_strings = _recursive_strings(manifest)
    lower_text = " ".join(all_strings).lower()

    for label, pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(lower_text):
            pytest.fail(
                f"Prompt-injection pattern '{label}' found in manifest: "
                f"matched by {pattern.pattern!r}"
            )
