"""Deterministic tests for the Bernie manifest prompt-consumption gate (Sprint R20).

All tests are pure-python with no DB, no Gemini/provider calls, and no PHI.
"""

from __future__ import annotations

import json

import pytest

from app.services.diary.capability_manifest import (
    MANIFEST_PROMPT_CONTEXT_MAX_CHARS,
    assert_manifest_prompt_safe,
    build_bernie_diary_capability_manifest,
    build_manifest_prompt_context,
    render_manifest_prompt_block,
)


def test_prompt_context_is_json_serializable_and_round_trips():
    ctx = build_manifest_prompt_context()
    serialized = json.dumps(ctx)
    assert json.loads(serialized) == ctx


def test_prompt_context_is_deterministic():
    assert build_manifest_prompt_context() == build_manifest_prompt_context()


def test_prompt_context_within_char_budget():
    ctx = build_manifest_prompt_context()
    size = len(json.dumps(ctx))
    assert size <= MANIFEST_PROMPT_CONTEXT_MAX_CHARS, (
        f"Manifest prompt context is {size} chars, exceeds budget of {MANIFEST_PROMPT_CONTEXT_MAX_CHARS}"
    )


def test_prompt_context_materially_smaller_than_full_manifest():
    compact_size = len(json.dumps(build_manifest_prompt_context()))
    full_size = len(json.dumps(build_bernie_diary_capability_manifest()))
    assert compact_size < full_size * 0.8, (
        f"Compact context ({compact_size}) is not materially smaller than full manifest ({full_size})"
    )


def test_prompt_context_no_phi_or_credential_keys():
    ctx = build_manifest_prompt_context()

    phi_credential_markers = {
        "medicare", "dob", "date_of_birth", "phone", "first_name", "last_name",
        "given_name", "family_name", "address", "patient_id",
        "credential", "token", "secret", "password", "api_key", "apikey",
        "private_key", "signing_key",
    }

    def collect_keys(obj: object, found: set[str]) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                found.add(k.lower())
                collect_keys(v, found)
        elif isinstance(obj, list):
            for item in obj:
                collect_keys(item, found)

    all_keys: set[str] = set()
    collect_keys(ctx, all_keys)

    bad = phi_credential_markers & all_keys
    assert not bad, f"Prompt context has forbidden key(s): {bad}"


def test_prompt_context_writes_authorized_only_for_labelled_confirmation_entry():
    ctx = build_manifest_prompt_context()
    seq = ctx["confirmation_envelope_sequence"]

    confirm_entries = [e for e in seq if e["type"] == "confirmation"]
    assert len(confirm_entries) == 1
    assert confirm_entries[0]["writes_authorized"] is True
    assert confirm_entries[0]["requires_staff_confirmation"] is True

    for entry in seq:
        if entry["type"] != "confirmation":
            assert entry["writes_authorized"] is False, (
                f"Non-confirmation entry '{entry['type']}' has writes_authorized=True"
            )


def test_assert_safe_raises_on_phi_key_medicare():
    with pytest.raises(ValueError, match="medicare"):
        assert_manifest_prompt_safe({"patient_info": {"medicare": "2123456701"}})


def test_assert_safe_raises_on_credential_key():
    with pytest.raises(ValueError, match="api_key"):
        assert_manifest_prompt_safe({"provider_config": {"api_key": "sk-test"}})


def test_assert_safe_raises_on_unexpected_write_authority():
    poisoned: dict = {"some_field": {"writes_authorized": True}}
    with pytest.raises(ValueError, match="write authority"):
        assert_manifest_prompt_safe(poisoned)


def test_assert_safe_write_authority_allowed_for_proper_confirmation_entry():
    proper = {
        "confirmation_envelope_sequence": [
            {"type": "confirmation", "writes_authorized": True, "requires_staff_confirmation": True},
        ]
    }
    assert_manifest_prompt_safe(proper)


def test_assert_safe_raises_when_confirmation_missing_staff_flag():
    unlabelled = {
        "confirmation_envelope_sequence": [
            {"type": "confirmation", "writes_authorized": True},
        ]
    }
    with pytest.raises(ValueError, match="write authority"):
        assert_manifest_prompt_safe(unlabelled)


def test_assert_safe_passes_on_real_context():
    ctx = build_manifest_prompt_context()
    assert_manifest_prompt_safe(ctx)


def test_render_manifest_prompt_block_is_string_with_authority_statement():
    block = render_manifest_prompt_block()
    assert isinstance(block, str)
    assert "cannot authorize writes" in block


def test_render_manifest_prompt_block_is_deterministic():
    assert render_manifest_prompt_block() == render_manifest_prompt_block()


def test_render_manifest_prompt_block_accepts_prebuilt_context():
    ctx = build_manifest_prompt_context()
    assert render_manifest_prompt_block(context=ctx) == render_manifest_prompt_block()


def test_render_manifest_prompt_block_contains_capability_names():
    ctx = build_manifest_prompt_context()
    block = render_manifest_prompt_block(context=ctx)
    for item in ctx["capabilities"]["items"]:
        assert item["name"] in block, f"Capability '{item['name']}' missing from prompt block"


def test_prompt_context_strips_verbose_fields_from_capability_items():
    ctx = build_manifest_prompt_context()
    for item in ctx["capabilities"]["items"]:
        assert "summary" not in item, "Compact context must not carry verbose 'summary' field"
        assert "implemented_as" not in item, "Compact context must not carry verbose 'implemented_as' field"
        assert "allowed_authors" not in item, "Compact context must not carry verbose 'allowed_authors' field"


def test_full_manifest_items_still_have_verbose_fields():
    manifest = build_bernie_diary_capability_manifest()
    assert all("summary" in item for item in manifest["capabilities"]["items"])
    assert all("implemented_as" in item for item in manifest["capabilities"]["items"])


def test_build_manifest_prompt_context_does_not_mutate_full_manifest():
    manifest_before = build_bernie_diary_capability_manifest()
    build_manifest_prompt_context()
    manifest_after = build_bernie_diary_capability_manifest()
    assert manifest_before == manifest_after
