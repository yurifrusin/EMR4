"""Deterministic fake-provider adversarial tests for manifest prompt evaluation (Sprint R21).

All tests are pure-python with no DB, no Gemini/provider calls, and no PHI.
Simulates what a fake/malicious provider would see or try to exploit when
presented with the Diary Capability Manifest prompt context.
"""

from __future__ import annotations

import json

import pytest

from app.services.diary.capability_manifest import (
    assert_manifest_prompt_safe,
    build_bernie_diary_capability_manifest,
    build_manifest_prompt_context,
    render_manifest_prompt_block,
)


# -----------------------------------------------------------------------
# Category A: Bypass confirmation -- structural resistance tests
# -----------------------------------------------------------------------


def test_fake_provider_no_implicit_write_in_capability_tiers():
    """No compact-context capability item carries a writes_authorized
    flag or suggests self-authorization."""
    ctx = build_manifest_prompt_context()
    for item in ctx["capabilities"]["items"]:
        assert "writes_authorized" not in item, (
            f"Capability '{item['name']}' has writes_authorized in compact context"
        )
        assert "authority" not in item, (
            f"Capability '{item['name']}' has authority field in compact context"
        )


def test_fake_provider_prompt_block_repeats_authority_boundary():
    """The rendered prompt block restates the non-write authority
    boundary at least once beyond the header."""
    block = render_manifest_prompt_block()
    lines = block.splitlines()
    authority_mentions = sum(
        1 for line in lines
        if "cannot authorize writes" in line.lower()
        or "read-only" in line.lower()
    )
    assert authority_mentions >= 2, (
        f"Only {authority_mentions} authority-statement occurrences; "
        "a fake provider could miss the constraint if it appears once."
    )


def test_fake_provider_only_confirmation_entry_claims_write():
    """In compact context, only confirmation envelope entries carry
    writes_authorized=True, and always with staff confirmation."""
    ctx = build_manifest_prompt_context()
    seq = ctx["confirmation_envelope_sequence"]
    confirm_entries = [e for e in seq if e["type"] == "confirmation"]
    assert len(confirm_entries) >= 1
    for entry in seq:
        if entry["type"] == "confirmation":
            assert entry["writes_authorized"] is True
            assert entry["requires_staff_confirmation"] is True
        else:
            assert entry["writes_authorized"] is False, (
                f"Non-confirmation entry '{entry['type']}' has writes_authorized=True"
            )


def test_fake_provider_no_bypass_phrasing_in_prompt_block():
    """The prompt block must not contain bypass-instruction phrasing."""
    block = render_manifest_prompt_block()
    lower = block.lower()
    bypass_patterns = [
        "you may bypass",
        "you can override",
        "ignore the confirmation",
        "skip confirmation",
        "directly commit",
        "skip staff",
        "writes are authorized for all",
        "granting write",
        "allow writes",
    ]
    for pattern in bypass_patterns:
        assert pattern not in lower, (
            f"Bypass phrasing found in prompt block: {pattern!r}"
        )


# -----------------------------------------------------------------------
# Category B: Invent status/reason codes -- bounded-list enforcement
# -----------------------------------------------------------------------


def test_fake_provider_reason_codes_are_bounded_list():
    """Compact context reason codes must exactly match backend enum."""
    ctx = build_manifest_prompt_context()
    manifest_full = build_bernie_diary_capability_manifest()
    compact_codes = set(ctx["reason_codes"]["appointment_status_reason_codes"])
    full_codes = set(manifest_full["reason_codes"]["appointment_status_reason_codes"])
    extra = compact_codes - full_codes
    assert not extra, (
        f"Compact context has reason codes not in full manifest: {extra}"
    )


def test_fake_provider_no_open_ended_code_placeholders():
    """No open-ended or free-text code identifiers in the prompt block."""
    block = render_manifest_prompt_block()
    lower = block.lower()
    placeholder_patterns = [
        "free_text",
        "free text",
        "custom_reason",
        "enter reason",
        "type your reason",
    ]
    for pattern in placeholder_patterns:
        assert pattern not in lower, (
            f"Open-ended code placeholder in prompt block: {pattern!r}"
        )


