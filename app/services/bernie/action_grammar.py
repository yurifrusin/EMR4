"""Compatibility facade for the diary-domain action grammar contract."""

from app.services.diary.action_grammar import (
    DIARY_ACTION_GRAMMAR,
    GRAMMAR_SCHEMA_VERSION,
    DiaryActionVerb,
    DiaryActionVerbDescriptor,
    action_verb_for_envelope,
    assert_grammar_consistency,
    get_verb_descriptor,
)

__all__ = [
    "GRAMMAR_SCHEMA_VERSION",
    "DiaryActionVerb",
    "DiaryActionVerbDescriptor",
    "DIARY_ACTION_GRAMMAR",
    "get_verb_descriptor",
    "action_verb_for_envelope",
    "assert_grammar_consistency",
]