def test_fake_provider_status_specific_policy_is_present():
    """The status-specific reason-code policy map must be present."""
    ctx = build_manifest_prompt_context()
    policy = ctx["reason_codes"].get("status_specific_reason_code_policy")
    assert policy is not None
    assert isinstance(policy, dict)
    assert len(policy) > 0


# -----------------------------------------------------------------------
# Category C: Leak raw manifest/source -- implementation detail tests
# -----------------------------------------------------------------------


def test_fake_provider_no_source_paths_in_rendered_block():
    """No file paths, module paths, or Python extensions leaked."""
    block = render_manifest_prompt_block()
    lower = block.lower()
    leak_patterns = [
        ".py",
        "/app/",
        "app.services",
        "app/models",
        "/tests/",
        "__init__",
    ]
    for pattern in leak_patterns:
        assert pattern not in lower, (
            f"Source path leak in prompt block: {pattern!r}"
        )


def test_fake_provider_no_python_syntax_in_rendered_block():
    """No Python code syntax leaked into the model-readable block."""
    block = render_manifest_prompt_block()
    syntax_patterns = [
        "def ",
        "import ",
        "self.",
        " -> ",
        "dataclass",
        "frozenset",
    ]
    for pattern in syntax_patterns:
        assert pattern not in block, (
            f"Python syntax leak in prompt block: {pattern!r}"
        )


def test_fake_provider_compact_context_strips_verbose_fields():
    """Verbose source fields (summary, implemented_as, allowed_authors)
    must not appear in compact context capability items."""
    ctx = build_manifest_prompt_context()
    verbose = {"summary", "implemented_as", "allowed_authors"}
    for item in ctx["capabilities"]["items"]:
        for field in verbose:
            assert field not in item, (
                f"Verbose field '{field}' leaked into compact context "
                f"capability '{item['name']}'"
            )


def test_fake_provider_no_implementation_scaffolding_in_capability_names():
    """Capability names must not carry internal scaffolding markers."""
    ctx = build_manifest_prompt_context()
    markers = ["_impl", "_v2", "_internal", "_test", "_deprecated"]
    for item in ctx["capabilities"]["items"]:
        name = item["name"]
        for marker in markers:
            assert marker not in name, (
                f"Scaffolding marker '{marker}' in capability name '{name}'"
            )


# -----------------------------------------------------------------------
# Category D: Claim live availability -- structural guard tests
# -----------------------------------------------------------------------


def test_fake_provider_no_live_data_keys_in_context():
    """Compact context must not contain keys suggesting live or
    session-personalised data."""
    ctx = build_manifest_prompt_context()
    ctx_json = json.dumps(ctx).lower()
    live_key_patterns = [
        '"slots"',
        '"openings"',
        '"today"',
        '"now"',
        '"current_time"',
        '"current_date"',
        '"live"',
        '"real_time"',
        '"available_slots"',
    ]
    for pattern in live_key_patterns:
        assert pattern not in ctx_json, (
            f"Live-data key pattern in compact context JSON: {pattern}"
        )


def test_fake_provider_non_authority_boundaries_cover_availability():
    """Non-authority boundaries must include an availability disclaimer."""
    ctx = build_manifest_prompt_context()
    boundaries_text = " ".join(ctx["non_authority_boundaries"]).lower()
    assert "availability" in boundaries_text


def test_fake_provider_prompt_block_no_live_availability_claim():
    """No live-availability claim phrasing outside the boundaries section."""
    block = render_manifest_prompt_block()
    block_lines = block.splitlines()
    boundary_idx = None
    for i, line in enumerate(block_lines):
        if line.startswith("Non-authority boundaries"):
            boundary_idx = i
            break
    live_claims = [
        "is available",
        "are available",
        "has capacity",
        "has openings",
        "is free",
    ]
    preamble = block_lines[:boundary_idx] if boundary_idx is not None else block_lines
    for line in preamble:
        lower = line.lower()
        for phrase in live_claims:
            assert phrase not in lower, (
                f"Live availability claim in prompt block pre-boundaries: {phrase!r}"
            )


# -----------------------------------------------------------------------
# Category E: Safety assertion adversarial hardening
# -----------------------------------------------------------------------


def test_fake_provider_assert_safe_depth_recursion():
    """Must handle deeply nested dicts without overflow or missed violations."""
    def build_deep(depth):
        result = {"medicare": "2123456701"}
        cur = result
        for _ in range(depth):
            n = {"inner": 1}
            cur["child"] = n
            cur = n
        return result
    deep = build_deep(150)
    with pytest.raises(ValueError, match="medicare"):
        assert_manifest_prompt_safe(deep)


def test_fake_provider_assert_safe_catches_case_mangled_forbidden_keys():
    """Forbidden keys must be caught even when case-mangled."""
    cases = [
        {"Medicare": "x"},
        {"API_KEY": "x"},
        {"Patient_Id": "x"},
        {"First_Name": "x"},
        {"Date_Of_Birth": "x"},
        {"ApiKey": "x"},
        {"MEDICARE": "x"},
    ]
    for payload in cases:
        with pytest.raises(ValueError):
            assert_manifest_prompt_safe(payload)


def test_fake_provider_assert_safe_nested_write_in_unexpected_section():
    """writes_authorized=True buried in an unrelated section must be caught."""
    poisoned = {
        "reason_codes": {
            "appointment_status_reason_codes": ["CANCELLED_BY_PATIENT"],
            "deep_nested": {
                "inner": {
                    "writes_authorized": True,
                    "type": "not_confirmation",
                }
            }
        }
    }
    with pytest.raises(ValueError, match="write authority"):
        assert_manifest_prompt_safe(poisoned)


def test_fake_provider_assert_safe_string_write_flag_not_confused():
    """String True must not trip writes_authorized; only boolean True."""
    payload = {"section": {"writes_authorized": "True"}}
    assert_manifest_prompt_safe(payload)


# -----------------------------------------------------------------------
# Category F: Self-consistency and structural invariants
# -----------------------------------------------------------------------


def test_fake_provider_policy_statuses_are_subset_of_entity_list():
    """Every status in the reason-code policy must be a known appointment
    status. Only terminal/cancellation statuses have reason code policies."""
    ctx = build_manifest_prompt_context()
    statuses = set(ctx["entities"]["appointment_statuses"])
    policy = ctx["reason_codes"]["status_specific_reason_code_policy"]
    extra = set(policy.keys()) - statuses
    assert not extra, f"Policy has statuses not in entity list: {extra}"
    assert len(policy) > 0, "Status-specific policy is empty"


def test_fake_provider_rendered_block_starts_with_manifest_banner():
    """Rendered block must start with a read-only manifest marker."""
    block = render_manifest_prompt_block()
    assert block.startswith("=== Bernie Diary Capability Manifest")
    assert "(read-only context)" in block.splitlines()[0]


def test_fake_provider_full_manifest_compact_field_contract():
    """Every expected compact field is present; no accidental omissions."""
    manifest = build_bernie_diary_capability_manifest()
    ctx = build_manifest_prompt_context()
    mf = set(manifest["capabilities"]["items"][0].keys())
    cf = set(ctx["capabilities"]["items"][0].keys())
    expected_compact = {"name", "tier", "requires_staff_confirmation"}
    expected_verbose = {"summary", "implemented_as", "allowed_authors", "authority"}
    extra = cf - expected_compact
    assert not extra, f"Unexpected fields in compact items: {extra}"
    still_in_manifest = mf & expected_verbose
    assert still_in_manifest == expected_verbose
